package publicquality

import (
	"os"
	"os/exec"

	"github.com/Everloster/EverAgent/packages/everagent-core/processtree"
)

// Pre-open type validation rejects non-files; os.Root contains the path and
// the opened inode is checked again by openRootFile.
func openInput(root *os.Root, name string) (*os.File, error) {
	return root.Open(name)
}

func runCheckProcess(cmd *exec.Cmd) error {
	return processtree.Run(cmd)
}
