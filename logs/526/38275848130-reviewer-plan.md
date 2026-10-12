# reviewer (plan) for #526

Run: https://github.com/dokima-dev/dokima/actions/runs/38275848130

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #526: Source shows only when it points elsewhere
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A criterion's Source shows on the card only when it points somewhere other than the issue itself.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/527
> 
> 
> **User story:** The owner sees a criterion's Source only when it points somewhere other than the issue itself.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A criterion whose source is its own issue shows no Source line on the issue or pull request card.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-526/tests/test_card_source_elsewhere.py#L74"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A criterion quoting its own issue shows no Source line on either card.*
>   - Source: https://github.com/dokima-dev/dokima/issues/524
> - <img src="https:

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/ | head -300; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit 7840ee2253e5cb047ece0a1503dad53ebd96214d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 16:12:54 2026 +0000
> 
>     planner for #526 (run 38274240578)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_card_bullets.py          |  2 +-
>  tests/test_card_refs.py             | 11 ++---
>  tests/test_card_source_elsewhere.py | 85 +++++++++++++++++++++++++++++++++++++
>  tests/test_parent_source.py         | 16 ++++++-
>  4 files changed, 107 insertions(+), 7 deletions(-)
> commit 7840ee2253e5cb047ece0a1503dad53ebd96214d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 16:12:54 2026 +0000
> 
>     planner for #526 (run 38274240578)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_card_bullets.py b/tests/test_card_bullets.py
> index 6c4f4b3..60c3310 100644
> --- a/tests/test_card_bullets.py
> +++ b/tests/test_card_bullets.py
> @@ -29,7 +29,7 @@ ROOT = os.path.join(os.path.dirname(__file__), "..")
>  REPO = "o/r"
>  ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
>  ASK_1 = "https://github.com/o/r/issues/40#issuecomment-111"
> -ASK_2 = "https://github.com/o/r/issues/40"
> +ASK_2 = "https://github.com/o/r/issues/30"  # the parent: the issue's own link shows no Source line since #526
>  PLAN = {"kind": "user_story", "summary": "Owners see one card.", "user_s

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^COMMENT\|^PARENT\|^ISSUE\|Source" tests/test_card_refs.py | head -20; timeout 600 python3 -m pytest -q tests/test_card_source_elsewhere.py tests/test_card_refs.py tests/test_parent_source.py tests/test_card_bullets.py 2>&1 | tail -15; grep -n "Source" dokima/card.py | head
```

> 6:link of its own, `[issue #40](...)` or `<a href="...">Source</a>`, shows only the wrapped words, with no icon and no
> 22:ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
> 23:COMMENT = "https://github.com/o/r/issues/40#issuecomment-111"
> 24:PARENT = "https://github.com/o/r/issues/30"
> 133:# 359.1: Source shows as a GitHub reference to wherever the ask is
> 136:    """Each Source shows its comment, issue or parent story as a GitHub reference.
> 139:    each such criterion's last line reads Source: followed by its own link written out bare, so GitHub draws it with its
> 140:    icon and title, that no Source is the word Source linked to a page, and that a criterion with no source shows no
> 141:    Source line. Proves 359.1, and 526.2: a source on a comment or the parent still shows."""
> 146:        # The criterion sourced from the issue itself shows no Source line since #526.
> 152:                f"359.1: the Source of “{words}” is a link with words of its own, not a GitHub reference: {last.strip()}"
> 154:                f"359.1: the Source of “{words}” should be {url} written out bare, the line is: {last.strip()}"
> 156:            assert said == f"Source: {url}", \
> 157:                f"359.1: the Source line of “{words}” should read “Source: {url}”, it reads “{said}”"
> 158:        assert "Source</a>" not in text and "[Source]" not in text, f"359.1: the {page} card still links the word Source"
> 160:    assert not [l for l in under(draw(recs=[rec("planner", n=11, **no_source)]

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote one new test that hides a Source pointing at the issue itself, on both cards.",
          "The planner changed two card tests that expected the issue's own Source line."],
  "decided": ["Run comments keep their Source lines; only the card changes.",
              "Sources stay checked and recorded as today, proven by the existing parent source test."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries all three asks, and each has a test that fails without its behavior.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A criterion whose source is its own issue shows no Source line on the card.", "source": "https://github.com/dokima-dev/dokima/issues/526", "criterion": "526.1"},
  {"ask": "A criterion sourced from the parent issue or a comment still shows its Source line.", "source": "https://github.com/dokima-dev/dokima/issues/526", "criterion": "526.2"},
  {"ask": "Every criterion's source is still recorded and checked as today.", "source": "https://github.com/dokima-dev/dokima/issues/526", "criterion": "526.3"}],
 "behaviors": [
  {"criterion": "526.1", "one_behavior": true, "why": "Hides one line for one kind of source, on both cards."},
  {"criterion": "526.2", "one_behavior": true, "why": "Keeps the Source line for sources pointing elsewhere."},
  {"criterion": "526.3", "one_behavior": true, "why": "Keeps the source checked and stored unchanged."}],
 "tests": [
  {"test": "tests/test_card_source_elsewhere.py::test_a_criterion_sourced_from_its_own_issue_shows_no_source_line", "only_its_behavior": true, "why": "Fails today on both cards; also guards against dropping every Source line."},
  {"test": "tests/test_card_refs.py::test_each_source_shows_as_a_github_reference_to_where_the_ask_is", "only_its_behavior": true, "why": "Checks a comment on the issue and the parent still show, so hiding by prefix fails."},
  {"test": "tests
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i "s/The planner wrote one new test that hides a Source pointing at the issue itself, on both cards./The planner wrote a test that hides a Source naming the issue itself./" /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 526 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#526](https://github.com/dokima-dev/dokima/issues/526) (cards hide a Source that points at the issue itself). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **The asks:** the issue has three, and each one has exactly one criterion. I found nothing missing and nothing added, and each criterion covers a single behavior.
- **526.1 (hide the issue's own Source):** the new test fails today on both the issue card and the pull request card, which is the right reason. It also checks that a Source from the parent still shows on the same card, so removing every Source line would not pass.
- **526.2 (other Sources still show):** the changed test checks that a comment on the issue and the parent issue still show. A fix that hid anything starting with the issue's own link would fail it.
- **526.3 (Sources still checked and recorded):** the test runs the real planner check, then reads every Source back from the planner's run comment.
- **Tests that pass today:** the 526.2 and 526.3 tests already pass. That fits, because those criteria are about keeping current behavior.

There were no open blockers to answer and I raised nothing.
