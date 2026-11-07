package publicquality

import (
	"errors"
	"math"
	"net/netip"
	"net/url"
	"path"
	"regexp"
	"strconv"
	"strings"
	"unicode/utf8"
)

var transcriptStamp = regexp.MustCompile(`^\[(\d+):(\d+):(\d+) -> (\d+):(\d+):(\d+)\]\s*(.*)$`)
var sourceRef = regexp.MustCompile(`^sha256:[0-9a-f]{64}$`)
var privateQuery = regexp.MustCompile(`(?i)token|secret|password|signature|api.?key|auth`)
var compression = regexp.MustCompile(`约 raw 的 ([\d.]+)%`)
var transcriptFields = []string{"transcript_path", "polished_transcript_path", "transcript_audit_path"}
var metricFields = []string{"ok", "size", "sha256", "lines", "segments", "duration_seconds", "max_consecutive_identical", "timestamp_errors", "malformed_lines", "tail_gap_seconds"}

type TranscriptResult struct {
	Metrics  Object    `json:"audit"`
	Findings []Finding `json:"findings"`
}

// Deterministic syntax/repetition checks do not establish semantic completeness.
// No samples or private source paths are included in a public receipt.
func AuditTranscript(data []byte, file string) TranscriptResult {
	out := TranscriptResult{Metrics: Object{"ok": false, "size": len(data), "sha256": digest(data), "duration_seconds": nil}, Findings: []Finding{}}
	if !utf8.Valid(data) {
		out.Findings = append(out.Findings, issue(file, "POD102", "转写不是有效UTF-8。"))
		return out
	}
	text := strings.ReplaceAll(string(data), "\r\n", "\n")
	text = strings.ReplaceAll(text, "\r", "\n")
	lines := strings.Split(text, "\n")
	if lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	malformed, timestampErrors, longest, run, segments := 0, 0, 0, 0, 0
	previousStart, previousEnd, previousText, lastGap := -1, 0, "", 0
	for _, line := range lines {
		m := transcriptStamp.FindStringSubmatch(line)
		if m == nil {
			if strings.TrimSpace(line) != "" {
				malformed++
			}
			continue
		}
		values := make([]int, 6)
		valid := true
		for i := range values {
			n, e := strconv.ParseInt(m[i+1], 10, 32)
			if e != nil || n > 1_000_000 {
				valid = false
			}
			values[i] = int(n)
		}
		if !valid {
			timestampErrors++
			continue
		}
		start, end := values[0]*3600+values[1]*60+values[2], values[3]*3600+values[4]*60+values[5]
		if values[1] >= 60 || values[2] >= 60 || values[4] >= 60 || values[5] >= 60 {
			timestampErrors++
		}
		if end < start {
			timestampErrors++
		}
		if start < previousStart {
			timestampErrors++
		}
		if segments > 0 {
			lastGap = start - previousEnd
		}
		previousStart, previousEnd = start, end
		speech := strings.Join(strings.Fields(m[7]), " ")
		if speech == "" {
			run = 0
		} else if speech == previousText {
			run++
		} else {
			run = 1
		}
		previousText = speech
		longest = max(longest, run)
		segments++
	}
	if segments == 0 {
		out.Findings = append(out.Findings, issue(file, "POD102", "没有带时间戳的转写片段。"))
	} else {
		out.Metrics["duration_seconds"] = previousEnd
	}
	if timestampErrors > 0 {
		out.Findings = append(out.Findings, issue(file, "POD102", "转写时间戳非法、倒置或起点不单调。"))
	}
	if longest > 3 {
		out.Findings = append(out.Findings, issue(file, "POD102", "连续相同文本超过3段。"))
	}
	if malformed > 0 {
		out.Findings = append(out.Findings, warning(file, "POD103", "存在缺少时间戳的非空行；需人工复核。"))
	}
	if lastGap > 30 {
		out.Findings = append(out.Findings, warning(file, "POD103", "最后一段前有超过30秒的间隔；需人工复核。"))
	}
	out.Metrics["ok"] = segments > 0 && timestampErrors == 0 && longest <= 3
	for k, v := range map[string]int{"lines": len(lines), "segments": segments, "max_consecutive_identical": longest, "timestamp_errors": timestampErrors, "malformed_lines": malformed, "tail_gap_seconds": lastGap} {
		out.Metrics[k] = v
	}
	return out
}

