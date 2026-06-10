+++
title = "Templates: updates that prove themselves before they land"
date = 2026-06-10
description = "qdistro's next big promise — templated workloads get versioned software, updated by validation and promotion instead of in-place mutation. Specified now, shipping before 1.0."
[taxonomies]
tags = ["design", "templates", "silos"]
+++

*This post announces a design ahead of its delivery. The model below is fully
specified in [templates.md](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/templates.md)
and the first slice is being built in the open — but as of today you cannot
install it. We're publishing the promise first so you can hold us to it.*

## The problem

Every desktop user knows the feeling: an update lands, and something you
relied on is gone. The classic worst case — a vendor "improves" your office
suite and Save quietly stops working. On a normal distro your options are
archaeology (downgrade packages, hope the profile still opens) or
acceptance.

qdistro's silo model already keeps your work, personal, and dev worlds
apart. Templates extend that separation to *time*: the version of an app
you're using is kept apart from the version an update wants you to use,
until the new one proves itself.

## The model

A templated silo gets its software from a **template** — a versioned
installation containing no configuration and no user data. This covers dev
toolchains, containers, VMs, and cleanly packaged desktop apps; plugin-heavy
apps whose profiles blur the software/state line keep a snapshot-based path
and are labeled as such. Your silo owns only its config, state, and
authority; the binding between silo and template version is one small file.

Updates never mutate the version you're running:

1. The update is applied to a **candidate clone** of the template.
2. The candidate is probed and validated in a disposable environment — for
   the office suite, an agent literally creates a document, saves it,
   reopens it, and checks the content survived. Account-bearing checks use
   dedicated test accounts, never your sessions.
3. Untrusted installer code — npm postinstall scripts, vendor auto-updaters
   — runs **only inside the candidate**, which holds no secrets, no
   credentials, no documents. It can be caught poisoning the update — but
   your documents, sessions, and keys aren't in the room to steal.
4. Only after the candidate passes (plus an audit gate for untrusted
   sources) does your launcher flip to it, at the next natural restart. You
   never wait for an upgrade.

If the save-reopen check fails? The candidate is discarded, the failure and
evidence land in your admin queue, and your desktop icon keeps opening the
version that works. Recovery isn't a procedure — nothing you use was ever
touched.

## Honest edges

We're deliberately precise about what this does *not* promise. Validation
is never complete — passing save-reopen doesn't prove every macro works.
Cloud-synced data can't be rolled back by any local system, and we say so
per silo instead of pretending. Apps whose plugins and profiles blur the
software/state line (looking at you, IDE marketplaces) get a weaker,
snapshot-based path and are labeled as such. And in the full design, first-launch
profile migrations — the one step that must touch real state — will run
under a declared network policy with a pre-migration snapshot, so even that
step has a defined undo (this lands later in the rollout, after the first
backend).

## When

The on-disk model is boring on purpose — TOML files, btrfs snapshots,
podman image digests, systemd one-shot units; no control plane, no daemons
watching daemons. The first backend (podman container images, starting with
the dev-toolchain workload) is in active development, with Nix-backed
toolchains and golden-VM artifacts following the same contract. Watch the
repo, read the spec, and tell us where the promise has holes — that's what
this stage is for.
