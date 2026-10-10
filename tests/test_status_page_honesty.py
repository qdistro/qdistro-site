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


def test_signed_extension_distribution_is_planned_not_shipped():
    """R4: v1 documents MANUAL extension load. The signed channel (AMO / CRX +
    update.xml) must live in Planned, and the shipped browser-bridge row must
    disclose the manual-load reality rather than implying a normal install."""
    in_v1, experimental, planned = _sections()
    rows = _planned_rows()
    signed = next(
        (r for cap, r in rows.items() if cap.startswith("Signed extension")),
        None)
    assert signed, "Signed extension distribution must be a Planned row"
    assert "Planned, not shipped" in signed
    for needle in ("AMO", "update.xml", "auto-update"):
        assert needle in signed, f"signed-distribution row omits {needle!r}"
    assert "Signed extension distribution" not in in_v1
    assert "Signed extension distribution" not in experimental
    # The shipped row must not present the extensions as normally installable.
    browser_row = next(
        (line for line in in_v1.splitlines()
         if line.startswith("| Browser bridge")), None)
    assert browser_row, "shipped browser-bridge row missing"
    assert "manual" in browser_row.lower()
    assert "no signed extension channel" in browser_row.lower()
    assert "re-loaded after every browser restart" in browser_row


def test_tty4_lxqt_escape_hatch_is_not_shipped():
    in_v1, _, _ = _sections()
    assert "tty4" in in_v1
    assert "no tty4 LXQt escape hatch" in in_v1
    assert "escape hatch on tty4" not in in_v1


def test_printing_is_not_an_isolated_cups_vm():
    in_v1, _, _ = _sections()
    printing = next(
        (line for line in in_v1.splitlines() if line.startswith("| Printing")),
        None)
    assert printing, "Printing row missing from In v1"
    assert "isolated CUPS VM" in printing
    assert "never built" in printing
    assert "CUPS in an isolated VM" not in printing


def test_admin_app_installs_as_chain_step_and_has_no_snapshots_printers_panels():
    # installer_chain_entries (scripts/install/qdistro-bootstrap.sh) lists
    # admin-app, so a claim that it is "not installed" is stale — the page
    # must say the approval paths land, and still bound the panel scope.
    in_v1, _, _ = _sections()
    admin = next(
        (line for line in in_v1.splitlines() if line.startswith("| Admin app")),
        None)
    assert admin, "Admin app row missing"
    assert "not installed" not in admin.lower()
    assert "installer-chain" in admin.lower()
    assert "snapshots or printers" in admin.lower() or "no snapshots or printers" in admin.lower()


def test_portal_backend_is_in_v1_not_planned():
    in_v1, _, planned = _sections()
    assert "Portal backend" in in_v1
    assert "portal backend" not in planned.lower()
    lump = next(
        (line for line in planned.splitlines()
         if line.startswith("| Workflow engine")),
        None)
    assert lump
    assert "portal backend" not in lump.lower()


def test_templates_row_is_dirs_not_a_promotion_ui():
    in_v1, _, _ = _sections()
    templates = next(
        (line for line in in_v1.splitlines() if line.startswith("| Templates")),
        None)
    assert templates, "Templates row missing from In v1"
    assert "directories" in templates.lower() or "example" in templates.lower()
    assert "not a shipped UI" in templates
    assert "gated promotion" in templates.lower() or "promotion" in templates.lower()


def test_installable_iso_stays_cut_tester_raw_is_experimental():
    in_v1, experimental, planned = _sections()
    rows = _planned_rows()
    iso = next((r for cap, r in rows.items() if cap.startswith("Installable ISO")), None)
    assert iso and "Cut from v1" in iso
    assert "Installable ISO" not in in_v1
    assert "Tester disk image" in experimental
    assert "raw.xz" in experimental
    assert "Not a signed release" in experimental


def test_selinux_row_does_not_claim_enforcing_on_the_tester_image():
    in_v1, _, _ = _sections()
    selinux = next(
        (line for line in in_v1.splitlines() if line.startswith("| SELinux")),
        None)
    assert selinux
    assert "permissive" in selinux.lower()
    assert "lineage_enforce" in selinux
    assert "defaults false" in selinux

