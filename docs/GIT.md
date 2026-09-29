# Git — no AI attribution on commits

## Your repo status

Commits should list **you** as author only. This project has no `Co-authored-by: Cursor` in source files.

## Enable hook (strips Cursor trailers if the IDE adds them)

From repo root (Git Bash or any shell with `git`):

```bash
git config core.hooksPath .githooks
```

## Cursor IDE (turn off attribution)

1. **Cursor Settings** (not VS Code settings)
2. **Agents → Attribution** (or **Git & PRs → Attribution**)
3. Turn **off** commit and PR attribution
4. Restart Cursor

Optional CLI (`%USERPROFILE%\.cursor\cli-config.json`):

```json
"attribution": {
  "attributeCommitsToAgent": false,
  "attributePRsToAgent": false
}
```

## Commit and push yourself (recommended)

```powershell
git config core.hooksPath .githooks
git commit -m "Initial commit: governance RAG platform with eval and demo UI."
git remote add origin https://github.com/laharsh/RAG_Eval.git
git push -u origin main
```

If a commit already has a Cursor trailer, amend once (only if not pushed):

```bash
git commit --amend
# remove the Co-authored-by line, save, exit editor
```
