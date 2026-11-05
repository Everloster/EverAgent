//go:build windows

package core

import (
	"errors"
	"os"
	"path/filepath"
	"strconv"
	"time"
	"unsafe"

	"golang.org/x/sys/windows"
)

func ownedFile(s os.FileInfo, private bool) bool { return true } // ACLs, not POSIX mode bits, govern Windows files.
func readProcess(pid int) (Process, error) {
	// Toolhelp supplies parent IDs; only the selected ancestor's image and
	// creation time are opened. No unrelated command lines or environments.
	snap, e := windows.CreateToolhelp32Snapshot(windows.TH32CS_SNAPPROCESS, 0)
	if e != nil {
		return Process{}, e
	}
	defer windows.CloseHandle(snap)
	entry := windows.ProcessEntry32{Size: uint32(unsafe.Sizeof(windows.ProcessEntry32{}))}
	e = windows.Process32First(snap, &entry)
	for e == nil && int(entry.ProcessID) != pid {
		e = windows.Process32Next(snap, &entry)
	}
	if e != nil {
		return Process{}, errors.New("ancestor unavailable")
	}
	h, e := windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION, false, uint32(pid))
	if e != nil {
		return Process{}, e
	}
	defer windows.CloseHandle(h)
	var created, exited, kernel, user windows.Filetime
	if e = windows.GetProcessTimes(h, &created, &exited, &kernel, &user); e != nil {
		return Process{}, e
	}
	b := make([]uint16, 32768)
	size := uint32(len(b))
	if e = windows.QueryFullProcessImageName(h, 0, &b[0], &size); e != nil {
		return Process{}, e
	}
	image := windows.UTF16ToString(b[:size])
	ticks := uint64(created.HighDateTime)<<32 | uint64(created.LowDateTime)
	at := time.Unix(0, created.Nanoseconds())
	return Process{PID: pid, Parent: int(entry.ParentProcessID), Image: image, Name: filepath.Base(image), Started: strconv.FormatUint(ticks, 10), StartTime: at}, nil
}
func processArgs(pid int) ([]string, error) {
	return nil, errors.New("Windows native argv reader is not yet supported")
}
func processCwd(p Process) (string, error) {
	return "", errors.New("Windows native cwd reader is not yet supported")
}
