"""The public threat-model page must stay faithful to doc/threat-model.md: it
must keep the honest limits (tiers 0-3 share host-kernel fate; first-party
read-only is cooperative, not a kernel sandbox; TCB no-network is
shipped-with-exceptions; v1 networking is interim) and must not drift into
claiming containment guarantees the model explicitly disclaims."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "content" / "threat-model.md")


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def _flat() -> str:
    # Whitespace-normalized, so phrase checks survive markdown line-wrapping.
    return " ".join(_page().split())


def _section(heading: str) -> str:
    # Whitespace-normalized text of one "## heading" section.
    body = _page().split("## " + heading, 1)[1]
    body = body.split("\n## ", 1)[0]
    return " ".join(body.split())


def test_page_exists_and_is_linked_in_nav():
    assert PAGE.is_file()
    nav = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    assert "@/threat-model.md" in nav


def test_keeps_host_kernel_fate_honesty():
    # Tiers 0-3 share host-kernel fate; the VM tiers are the real boundary.
    boundary = _section("Where the boundary really is")
    assert "host-kernel fate" in boundary
    assert "VM tier" in boundary


def test_hostile_code_requires_a_vm_tier():
    # The model does NOT claim tiers 0-3 contain an adversarial session: hostile
    # escape code is only contained in a VM tier. This must be stated where the
    # page enumerates what it does NOT defend.
    does_not = _section("What it does not")
    assert "VM tier" in does_not
    assert "adversarial" in does_not.lower() or "hostile" in does_not.lower()


def test_first_party_readonly_is_cooperative_not_kernel_sandbox():
    does_not = _section("What it does not")
    assert "cooperative" in does_not
    assert "not a kernel-enforced sandbox" in does_not


def test_tcb_no_network_is_shipped_with_exceptions_not_done():
    # Must not claim full TCB no-network. v1 is shipped-with-exceptions: broker
    # has the SELinux+runtime evidence; polkit/locker only the runtime half;
    # session manager is the explicit exception; broker ev. doesn't cover others.
    boundary = _section("Where the boundary really is")
    assert "shipped-with-exceptions" in boundary
    assert "broker" in boundary
    assert "polkit" in boundary and "locker" in boundary
    assert "explicit exception" in boundary
    assert "session manager" in boundary


def test_interim_networking_named_and_deferred():
    flat = _flat()
    # Interim host-netns; the things still on the host kernel; deferred net VM.
    assert "host-netns" in flat
    for needle in ("802.11", "DHCP", "DNS"):
        assert needle in flat
    assert "Network VM swap-in" in flat


def test_has_deferred_by_design_ledger():
    assert "Deferred by design" in _flat()
