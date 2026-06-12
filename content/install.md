+++
title = "Install qdistro"
template = "page.html"
description = "From a minimal openSUSE Tumbleweed to a running qdistro desktop — the hardened, signature-verified install path. Verify the signed release manifest before root clones or builds any source."
[extra]
summary = "Tumbleweed-minimal → verify the signed manifest → bootstrap → first boot. The release install verifies a published signing key before root ever clones or builds anything."
+++

This guide takes a clean **openSUSE Tumbleweed** machine to a running qdistro
desktop. It documents the **hardened, signature-verified** install — the path a
real machine should use, where the bootstrap refuses to clone, build, or
root-install any source tree until it has verified a **signed release manifest**
against a published key.

There are two ways to install qdistro, and they are not the same trust level:

- **Developer preview** (what the [home page](@/_index.md) shows): clone three
  repos and run the bootstrap. Fast, but the sources are pinned to `main` and
  nothing is signature-verified — fine for a throwaway VM, *not* a trust anchor.
- **Hardened release install** (this page): start from a published, signed
  release manifest. The bootstrap verifies its signature **before any clone or
  build runs as root**, and pins every repo to the exact commit the release was
  tested from. This is the path the clean-room install verification follows
  verbatim.

> **Release-key status.** The signing/verification machinery and the
> [key-custody policy](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/release-signing.md)
> are in place, but the **v1 release key has not been generated and published
> yet**. Until it is, the published fingerprint below is a placeholder and only
> the developer-preview path can complete end to end. This page is the
> specification the first signed release will ship against — published ahead of
> the key so you can hold the verification flow to it.

## What you need

- A spare machine or VM — qdistro is single-tenant and takes over the session.
  ≥16 GB RAM, ≥100 GB free disk. A fingerprint reader is optional but used by
  the locker if present.
- A **fresh, terminal-only openSUSE Tumbleweed** install (Minimal or Server — no
  desktop). qdistro layers onto Tumbleweed rather than replacing it; you keep
  its package updates and Snapper rollback.
- The first user must be named **`admin`** — qdistro reserves `admin` at uid
  1000 and the rest of the tree hardcodes that. You run the bootstrap with
  `sudo` (entering the root/admin password when prompted); the bootstrap itself
  adds `admin` to `wheel` as part of the install.

## Step 1 — Install Tumbleweed

