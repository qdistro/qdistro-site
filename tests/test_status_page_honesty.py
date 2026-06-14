"""The feature-status page must stay honest: the things 01-v1-scope.md flags
as cut or over-promised must be presented as planned/not-shipped, never as
shipped v1 capabilities. These guard against a future edit quietly promoting
them — so they parse the section a claim lives in, not just whether a substring
appears somewhere on the page."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = (ROOT / "content" / "status.md")


def _page() -> str:
    return STATUS.read_text(encoding="utf-8")


def _sections() -> tuple[str, str, str]:
    """(in_v1, experimental, planned) — the three honesty buckets."""
    page = _page()
    in_v1, _, rest = page.partition("## Experimental in v1")
    experimental, _, planned = rest.partition("## Planned")
    assert "## In v1" in in_v1, "In v1 section missing"
    assert experimental.strip(), "Experimental section missing"
    assert planned.strip(), "Planned section missing"
    return in_v1, experimental, planned


def _planned_rows() -> dict[str, str]:
    """Capability -> full row text, for rows in the Planned table."""
    _, _, planned = _sections()
    rows = {}
    for line in planned.splitlines():
        if line.startswith("|") and "|" in line[1:]:
            cap = line.split("|")[1].strip()
            rows[cap] = line
    return rows


def test_status_page_exists_and_is_linked_in_nav():
    assert STATUS.is_file()
    nav = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    assert "@/status.md" in nav


def test_recall_and_phone_rows_are_marked_cut():
    rows = _planned_rows()
    recall = next((r for cap, r in rows.items() if cap.startswith("Recall")), None)
    phone = next((r for cap, r in rows.items() if cap.startswith("Phone")), None)
    assert recall and "Cut from v1" in recall, "Recall must be a Planned row marked cut"
    assert phone and "Cut from v1" in phone, "Phone companion must be a Planned row marked cut"
    # And they must NOT appear in the shipped section.
    in_v1, _, _ = _sections()
    assert "Recall" not in in_v1
    assert "Phone companion" not in in_v1


def test_backup_is_planned_not_shipped():
    in_v1, experimental, planned = _sections()
    # The dedicated backup/export/restore capability row lives ONLY in Planned —
    # never promoted into the shipped or experimental tables.
    assert "Scheduled backup / export / restore" in planned
    assert "Scheduled backup / export / restore" not in in_v1
    assert "Scheduled backup / export / restore" not in experimental
    assert "Planned, not shipped" in planned
    # And the shipped filesystem row must explicitly disclaim it.
    assert "does not promise automated backup" in in_v1


def test_interim_networking_caveat_is_complete():
    # v1 ships the interim host-netns backend; the page must name every thing it
    # does NOT protect (802.11/DHCP/DNS still on the host kernel).
    page = _page()
    for needle in ("host-netns", "does not protect",
                   "802.11", "DHCP", "DNS", "host kernel"):
        assert needle in page, f"networking caveat missing: {needle!r}"


def test_release_is_framed_pre_release_not_done():
    # Honest about state: v1 scope, not a shipped-and-signed build.
    assert "pre-release" in _page()
