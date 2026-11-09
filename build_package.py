import re
import zipfile
from pathlib import Path

BASE_DIR = Path(r"C:\Users\k\.gemini\antigravity\scratch\nemesis-arabic-package")
SRC_DIR = BASE_DIR / "arabic.locale"
USB_PKG_DIR = BASE_DIR / "usb_package"
USB_RECOVERY_DIR = BASE_DIR / "usb_emergency_recovery"

SHORT_MAX = 64
DETAIL_MAX = 256
VER_RE = re.compile(r"^\d+(\.\d+)*$")
ID_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]{0,63}$")


def validate_descriptor(meta_path: Path):
    text = meta_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith(("#", ";"))]
    data = {}
    sec = ""
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            sec = line[1:-1].strip()
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"')
            data[(sec, k.strip())] = v

    ver = data.get(("nemesis", "version"), "1.0")
    if not VER_RE.match(ver):
        raise ValueError(f"Invalid version: {ver}")

    pid = data.get(("nemesis", "id"), "")
    if not ID_RE.match(pid):
        raise ValueError(f"Invalid id: {pid}")

    s_desc = data.get(("nemesis", "short-desc"), "")
    if len(s_desc) > SHORT_MAX:
        raise ValueError(f"short-desc exceeds {SHORT_MAX} chars: ({len(s_desc)})")

    d_desc = data.get(("nemesis", "detailed-desc"), "")
    if len(d_desc) > DETAIL_MAX:
        raise ValueError(f"detailed-desc exceeds {DETAIL_MAX} chars: ({len(d_desc)})")

    print(f"Validation PASSED: {pid} v{data.get(('nemesis', 'package-version'))}")


def build_zip():
    meta = SRC_DIR / "NEMESIS.data"
    validate_descriptor(meta)

    out_zip = USB_PKG_DIR / "packages" / "arabic.locale.zip"
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SRC_DIR.rglob("*")):
            if p.is_file():
                content = p.read_bytes()
                if p.suffix in (".sh", ".data", ".prop"):
                    content = content.replace(b"\r\n", b"\n")
                arcname = p.relative_to(SRC_DIR).as_posix()
                z.writestr(arcname, content)
                print(f"Added to zip: {arcname}")

    print(f"Package built successfully: {out_zip} ({out_zip.stat().st_size} bytes)")


def create_usb_installer_files():
    usb_data = """[nemesis]
version=1.0
type=install
path=packages/arabic.locale.zip
"""
    usb_data_file = USB_PKG_DIR / "NEMESIS.data"
    with open(usb_data_file, "w", newline="\n", encoding="utf-8") as f:
        f.write(usb_data)
    print(f"Created: {usb_data_file}")


def create_emergency_recovery_files():
    emerg_flag = USB_RECOVERY_DIR / "NEMESIS.emergency"
    emerg_flag.write_bytes(b"")

    emerg_data = """[nemesis]
version=1.0
type=execute
path=NEMESIS.sh
"""
    with open(USB_RECOVERY_DIR / "NEMESIS.data", "w", newline="\n", encoding="utf-8") as f:
        f.write(emerg_data)

    emerg_sh = """#!/system/bin/sh
# Failsafe Emergency Recovery Script for Gen5W (Pure toolbox compatible)
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

BP=/system/build.prop
BACKUP1=/data/nemesis/backup/arabic.locale/build.prop.stock
BACKUP2=/data/nemesis/build.prop.stock
USB_BACKUP=./build.prop
LOG=./emergency-recover.log

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

sys_rw() {
    /system/xbin/nemesis remount rw >/dev/null 2>&1 && return 0
    mount -o remount,rw /system 2>/dev/null && return 0
    mount -o rw,remount /system 2>/dev/null && return 0
    return 1
}

sys_ro() {
    /system/xbin/nemesis remount ro >/dev/null 2>&1 || true
    mount -o remount,ro /system 2>/dev/null || true
}

log "=== EMERGENCY RESTORATION TRIGGERED ==="

SOURCE=""
if [ -s "$USB_BACKUP" ]; then
    SOURCE="$USB_BACKUP"
    log "Using USB backup: $SOURCE"
elif [ -s "$BACKUP1" ]; then
    SOURCE="$BACKUP1"
    log "Using package backup: $SOURCE"
elif [ -s "$BACKUP2" ]; then
    SOURCE="$BACKUP2"
    log "Using global backup: $SOURCE"
else
    log "CRITICAL: No valid backup file found!"
    exit 1
fi

if ! sys_rw; then
    log "FAIL: cannot remount /system rw"
    exit 1
fi

cp -f "$SOURCE" "$BP" || {
    sys_ro
    log "FAIL: cp failed"
    exit 1
}

chmod 644 "$BP" 2>/dev/null || true
chown 0.0 "$BP" 2>/dev/null || chown 0:0 "$BP" 2>/dev/null || true

# Clear persist locale overrides
rm -f /data/property/persist.sys.language_list 2>/dev/null || true
rm -f /data/property/persist.sys.timezone 2>/dev/null || true

sys_ro
sync
log "=== EMERGENCY RESTORE COMPLETED SUCCESSFULLY. REBOOTING ==="
reboot
exit 0
"""
    with open(USB_RECOVERY_DIR / "NEMESIS.sh", "w", newline="\n", encoding="utf-8") as f:
        f.write(emerg_sh)

    print(f"Created emergency recovery tools in: {USB_RECOVERY_DIR}")


if __name__ == "__main__":
    build_zip()
    create_usb_installer_files()
    create_emergency_recovery_files()
