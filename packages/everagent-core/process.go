package core

import (
	"errors"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

type Process struct {
	PID, Parent          int
	Name, Image, Started string
	StartTime            time.Time
}

type Inspector struct {
	Home, Directory string
	Getenv          func(string) string
	Now             func() time.Time
	Rules           map[string]Rule
	Processes       []Process
	ReadProcess     func(int) (Process, error)
	ProcessArgs     func(int) ([]string, error)
	ProcessCwd      func(Process) (string, error)
}

func NewInspector() (*Inspector, error) {
	home, _ := os.UserHomeDir()
	cwd, e := os.Getwd()
	if e != nil {
		return nil, e
	}
	rules, e := readerRules(expandHome(os.Getenv("EVERAGENT_IDENTITY_CONFIG"), home))
	if e != nil {
		return nil, e
	}
	i := &Inspector{Home: home, Directory: realPath(cwd), Getenv: os.Getenv, Now: time.Now, Rules: rules, ReadProcess: readProcess, ProcessArgs: processArgs, ProcessCwd: processCwd}
	pid := os.Getpid()
	seen := map[int]bool{}
	for len(i.Processes) < 16 && pid > 1 && !seen[pid] {
		seen[pid] = true
		p, e := i.ReadProcess(pid)
		if e != nil {
			break
		}
		i.Processes = append(i.Processes, p)
		if p.Parent <= 1 || p.Parent == pid {
			break
		}
		pid = p.Parent
	}
	return i, nil
}

var shells = map[string]bool{"bash": true, "zsh": true, "sh": true, "fish": true, "cmd.exe": true, "powershell.exe": true, "pwsh.exe": true, "pwsh": true}

func appForProcess(p Process, windows bool) string {
	for id, name := range map[string]string{"kimi-desktop": "Kimi", "minimax-code": "MiniMax Code", "zcode": "ZCode"} {
		if !windows && strings.Contains(p.Image, name+".app/Contents/") {
			return id
		}
		if windows {
			parts := strings.Split(strings.ReplaceAll(p.Image, "\\", "/"), "/")
			product := strings.ToLower(strings.ReplaceAll(name, " ", ""))
			executable := strings.ReplaceAll(strings.TrimSuffix(strings.ToLower(p.Name), ".exe"), " ", "")
			for _, part := range parts[:max(0, len(parts)-1)] {
				if strings.ToLower(strings.ReplaceAll(part, " ", "")) == product && (executable == product || strings.HasPrefix(executable, product+"helper")) {
					return id
				}
			}
		}
	}
	return ""
}
func (i *Inspector) matches(p Process, harness string) bool {
	names := i.Rules[harness].ProcessNames
	base := p.Name
	if harness == "dsh" && contains([]string{"node", "mainthread"}, strings.TrimSuffix(strings.ToLower(base), ".exe")) {
		if runtime.GOOS == "windows" || strconv.Itoa(p.PID) != i.Getenv("DSH_RUNTIME_PID") {
			return false
		}
		a, e := i.ProcessArgs(p.PID)
		return e == nil && len(a) >= 3 && strings.HasSuffix(a[1], "/node_modules/@deepseek-ai/dsh/lib/bin.js")
	}
	if runtime.GOOS == "windows" {
		if contains([]string{"kimi-cli", "kimi-desktop", "zcode", "minimax-code"}, harness) {
			app := appForProcess(p, true)
			if app != "" {
				return app == harness
			}
			if harness == "kimi-cli" && strings.EqualFold(strings.TrimSuffix(base, ".exe"), "kimi") {
				path := strings.ToLower(strings.ReplaceAll(p.Image, "\\", "/"))
				for _, part := range []string{"/.local/bin/", "/scripts/", "/kimi-cli/", "/.kimi/bin/"} {
					if strings.Contains(path, part) {
						return true
					}
				}
				return false
			}
			if contains([]string{"kimi-desktop", "minimax-code", "zcode"}, harness) {
				return false
			}
		}
		base = strings.TrimSuffix(strings.ToLower(base), ".exe")
	}
	for _, n := range names {
		if runtime.GOOS == "windows" {
			n = strings.ToLower(n)
		}
		if base == n || n == "zcode-host" && strings.HasPrefix(base, "zcode-host-") || n == "MiniMax Code" && strings.HasPrefix(base, "MiniMax Code Helper") {
			return true
		}
	}
	return false
}
func (i *Inspector) owner(harness string) (Process, bool) {
	if harness == "cowork" {
		harness = "claude-code"
	}
	for _, p := range i.Processes {
		if i.matches(p, harness) {
			return p, true
		}
	}
	return Process{}, false
}
func (i *Inspector) sameProcess(p Process) bool {
	latest, e := i.ReadProcess(p.PID)
	return e == nil && p.Started != "" && latest.Started == p.Started && latest.Name == p.Name && latest.Parent == p.Parent
}
func (i *Inspector) callerCwd(p Process) string {
	if !i.sameProcess(p) {
		return ""
	}
	cwd, e := i.ProcessCwd(p)
	if e != nil || !filepath.IsAbs(cwd) || !i.sameProcess(p) {
		return ""
	}
	return realPath(cwd)
}

func processFromPS(pid int) (Process, error) {
	b, e := boundedCommand("", append(os.Environ(), "LC_ALL=C"), time.Second, 8192, "ps", "-o", "ppid=,lstart=,comm=", "-p", strconv.Itoa(pid))
	if e != nil {
		return Process{}, e
	}
	parts := strings.Fields(string(b))
	if len(parts) < 7 {
		return Process{}, errors.New("ancestor unavailable")
	}
	parent, e := strconv.Atoi(parts[0])
	if e != nil {
		return Process{}, e
	}
	started := strings.Join(parts[1:6], " ")
	at, e := time.ParseInLocation("Mon Jan 2 15:04:05 2006", started, time.Local)
	if e != nil {
		return Process{}, e
	}
	image := strings.Join(parts[6:], " ")
	return Process{PID: pid, Parent: parent, Started: started, StartTime: at, Image: image, Name: filepath.Base(image)}, nil
}
