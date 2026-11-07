package publicquality

import (
	"errors"
	"fmt"
	"strings"

	jsonschema "github.com/santhosh-tekuri/jsonschema/v6"
)

const scriptCatalogPath = "scripts/script-catalog.json"
const scriptIndexPath = "scripts/SCRIPT_INDEX.md"
const scriptGenerator = moduleDir + "/internal/publicquality/script_catalog.go"
const scriptSchema = moduleDir + "/src/everagent_core/schemas/script-catalog-v1.json"

// ScriptCatalog reuses the existing schema and describes whole Go entries,
// not another registry of individual commands or private runtime facts.
func ScriptCatalog(s *Snapshot) (Object, []Finding) {
	f := findingList{file: scriptCatalogPath, items: []Finding{}}
	b, err := s.Bytes(scriptCatalogPath, 256<<10)
	if err != nil {
		return nil, []Finding{issue(scriptCatalogPath, "SCRIPT_CATALOG", "脚本描述目录不可读。")}
	}
	raw, err := DecodeJSON(b)
	value := obj(raw)
	schema, schemaErr := JSON(s, scriptSchema)
	compiler := jsonschema.NewCompiler()
	compiler.UseLoader(offlineSchemas{})
	const id = "https://quality.invalid/script-catalog-v1.json"
	if err != nil || schemaErr != nil || compiler.AddResource(id, schema) != nil {
		return value, []Finding{issue(scriptCatalogPath, "SCRIPT_CATALOG", "脚本描述或schema无效。")}
	}
	compiled, err := compiler.Compile(id)
	if err != nil || compiled.Validate(value) != nil {
		return value, []Finding{issue(scriptCatalogPath, "SCRIPT_CATALOG", "脚本描述不符合既有schema。")}
	}
	f.require(value["repository"] == "EverAgent" && nonempty(value["scope"]), "SCRIPT_REPOSITORY", "公共目录必须绑定本仓。")
	ids, paths := map[string]bool{}, map[string]bool{}
	localFile := func(p string) bool {
		if !safePath(p) || strings.Contains(p, ":") {
			return false
		}
		_, err := s.Bytes(p, TextLimit)
		return err == nil
	}
	for _, raw := range array(value["scripts"]) {
		row := obj(raw)
		id := str(row["id"])
		f.require(!ids[id], "SCRIPT_ID", "脚本id重复。")
		ids[id] = true
		for _, field := range []string{"input", "output", "scope"} {
			f.require(nonempty(row[field]), "SCRIPT_CONTRACT", "脚本缺输入、输出或边界。")
		}
		entries := []string{str(row["entrypoint"])}
		for _, alias := range array(row["aliases"]) {
			entries = append(entries, str(obj(alias)["path"]))
		}
		for _, p := range entries {
			f.require(!paths[p] && localFile(p), "SCRIPT_ENTRY", "脚本入口/兼容名重复、越界或不可读。")
			paths[p] = true
		}
		for _, field := range []string{"owner", "authorization"} {
			ref := obj(row[field])
			f.require(ref["repository"] == value["repository"] && localFile(str(ref["path"])), "SCRIPT_OWNER", "公共脚本的owner/授权须在本仓且可读。")
			if field == "authorization" {
				f.require(nonempty(ref["section"]), "SCRIPT_AUTHORIZATION", "脚本授权缺操作/章节说明。")
			}
		}
	}
	return value, f.items
}

func GeneratedScriptIndex(s *Snapshot) ([]byte, []Finding) {
	value, findings := ScriptCatalog(s)
	if !noErrors(findings) {
		return nil, findings
	}
	source, _ := s.Bytes(scriptCatalogPath, 256<<10)
	generator, err := s.Bytes(scriptGenerator, TextLimit)
	if err != nil {
		return nil, []Finding{issue(scriptGenerator, "SCRIPT_GENERATOR", "脚本索引生成器不可读。")}
	}
	var b strings.Builder
	fmt.Fprintf(&b, "# 脚本目录\n\n> Generated from script-catalog.json; do not edit by hand.\n> source-sha256: `%s`\n> generator-sha256: `%s`\n\n| ID | 入口 | 描述 | 范围 |\n|---|---|---|---|\n", digest(source), digest(generator))
	for _, raw := range array(value["scripts"]) {
		row := obj(raw)
		fmt.Fprintf(&b, "| `%s` | `%s` | %s | %s |\n", row["id"], row["entrypoint"], mdCell(str(row["description"])), mdCell(str(row["scope"])))
		for _, raw := range array(row["aliases"]) {
			alias := obj(raw)
			fmt.Fprintf(&b, "| ↳ compatibility | `%s` | %s | 同 canonical |\n", alias["path"], mdCell(str(alias["description"])))
		}
	}
	return []byte(b.String()), findings
}

func CheckScriptIndex(s *Snapshot) []Finding {
	expected, findings := GeneratedScriptIndex(s)
	if !noErrors(findings) {
		return findings
	}
	actual, err := s.Bytes(scriptIndexPath, TextLimit)
	if err != nil || string(actual) != string(expected) {
		return append(findings, issue(scriptIndexPath, "SCRIPT_INDEX_STALE", "脚本索引需用ea-quality index --write更新。"))
	}
	return findings
}

func scriptIndexForWrite(s *Snapshot) ([]byte, error) {
	b, findings := GeneratedScriptIndex(s)
	if !noErrors(findings) {
		return nil, errors.New("script-catalog-invalid")
	}
	return b, nil
}
