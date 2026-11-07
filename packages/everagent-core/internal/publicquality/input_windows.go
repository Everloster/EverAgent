package publicquality

import (
	"errors"
	"os"
	"os/exec"
)

// Pre-open type validation rejects non-files; os.Root contains the path and
// the opened inode is checked again by openRootFile.
func openInput(root *os.Root, name string) (*os.File, error) {
	return root.Open(name)
}

func runCheckProcess(cmd *exec.Cmd) error {
	// Do not start tests until a race-free Windows Job Object adapter exists.
	// Killing only the Go parent would leave its test executables running.
	return errors.New("Windows检查进程树回收尚未实现；未启动Go子进程。")
}
