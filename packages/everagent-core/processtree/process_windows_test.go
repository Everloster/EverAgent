//go:build windows

package processtree

import (
	"bytes"
	"context"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
	"time"
)

func TestHelperProcess(t *testing.T) {
	role := os.Getenv("EVERAGENT_PROCESS_HELPER")
	if role == "" {
		return
	}
	if role == "parent" {
		command := exec.Command(os.Args[0], "-test.run=TestHelperProcess")
		command.Env = append(os.Environ(), "EVERAGENT_PROCESS_HELPER=leaf")
		if err := command.Start(); err != nil {
			os.Exit(2)
		}
		os.Exit(0)
	}
	time.Sleep(1500 * time.Millisecond)
	if marker := os.Getenv("EVERAGENT_PROCESS_MARKER"); marker != "" {
		_ = os.WriteFile(marker, []byte("leaked"), 0600)
	}
	os.Exit(0)
}

func helperCommand(role, marker string) *exec.Cmd {
	command := exec.Command(os.Args[0], "-test.run=TestHelperProcess")
	command.Env = append(os.Environ(), "EVERAGENT_PROCESS_HELPER="+role, "EVERAGENT_PROCESS_MARKER="+marker)
	return command
}

func TestRunPreservesOutputAndExitStatus(t *testing.T) {
	var output bytes.Buffer
	command := exec.Command("cmd.exe", "/c", "echo synthetic-output")
	command.Stdout = &output
	if err := Run(command); err != nil {
		t.Fatal(err)
	}
	if output.String() != "synthetic-output\r\n" {
		t.Fatalf("output changed: %q", output.String())
	}
	if err := Run(exec.Command("cmd.exe", "/c", "exit", "7")); err == nil {
		t.Fatal("nonzero command passed")
	} else {
		var exit *exec.ExitError
		if !errors.As(err, &exit) || exit.ExitCode() != 7 {
			t.Fatalf("exit status changed: %v", err)
		}
	}
}

func TestRunReapsDescendantsAfterParentExit(t *testing.T) {
	marker := filepath.Join(t.TempDir(), "descendant-survived")
	err := Run(helperCommand("parent", marker))
	if !errors.Is(err, ErrDescendantsReaped) {
		t.Fatalf("descendant cleanup was not reported: %v", err)
	}
	time.Sleep(2 * time.Second)
	if _, err = os.Stat(marker); !os.IsNotExist(err) {
		t.Fatal("descendant escaped the job")
	}
}

func TestRunContextStopsProcessTree(t *testing.T) {
	marker := filepath.Join(t.TempDir(), "cancelled-process-survived")
	ctx, cancel := context.WithTimeout(t.Context(), 100*time.Millisecond)
	defer cancel()
	command := exec.CommandContext(ctx, os.Args[0], "-test.run=TestHelperProcess")
	command.Env = append(os.Environ(), "EVERAGENT_PROCESS_HELPER=leaf", "EVERAGENT_PROCESS_MARKER="+marker)
	if err := Run(command); err == nil {
		t.Fatal("cancelled command passed")
	}
	time.Sleep(2 * time.Second)
	if _, err := os.Stat(marker); !os.IsNotExist(err) {
		t.Fatal("cancelled process escaped the job")
	}
}
