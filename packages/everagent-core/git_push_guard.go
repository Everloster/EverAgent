package core

import (
	"context"
	"regexp"
	"strings"
)

// PushIdentityPolicy validates only commits newly reachable from this update.
// Commit-time runtime evidence verifies a model; stored metadata alone cannot.
// Historical commits already on the destination are not retrospectively judged.
type PushIdentityPolicy struct {
	Author           Author
	ForbiddenCommits []string
}

func CheckPushIdentities(ctx context.Context, root, base, head string, policy PushIdentityPolicy) error {
	objectID := regexp.MustCompile(`^(?:[0-9a-f]{40}|[0-9a-f]{64})$`)
	if !objectID.MatchString(base) || !objectID.MatchString(head) || strings.TrimSpace(policy.Author.Name) == "" || strings.ContainsAny(policy.Author.Name, "\r\n<>") || !regexp.MustCompile(`^[^\s<>@]+@[^\s<>@]+$`).MatchString(policy.Author.Email) {
		return blocked("push identity policy or revisions invalid", 2)
	}
	shallow, err := gitRead(ctx, root, nil, "rev-parse", "--is-shallow-repository")
	if err != nil || shallow != "false" {
		return blocked("push identity check needs complete commit ancestry; not pushed", 3)
	}
	for _, sha := range policy.ForbiddenCommits {
		if !objectID.MatchString(sha) {
			return blocked("revoked commit policy invalid", 2)
		}
		// rev-list sees real objects, not replace refs. An absent revoked object
		// cannot be an ancestor of a complete, readable local head.
	}
	out, err := command(ctx, root, nil, 2<<20, "git", "--no-replace-objects", "rev-list", head)
	if err != nil {
		return blocked("cannot inspect push ancestry; not pushed", 1)
	}
	revoked := map[string]bool{}
	for _, sha := range policy.ForbiddenCommits {
		revoked[sha] = true
	}
	for _, sha := range strings.Fields(string(out)) {
		if revoked[sha] {
			return blocked("push contains a revoked incident commit; do not merge old history back", 3)
		}
	}
	out, err = command(ctx, root, nil, 2<<20, "git", "--no-replace-objects", "log", "--format=%H%x00%an%x00%ae%x00%cn%x00%ce%x00", base+".."+head)
	if err != nil {
		return blocked("cannot inspect new commit identities; not pushed", 1)
	}
	fields := strings.Split(string(out), "\x00")
	for len(fields) > 1 {
		if len(fields) < 6 || !objectID.MatchString(strings.TrimSpace(fields[0])) {
			return blocked("invalid commit identity response; not pushed", 1)
		}
		if fields[1] != policy.Author.Name || fields[2] != policy.Author.Email {
			return blocked("new commit Author differs from repository policy; not pushed", 3)
		}
		if !regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]{0,160}$`).MatchString(fields[3]) || strings.HasSuffix(fields[3], "-unknown") || !regexp.MustCompile(`^noreply@[^\s<>@]+$`).MatchString(fields[4]) {
			return blocked("new commit Committer is not a qualified Agent identity; not pushed", 3)
		}
		fields = fields[5:]
	}
	if len(fields) == 1 && strings.TrimSpace(fields[0]) != "" {
		return blocked("incomplete commit identity response; not pushed", 1)
	}
	return nil
}
