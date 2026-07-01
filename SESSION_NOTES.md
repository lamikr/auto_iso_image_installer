# Session Notes

## Current Status

- ISO automation is implemented and builds successfully.
- Output ISO path:
  - `~/rockylinux_8_10_iso/output/Rocky-8.10-x86_64-autoinstall.iso`
- Kickstart is embedded and boot args include:
  - `inst.ks=cdrom:/ks.cfg`
- `therock` is configured as:
  - locked password account
  - SSH key login via Kickstart `sshkey`
  - passwordless sudo
- Partition layout:
  - `/boot` = `1536 MiB`
  - `/` grows (`--grow`)
  - no separate `/home`

## Why SSH Login Test Failed Last Time

- VM network forward (`2222 -> guest 22`) was open.
- SSH timed out at banner exchange, meaning guest `sshd` was not ready yet.
- Likely causes:
  - QEMU used slow TCG fallback because KVM access was denied in that session.
  - Installer may not have completed first boot yet.

## After New SSH Login

Run these first:

```bash
cd ~/rockylinux_8_10_iso
id
groups
ls -l /dev/kvm
```

Expected: `kvm` appears in groups and `/dev/kvm` is group-readable/writable by `kvm`.

## Rebuild + Validate

```bash
cd ~/rockylinux_8_10_iso
python3 ./validate-config.py ./build-config.json
python3 ./build_rockylinux_8_10_iso.py ./build-config.json
```

## KVM Test Commands

```bash
cd ~/rockylinux_8_10_iso
rm -f ./output/rocky810-test.qcow2 ./output/rocky810-test.pid
qemu-img create -f qcow2 ./output/rocky810-test.qcow2 30G
qemu-system-x86_64 \
  -name rocky810-test \
  -machine accel=kvm:tcg \
  -m 4096 -smp 2 \
  -drive file=./output/rocky810-test.qcow2,if=virtio,format=qcow2 \
  -cdrom ./output/Rocky-8.10-x86_64-autoinstall.iso \
  -boot once=d,menu=off \
  -netdev user,id=n1,hostfwd=tcp::2222-:22 \
  -device virtio-net-pci,netdev=n1 \
  -display none \
  -serial file:./output/qemu-serial.log \
  -daemonize \
  -pidfile ./output/rocky810-test.pid
```

## SSH Poll Test

```bash
cd ~/rockylinux_8_10_iso
for i in $(seq 1 180); do
  ssh -i ./output/ssh/therock_ed25519 \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=5 \
    -p 2222 therock@127.0.0.1 "echo SSH_OK && id && hostnamectl --static" && break
  sleep 10
done
```

## Cleanup

```bash
cd ~/rockylinux_8_10_iso
if [ -f ./output/rocky810-test.pid ]; then
  kill "$(cat ./output/rocky810-test.pid)" 2>/dev/null || true
fi
```
