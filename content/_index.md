+++
title = "qdistro"
template = "index.html"
+++

A **single-tenant Linux distribution** with Qubes-inspired seamless app
isolation — built on libweston + Wayland + Python/Qt/QML and designed
to be **easy to modify with LLM assistance**.

## Status

Pre-release. The design is settled; implementation is a moving
target. No installable image yet — the repos build and run inside
test VMs.

## Principles

1. **LLM-modifiability first.** Userspace (apps, shell, session manager,
   admin tools) is Python + Qt + QML so humans and LLMs can modify it
   directly. The compositor core and transport infrastructure are
   commodity C (libweston, PipeWire, FreeRDP, qemu, kernel) —
   leveraged, not rewritten.
2. **Single-tenant.** One physical person, one fingerprint. Multiple
   Linux users exist only to separate *data*, not to authenticate
   different humans.
3. **Admin is the trusted base.** One admin user owns all hardware
   and approves all cross-silo actions.

## Repositories

qdistro is split across three sibling repos that check out side-by-side:

| Repo | Role |
|---|---|
| [qdistro](https://codeberg.org/qdistro/qdistro) | Umbrella: docs, permission infra, daemons, SDK, admin app, integration tests |
| [qdwin](https://codeberg.org/qdistro/qdwin) | Wayland compositor (libweston) |
| [qdshell](https://codeberg.org/qdistro/qdshell) | Desktop shell (Noctalia QML fork) |

```sh
mkdir qdistro-org && cd qdistro-org
git clone https://codeberg.org/qdistro/qdistro.git
git clone https://codeberg.org/qdistro/qdwin.git
git clone https://codeberg.org/qdistro/qdshell.git
```

Build order: `qdwin` first (the umbrella's daemons compile against
qdwin's protocol XML), then `qdistro`, then `qdshell`.

## Sister projects

- [qnotebook.org](https://qnotebook.org) — PyQt6 markdown wiki editor
- [qterminator.org](https://qterminator.org) — Qt port of Terminator
