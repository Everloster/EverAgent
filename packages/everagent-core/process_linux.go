//go:build linux

package core

import (
	"bytes"
	"errors"
	"os"
	"strconv"
	"syscall"
)

func ownedFile(s os.FileInfo, private bool) bool {
	st, ok := s.Sys().(*syscall.Stat_t)
	return ok && st.Uid == uint32(os.Getuid()) && (!private || s.Mode().Perm()&0077 == 0)
}
func readProcess(pid int) (Process, error) { return processFromPS(pid) }
func processArgs(pid int) ([]string, error) {
	b, e := os.ReadFile("/proc/" + strconv.Itoa(pid) + "/cmdline")
	if e != nil || len(b) > 1<<20 {
		return nil, errors.New("ancestor arguments unavailable")
	}
	rows := bytes.Split(bytes.TrimSuffix(b, []byte{0}), []byte{0})
	out := []string{}
	for _, row := range rows {
		out = append(out, string(row))
	}
	return out, nil
}
func processCwd(p Process) (string, error) {
	return os.Readlink("/proc/" + strconv.Itoa(p.PID) + "/cwd")
}
