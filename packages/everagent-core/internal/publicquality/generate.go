package publicquality

import (
	"bytes"
	"crypto/rand"
	"errors"
	"os"
	"path"
)

// WriteIndexes changes only generated views, never report metadata or prose.
// Each replacement is atomic and checks its preimage. A partial write is
// reported explicitly and is safe to rerun; this is not a multi-file transaction.
func WriteIndexes(c *Candidate) ([]string, error) {
	written := []string{}
	if c.Scope != "worktree" || c.root == nil {
		return written, errors.New("index-write-requires-worktree-snapshot")
	}
	reports, findings := Catalog(c.After)
	if !noErrors(findings) {
		return written, errors.New("report-catalog-invalid")
	}
	readme, err := GeneratedREADME(c.After, reports)
	if err != nil {
		return written, err
	}
	generated := map[string][]byte{"README.md": readme, "docs/REPORT_INDEX.md": GeneratedIndex(reports)}
	scripts, err := scriptIndexForWrite(c.After)
	if err != nil {
		return written, err
	}
	generated[scriptIndexPath] = scripts
	if err := c.Verify(); err != nil {
		return written, err
	}
	for _, p := range keysBytes(generated) {
		after := generated[p]
		before, err := c.After.Bytes(p, TextLimit)
		if err != nil && !os.IsNotExist(err) {
			return written, err
		}
		if bytes.Equal(before, after) {
			continue
		}
		if err := writeGenerated(c.root, p, before, after, c.After.Has(p)); err != nil {
			return written, err
		}
		written = append(written, p)
	}
	return written, nil
}

func keysBytes(m map[string][]byte) []string {
	paths := map[string]bool{}
	for p := range m {
		paths[p] = true
	}
	return sortedBoolKeys(paths)
}

func writeGenerated(root *os.Root, p string, before, after []byte, existed bool) error {
	// The filename is unpredictable and opened exclusively within os.Root.
	// No symlink can redirect a generated view to another checkout.
	name := path.Join(path.Dir(p), ".ea-index-"+rand.Text())
	f, err := root.OpenFile(name, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
	if err != nil {
		return err
	}
	defer root.Remove(name)
	if _, err = f.Write(after); err == nil {
		err = f.Chmod(0644)
	}
	if err == nil {
		err = f.Sync()
	}
	closeErr := f.Close()
	if err != nil {
		return err
	}
	if closeErr != nil {
		return closeErr
	}
	current, err := readRoot(root, p, TextLimit)
	if existed {
		if err != nil || !bytes.Equal(before, current) {
			return errors.New("generated-view-changed-before-write")
		}
	} else if !os.IsNotExist(err) {
		return errors.New("generated-view-created-before-write")
	}
	return root.Rename(name, p)
}
