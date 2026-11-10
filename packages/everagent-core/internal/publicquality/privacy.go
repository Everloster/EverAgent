package publicquality

import (
	"bytes"
	"go/ast"
	"go/parser"
	"go/token"
	"net/netip"
	"net/url"
	"path"
	"regexp"
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"
)

type privacyRule struct{ severity, code, pattern, message string }

var privacyRules = []privacyRule{
	{"error", "PRIVATE_KEY", `-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----|-----BEGIN PGP PRIVATE KEY` + ` BLOCK-----`, "发现私钥头；公开文件不得包含私钥正文。"},
	{"error", "ABSOLUTE_HOME_PATH", `(?i)/(?:Users|home)/[^/\\\s"'<>\x60]+|/root(?:[/\\\s"'<>\x60]|$)|[A-Za-z]:[\\/]+Users[\\/]+[^\\/:\s"'<>\x60]+`, "发现个人主目录绝对路径；改成相对路径或抽象描述。"},
	{"error", "URL_CREDENTIAL", `\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/@?#]+@[^\s/?#]+`, "URL包含用户信息；确认是否暴露账号或凭据。"},
	{"error", "CREDENTIAL_VALUE", `(?i)["']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)["']?\s*[:=]\s*["']?[A-Za-z0-9_./+=-]{8,}`, "发现疑似凭据赋值；公开文档应使用占位符。"},
	{"error", "BEARER_TOKEN", `(?i)["']?authorization["']?\s*[:=]\s*["']?bearer\s+[A-Za-z0-9._~+/=-]{8,}`, "发现疑似Bearer Token。"},
	{"error", "KNOWN_TOKEN_PREFIX", `\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b`, "发现具有常见前缀的疑似访问Token。"},
	{"warning", "IP_ADDRESS", `(?:\d{1,3}\.){3}\d{1,3}|(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f:.]*(?:%[A-Za-z0-9_.-]+)?`, "发现IP地址；确认是否适合公开。"},
	{"warning", "EMAIL_ADDRESS", `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`, "发现邮箱地址；确认已获公开授权。"},
	{"warning", "SSH_ENDPOINT", `(?i)\bssh\s+(?:-[^\s]+\s+)*[^\s@]+@[^\s]+|\bssh://[^\s]+|\b(?:scp|sftp)\s+[^\s@]+@[^\s:]+:`, "发现SSH入口；公开案例应移除用户、主机与端口。"},
}
var privacyPatterns = func() []*regexp.Regexp {
	out := []*regexp.Regexp{}
	for _, r := range privacyRules {
		out = append(out, regexp.MustCompile(r.pattern))
	}
	return out
}()

var privateKeyEnd = regexp.MustCompile(`-----END (?:[A-Z0-9 ]+ )?PRIVATE KEY(?: BLOCK)?-----`)
var credentialAssignment = regexp.MustCompile(`[:=]\s*(["']?)(.*)$`)
var plainReference = regexp.MustCompile(`^[A-Za-z_][A-Za-z0-9_]*(?:[.][A-Za-z_][A-Za-z0-9_]*)*$`)

func disclosurePlaceholder(value string) bool {
	v := strings.ToLower(value)
	for _, prefix := range []string{"your_", "your-", "example", "dummy", "placeholder", "redacted", "test_", "test-", "changeme", "<", "${"} {
		if strings.HasPrefix(v, prefix) {
			return true
		}
	}
	return false
}
func definiteDisclosure(code, value string) bool {
	switch code {
	case "PRIVATE_KEY", "KNOWN_TOKEN_PREFIX":
		return true
	case "BEARER_TOKEN":
		parts := strings.Fields(value)
		return len(parts) > 0 && !disclosurePlaceholder(parts[len(parts)-1])
	case "URL_CREDENTIAL":
		u, err := url.Parse(value)
		if err == nil && u.User != nil {
			password, present := u.User.Password()
			return present && password != "" && !disclosurePlaceholder(password)
		}
	case "CREDENTIAL_VALUE":
		m := credentialAssignment.FindStringSubmatch(value)
		if len(m) != 3 || disclosurePlaceholder(m[2]) {
			return false
		}
		// Bare references in code are advice, not proof of an embedded secret.
		return m[1] != "" || !plainReference.MatchString(m[2])
	}
	return false
}

