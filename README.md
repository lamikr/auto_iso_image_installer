# Rocky Linux 8.10 Unattended ISO Builder

This workspace creates a repeatable Rocky Linux 8.10 installer ISO using:

- a JSON config file (`build-config.json`)
- a Kickstart template (`templates/rocky8.ks.tmpl`)
- a non-interactive build script (`build_rockylinux_8_10_iso.py`)

## What this produces

An output ISO that boots the Rocky installer and uses embedded Kickstart values for unattended installation.

Configured defaults include:

- user `therock`
- `therock` account created locked (no password login)
- user in `wheel`
- passwordless sudo for `therock`
- `sshd` enabled
- ping (ICMP echo) allowed
- generated passwordless SSH keypair for `therock`
- key-only SSH login policy for `therock` (password auth disabled)

## Prerequisites (on the build host)

Install required tools:

```bash
sudo apt-get update
sudo apt-get install -y genisoimage xorriso isolinux syslinux-utils openssh-client python3
```

The build script prefers `mkisofs` (from `genisoimage`) and falls back to `xorrisofs`/`xorriso`.
On Rocky/RHEL build hosts, install equivalent packages that provide either `mkisofs` or `xorrisofs`.

## Configure

Edit `build-config.json`:

- all keys are required; the build script does not apply defaults
- optionally set `source_iso_sha256` for checksum verification
- customize hostname/timezone/lang/paths as needed
- SSH behavior:
  - leave `ssh_authorized_public_key` empty to auto-generate keypair
  - generated keys default to `./output/ssh/therock_ed25519` and `.pub`
  - set `ssh_authorized_public_key` if you want to inject an existing public key
  - keep `disable_user_password_auth: true` to enforce key-only login for `therock`

## Build

From this directory:

```bash
python3 ./build_rockylinux_8_10_iso.py ./build-config.json
```

Output ISO path (default):

`./output/Rocky-8.10-x86_64-autoinstall.iso`

Generated SSH keys (default):

- private key: `./output/ssh/therock_ed25519`
- public key: `./output/ssh/therock_ed25519.pub`

Example login after install:

```bash
ssh -i ./output/ssh/therock_ed25519 therock@<installed-host-ip>
```

## Notes

- The Kickstart template uses `clearpart --all --initlabel` with explicit partition rules, which wipes target disks during install.
- `/boot` is explicitly set to `1536 MiB` (1.5 GiB).
- `/home` is not created as a separate filesystem; user homes live under `/`.
- SSH key authorization for `therock` is configured by Kickstart `sshkey` during install.
- Boot configs are patched to default to direct install (skip media-check default) and include serial console args for headless VM troubleshooting.