func publicSourceURL(raw string) bool {
	u, e := url.Parse(raw)
	if e != nil || u.Scheme != "https" && u.Scheme != "http" || u.Hostname() == "" || u.User != nil || u.Fragment != "" {
		return false
	}
	host := strings.TrimSuffix(strings.ToLower(u.Hostname()), ".")
	if ip, e := netip.ParseAddr(host); e == nil {
		ip = ip.Unmap()
		if !ip.IsGlobalUnicast() || ip.IsPrivate() || ip.IsLoopback() || ip.IsLinkLocalUnicast() || netip.MustParsePrefix("100.64.0.0/10").Contains(ip) {
			return false
		}
	} else if !strings.Contains(host, ".") {
		return false
	}
	for _, suffix := range []string{".local", ".internal", ".localhost", ".ts.net"} {
		if strings.HasSuffix(host, suffix) {
			return false
		}
	}
	query, e := url.ParseQuery(u.RawQuery)
	if e != nil {
		return false
	}
	for key := range query {
		if privateQuery.MatchString(key) {
			return false
		}
	}
	return true
}

func receiptFindings(file string, receipt Object, ref, source string) []Finding {
	f := findingList{file: file}
	if !sameStrings(keys(receipt), []string{"schema_version", "kind", "source_url", "source_ref", "max_consecutive_limit", "audit"}) {
		return []Finding{issue(file, "POD107", "转写收据必须严格符合公开字段白名单。")}
	}
	version, _ := integer(receipt["schema_version"])
	limit, _ := integer(receipt["max_consecutive_limit"])
	f.require(version == 2 && receipt["kind"] == "podcast-transcript-audit", "POD107", "不支持的转写收据版本。")
	f.require(sourceRef.MatchString(ref) && receipt["source_ref"] == ref, "POD107", "收据与原文来源摘要不一致。")
	f.require(publicSourceURL(source) && receipt["source_url"] == source, "POD107", "来源URL不适合公开或与收据不一致。")
	f.require(limit == 3, "POD107", "收据重复阈值与合同不一致。")
	metrics := obj(receipt["audit"])
	if !sameStrings(keys(metrics), metricFields) {
		f.require(false, "POD107", "收据缺少审计指标或包含非公开字段。")
		return f.items
	}
	for _, key := range metricFields {
		if key == "ok" || key == "sha256" {
			continue
		}
		n, ok := number(metrics[key])
		f.require(ok && math.Trunc(n) == n && math.Abs(n) <= math.MaxInt32 && (key == "tail_gap_seconds" || n >= 0), "POD107", "收据指标不是有效整数："+key)
	}
	if len(f.items) > 0 {
		return f.items
	}
	value := func(key string) float64 { n, _ := number(metrics[key]); return n }
	f.require(metrics["sha256"] == strings.TrimPrefix(ref, "sha256:"), "POD107", "指标SHA与来源摘要不一致。")
	f.require(metrics["ok"] == true && value("segments") > 0 && value("timestamp_errors") == 0 && value("max_consecutive_identical") <= 3, "POD107", "收据记录了失败的转写审计。")
	f.require(value("size") > 0 && value("lines") >= value("segments")+value("malformed_lines") && value("segments") >= value("max_consecutive_identical"), "POD107", "转写收据指标互相矛盾。")
	return f.items
}

func transcriptPath(raw string) (string, error) {
	if containsString([]string{"", "null", "none", "~"}, strings.ToLower(raw)) {
		return "", nil
	}
	if !safePath(raw) || strings.Contains(raw, ":") || containsString(strings.Split(raw, "/"), "..") {
		return "", errors.New("unsafe-transcript-path")
	}
	if !strings.HasPrefix(raw, "podcast-learning/") {
		raw = path.Join("podcast-learning", raw)
	}
	return raw, nil
}

