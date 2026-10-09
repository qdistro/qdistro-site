+++
title = "Paravirt mode: a silo under a gVisor application kernel"
date = 2026-10-09
description = "Tier 3s lands in the tree: an opt-in, dev-only isolation rung where a silo workload's syscalls are served by the gVisor Sentry instead of the host kernel — GUI windows included, over a waypipe byte-stream bridge."
[taxonomies]
tags = ["isolation", "paravirt", "gvisor"]
+++

*This post describes an experimental feature. It is opt-in, dev-profile only,
and is not on the tester image — but it is real code with a VM acceptance
lane, and the scope below is what the tree enforces, not a roadmap.*

## The gap it fills

qdistro's isolation ladder has always run from "confined but on the host
kernel" (tiers 0–3: SELinux, rootless podman, separate uids) to "a whole
virtual machine" (tiers 4–5, KVM). Between them was nothing — until now.
Tier 3s is the middle rung: a workload runs in rootless podman under the
gVisor `runsc` application kernel (systrap platform), so its system calls
are answered by the gVisor Sentry — a userspace kernel — instead of the
host kernel.

That matters for the threat model: tiers 0–3 share host-kernel fate, so a
host-kernel bug collapses them together. In tier 3s the Sentry mediates
workload syscalls and exposes a reduced, seccomp-narrowed host-kernel
surface. It is still not a VM boundary — there is no KVM claim — but it is
a meaningfully different failure shape than a plain container.

## What it looks like

Each tier-3s silo gets a dedicated host account (`qt3s-<silo>`) that owns
the podman store and the runsc state root — nothing runs podman or runsc
as root or as admin. The workload gets a read-only root, no capabilities,
`no-new-privileges`, a per-workload seccomp profile, and `network=none` —
the only network mode.

GUI apps work too. gVisor cannot pass host file descriptors across its
boundary, so instead of handing the workload a Wayland socket, a
`waypipe` pair bridges the protocol as a byte stream: a host-side client
(tagged with a trusted security context so the compositor and shell know
which silo a window belongs to) and a sandbox-side server. Windows land on
the admin desktop tagged `[3s:<silo>]` like any other silo window —
software rendering only, no GPU. The VM acceptance lane verifies that a
malformed stream terminates only its own bridge connection — the
compositor and sibling launches keep running — while the host-side
bridge client remains a trusted parsing surface by contract. The attach
is one-shot: a dropped bridge means relaunch, not reconnect.

Clipboard crossing stays default-deny and goes through the same broker
gates as every other tier, with the strict MIME allow-list.

## How you get it (and how you don't)

Nothing selects this tier automatically — a silo is tier 3s only because
it was created that way, and a refused launch never falls back to tier 2
or 3. The launch path installs only when you ask for it:

```sh
# dev VM, as root, from a root-owned checkout (the provisioner refuses one
# another uid could modify):
QDISTRO_TIER3S=1 scripts/install/install-session-manager.sh "$PWD/session_manager"
tier3s/provision-runsc.sh            # installs a pinned, sha512-verified runsc bundle
tier3s/probe.sh --user admin         # prerequisite screen; refuses non-dev profiles
```

`runsc` is deliberately *not* in the image, the installer, or any kiwi
config: it is provisioned on demand from a dated, hash-pinned upstream
release, and the provisioner fails closed on any hash, file-set, or
version mismatch.

## What it is not

- **Not shipped.** Dev profile only; the launch path, the probe, and the
  session manager all refuse anything else, and none of it is on the
  tester image.
- **Not a VM.** No KVM, no guest kernel — the VM tiers remain where
  containment survives a host-kernel-quality bug.
- **Not networked.** `network=none` is the only mode.
- **Not seamless magic.** The GUI bridge is a byte stream with software
  rendering — fine for terminals and editors, not a GPU path.

The contract and the tested lifecycle guarantees live in
[`tier3s/`](https://github.com/qdistro/qdistro/tree/main/tier3s) — the
README there is the operator page; [`doc/isolation-tiers.md`](https://github.com/qdistro/qdistro/blob/main/doc/isolation-tiers.md)
places the rung on the ladder.
