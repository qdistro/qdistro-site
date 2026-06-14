+++
title = "What qdistro protects against"
template = "page.html"
description = "qdistro's threat model in plain terms: the cross-silo leaks and app-compromise containment it is built to stop, the adversarial cases it explicitly does not, and where isolation rests on the host kernel versus a VM boundary."
[extra]
summary = "An explicit threat model: containment for accidental leaks and app compromise limited by the tier you choose, honest that tiers 0–3 share host-kernel fate and hostile code needs a VM tier, with a deferred-by-design ledger of what hardens later."
+++

qdistro aims for **brokered provenance and contamination control** — not full
fine-grained information-flow noninterference. The model is stated explicitly on
purpose: several design choices (hide-the-UI vs. sandbox, cooperative vs. enforced
read-only, one-fingerprint vs. per-user auth) only make sense once you know what is
and isn't being defended. This page is the public summary; the
[full threat model](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/threat-model.md)
in the source tree is authoritative.

A guiding rule: **apps are not trusted to self-report their own security-relevant
identity.** Authoritative lineage and audit identity come from broker decisions,
kernel peer credentials, SELinux labels, and compositor endpoint identity — never
from an app's say-so.

## What it protects against

- **Accidental cross-silo leaks.** Working in `work-user`, you shouldn't paste a
  password into `personal-user`'s browser. Clipboard, file-chooser, device-access,
  and window-handoff flows make the silo identity clear and gate cross-silo
  transfers.
- **Containment of a compromised app.** Compromise one app (a browser, an IDE) and
  the blast radius is limited to the uid / container / VM it runs in — not other
  silos' files, clipboards, or device streams. The strength of that limit is the
  tier you chose: defeating an *actively hostile* escape attempt needs a VM tier
  (see below), since tiers 0–3 share host-kernel fate.
- **A smaller surface for regular users.** Wi-Fi pickers, display and Bluetooth
  settings, and other hardware-config dialogs are admin-only. Less to misconfigure,
  less to misuse.
- **An authored approval chain.** Every cross-silo action leaves a polkit trail —
  who asked, when, what scope admin granted — that admin can review and revoke.

## What it does not

These are out of scope **by design**, not gaps to be fixed later:

- **A fully adversarial user session.** A regular session is not assumed to be
  actively hostile. Code that aggressively tries to escape its uid/container is only
  contained when it runs in a **VM tier** — that is what the VM tiers are for.
- **App authors targeting qdistro specifically.** First-party apps honour the SDK
  cooperatively; read-only is a cooperative D-Bus flag, not a kernel-enforced
  sandbox. Fine for apps you wrote or trust; not a defence against a malicious app.
  Third-party apps get the coarser tier-2 enforcement (nested-compositor input
  filter, container isolation).
- **Hardware-level attacks.** Evil-maid, cold-boot, firmware implants, and
  fingerprint-reader side-channels are out of scope.
- **Forensic detection-evasion.** Logging and activity indicators are for *your*
  awareness, not forensic resistance.
- **Multi-tenant machines.** One fingerprint, one person — sharing a machine
  between people is not a goal.

## Where the boundary really is

Isolation tiers 0–3 (none / SELinux / podman / different-uid) all rest on the
**host kernel**: a single kernel privilege-escalation collapses them together.
That is stated honestly rather than papered over —

- Tiers 0–3 are graduated *authority and code* confinement that **share host-kernel
  fate**. The **VM tiers** are where containment survives a host-kernel-quality bug.
- Hardware-facing parsing (802.11 frames, Bluetooth, USB descriptors, printing) is
  migrating off the host into **device silos** as they land — printing first.
- **v1 networking is interim:** a host-netns backend ships now; 802.11, DHCP, and
  DNS parsing still run on the host kernel until the network-VM swap-in. See the
  [feature status page](@/status.md).

**Admin is the trusted computing base.** Admin's compositor, session manager,
polkit agent, and locker run with full trust — if admin is compromised, so is the
machine. The intended discipline for those TCB processes is **no-network +
envelope-only parsing**; in v1 the no-network half is **shipped-with-exceptions**:
the broker has VM-verified SELinux *and* runtime no-network coverage; the polkit
agent and locker have only the runtime half (the SELinux/VM-negative half is still
landing); and the session manager is an **explicit exception** while it owns the
network control client. The broker's evidence does not speak for the others.

## Deferred by design

Hardening that is planned but explicitly **not** in v1 — listed so the scope is honest:

- **Network VM swap-in** — moves 802.11/DHCP/DNS parsing off the host kernel.
- **Device silos** for the remaining hardware-facing parsers (Bluetooth, USB).
- **Full per-class compositor global visibility** — closing low-severity metadata
  side-channels (e.g. display-topology enumeration across silos).
- **TPM-sealed vault (v2)** — engages only where the hardware path validates;
  otherwise the vault ships password-only.
- **Adversarial-session hardening** — for genuinely hostile code, run it in a VM tier.

See [what ships in v1](@/status.md) for the per-feature breakdown, or
[how qdistro is different](@/different.md) for the design behind the model.