func checkPodcast(s *Snapshot, r Report, text string) []Finding {
	f := findingList{file: r.Path, items: []Finding{}}
	paths := map[string]string{}
	for _, key := range transcriptFields {
		p, e := transcriptPath(r.Metadata.String(key))
		if e != nil {
			f.require(false, "POD101", "转写来源路径不安全："+key)
			continue
		}
		if p == "" {
			continue
		}
		row, ok := s.entries[p]
		if !ok || row.Mode != "100644" && row.Mode != "100755" {
			f.require(false, "POD101", "转写来源不是仓内普通文件："+key)
			continue
		}
		paths[key] = p
	}
	var measured Object
	rawPath, polishedPath := paths["transcript_path"], paths["polished_transcript_path"]
	if rawPath != "" {
		data, e := s.Bytes(rawPath, TextLimit)
		if e != nil {
			f.require(false, "POD101", "原始转写未能完整读取。")
		} else {
			result := AuditTranscript(data, rawPath)
			measured = result.Metrics
			f.items = append(f.items, result.Findings...)
		}
	}
	ref, receiptPath := r.Metadata.String("transcript_source_ref"), paths["transcript_audit_path"]
	private := r.Metadata.String("transcript_visibility") == "private"
	if private {
		for _, key := range []string{"transcript_path", "polished_transcript_path"} {
			p, e := transcriptPath(r.Metadata.String(key))
			f.require(e == nil && p == "", "POD107", "私有转写不能声明公开全文路径。")
		}
	}
	if private || ref != "" || receiptPath != "" {
		receipt, e := JSON(s, receiptPath)
		if receiptPath == "" || e != nil {
			f.require(false, "POD107", "私有来源或source_ref缺少可读审计收据。")
		} else {
			findings := receiptFindings(receiptPath, receipt, ref, r.Metadata.String("source_url"))
			f.items = append(f.items, findings...)
			if len(findings) == 0 {
				metrics := obj(receipt["audit"])
				if measured == nil {
					measured = metrics
					f.warn("POD109", "receipt_only：只验证收据结构和来源绑定，未重读私有全文，收据不是签名证明。")
					bad, _ := number(metrics["malformed_lines"])
					gap, _ := number(metrics["tail_gap_seconds"])
					if bad > 0 || gap > 30 {
						f.warn("POD103", "收据记录非时间戳行或尾部间隔，需人工复核。")
					}
				} else {
					for _, key := range metricFields {
						if key == "ok" || key == "sha256" {
							f.require(measured[key] == metrics[key], "POD108", "收据与当前原文实测值不一致。")
						} else {
							a, aOK := number(measured[key])
							b, bOK := number(metrics[key])
							f.require(aOK && bOK && a == b, "POD108", "收据与当前原文实测指标不一致："+key)
						}
					}
				}
			}
		}
	}
	if measured != nil {
		for _, pair := range []struct {
			field, metric string
			tolerance     float64
		}{{"duration_seconds", "duration_seconds", 120}, {"transcript_segments", "segments", 0}} {
			if _, ok := r.Metadata[pair.field]; !ok {
				continue
			}
			n, e := strconv.ParseInt(r.Metadata.String(pair.field), 10, 32)
			actual, ok := number(measured[pair.metric])
			f.require(e == nil && n >= 0, "POD104", "声明的转写指标不是非负整数："+pair.field)
			if e == nil && ok {
				f.require(math.Abs(float64(n)-actual) <= pair.tolerance, "POD104", "声明指标与来源实测值不一致："+pair.field)
			}
		}
	}
	declaration := compression.FindStringSubmatch(text)
	if rawPath != "" && polishedPath != "" {
		raw, re := s.Text(rawPath)
		polished, pe := s.Text(polishedPath)
		if re != nil || pe != nil {
			f.require(false, "POD101", "润色稿或原文未能完整读取。")
		} else {
			n, m := hanzi(raw), hanzi(polished)
			if n > 0 {
				ratio := float64(m) / float64(n) * 100
				if declaration != nil {
					want, e := strconv.ParseFloat(declaration[1], 64)
					f.require(e == nil && math.Abs(want-ratio) <= 2, "POD105", "声明压缩比与全文实测相差超过2个百分点。")
				}
				if ratio < 10 || ratio > 110 {
					f.warn("POD106", "润色稿字数比例异常；需人工核对是否遗漏或扩写。")
				}
			} else if declaration != nil {
				f.warn("POD106", "原文无汉字，不能核实汉字压缩比。")
			}
		}
	} else if declaration != nil {
		f.warn("POD106", "未取得raw/polished全文，压缩比声明未核实。")
	}
	return f.items
}

func hanzi(text string) int {
	n := 0
	for _, r := range text {
		if r >= 0x4e00 && r <= 0x9fff {
			n++
		}
	}
	return n
}