Install openSUSE Tumbleweed from
[get.opensuse.org](https://get.opensuse.org/tumbleweed/), choosing the
**Minimal** or **Server** system role (no desktop). Create the first user as
`admin`. Boot to the text console and log in as `admin`.

`git` is not on a Minimal/Server image — install it:

```sh
sudo zypper install -y git
```

## Step 2 — Fetch the bootstrap and the release artifacts

A signed release is four files, all fetched over TLS from the install site
alongside the bootstrap:

| File | What it is |
| --- | --- |
| `qdistro-bootstrap.sh` | the installer (ships inside the `qdistro` repo) |
| `source-manifest.txt` | the signed release manifest — every repo pinned to a commit |
| `source-manifest.txt.sig` | the detached OpenPGP signature over the manifest |
| `qdistro-release-keyring.gpg` | the published release public key, for `gpgv` |

Clone the `qdistro` repo (it carries the bootstrap and the verification tools),
then place the release manifest, its signature, and the keyring next to the
bootstrap under `scripts/install/`:

```sh
git clone https://codeberg.org/qdistro/qdistro.git
cd qdistro/scripts/install

# Fetch the three signed-release artifacts. These URLs are the planned
# publish convention — they 404 until the first signed release ships
# (see the release-key status note above); only the developer preview
# works end to end today.
curl -fLO https://qdistro.org/release/source-manifest.txt
curl -fLO https://qdistro.org/release/source-manifest.txt.sig
curl -fLO https://qdistro.org/release/qdistro-release-keyring.gpg
```

The bootstrap looks for `source-manifest.txt`, `source-manifest.txt.sig`, and
`qdistro-release-keyring.gpg` in `scripts/install/` by default. Override the
signature and keyring with `--manifest-sig` / `--release-keyring`, and any of
the three (manifest included) with the matching `QDISTRO_SOURCE_MANIFEST`,
`QDISTRO_SOURCE_MANIFEST_SIG`, and `QDISTRO_RELEASE_KEYRING` environment
variables (see
[release-signing.md](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/release-signing.md)).

## Step 3 — Verify before you run anything as root

This is the step that makes the install a release rather than "curl | sudo
bash". **Do it before the bootstrap, and confirm the key fingerprint out of
band.**

First, confirm the keyring you downloaded really is the qdistro release key.
Compare its fingerprint against the one published here and in
[release-signing.md](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/release-signing.md)
— ideally cross-checked against a second source you trust:

```sh
gpg --show-keys --with-fingerprint qdistro-release-keyring.gpg
```

> **v1 release fingerprint:** `0xUNPUBLISHED` — *placeholder; the real
> fingerprint is published here when the v1 release key is generated.* Treat any
> keyring that does not match the published fingerprint as untrusted.

Then verify the manifest signature, binding it to that exact fingerprint:

```sh
./verify-source-manifest.sh \
    source-manifest.txt \
    source-manifest.txt.sig \
    qdistro-release-keyring.gpg \
    0xUNPUBLISHED        # the full 40-hex release fingerprint
```

(Run verbatim with the `0xUNPUBLISHED` placeholder, this command exits with an
error — the verifier rejects anything that isn't a full 40-hex fingerprint.
Substitute the real fingerprint once the v1 key is published.)

`verify-source-manifest.sh` does three things, all fail-closed:

1. **`gpgv`** verifies the detached signature over the manifest.
2. If you pass the expected signer, the **authoritative** signing key reported
   by `gpgv` (its `VALIDSIG` full fingerprint) must equal it exactly. This binds
   the manifest to your published key even if the keyring holds several — and it
   ignores any advisory `signer=` field *inside* the document. A short key id is
   rejected; suffix matching is not collision-resistant.
3. The manifest is re-checked to be exactly the bootstrap-compatible
   `<repo> <40-hex-sha>[ tag=… artifact=… signer=…]` pin format.

A printed `verify-source-manifest: OK source-manifest.txt` is your go-ahead.
Anything else — bad signature, wrong signer, malformed manifest — means **stop**.

You do not strictly *have* to run the verifier by hand: the bootstrap runs the
same gate itself (next step). Doing it first lets you confirm the key
fingerprint with your own eyes before any privileged code starts.

## Step 4 — Run the bootstrap

The default profile is **`daily-driver`** — the hardened path. A caller who
forgets to choose still gets the safe profile, never the throwaway one. From the
`qdistro` repo root:

```sh
cd ~/qdistro
sudo bash scripts/install/qdistro-bootstrap.sh \
    --release-signer 0xUNPUBLISHED
```

Pass `--release-signer` (the full release fingerprint) so the bootstrap binds
the manifest to your published key, not merely to "some key in the keyring".
The keyring and signature are found automatically in `scripts/install/`; point
elsewhere with `--release-keyring` / `--manifest-sig` if needed.

What happens, in order:

1. **Signature gate first.** At the very top of source acquisition — ahead of
   even `--skip-sources` — the bootstrap copies the manifest and its signature
   into a **root-owned `0700` directory** and verifies them *there* (closing the
   time-of-check/time-of-use window when bootstrap runs out of a user-owned
   tree). A missing keyring or signature, a bad signature, or a signer mismatch
   is **fatal** — root will not clone, pin-check, build, or install any source
   tree until the manifest verifies. Once the manifest carries any active pin
   line, a hardened profile *requires* it to verify. (This gate covers the
   *source* you build; it does not itself verify the bootstrap script you
   launched with `sudo` — fetch that over TLS and review it, since it runs
   privileged before the gate does.)
2. **Per-repo pinning.** Every repo is checked out at the exact commit the
   manifest names; if a line carries a `tag=`, the tag must resolve to that
   commit (a mismatch is tamper-evidence and is fatal).
3. **Build and install.** Dependencies install, qdwin (the libweston shell
   plugin) and the C daemons build, the qdshell QML plugin builds, and the
   Python apps (qdgreeter, qdlocker, qdbrowser, qterminator, qnotebook,
   qfileman) install into an isolated `/opt/qdistro` prefix with `/usr/bin`
   wrappers.
4. **Session wiring.** SELinux policy loads (permissive to start), the admin
   qdwin session installs, and greetd is configured to bring the desktop up on
   tty3.

The hardened profile holds the line on dev-only shortcuts: no
`admin NOPASSWD: ALL`, no `--no-gpg-checks` fetches, no passwords on argv/env
(use `--admin-password-fd` / `--user-password-fd` or interactive entry), btrfs
subvolume failures are fatal, and the dev-only phone-companion step is skipped
entirely. The run is idempotent — re-running is safe. It takes roughly 10–20
minutes.

## Step 5 — First boot

Reboot. greetd brings up the **qdgreeter login** on tty3 (a
password-required greeter — autologin is off by default). Log in as `admin`;
greetd starts the qdwin compositor and the qdshell desktop
(`qdwin-session.target`).

If something goes sideways, the install leaves you escape hatches:

- **tty4** (`Ctrl+Alt+F4`) is a deliberate recovery session: greetd's
  `greetd-fallback.service` brings up a legacy LXQt + labwc Wayland session as
  `admin`, so a wedged qdwin/qdshell commit still leaves you a working desktop.
- The plain text consoles (`Ctrl+Alt+F2`/`F1`) remain available for a shell.
- Tumbleweed's stock **Snapper + GRUB snapshot boot** still recovers the base
  OS, but note it does *not* roll back the qdistro install on its own: the
  bootstrap takes no pre-install root snapshot, and qdistro's files live under
  `/opt/qdistro`, `/opt/qdistro-src`, and `/var/lib/qdistro`, which the default
  root-snapshot layout excludes.
- The bootstrap is idempotent — re-run it to repair a partial install.

From here, read the [overview](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/overview.md)
and [isolation-tiers](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/isolation-tiers.md)
docs to start placing apps into silos.

## What this verifies — and what it doesn't

The signed manifest is a **source-integrity** anchor: it proves the commits you
build came from the holder of the release key, unaltered in transit, and pins
every repo to a tested commit. It does **not** yet enforce a built-artifact hash
against the binaries the build produces — the manifest carries an `artifact=`
digest field for that story, but the build step does not yet check binaries
against it. And it is only as strong as your confidence in the published
fingerprint: verify it out of band.

The full custody model — key generation, storage on an offline token, rotation,
and revocation — is documented in
[release-signing.md](https://codeberg.org/qdistro/qdistro/src/branch/main/doc/release-signing.md).
That page is the one-page custody record the v1 release blocks on.
