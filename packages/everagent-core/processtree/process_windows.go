//go:build windows

package processtree

import (
	"errors"
	"os"
	"os/exec"
	"syscall"
	"unsafe"

	"golang.org/x/sys/windows"
)

var (
	ErrDescendantsReaped = errors.New("command_left_descendants_reaped")
	ErrCleanup           = errors.New("process_tree_exit_unverified")
)

type basicAccountingInformation struct {
	TotalUserTime             windows.Filetime
	TotalKernelTime           windows.Filetime
	ThisPeriodTotalUserTime   windows.Filetime
	ThisPeriodTotalKernelTime windows.Filetime
	TotalPageFaultCount       uint32
	TotalProcesses            uint32
	ActiveProcesses           uint32
	TotalTerminatedProcesses  uint32
}

func suspendedMainThread(pid int) (windows.Handle, error) {
	snapshot, err := windows.CreateToolhelp32Snapshot(windows.TH32CS_SNAPTHREAD, 0)
	if err != nil {
		return 0, err
	}
	defer windows.CloseHandle(snapshot)
	entry := windows.ThreadEntry32{Size: uint32(unsafe.Sizeof(windows.ThreadEntry32{}))}
	for err = windows.Thread32First(snapshot, &entry); err == nil; err = windows.Thread32Next(snapshot, &entry) {
		if entry.OwnerProcessID == uint32(pid) {
			return windows.OpenThread(windows.THREAD_SUSPEND_RESUME, false, entry.ThreadID)
		}
	}
	return 0, errors.New("suspended main thread unavailable")
}

func activeProcesses(job windows.Handle) (uint32, error) {
	var accounting basicAccountingInformation
	err := windows.QueryInformationJobObject(job, windows.JobObjectBasicAccountingInformation, uintptr(unsafe.Pointer(&accounting)), uint32(unsafe.Sizeof(accounting)), nil)
	return accounting.ActiveProcesses, err
}

func Run(command *exec.Cmd) (result error) {
	job, err := windows.CreateJobObject(nil, nil)
	if err != nil {
		return err
	}
	defer func() {
		if err := windows.CloseHandle(job); err != nil {
			result = errors.Join(result, ErrCleanup)
		}
	}()
	limits := windows.JOBOBJECT_EXTENDED_LIMIT_INFORMATION{}
	limits.BasicLimitInformation.LimitFlags = windows.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
	if _, err = windows.SetInformationJobObject(job, windows.JobObjectExtendedLimitInformation, uintptr(unsafe.Pointer(&limits)), uint32(unsafe.Sizeof(limits))); err != nil {
		return err
	}
	if command.SysProcAttr == nil {
		command.SysProcAttr = &syscall.SysProcAttr{}
	}
	command.SysProcAttr.CreationFlags |= windows.CREATE_SUSPENDED
	if command.Cancel != nil {
		command.Cancel = func() error {
			if command.Process == nil {
				return os.ErrProcessDone
			}
			return windows.TerminateJobObject(job, 1)
		}
	}
	if err = command.Start(); err != nil {
		return err
	}
	process, err := windows.OpenProcess(windows.PROCESS_SET_QUOTA|windows.PROCESS_TERMINATE, false, uint32(command.Process.Pid))
	if err == nil {
		err = windows.AssignProcessToJobObject(job, process)
		if closeErr := windows.CloseHandle(process); err == nil {
			err = closeErr
		}
	}
	if err == nil {
		var thread windows.Handle
		thread, err = suspendedMainThread(command.Process.Pid)
		if err == nil {
			_, err = windows.ResumeThread(thread)
			if closeErr := windows.CloseHandle(thread); err == nil {
				err = closeErr
			}
		}
	}
	if err != nil {
		_ = windows.TerminateJobObject(job, 1)
		_ = command.Wait()
		return err
	}
	result = command.Wait()
	active, err := activeProcesses(job)
	if err != nil {
		_ = windows.TerminateJobObject(job, 1)
		return errors.Join(result, ErrCleanup)
	}
	if active > 0 {
		if err = windows.TerminateJobObject(job, 1); err != nil {
			return errors.Join(result, ErrCleanup)
		}
		return errors.Join(result, ErrDescendantsReaped)
	}
	return result
}
