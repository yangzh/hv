# Workflow

## PRs and review

For every piece of work, follow this loop without asking for approval at each step:

1. **Create the PR automatically.** When work on a branch is ready (commits pushed), open a PR against `main` immediately. Do not wait for the user to ask.
2. **Push commits straight to the PR branch.** No approval needed for pushing additional commits to an open PR.
3. **Address each review comment.**
   - Reply to the comment with either a brief explanation or just `done`.
   - When the comment requires a code change, **amend the relevant existing commit** (not a fixup commit), then force-push the branch. The PR history should stay clean.
   - Use `git commit --amend` for the latest commit, or `git rebase -i` (non-interactive form via `GIT_SEQUENCE_EDITOR`) for older ones. Force-push with `--force-with-lease`.
4. **Do not merge or close the PR** until the user explicitly says **"approve and merge"** (or equivalent explicit approval). Until then, the PR stays open even if all comments are resolved.

Exception to the "always create new commits" default in the system prompt: this workflow explicitly opts into amending. Treat that as authorized for PR review iteration on this repo.
