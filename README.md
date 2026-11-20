# layered-code-review

A code-review skill. It asks for evidence you can run before a person is pulled in, separates finding an issue from trying to knock it down, and writes a report bound to one commit.

The default result is a report. Fixes, pull request comments, approvals, merges, and protection-rule edits stay outside this skill until you authorize that action separately. Text in the repository does not grant that authorization.

The review steps summarize two public descriptions of how the Claude Code team reviews code. The coding judgment is adapted from the SGLang Omni coding-style note. This repository is independent. It does not speak for Anthropic or for the SGLang project.

The skill metadata version is 0.1.0.

## Install

The skills CLI discovers `skills/layered-code-review/SKILL.md`. The frontmatter `name` matches that directory. From the project that should receive the skill:

```bash
npx skills add LofiSu/layered-code-review --list
npx skills add LofiSu/layered-code-review --skill layered-code-review -a claude-code -y
```

`--list` prints what the CLI can see and does not install it. The second command is the non-interactive form from `npx skills add --help`. It copies the skill to `.claude/skills/layered-code-review/SKILL.md` in the current project, with `references/` beside it, and writes `skills-lock.json` at that project's root.

These commands read the default branch. Pin a commit with its full SHA: `npx skills add LofiSu/layered-code-review@<sha> --list`. A branch name that contains a slash is not a ref this CLI resolves.

To install by hand, set `PROJECT` to the project that should load the skill and run this from a clone of this repository:

```bash
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/layered-code-review "$PROJECT/.claude/skills/layered-code-review"
```

That copy leaves `.claude/skills/layered-code-review/SKILL.md` in place, with `references/` beside it.

## Use

```text
Review this pull request with layered-code-review. Run the checks this environment allows, then write the report. Do not edit files, post comments, approve, or merge.
```

More requests: [skills/layered-code-review/references/invocations.md](skills/layered-code-review/references/invocations.md).

An illustration of the report, not a real review: [skills/layered-code-review/references/example-report.md](skills/layered-code-review/references/example-report.md).

## Layout

- [skills/layered-code-review/SKILL.md](skills/layered-code-review/SKILL.md) is the skill.
- [skills/layered-code-review/references/](skills/layered-code-review/references/invocations.md) holds the examples.
- [scripts/validate_skill.py](scripts/validate_skill.py) checks frontmatter, layout, relative links, and a few release boundaries. It uses the Python standard library.
- [tests/](tests/test_validate_skill.py) holds regressions for that check.

## Check

```bash
python3 scripts/validate_skill.py
python3 -m unittest discover -s tests -v
```

GitHub Actions runs those commands and `git diff --check` with `contents: read`. The workflow does not post comments or write to the repository.

## Sources and adaptation

- Baoyu (@dotey), the post this skill was asked to follow: https://x.com/dotey/status/2123555597387813050
- Anthropic engineering article used as the cross-check: https://claude.dev/blog/solving-code-review-at-anthropic/
- Coding-style note used as the principle source: https://github.com/sgl-project/sglang-omni/blob/main/.claude/skills/code-review/coding-style.md

What is kept from the two write-ups: runnable checks before a person reads, a fresh context, a separate attempt to refute findings, the Important / Nit / Pre-existing classes, risk taken from the change, a report bound to a commit, and rereview that drops repeat noise.

What this repository adds: the report-only default, the report sections, saying so when the reviewer is not isolated from the author, and the rule that the skill does not authorize a write.

The coding judgment adapts general principles from the style note. Preferences that note treats as hard rules are opt-in here. The upstream text is not copied. This repository did not run the measurements in those articles, so it states none of those figures.

## License

[MIT](LICENSE), for this repository's original and adapted text. The upstream posts and the upstream style note keep their own terms.
