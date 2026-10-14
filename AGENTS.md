# Dokima

*The one place for how Dokima works, for people and for every agent (Claude, Codex and others read this file and the topic files it links; their own files just point here). Decisions land here once they're made; the issues hold how we got there. Items marked (planned) are decided but not built yet.*

## Working in this repo

- Python 3.12. Run the tests with `pytest -q`; tests live in `tests/`.
- Never change `.github/workflows/`, `dokima/card.py` or `dokima/roles/` unless the issue explicitly asks.
- Keep changes small. Add no dependencies unless the issue asks.
- Read this whole file and every topic file it links before changing how Dokima works.
- Whenever an agent or assistant refers the owner to an issue or pull request, it writes the number as a clickable link followed by a few plain words saying what it is about, e.g. [#289](https://github.com/dokima-dev/dokima/issues/289) (raises and answers). Never a bare number.

## Topics

Each topic lives in its own file.

- [The picture](rules/picture.md)
- [The core rule](rules/core-rule.md)
- [Principles](rules/principles.md)
- [Roles](rules/roles.md)
- [The flow (the river)](rules/flow.md)
- [Commands](rules/commands.md)
- [Raising and answering](rules/raising.md)
- [Where specs go](rules/specs.md)
- [The board](rules/board.md)
- [The issue body](rules/issue-body.md)
- [Agent records and cards](rules/records.md)
- [Splitting and the graph](rules/splitting.md)
- [Changing scope](rules/scope.md)
- [Identity and safety](rules/identity.md)
- [Decisions log](rules/decisions.md)
