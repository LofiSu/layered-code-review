# Invocations

These requests ask for a report. They do not authorize edits, pull request comments, approvals, or merges.

## First review

```text
Review this pull request with layered-code-review. Run the checks this environment allows, then write the report. Bind it to the current head SHA. Do not edit files, post comments, approve, or merge.
```

## A local diff

```text
Review the diff from BASE_SHA to HEAD_SHA with layered-code-review. The stated intent is that the retry loop drops the last error. Report only, and bind the report to HEAD_SHA.
```

## Rereview

```text
Rereview this pull request with layered-code-review. Here are the earlier Important findings and which of them the author says are fixed. Review the new diff, any regression the fix added, and every Important item that is still open. If you find a new serious issue, include it. Do not repeat findings that are unchanged. Do not edit, comment, approve, or merge.
```

## 中文

```text
用 layered-code-review 审查这个 PR。先跑当前环境允许的检查，再给出报告，并写明 head SHA。不要改代码，不要发评论，不要批准或合并。
```
