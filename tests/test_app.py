import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def read(path):
    return open(os.path.join(ROOT, path)).read()


def test_worker_and_card_act_as_the_dokima_app(record_property):
    record_property("proves", "40.1")
    for name in ("agent.yml", "card.yml"):
        text = read(f".github/workflows/{name}")
        assert "actions/create-github-app-token@v2" in text
        assert "app-id: ${{ vars.DOKIMA_APP_ID }}" in text
        assert "private-key: ${{ secrets.DOKIMA_APP_KEY }}" in text
        assert "DOKIMA_TOKEN" not in text
    agent = read(".github/workflows/agent.yml")
    push = agent[agent.index("name: Push the planner's tests or the worker's code"):]  # identity is set when committing (#113)
    assert "GH_TOKEN: ${{ steps.app.outputs.token }}" in push and "SLUG: ${{ steps.app.outputs.app-slug }}" in push
    assert 'git config user.name "${SLUG}[bot]"' in push
    card = read(".github/workflows/card.yml")
    assert "GH_TOKEN: ${{ steps.app.outputs.token }}" in card[card.index("name: Write the card"):]


def test_one_code_owner_rule_covers_every_file(record_property):
    record_property("proves", "40.2")
    rules = [line.split() for line in read(".github/CODEOWNERS").splitlines()
             if line.strip() and not line.startswith("#")]
    assert len(rules) == 1 and rules[0][0] == "*" and len(rules[0]) > 1


def test_app_cannot_change_rules_or_workflows(record_property):
    record_property("proves", "40.3")
    perms = json.loads(read("dokima/app.json"))["default_permissions"]
    # Administration is read-only since #282, so the app can read branch rules but never change them.
    assert perms.get("administration") in (None, "read")
    # The bot may push workflow files since #126: a PR's workflow edits can't reach the
    # keys before merge, so the owner's merge is the approval.
    assert all(level in ("read", "write") for level in perms.values())
