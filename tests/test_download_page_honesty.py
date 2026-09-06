"""The download page must describe the tester raw image honestly.

Pins the Phase F (todo/iso/14) contract: tester disk image, not an ISO;
dev profile; default password; sshd off; UEFI-only; 32 GB; checksum before
dd; no signature; 04 caveats. A future edit that turns this into a signed
ISO download, or that hides the missing public host, must fail here.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "content" / "download.md"


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def _flat() -> str:
    return " ".join(_page().split())


def test_download_page_exists_and_is_linked_in_nav():
    assert PAGE.is_file()
    nav = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    assert "@/download.md" in nav
    home = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "@/download.md" in home


def test_is_a_tester_raw_image_not_an_iso():
    page = _page()
    flat = _flat()
    assert "tester disk image" in page
    assert "not an installable ISO" in flat
    assert "does not ship that ISO" in flat
    assert "**dev**" in page
    assert "Password | `qdistro`" in flat or "password `qdistro`" in page.lower()
    assert "never enabled" in page
    assert "UEFI-only" in page
    assert "32 GB" in page
    assert "xzcat" in page
    assert "dd of=" in page
    assert "sha256sum -c" in page
    assert "post-v1" in page
    assert "no release signature" in page.lower() or "Signing is **post-v1**" in page


def test_checksum_before_write_and_no_fake_host():
    page = _page()
    flat = _flat()
    check_at = page.index("sha256sum -c")
    dd_at = page.index("dd of=")
    assert check_at < dd_at
    assert "No public download is published yet" in flat
    # Do not invent a 404 asset URL as if testers can fetch it today.
    assert "releases/download/" not in page


def test_caveats_from_iso04():
    page = _page()
    flat = _flat()
    for needle in (
        "No approval-queue UI",
        "No isolated print VM",
        "permissive",
        "Polkit agent cannot grant",
        "Tiers 4/5 experimental",
        "real USB stick on real hardware",
    ):
        assert needle in page or needle in flat, f"download page missing caveat {needle!r}"


def test_vm_line_is_uefi():
    page = _page()
    assert "OVMF" in page
    assert "qcow2" in page
    assert "Legacy BIOS will not boot" in page or "Legacy BIOS/CSM will not boot" in page
