# Remaining branch consolidation — 2026-11-16

All 12 remaining remote work branches and the three previously archived branches were audited against main (PR #6). Existing main already contains their current intended implementation. The divergent Alpine and equivalent cherry-pick histories are reconciled with explicit `ours` history merges, keeping the validated production tree unchanged. This deliberately does not restore superseded large seasonal assets or older implementations.

`branches.json` records the original branch tips and disposition. Every audited tip is an ancestor of this PR head. Before this audit document was added, the complete tree was byte-identical to the original main. No runtime rebuild is needed for this history/documentation-only PR; the 96-variant Alpine size cap and all prior native validation remain applicable.

After this PR merges, preserve each old tip with a remote annotated archive tag, then remove its obsolete remote branch. Preserve local worktrees and their uncommitted files. The newly active `codex/moke-font-skill-20261116` worktree is outside this closed historical set and is not modified.
