import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from blast_score import score, report


def d(path, lines, new=False, extra=""):
    h = (
        f"diff --git a/{path} b/{path}\n"
        + extra
        + ("new file mode 100644\n" if new else "")
        + f"--- a/{path}\n+++ b/{path}\n"
    )
    return h + "\n".join(lines) + "\n"


def test_docs_low():
    assert score(d("docs/readme.md", ["+Fix a typo in the guide."]))[0] == "LOW"


def test_added_test_medium():
    assert score(d("tests/test_parse.py", ["+def test_parse_empty():", "+    assert parse('') == []"], new=True))[0] == "MEDIUM"


def test_send_high():
    assert score(d("bin/sweep.py", ["+    send_email(lead)"]))[0] == "HIGH"


def test_delete_high():
    t = "diff --git a/docs/a.md b/docs/a.md\ndeleted file mode 100644\n--- a/docs/a.md\n+++ /dev/null\n-old\n"
    assert score(t)[0] == "HIGH"


def test_removed_assert_high():
    assert score(d("tests/test_x.py", ["-    assert x == 1"]))[0] == "HIGH"


def test_code_medium():
    assert score(d("bin/parse.py", ["+def parse(s):", "+    return s.split(',')"]))[0] == "MEDIUM"


def test_secret_high():
    assert score(d("bin/client.py", ["+API_KEY = os.environ['X_API_KEY']"]))[0] == "HIGH"


def test_payment_high():
    assert score(d("docs/runbook.md", ["+Charge the card and issue a refund."]))[0] == "HIGH"


def test_empty_high():
    assert score("")[0] == "HIGH"


def test_unparseable_high():
    assert score("not a diff")[0] == "HIGH"


def test_annotate_low_auto_eligible():
    out = report(d("docs/readme.md", ["+Fix a typo in the guide."]))
    assert out["tier"] == "LOW"
    assert out["color"] == "green"
    assert out["auto_merge_eligible"] is True


def test_annotate_high_never_auto():
    out = report(d("bin/client.py", ["+API_KEY = os.environ['X_API_KEY']"]))
    assert out["tier"] == "HIGH"
    assert out["auto_merge_eligible"] is False


def test_workflow_path_high():
    assert score(d(".github/workflows/ci.yml", ["+    run: pytest"]))[0] == "HIGH"


def test_dockerfile_high():
    assert score(d("Dockerfile", ["+FROM python:3.12"]))[0] == "HIGH"


def test_lockfile_high():
    assert score(d("package-lock.json", ["+  \"version\": \"1.2.3\""]))[0] == "HIGH"
