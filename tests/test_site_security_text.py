from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_preview_warning_precedes_root_bootstrap_command():
    page = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    warning = page.index("not a verified release channel")
    command = page.index("sudo bash scripts/install/qdistro-bootstrap.sh")
    assert warning < command


def test_deploy_uses_pinned_host_key_secret_not_keyscan():
    ci = (ROOT / ".woodpecker.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "CODEBERG_HOST_KEY" in ci
    assert "codeberg_host_key" in readme
    assert "ssh-keyscan" not in ci
