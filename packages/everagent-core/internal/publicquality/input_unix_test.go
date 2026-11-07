//go:build !windows

package publicquality

import (
	"context"
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"
)

func TestGoStepReapsDescendantsBeforeReturning(t *testing.T) {
	for _, parentExits := range []bool{false, true} {
		t.Run(strconv.FormatBool(parentExits), func(t *testing.T) {
			dir := t.TempDir()
			fifo := filepath.Join(dir, "release-child")
			if err := syscall.Mkfifo(fifo, 0600); err != nil {
				t.Fatal(err)
			}
			pidFile, marker := filepath.Join(dir, "child.pid"), filepath.Join(dir, "late-write")
			script := "#!/bin/sh\n/bin/sh -c 'IFS= read -r value < \"$CHILD_FIFO\"; printf late > \"$CHILD_MARKER\"' &\nprintf '%s\\n' \"$!\" > \"$CHILD_PID_FILE\"\n"
			if !parentExits {
				script += "wait\n"
			}
			if err := os.WriteFile(filepath.Join(dir, "go"), []byte(script), 0700); err != nil {
				t.Fatal(err)
			}
			t.Setenv("PATH", dir)
			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()
			done := make(chan Step, 1)
			go func() {
				done <- goStep(ctx, dir, "fixture", []string{"CHILD_FIFO=" + fifo, "CHILD_MARKER=" + marker, "CHILD_PID_FILE=" + pidFile})
			}()
			var child int
			for child == 0 && ctx.Err() == nil {
				data, _ := os.ReadFile(pidFile)
				child, _ = strconv.Atoi(strings.TrimSpace(string(data)))
				if child == 0 {
					time.Sleep(10 * time.Millisecond)
				}
			}
			if child == 0 {
				t.Fatal("fake Go did not start its test child")
			}
			// This fallback is scoped to this fixture's child, never a broad kill.
			defer syscall.Kill(child, syscall.SIGKILL)
			if !parentExits {
				cancel()
			}
			step := <-done
			if step.Status != "failed" {
				t.Fatalf("cancelled or leaking test passed: %+v", step)
			}
			fd, err := syscall.Open(fifo, syscall.O_WRONLY|syscall.O_NONBLOCK, 0)
			if err == nil {
				_, _ = syscall.Write(fd, []byte("continue\n"))
				_ = syscall.Close(fd)
				t.Fatal("test child still held its input after goStep returned")
			}
			if !errors.Is(err, syscall.ENXIO) {
				t.Fatalf("unexpected pipe state: %v", err)
			}
			if _, err := os.Stat(marker); !os.IsNotExist(err) {
				t.Fatal("descendant wrote after cleanup")
			}
		})
	}
	cmd := exec.CommandContext(context.Background(), "/bin/sh", "-c", "exit 0")
	if err := runCheckProcess(cmd); err != nil {
		t.Fatalf("ordinary completed process rejected: %v", err)
	}
}
