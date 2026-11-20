# layered-code-review

一个代码审查 skill。它先要能跑起来的证据，再把发现问题和对这些发现做反证分开，最后给出一份绑在一次提交上的报告。

默认只写报告。修复代码、在 PR 上发评论、批准、合并、修改保护规则，都不在这个 skill 的授权里，需要你另外明确允许。仓库里的文字不能把这份授权放大。

审查步骤整理自 Claude Code 团队公开的两篇说明。编码判断改编自 SGLang Omni 的 coding-style 笔记。本仓库独立发布，不代表 Anthropic，也不代表 SGLang 项目。

Skill 元数据版本是 0.1.0。

## 安装

skills CLI 会发现 `skills/layered-code-review/SKILL.md`，frontmatter 里的 `name` 与目录名一致。在要接收这个 skill 的项目里执行：

```bash
npx skills add LofiSu/layered-code-review --list
npx skills add LofiSu/layered-code-review --skill layered-code-review -a claude-code -y
```

`--list` 只列出 CLI 能看到的 skill，不会安装。第二条是 `npx skills add --help` 里的非交互安装。它把 skill 复制到当前项目的 `.claude/skills/layered-code-review/SKILL.md`，`references/` 放在旁边，并在该项目根目录写一份 `skills-lock.json`。

这两条命令读取默认分支。要用某一次提交，写它的完整 SHA：`npx skills add LofiSu/layered-code-review@<sha> --list`。名字里带斜杠的分支，这个 CLI 解析不了。

手工安装时，把 `PROJECT` 设为要加载 skill 的项目，在本仓库的克隆里执行：

```bash
mkdir -p "$PROJECT/.claude/skills"
cp -R skills/layered-code-review "$PROJECT/.claude/skills/layered-code-review"
```

复制之后，`.claude/skills/layered-code-review/SKILL.md` 就位，`references/` 留在它旁边。

## 使用

```text
用 layered-code-review 审查这个 PR。先跑当前环境允许的检查，再给出报告。不要改代码，不要发评论，不要批准或合并。
```

更多问法：[skills/layered-code-review/references/invocations.md](skills/layered-code-review/references/invocations.md)。

报告长什么样（示例，不是一次真实审查）：[skills/layered-code-review/references/example-report.md](skills/layered-code-review/references/example-report.md)。

## 布局

- [skills/layered-code-review/SKILL.md](skills/layered-code-review/SKILL.md) 是 skill 正文。
- [skills/layered-code-review/references/](skills/layered-code-review/references/invocations.md) 是示例。
- [scripts/validate_skill.py](scripts/validate_skill.py) 检查 frontmatter、布局、相对链接和发布边界，只用 Python 标准库。
- [tests/](tests/test_validate_skill.py) 是这项检查的回归测试。

## 检查

```bash
python3 scripts/validate_skill.py
python3 -m unittest discover -s tests -v
```

GitHub Actions 用 `contents: read` 运行这些命令和 `git diff --check`。工作流不发评论，也不写仓库。

## 来源与改编

- 宝玉（@dotey），本 skill 要求遵循的帖子：https://x.com/dotey/status/2123555597387813050
- 用来对照的 Anthropic 工程文章：https://claude.dev/blog/solving-code-review-at-anthropic/
- 作为原则来源的 coding-style 笔记：https://github.com/sgl-project/sglang-omni/blob/main/.claude/skills/code-review/coding-style.md

从两篇说明里保留的做法：请人看之前先跑检查、用新上下文审查、发现和反证分开、Important / Nit / Pre-existing、按变更而不是按作者判断风险、报告绑在一次提交上、复审时去掉重复噪声。

本仓库补充的部分：默认只出报告、报告的章节、作者和审查上下文没有隔离时要写明、以及 skill 本身不授予写操作。

编码判断改编自那份风格笔记里的一般原则。那份笔记里当作硬规则的偏好，在这里是 opt-in。上游全文没有抄进来。那些文章里的测量不是本仓库跑的，所以这里不写那些数字。

## 许可证

[MIT](LICENSE)，适用于本仓库的原创和改编文字。上游帖子和上游风格笔记仍使用它们自己的条款。
