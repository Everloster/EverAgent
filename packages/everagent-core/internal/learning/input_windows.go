package learning

import (
	"os"

	"golang.org/x/sys/windows"
)

func openFile(root *os.Root, p string) (*os.File, error) { return root.Open(p) }
func singleLink(f *os.File, _ os.FileInfo) bool {
	var info windows.ByHandleFileInformation
	return windows.GetFileInformationByHandle(windows.Handle(f.Fd()), &info) == nil && info.NumberOfLinks == 1
}
