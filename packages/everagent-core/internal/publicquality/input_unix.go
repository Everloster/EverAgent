//go:build !windows

package publicquality

import (
	"errors"
	"os"
	"os/exec"
	"syscall"
	"time"
)

func openInput(root *os.Root, name string) (*os.File, error) {
	return root.OpenFile(name, os.O_RDONLY|syscall.O_NONBLOCK|syscall.O_NOFOLLOW, 0)
}

// Tests run in a disposable process group. This is lifecycle containment, not
// a sandbox against code that deliberately starts a new session/group.
func runCheckProcess(cmd *exec.Cmd) error {
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	cmd.Cancel = func() error {
		if cmd.Process == nil {
			return os.ErrProcessDone
		}
		err := syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
		if errors.Is(err, syscall.ESRCH) {
			return os.ErrProcessDone
		}
		return err
	}
	err := cmd.Run()
	if cmd.Process == nil {
		return err
	}
	// Also reap ordinary descendants left by a parent that exited normally.
	// cmd.Wait only observes the parent; closed stdout is not exit evidence.
	pid := cmd.Process.Pid
	if e := syscall.Kill(-pid, syscall.SIGKILL); errors.Is(e, syscall.ESRCH) {
		return err
	} else if e != nil {
		return errors.Join(err, errProcessCleanup)
	}
	deadline := time.Now().Add(2 * time.Second)
	for time.Now().Before(deadline) {
		if e := syscall.Kill(-pid, 0); errors.Is(e, syscall.ESRCH) {
			if err == nil {
				return errors.New("Go检查遗留了子进程，已回收；检查未通过。")
			}
			return err
		} else if e != nil {
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	return errors.Join(err, errProcessCleanup)
}
