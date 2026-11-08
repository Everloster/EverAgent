//go:build windows

package core

import (
	"encoding/binary"
	"errors"
	"os"
	"path/filepath"
	"runtime"
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

type processBasicInformation struct {
	ExitStatus                   uintptr
	PebBaseAddress               uintptr
	AffinityMask                 uintptr
	BasePriority                 uintptr
	UniqueProcessID              uintptr
	InheritedFromUniqueProcessID uintptr
}

func readProcessMemory(process windows.Handle, address uintptr, size uint32) ([]byte, error) {
	if address == 0 || size == 0 {
		return nil, errors.New("process memory address unavailable")
	}
	buffer := make([]byte, int(size))
	var read uintptr
	if err := windows.ReadProcessMemory(process, address, &buffer[0], uintptr(size), &read); err != nil {
		return nil, err
	}
	if read != uintptr(size) {
		return nil, errors.New("process memory read incomplete")
	}
	return buffer, nil
}

func processCwd(p Process) (string, error) {
	if runtime.GOARCH != "amd64" {
		return "", errors.New("Windows native cwd requires amd64")
	}
	process, err := windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION|windows.PROCESS_VM_READ, false, uint32(p.PID))
	if err != nil {
		return "", err
	}
	defer windows.CloseHandle(process)
	var basic processBasicInformation
	if err = windows.NtQueryInformationProcess(process, windows.ProcessBasicInformation, unsafe.Pointer(&basic), uint32(unsafe.Sizeof(basic)), nil); err != nil {
		return "", err
	}
	parametersBytes, err := readProcessMemory(process, basic.PebBaseAddress+0x20, uint32(unsafe.Sizeof(uintptr(0))))
	if err != nil {
		return "", err
	}
	parameters := uintptr(binary.LittleEndian.Uint64(parametersBytes))
	directoryBytes, err := readProcessMemory(process, parameters+0x38, 16)
	if err != nil {
		return "", err
	}
	length := binary.LittleEndian.Uint16(directoryBytes[:2])
	buffer := uintptr(binary.LittleEndian.Uint64(directoryBytes[8:16]))
	if length == 0 || length%2 != 0 || length > 32766 {
		return "", errors.New("process cwd length invalid")
	}
	utf16, err := readProcessMemory(process, buffer, uint32(length))
	if err != nil {
		return "", err
	}
	values := make([]uint16, int(length)/2)
	for index := range values {
		values[index] = binary.LittleEndian.Uint16(utf16[index*2:])
	}
	cwd := windows.UTF16ToString(values)
	if !filepath.IsAbs(cwd) {
		return "", errors.New("process cwd is not absolute")
	}
	return cwd, nil
}
