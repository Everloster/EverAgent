// everagent-identity is the standalone public core. The private eacli imports
// the same package; neither entry starts a language interpreter or helper.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	core "github.com/Everloster/EverAgent/packages/everagent-core"
)

func run(args []string) int {
	action := "inspect"
	if len(args) > 0 && args[0] == "--version" {
		fmt.Println(core.Version)
		return 0
	}
	if len(args) > 0 && args[0] != "" && args[0][0] != '-' {
		action, args = args[0], args[1:]
	}
	flags := flag.NewFlagSet("everagent-identity "+action, flag.ContinueOnError)
	flags.Bool("json", false, "structured output (also the default)")
	confirmed := flags.Bool("user-confirmed", false, "facts explicitly supplied by the user")
	ttl := flags.Int("ttl-seconds", 14400, "declaration lifetime, 300–43200 seconds")
	model := flags.String("model", "", "explicitly user-supplied model")
	harness := flags.String("harness", "", "explicitly user-supplied harness")
	form := flags.String("form", "", "explicitly user-supplied cli, desktop, or web form")
	if err := flags.Parse(args); err != nil || len(flags.Args()) != 0 {
		return 2
	}
	if action != "inspect" && action != "diagnose" && action != "declare" && action != "declare-model" {
		fmt.Fprintln(os.Stderr, "use inspect, diagnose, declare, or --version")
		return 2
	}
	i, err := core.NewInspector()
	var value core.Object
	code := 0
	if err == nil {
		switch action {
		case "inspect":
			value = i.Inspect()
		case "diagnose":
			value = i.Diagnose()
		default:
			fields := core.Object{}
			for key, v := range map[string]string{"model": *model, "harness": *harness, "form": *form} {
				if v != "" {
					fields[key] = v
				}
			}
			observed := i.Inspect()
			facts := core.Object{}
			if observed["cli_source"] == "process-ancestry" || observed["cli_source"] == "runtime-environment" {
				facts["harness"] = observed["cli"]
			}
			if observed["current_model_confirmed"] == true {
				facts["model"] = observed["model"]
			}
			value, err = i.DeclareFacts(fields, *confirmed, *ttl, facts)
		}
	}
	if err != nil {
		value, code = core.Object{"status": "unavailable", "error": err.Error()}, 2
	}
	e := json.NewEncoder(os.Stdout)
	e.SetEscapeHTML(false)
	if err := e.Encode(value); err != nil {
		return 1
	}
	return code
}

func main() { os.Exit(run(os.Args[1:])) }
