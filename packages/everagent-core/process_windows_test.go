//go:build windows

package core

import (
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func TestWindowsKimiInstallationAndGitBashScope(t *testing.T) {
	i, _ := testInspector(t, "kimi-cli")
	i.Processes[0].Name = "bash.exe"
	i.Processes[0].Image = `C:\Program Files\Git\bin\bash.exe`
	i.Processes[1].Name = "kimi.exe"
	i.Processes[1].Image = `D:\sdk\.kimi-code\bin\kimi.exe`
	if harness, _ := i.detectHarness(); harness != "kimi-cli" {
		t.Fatalf("Kimi installation was not recognized: %q", harness)
	}
	if scope := i.scope("kimi-cli"); scope == nil || scope["execution_ref"] == nil {
		t.Fatal("Git Bash execution scope was not bound")
	}
	i.Processes[1].Image = `D:\sdk\Downloads\kimi.exe`
	if harness, _ := i.detectHarness(); harness != "" {
		t.Fatal("untrusted Kimi executable path was accepted")
	}
}

func TestProcessCwdCurrentProcess(t *testing.T) {
	wd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	want := realPath(wd)
	got, err := processCwd(Process{PID: os.Getpid()})
	if err != nil {
		t.Fatal(err)
	}
	if realPath(got) != want {
		t.Fatalf("cwd mismatch: got %q want %q", got, want)
	}
}

func TestProcessCwdChildProcess(t *testing.T) {
	directory := t.TempDir()
	command := exec.Command("cmd.exe", "/c", "ping", "-n", "5", "127.0.0.1", ">", "NUL")
	command.Dir = directory
	if err := command.Start(); err != nil {
		t.Fatal(err)
	}
	defer func() {
		_ = command.Process.Kill()
		_, _ = command.Process.Wait()
	}()
	got, err := processCwd(Process{PID: command.Process.Pid})
	if err != nil {
		t.Fatal(err)
	}
	want := realPath(directory)
	if realPath(got) != filepath.Clean(want) {
		t.Fatalf("child cwd mismatch: got %q want %q", got, want)
	}
}
