# Example report

Illustration only. `example-not-a-commit` is not a real commit, the paths are fictional, and nothing here was measured. Do not copy these findings into a review of a real change.

One Important defect in the billing retry path, one Nit, and one Pre-existing log gap. This illustration did not run the suite.

## Scope

- Target: fictional pull request "surface the last retry error".
- Base: `example-base`. Head SHA: `example-not-a-commit`.
- Stated intent: the retry loop drops the last error, so callers see a generic failure.
- Rules followed: this file's review procedure. The fictional repository has no `REVIEW.md` and no declared risk tiers.

## Verification

No command was run. This illustration has no repository to execute. The absence is uncovered, not a pass. There is no CI result for `example-not-a-commit`.

## Findings

### Important

`payments/retry.py:48`. When the last attempt raises, the loop assigns the generic message and discards the exception. Callers then retry a permanent card decline. The assignment is the only write to `failure`, and the function returns it on line 61. Suggested fix: return the last exception's message, and add a test whose expected text is that message. This suggestion is not a change already made.

### Nit

`payments/retry.py:12`. The delay helper's name does not say it returns milliseconds. A caller can pass seconds and sleep for the wrong interval. Non-blocking. Worth one rename if that helper is touched anyway.

### Pre-existing

`payments/log.py:20` already drops the provider code on the base. This diff does not read that field. No incremental impact. Left as pre-existing, not as a defect of this change.

## Filtered

A comment that the new test "should use a fixture" repeated the linter and named no behavior change. Dropped.

## Needs a person

Whether a declined card should retry at all is a product decision. The diff touches billing, so a person should look. Nothing here is an approval, and this illustration does not set an approval count.

## Uncovered

The suite, the type check, and a UI pass were not run. Finding and refutation were not separate reviewers. No cross-repository caller was available to read.

## Next

The Important item is still open. Policy for who must approve a billing change is not declared in this illustration, so none is invented here.