type privacyHit struct {
	finding  Finding
	key      string
	definite bool // High-confidence disclosure, not merely a private-looking example.
}
type span struct{ start, end int }

// Exempt only syntactically parsed Go reference values, never quoted literals
// or fallback secrets. Other languages remain conservatively scanned.
func goReferences(text, file string) []span {
	if path.Ext(file) != ".go" {
		return nil
	}
	fs := token.NewFileSet()
	f, e := parser.ParseFile(fs, file, text, 0)
	if e != nil {
		return nil
	}
	var safe func(ast.Expr) bool
	safe = func(n ast.Expr) bool {
		switch x := n.(type) {
		case *ast.Ident:
			return true
		case *ast.SelectorExpr:
			return safe(x.X)
		case *ast.IndexExpr:
			switch x.Index.(type) {
			case *ast.Ident, *ast.BasicLit:
				return safe(x.X)
			}
		case *ast.CallExpr:
			fn, ok := x.Fun.(*ast.SelectorExpr)
			if !ok || fn.Sel.Name != "Getenv" || len(x.Args) != 1 {
				return false
			}
			base, ok := fn.X.(*ast.Ident)
			arg, literal := x.Args[0].(*ast.BasicLit)
			return ok && base.Name == "os" && literal && arg.Kind == token.STRING
		}
		return false
	}
	spans := []span{}
	ast.Inspect(f, func(n ast.Node) bool {
		var values []ast.Expr
		switch x := n.(type) {
		case *ast.AssignStmt:
			values = x.Rhs
		case *ast.ValueSpec:
			values = x.Values
		case *ast.KeyValueExpr:
			values = []ast.Expr{x.Value}
		}
		for _, v := range values {
			if safe(v) {
				spans = append(spans, span{fs.Position(v.Pos()).Offset, fs.Position(v.End()).Offset})
			}
		}
		return true
	})
	return spans
}
func word(r rune) bool { return unicode.IsLetter(r) || unicode.IsDigit(r) || r == '_' }
func textHits(text, file string, decoded bool) []privacyHit {
	out := []privacyHit{}
	refs := []span{}
	if !decoded {
		refs = goReferences(text, file)
	}
	for i, rule := range privacyRules {
		for _, loc := range privacyPatterns[i].FindAllStringIndex(text, -1) {
			start, end := loc[0], loc[1]
			before := rune(0)
			after := rune(0)
			if start > 0 {
				before, _ = utf8.DecodeLastRuneInString(text[:start])
			}
			if end < len(text) {
				after, _ = utf8.DecodeRuneInString(text[end:])
			}
			if rule.code == "CREDENTIAL_VALUE" && (word(before) || before == '-') {
				continue
			}
			if rule.code == "ABSOLUTE_HOME_PATH" && word(before) {
				continue
			}
			if rule.code == "CREDENTIAL_VALUE" {
				reference := false
				for _, s := range refs {
					if start <= s.start && s.start < end && end <= s.end {
						reference = true
						break
					}
				}
				if reference {
					continue
				}
			}
			value := text[start:end]
			if rule.code == "IP_ADDRESS" {
				if word(before) || word(after) || before == ':' || before == '.' || after == ':' {
					continue
				}
				if _, e := netip.ParseAddr(strings.TrimRight(value, ".")); e != nil {
					continue
				}
			}
			line := 0
			if !decoded {
				line = 1 + strings.Count(text[:start], "\n")
			}
			material := value
			if rule.code == "PRIVATE_KEY" {
				// A changed key body is new disclosure even if its header is unchanged.
				material = text[start:]
				if end := privateKeyEnd.FindStringIndex(material); end != nil {
					material = material[:end[1]]
				}
			}
			key := rule.code + ":" + digest([]byte(material))
			if decoded {
				key += ":decoded"
			}
			out = append(out, privacyHit{finding: Finding{File: file, Line: line, Severity: rule.severity, Code: rule.code, Message: rule.message}, key: key, definite: definiteDisclosure(rule.code, value)})
		}
	}
	return out
}
func contentHits(text, file string) []privacyHit {
	out := textHits(text, file, false)
	if strings.ToLower(path.Ext(file)) != ".json" {
		return out
	}
	value, e := DecodeJSON([]byte(text))
	if e != nil {
		return append(out, privacyHit{finding: issue(file, "INVALID_JSON", "JSON无法完整解析。")})
	}
	var visit func(any)
	visit = func(v any) {
		switch x := v.(type) {
		case string:
			out = append(out, textHits(x, file, true)...)
		case Object:
			keys := []string{}
			for k := range x {
				keys = append(keys, k)
			}
			sort.Strings(keys)
			for _, k := range keys {
				out = append(out, textHits(k, file, true)...)
				if value, ok := x[k].(string); ok {
					out = append(out, textHits(k+"="+value, file, true)...)
				}
				visit(x[k])
			}
		case []any:
			for _, item := range x {
				visit(item)
			}
		}
	}
	visit(value)
	return out
}
func protectedPath(p string) bool {
	n := strings.ToLower(path.Base(p))
	return n == ".env" || strings.HasPrefix(n, ".env.") || containsString([]string{"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}, n) || containsString([]string{".key", ".pem", ".p12", ".pfx"}, path.Ext(n))
}
func containsString(list []string, s string) bool {
	for _, v := range list {
		if s == v {
			return true
		}
	}
	return false
}
func fullTranscript(p string) bool {
	p = strings.ToLower(p)
	for _, suffix := range []string{".transcript.txt", ".polished.txt", ".transcript.md", ".polished.md", ".srt", ".vtt"} {
		if strings.HasSuffix(p, suffix) {
			return true
		}
	}
	return containsString(strings.Split(p, "/"), "transcripts") && containsString([]string{".md", ".txt"}, path.Ext(p)) && !containsString([]string{"readme.md", "index.md"}, path.Base(p))
}
func binaryExtension(p string) bool {
	return containsString([]string{".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".mp4", ".webm", ".ogg", ".mp3"}, strings.ToLower(path.Ext(p)))
}
func knownBinary(b []byte, p string) bool {
	ext := strings.ToLower(path.Ext(p))
	starts := func(s string) bool { return bytes.HasPrefix(b, []byte(s)) }
	if strings.HasPrefix(p, "docs/assets/public/") {
		switch ext {
		case ".mp4":
			return len(b) >= 8 && string(b[4:8]) == "ftyp"
		case ".webm":
			return starts("\x1aE\xdf\xa3")
		case ".ogg":
			return starts("OggS")
		case ".mp3":
			return starts("ID3") || len(b) > 1 && b[0] == 255 && b[1]&224 == 224
		}
	}
	switch ext {
	case ".pdf":
		return starts("%PDF-")
	case ".png":
		return starts("\x89PNG\r\n\x1a\n")
	case ".jpg", ".jpeg":
		return starts("\xff\xd8\xff")
	case ".gif":
		return starts("GIF87a") || starts("GIF89a")
	case ".webp":
		return starts("RIFF") && len(b) >= 12 && string(b[8:12]) == "WEBP"
	case ".ico":
		return starts("\x00\x00\x01\x00")
	}
	return false
}
func publicURL(s string) bool {
	u, e := url.Parse(s)
	return e == nil && (u.Scheme == "http" || u.Scheme == "https") && u.Hostname() != "" && u.User == nil
}
func publicationOK(s *Snapshot, p string, data []byte) bool {
	m, e := JSON(s, p+".publication.json")
	if e != nil || len(m) != 6 {
		return false
	}
	v, ok := integer(m["schema_version"])
	return ok && v == 1 && str(m["sha256"]) == digest(data) && m["maintainer_confirmed"] == true && nonempty(m["permission_note"]) && publicURL(str(m["source_url"])) && publicURL(str(m["permission_url"]))
}

type PrivacyResult struct {
	Selected      int       `json:"files_selected"`
	Scanned       int       `json:"files_scanned"`
	SkippedBinary int       `json:"files_skipped_binary"`
	Existing      int       `json:"existing_occurrences"`
	Findings      []Finding `json:"findings"`
}

func AuditPrivacy(c *Candidate, paths []string) PrivacyResult { return auditPrivacy(c, paths, false) }

// AuditDisclosure scans changed public paths only. Definite new credentials and
// raw-publication violations block; heuristic examples remain visible warnings.
func AuditDisclosure(c *Candidate) PrivacyResult { return auditPrivacy(c, nil, true) }

func auditPrivacy(c *Candidate, paths []string, light bool) PrivacyResult {
	if paths == nil {
		paths = c.Changed
	}
	names := map[string]bool{}
	for _, p := range paths {
		names[p] = true
		if strings.HasSuffix(p, ".publication.json") {
			source := strings.TrimSuffix(p, ".publication.json")
			if fullTranscript(source) {
				names[source] = true
			}
		}
	}
	ordered := []string{}
	for p := range names {
		if c.After.Has(p) {
			ordered = append(ordered, p)
		}
	}
	sort.Strings(ordered)
	out := PrivacyResult{Selected: len(ordered), Findings: []Finding{}}
	for _, p := range ordered {
		template := containsString([]string{".env.example", ".env.sample", ".env.template"}, strings.ToLower(path.Base(p)))
		if protectedPath(p) && !(light && template) {
			out.Findings = append(out.Findings, issue(p, "PROTECTED_FILE", "凭据文件不得进入公开仓库。"))
			continue
		}
		if binaryExtension(p) {
			prefix, e := c.After.Prefix(p, 16)
			if e == nil && knownBinary(prefix, p) {
				out.SkippedBinary++
				continue
			}
		}
		data, e := c.After.Bytes(p, TextLimit)
		if e != nil {
			out.Findings = append(out.Findings, issue(p, "INCOMPLETE_SCAN", "无法完整检查该路径；拒绝发布。"))
			continue
		}
		permission := p + ".publication.json"
		if fullTranscript(p) && (!c.Before.Has(p) || c.Before.Has(permission) || c.After.Has(permission)) && !publicationOK(c.After, p, data) {
			out.Findings = append(out.Findings, issue(p, "FULL_TRANSCRIPT_PUBLICATION", "公开全文需要内容绑定的授权依据和维护者确认；缺少、删除或失效均不能发布。"))
		}
		text, e := c.After.Text(p)
		if e != nil {
			out.Findings = append(out.Findings, issue(p, "INCOMPLETE_SCAN", "需要有界UTF-8文本；未识别二进制不默认放行。"))
			continue
		}
		old := map[string]int{}
		if before, e := c.Before.Text(p); e == nil {
			for _, h := range contentHits(before, p) {
				if h.key != "" && (light || h.finding.Code != "PRIVATE_KEY" && h.finding.Code != "CREDENTIAL_VALUE") {
					old[h.key]++
				}
			}
		}
		out.Scanned++
		for _, h := range contentHits(text, p) {
			if h.key != "" && old[h.key] > 0 {
				old[h.key]--
				out.Existing++
			} else {
				finding := h.finding
				if light && !h.definite {
					finding.Severity = "warning"
				}
				out.Findings = append(out.Findings, finding)
			}
		}
	}
	return out
}
