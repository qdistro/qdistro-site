+++
title = "What ships in v1"
template = "page.html"
description = "An honest feature-status page for qdistro v1: what ships, what ships behind an experimental label, and what is explicitly planned for later. Generated from the release scope table — including where the docs once over-promised."
[extra]
summary = "Three honest lists — shipped in v1, experimental (behind a label), and planned for later. If a feature isn't ready, it's here as planned, not dressed up as done."
+++

This page is the honest scope of qdistro **v1**: what the release includes,
what ships behind an *experimental* label, and what is **planned** for a later
version. It mirrors the project's internal release-scope table, including the
places where the documentation once promised more than the code delivers — those
are listed as **planned**, not quietly shipped.

A note on dates: v1 is **pre-release**. Everything under *In v1* is implemented
and is going through the release test battery; this page describes the v1
**scope**, not a shipped-and-signed build. When a signed release manifest exists,
the [install guide](@/install.md) is the trust anchor.

## In v1

Implemented, in scope, and going through the release verification passes.

| Capability | What it is |
|---|---|
| Tier 0–3 isolation | Direct, SELinux-confined, rootless-podman, and different-uid waypipe app isolation. Tier-1/2 spawn authorization moves out of shadow mode for the release. |
| qdwin compositor | The libweston + Wayland compositor, with the §4b capture-global gate (screen-capture is shell-only, hidden from ordinary clients). |
| Session stack | qdshell, qdgreeter, and qdlocker — login on tty3, an LXQt escape hatch on tty4, dynamic sessions on tty5+. |
| Broker + admin approval | The permission arbiter: CheckPermission / RequestPermission, rules + hooks, the admin approval queue, and an append-only audit trail. |
| Sessions / silo lifecycle | Create, start, stop, freeze, and egress changes for per-silo workloads. |
| Password vault | The v1 password master-key vault. (The TPM-sealed v2 path is *experimental* — see below.) |
| Printing | CUPS in an isolated VM. |
| Per-silo VPN | An interim host-netns backend. **What it does not protect:** 802.11, DHCP, and DNS parsing still run on the host kernel — the network-VM swap-in that closes this is post-v1. |
| Templates + promotion | Build → probe → validate → gated promotion, with per-silo btrfs state snapshots and crash-consistent rollback. Lifecycle decisions are recorded **journal-first** (the journal plus on-disk evidence are the durable audit record). |
| Browser bridge + extensions | A frozen v1 operation set — `ping` and `containers.*` only — with the Chrome-family and Firefox extensions. |
| Firefox containers | Round-trip container integration, relay, and CLI. |
| Filesystem / rollback | Per-user btrfs subvolumes with Snapper rollback. **Not in v1:** the scheduled backup service, export UI, and restore pipeline — see *Planned* below. v1 does not promise automated backup or data-loss protection. |
| First-party apps | qterminator, qnotebook, qfileman, and qdbrowser. |
| SELinux policy | Tier-1 enforcing policy modules, with the `lineage_enforce` switchover landing for the release. |
| Admin app | Rules, history, silos, snapshots, and printers. |

## Experimental in v1

Shipped behind an explicit *experimental* label and validated best-effort — use
them, but they carry stated prerequisites and unsupported-failure modes.

| Capability | Why it's experimental |
|---|---|
| Tier-4/5 VM windows | waypipe-over-vsock VM app windows. Functional, but the cross-domain virtio-gpu story is a post-v1 north star. |
| TPM-sealed vault (v2) | Hardware-sealed master key. Engages only where the TPM path validates on reference hardware; otherwise the vault ships password-only. |

## Planned (not in v1)

Explicitly **not** shipped in v1. These are named here so the scope is honest —
none of them are enabled by the release install.

| Capability | Status |
|---|---|
| Recall (capture + timeline) | **Cut from v1.** Capture and the viewer are disabled and the bridge `recall.push` op is off; the design is kept for a later version. |
| Phone companion (presence / 2FA) | **Cut from v1.** Pairing/presence code stays in the tree but is **not installed or enabled** by the release bootstrap profile. |
| Installable ISO image | **Cut from v1.** v1 installs from source via the [bootstrap](@/install.md); the image track (themes, firstboot, image gates) continues post-v1. |
| Scheduled backup / export / restore | **Planned, not shipped.** The docs once described a backup timer, export UI, and restore pipeline as product behavior — none ship in v1. A signed-manifest *source* verify/restore primitive exists, but the end-to-end user backup story is later. |
| Network VM swap-in | Planned. Moves 802.11/DHCP/DNS off the host kernel (see *Per-silo VPN* above). |
| Workflow engine, portal backend, cross-machine RDP, scanner, virtual-camera ML, lineage store, manifest registry | Post-v1 north stars, deferred by design. |

---

See [how qdistro is different](@/different.md) for the design ideas behind these
features, or the [install guide](@/install.md) for the hardened release-install
flow — signature-verified once the v1 key and manifest are published.
