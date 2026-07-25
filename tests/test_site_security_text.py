from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_preview_warning_precedes_root_bootstrap_command():
    page = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    warning = page.index("not a verified release channel")
    command = page.index("sudo bash scripts/install/qdistro-bootstrap.sh")
    assert warning < command


def test_deploy_trusts_nothing_unpinned():
    """The publish pipeline must not trust anything it fetches unverified.

    Pre-2026-07 this repo deployed over SSH to Codeberg Pages, and the
    invariant was "pin the SSH host key as a secret, never ssh-keyscan".
    Deployment now runs on GitHub Actions/Pages, where there is no SSH hop at
    all — the remaining fetched input is the Zola tarball, so the invariant
    carries forward as: the downloaded toolchain is checksum-pinned, and no
    step re-introduces trust-on-first-use.
    """
    ci = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Toolchain download is checksum-verified, at a pinned version.
    assert "sha256sum -c -" in ci
    assert "zola-v0.22.1" in ci
    # No trust-on-first-use host-key acceptance anywhere in the pipeline.
    assert "ssh-keyscan" not in ci
    assert "StrictHostKeyChecking=no" not in ci
    # The retired forge must not linger as a deploy target.
    assert "codeberg" not in ci.lower()
    assert "codeberg" not in readme.lower()
    # README documents the current deploy path.
    assert ".github/workflows/deploy.yml" in readme
