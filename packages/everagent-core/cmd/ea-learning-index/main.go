// ea-learning-index is the fixed JSON adapter used by the learning app's Node
// host. It reads public files only and never starts a server or a repository script.
package main

import (
	"encoding/json"
	"errors"
	"os"

	"github.com/Everloster/EverAgent/packages/everagent-core/internal/learning"
)

func run(args []string) (learning.Object, error) {
	if len(args) < 2 || len(args) > 3 {
		return nil, errors.New("bad_usage")
	}
	r, err := learning.Open(args[0])
	if err != nil {
		return nil, err
	}
	defer r.Close()
	switch {
	case args[1] == "list" && len(args) == 2:
		return r.List()
	case args[1] == "detail" && len(args) == 3:
		return r.Detail(args[2])
	case args[1] == "asset" && len(args) == 3:
		return r.Asset(args[2])
	default:
		return nil, errors.New("bad_usage")
	}
}
func main() {
	result, err := run(os.Args[1:])
	code := 0
	if err != nil {
		result = learning.Object{"ok": false, "error": err.Error()}
		code = 1
	} else {
		result["ok"] = true
	}
	if json.NewEncoder(os.Stdout).Encode(result) != nil {
		code = 1
	}
	os.Exit(code)
}
