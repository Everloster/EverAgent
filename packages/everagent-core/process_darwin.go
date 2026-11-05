//go:build darwin

package core

import (
	"bytes"
	"encoding/binary"
	"errors"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"time"

	"golang.org/x/sys/unix"
)

func ownedFile(s os.FileInfo, private bool) bool {
	st, ok := s.Sys().(*syscall.Stat_t)
	return ok && st.Uid == uint32(os.Getuid()) && (!private || s.Mode().Perm()&0077 == 0)
}
func readProcess(pid int) (Process, error) {
	if p, e := processFromPS(pid); e == nil {
		return p, nil
	}
	// No cgo/helper and no sandbox escape: query the same caller PID through
	// the supported kernel API if the sandbox prohibits spawning set-id ps.
	k, e := unix.SysctlKinfoProc("kern.proc.pid", pid)
	if e != nil || k.Proc.P_pid != int32(pid) || k.Proc.P_starttime.Sec <= 0 {
		return Process{}, errors.New("ancestor unavailable")
	}
	b, e := unix.SysctlRaw("kern.procargs2", pid)
	if e != nil || len(b) < 5 || len(b) > 1<<20 {
		return Process{}, errors.New("ancestor image unavailable")
	}
	end := bytes.IndexByte(b[4:], 0)
	if end < 0 {
		return Process{}, errors.New("ancestor image unavailable")
	}
	image := string(b[4 : 4+end])
	at := time.Unix(k.Proc.P_starttime.Sec, 0)
	return Process{PID: pid, Parent: int(k.Eproc.Ppid), Started: strings.Join(strings.Fields(at.Local().Format("Mon Jan _2 15:04:05 2006")), " "), StartTime: at, Name: filepath.Base(image), Image: image}, nil
}
func processArgs(pid int) ([]string, error) {
	b, e := unix.SysctlRaw("kern.procargs2", pid)
	if e != nil {
		return nil, e
	}
	return darwinArgs(b)
}
func darwinArgs(b []byte) ([]string, error) {
	if len(b) < 5 || len(b) > 1<<20 {
		return nil, errors.New("invalid process arguments")
	}
	n := int(binary.LittleEndian.Uint32(b))
	if n < 1 || n > 4096 {
		return nil, errors.New("invalid argument count")
	}
	end := bytes.IndexByte(b[4:], 0)
	if end < 0 {
		return nil, errors.New("missing image terminator")
	}
	b = b[5+end:]
	for len(b) > 0 && b[0] == 0 {
		b = b[1:]
	}
	out := []string{}
	for len(out) < n {
		end = bytes.IndexByte(b, 0)
		if end < 0 {
			return nil, errors.New("incomplete process arguments")
		}
		out = append(out, string(b[:end]))
		b = b[end+1:]
	}
	return out, nil // Never return the environment following argv.
}
func processCwd(p Process) (string, error) {
	b, e := boundedCommand("", nil, time.Second, 8192, "/usr/sbin/lsof", "-a", "-p", strconv.Itoa(p.PID), "-d", "cwd", "-Fpfn")
	if e != nil {
		return "", e
	}
	lines := strings.Split(strings.TrimSuffix(string(b), "\n"), "\n")
	if len(lines) != 3 || lines[0] != "p"+strconv.Itoa(p.PID) || lines[1] != "fcwd" || !strings.HasPrefix(lines[2], "n/") {
		return "", errors.New("ancestor cwd unavailable")
	}
	return lines[2][1:], nil
}
