+++
title = "Download the tester image"
template = "page.html"
description = "qdistro tester releases are a raw disk image, not an installable ISO. UEFI-only, 32 GB stick, default password qdistro, sshd off. Not a signed release."
[extra]
summary = "A xz-compressed raw disk image for a USB stick or a VM. Tester build, dev profile, checksum next to the file, no signature yet."
+++

This is a **tester disk image**, not an installable ISO and not a signed
release. Write the decompressed raw to a USB stick, or boot it as a VM
disk. A tester who boots an *install* ISO from a stick is offered a wipe
of their internal disk — qdistro does not ship that ISO.

| | |
|---|---|
| Artifact | `qdistro-<version>-<snapshot>.raw.xz` plus `qdistro-<version>-<snapshot>.raw.xz.sha256` |
| Profile | **dev** (passwordless `admin` sudoers) |
| Password | `qdistro` for `root`, `admin`, and `user` |
| sshd | Installed, **never enabled** |
| Firmware | **UEFI-only**. Legacy BIOS/CSM will not boot |
| Size | Raw is 28 GiB; **32 GB** minimum stick. USB 3 or an external SSD |
| Isolation | Tiers 0–3 supported. Tiers 4 and 5 are experimental (host side only; no guest image in the download). The tier-3s gVisor *paravirt* mode is opt-in and is not installed on this image |
| Snapshot | The `<snapshot>` in the filename is the Tumbleweed `history/<YYYYMMDD>/` pin baked into the image |

Signing is **post-v1**. There is no release signature and no signed
manifest for this file. Integrity is the sibling `.sha256`:

```sh
sha256sum -c qdistro-0.1.0-20260902.raw.xz.sha256
```

Use the names that actually arrived; the `0.1.0-20260902` token is the
current kiwi version and snapshot pin, not a promise that a file of that
name is hosted here.

## Get the file

The intended public host is a GitHub Release asset on
[github.com/qdistro/qdistro](https://github.com/qdistro/qdistro/releases)
once a tester cut is published. **No public download is published
yet.** Until it is, the bytes come from a kiwi build:

```sh
cd qdistro/image
QDISTRO_PROFILE=dev ./build-in-vm.sh
# bundle/qdistro-<version>-<snapshot>.raw.xz
# bundle/qdistro-<version>-<snapshot>.raw.xz.sha256
```

`build-in-vm.sh` needs a libvirt session; see
[image/AGENTS.md](https://github.com/qdistro/qdistro/blob/main/image/AGENTS.md).
Do not `dd` a file whose checksum does not match.

## Write it to a stick

Identify the stick (`lsblk`). The `of=` target is the whole disk, not a
partition. This destroys everything on that device.

```sh
xzcat qdistro-0.1.0-20260902.raw.xz | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress
```

Minimum 32 GB. USB 3 or an external SSD. First boot grows the btrfs
root onto leftover space (`oem-resize` on every boot; harmless when
there is nothing to grow).

## Boot it as a VM

Decompress, then attach the `.raw` as the VM disk under **OVMF / UEFI**.
Legacy BIOS will not boot. A qcow2 overlay on the raw is the usual
shape (that is what `image/verify.sh` does) so the published bytes stay
read-only:

```sh
unxz -k qdistro-0.1.0-20260902.raw.xz
qemu-img create -f qcow2 -F raw -b qdistro-0.1.0-20260902.raw overlay.qcow2
# virt-manager: firmware = UEFI (OVMF), disk = overlay.qcow2
```

Give the guest a few GiB of RAM. Nested KVM is required only for the
experimental tier-4/5 path.

## First login

greetd presents **qdgreeter** on tty3. Log in as `admin` / `qdistro`.
sshd is off; do not expect a network login.

## What this image is, and is not

VM-verified: first-boot grow, UUID identity, USB-bus boot, OpenSUSE
Secure Boot keys, persist across reboot, greeter login. A **real USB
stick on real hardware** (Secure Boot on, WPA2/WPA3, silos, reboot) is
not yet recorded.

Honest limits, so a first boot is not a surprise:

- **Not a signed v1.** Shared default password, dev profile, SELinux
  **permissive** on this image.
- **No approval-queue UI.** The broker is installed. The admin app is
  not an installer-chain step, so permission requests can enqueue with
  nobody to grant them.
- **No isolated print VM.** A host print proxy is installed; CUPS in
  a contained VM is not.
- **No installable ISO.** This file is a disk image. It is the system,
  not an installer that targets another disk.
- **Tiers 4/5 experimental.** The chain installs host launch code only.
  Build a guest image on the booted system if you have KVM
  (`qdistro-bootstrap.sh --tier4-base`).
- **No tier-3s paravirt.** The experimental gVisor application-kernel mode
  is an opt-in install (`QDISTRO_TIER3S=1` on
  `install-session-manager.sh`) and `runsc` is provisioned on demand —
  nothing of it is on this image. Launches are dev-profile only,
  `network=none`, and explicit; no KVM needed.
- **Polkit agent cannot grant** as uid 1000; that path fails closed.

From-source installs (Tumbleweed + bootstrap `--profile=dev`) stay on
the [homepage](https://qdistro.org/#try) for developers iterating the tree.
