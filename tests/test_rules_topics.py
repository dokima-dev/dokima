"""The word check reads every rules topic file the rules file links (#637).

The rules file (`AGENTS.md`) is becoming a short index that links topic files (#581). A plan reviewer may quote the
owner's words with source "AGENTS.md"; the word check (`said_there`) must find them in `AGENTS.md` or in any repo
markdown file it links. A run reads the rules from its runtime copy (`/tmp/runtime`, made by agent.yml's "Copy the
runtime" step), so that step must bring the linked topic files too.

Both tests run the real thing: the word check from a runtime copy of `dokima/` in a temp folder, and the workflow's
own copy step cut out of `.github/workflows/agent.yml` and run by bash in a temp checkout, holding Dokima's code where
the checkout of Dokima's own repo puts it.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPIC = "Needs you is a pill on the card, sorted to the top of each column."
INDEX_LINE = "Only a code owner's commands count."
INDEX = f"""# Rules

The rules live in topic files.

- [The board](rules/board.md)
- An example issue: [#289](https://github.com/dokima-dev/dokima/issues/289)

{INDEX_LINE}
"""


def write_rules(where):
    """Write a temp rules file linking one topic file, both under `where`."""
    (where / "rules").mkdir(parents=True, exist_ok=True)
    (where / "AGENTS.md").write_text(INDEX)
    (where / "rules" / "board.md").write_text(f"# The board\n\n{TOPIC}\n")


def word_check(runtime, words, cwd):
    """Run the word check from the runtime copy on words quoted from the rules file.

    Returns True or False; the source is "AGENTS.md"."""
    code = ("import sys\nfrom dokima import agent\n"
            "print(agent.said_there(sys.argv[1], 'AGENTS.md', [], '', [], 637))")
    env = {**os.environ, "PYTHONPATH": str(runtime)}
    env.pop("PYTHONSAFEPATH", None)
    r = subprocess.run([sys.executable, "-c", code, words], cwd=cwd, env=env, capture_output=True, text=True,
                       timeout=30)
    assert r.returncode == 0, f"the word check crashed on a rules file linking a topic file:\n{r.stderr[-800:]}"
    return r.stdout.strip() == "True"


def test_word_check_reads_linked_topic_files(tmp_path, record_property):
    """Quoted owner words pass when they sit only in a linked topic file.

    Proves 637.1. Builds a runtime copy of `dokima/` beside a temp rules file that links one topic file and one web page, then runs
    the word check from it. A quote found only in the topic file must pass. Beside it, a quote in the rules file
    itself must still pass, and a quote found nowhere must fail, so a check that passes everything fails here."""
    record_property("proves", "637.1")
    runtime = tmp_path / "runtime"
    shutil.copytree(os.path.join(ROOT, "dokima"), runtime / "dokima")
    write_rules(runtime)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert word_check(runtime, TOPIC, elsewhere), \
        "637.1: words found only in a topic file the rules file links do not pass the word check"
    assert word_check(runtime, INDEX_LINE, elsewhere), \
        "637.1: words in the rules file itself no longer pass the word check"
    assert not word_check(runtime, "Agents may approve their own pull requests.", elsewhere), \
        "637.1: words found in no rules file pass the word check, so it proves nothing"


def copy_step():
    """The shell script of agent.yml's "Copy the runtime" step."""
    lines = open(os.path.join(ROOT, ".github", "workflows", "agent.yml")).read().splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().startswith("- name: Copy the runtime"))
    indent = len(lines[start]) - len(lines[start].lstrip()) + 2
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        if line.strip().startswith("run:"):
            value = line.split("run:", 1)[1].strip()
            if value not in ("|", ">", "|-", ">-"):
                return value
            body = []
            for more in lines[i + 1:]:
                if more.strip() and len(more) - len(more.lstrip()) <= indent:
                    break
                body.append(more)
            return "\n".join(body)
    raise AssertionError("637.2: agent.yml has no run line in its Copy the runtime step")


def run_copy(checkout, runtime):
    """Run the copy step in `checkout`, writing to `runtime`; return the bash result.

    The step's `/tmp/runtime` is swapped for `runtime`."""
    script = copy_step().replace("/tmp/runtime", str(runtime))
    return subprocess.run(["bash", "-e", "-c", script], cwd=checkout, capture_output=True, text=True, timeout=30)


def test_runtime_copy_holds_linked_topic_files(tmp_path, record_property):
    """A run's copy of the rules brings every topic file the rules file links.

    Proves 637.2. Runs agent.yml's own "Copy the runtime" step in a temp checkout whose rules file links one topic file,
    with Dokima's code where the step before it checks Dokima's own repo out (`.dokima-code`, #812). The topic file must
    land beside the copied rules file, at the place its link points, unchanged. Beside it, a checkout with no
    rules file at all must still copy without failing, as repos without one do today."""
    record_property("proves", "637.2")
    checkout = tmp_path / "checkout"
    shutil.copytree(os.path.join(ROOT, "dokima"), checkout / ".dokima-code" / "dokima")
    write_rules(checkout)
    runtime = tmp_path / "runtime"
    r = run_copy(checkout, runtime)
    assert r.returncode == 0, f"637.2: the copy step failed on a rules file linking a topic file:\n{r.stderr[-800:]}"
    assert (runtime / "AGENTS.md").read_text() == INDEX, "637.2: the copy step no longer copies the rules file"
    topic = runtime / "rules" / "board.md"
    assert topic.exists() and TOPIC in topic.read_text(), \
        "637.2: the copy step leaves out the topic file the rules file links, so the word check cannot read it"
    bare = tmp_path / "bare"
    shutil.copytree(os.path.join(ROOT, "dokima"), bare / ".dokima-code" / "dokima")
    r = run_copy(bare, tmp_path / "bare-runtime")
    assert r.returncode == 0, f"637.2: the copy step fails in a repo with no rules file:\n{r.stderr[-800:]}"
