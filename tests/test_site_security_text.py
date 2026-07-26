from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_preview_warning_precedes_root_bootstrap_command():
    page = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    warning = page.index("not a verified release channel")
    command = page.index("sudo bash scripts/install/qdistro-bootstrap.sh")
    assert warning < command


def test_preview_command_selects_the_dev_profile():
    """The published preview command must pass --profile=dev.

    The bootstrap defaults to the hardened `daily-driver` profile, which
    refuses to build from a source tree that no populated, signed release
    manifest pins — and no such manifest is published yet. Source acquisition
    runs *after* package installation and user creation, so a site visitor who
    copies a profile-less command fails partway through a mutating install.
    """
    page = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    for line in page.splitlines():
        if "qdistro-bootstrap.sh" in line and "sudo bash" in line:
            assert "--profile=dev" in line, f"preview command lacks --profile=dev: {line!r}"
            break
    else:
        raise AssertionError("no bootstrap command found on the homepage")


def test_zola_download_is_checksum_pinned_before_use():
    """The one fetched executable input the site pipeline controls is pinned.

    Pre-2026-07 this repo deployed over SSH to Codeberg Pages, and the
    invariant was "pin the SSH host key as a secret, never ssh-keyscan".
    Deployment now runs on GitHub Actions/Pages, where there is no SSH hop at
    all — the remaining fetched input is the Zola tarball, so the invariant
    carries forward as: the downloaded toolchain is checksum-pinned, and no
    step re-introduces trust-on-first-use.

    Deliberately narrow: the `actions/*` steps are still major-version tags,
    which are mutable, so this does NOT claim the whole pipeline is pinned.
    SHA-pinning the actions is a separate follow-up.
    """
    ci = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Exact asset and exact digest — a bumped version with a stale digest, or a
    # digest edited without re-verifying, must not slip through as a substring.
    url = (
        "https://github.com/getzola/zola/releases/download/v0.22.1/"
        "zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz"
    )
    digest = "0ca09aa40376aaa9ddfb512ff9ad963262ef95edb0d0f2d5ec6961b6f5cf22ef"
    assert url in ci
    assert digest in ci

    # Order matters: the checksum must be verified BEFORE the tarball is
    # unpacked or installed, or the pin proves nothing.
    verify_at = ci.index("sha256sum -c -")
    assert verify_at < ci.index("tar xzf zola.tar.gz")
    assert verify_at < ci.index("install -m 0755 zola")

    # No trust-on-first-use host-key acceptance anywhere in the pipeline.
    assert "ssh-keyscan" not in ci
    assert "StrictHostKeyChecking=no" not in ci
    # The retired forge must not linger as a deploy target.
    assert "codeberg" not in ci.lower()
    assert "codeberg" not in readme.lower()
    # README documents the current deploy path.
    assert ".github/workflows/deploy.yml" in readme
