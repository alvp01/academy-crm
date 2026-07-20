# Skill Registry

> Generated: 2026-07-19 | Project: academy-crm | Source: ~/.config/opencode/skills/

## Registry Contract

- This is an INDEX, not a summary. `SKILL.md` is the source of truth.
- Paths are exact. Subagents read the full skill source, not this registry.
- Deduplicated by skill name. Project-level skills (none found) take precedence over user-level.
- SDD phase skills (`sdd-*`), `_shared`, and `skill-registry` are excluded from this index.

## Indexed Skills

| Skill | Trigger | Scope | Path |
|-------|---------|-------|------|
| branch-pr | creating, opening, or preparing PRs for review | GitHub PR workflow | /home/alvp01/.config/opencode/skills/branch-pr/SKILL.md |
| chained-pr | PRs over 400 lines, stacked PRs, review slices | PR splitting strategy | /home/alvp01/.config/opencode/skills/chained-pr/SKILL.md |
| cognitive-doc-design | writing guides, READMEs, RFCs, onboarding, architecture, or review-facing docs | Documentation design | /home/alvp01/.config/opencode/skills/cognitive-doc-design/SKILL.md |
| comment-writer | PR feedback, issue replies, reviews, Slack messages, or GitHub comments | Collaboration comments | /home/alvp01/.config/opencode/skills/comment-writer/SKILL.md |
| go-testing | Go tests, go test coverage, Bubbletea teatest, golden files | Go testing patterns | /home/alvp01/.config/opencode/skills/go-testing/SKILL.md |
| issue-creation | creating GitHub issues, bug reports, or feature requests | GitHub issue workflow | /home/alvp01/.config/opencode/skills/issue-creation/SKILL.md |
| judgment-day | judgment day, dual review, adversarial review, juzgar | Adversarial review | /home/alvp01/.config/opencode/skills/judgment-day/SKILL.md |
| skill-creator | new skills, agent instructions, documenting AI usage patterns | Skill creation | /home/alvp01/.config/opencode/skills/skill-creator/SKILL.md |
| skill-improver | improve skills, audit skills, refactor skills, skill quality | Skill auditing | /home/alvp01/.config/opencode/skills/skill-improver/SKILL.md |
| work-unit-commits | implementation, commit splitting, chained PRs, or keeping tests and docs with code | Commit planning | /home/alvp01/.config/opencode/skills/work-unit-commits/SKILL.md |

## SDD Phase Skills (delegated — not in this index)

These skills are available but delegate-only. They are invoked by the orchestrator, not directly:

- `sdd-init` — Initialize SDD context
- `sdd-explore` — Explore ideas before committing
- `sdd-propose` — Create change proposals
- `sdd-spec` — Write delta specs
- `sdd-design` — Technical design
- `sdd-tasks` — Break changes into tasks
- `sdd-apply` — Implement tasks
- `sdd-verify` — Verify implementation
- `sdd-archive` — Archive completed changes
- `sdd-onboard` — Walkthrough SDD cycle

## Scan Sources

- User skills: `~/.config/opencode/skills/` (22 entries scanned)
- Project skills: none found (empty project)
