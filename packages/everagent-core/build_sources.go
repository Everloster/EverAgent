package core

import (
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"io/fs"
)

// This small source manifest lets a checkout-owned quality gate reject a stale
// build or an unstaged implementation. Comparing executable bytes would reject
// normal `go run`, which deliberately omits debug data unlike `go build`.
// The manifest is not an attestation against a deliberately modified checker.
//
//go:embed *.go go.mod go.sum cmd internal processtree src/everagent_core/identity/readers.json src/everagent_core/identity/dsh_plugin.mjs src/everagent_core/identity/opencode_plugin.mjs src/everagent_core/schemas
var buildSources embed.FS

// OpenCodeShellPlugin is the minimal official V1 shell binding adapter. It
// contains no configuration, credentials or model assertions. Installers must
// preserve existing user plugins and explicitly load it in the native config.
func OpenCodeShellPlugin() []byte {
	b, _ := buildSources.ReadFile("src/everagent_core/identity/opencode_plugin.mjs")
	return b
}

// BuildSourceHashes returns module-relative hashes, not a second source tree on
// disk. Test sources are included so the gate also binds the tests it will run.
func BuildSourceHashes() map[string]string {
	out := map[string]string{}
	_ = fs.WalkDir(buildSources, ".", func(p string, entry fs.DirEntry, err error) error {
		if err != nil || entry.IsDir() {
			return err
		}
		b, err := buildSources.ReadFile(p)
		if err != nil {
			return err
		}
		h := sha256.Sum256(b)
		out[p] = hex.EncodeToString(h[:])
		return nil
	})
	return out
}
