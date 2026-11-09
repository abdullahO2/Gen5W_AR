import re
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(r"C:\Users\k\.gemini\antigravity\scratch\nemesis-arabic-package")
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
        raise ValueError(f"[{pid}] short-desc exceeds {SHORT_MAX} chars: ({len(s_desc)}): '{s_desc}'")

    d_desc = data.get(("nemesis", "detailed-desc"), "")
    if len(d_desc) > DETAIL_MAX:
        raise ValueError(f"[{pid}] detailed-desc exceeds {DETAIL_MAX} chars: ({len(d_desc)}): '{d_desc}'")

    print(f"Validation PASSED: {pid} v{data.get(('nemesis', 'package-version'))}")
    return pid


def build_single_zip(src_dir: Path, output_zip: Path):
    validate_descriptor(src_dir / "NEMESIS.data")
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src_dir.rglob("*")):
            if p.is_file():
                content = p.read_bytes()
                if p.suffix in (".sh", ".data", ".prop"):
                    content = content.replace(b"\r\n", b"\n")
                arcname = p.relative_to(src_dir).as_posix()
                z.writestr(arcname, content)
                print(f"  + {arcname}")

    print(f"Built: {output_zip.name} ({output_zip.stat().st_size} bytes)")


def build_all_packages():
    pkgs_dir = USB_PKG_DIR / "packages"
    pkgs_dir.mkdir(parents=True, exist_ok=True)

    # Clean legacy zip files if present
    legacy_zip = pkgs_dir / "arabic.locale.zip"
    if legacy_zip.exists():
        legacy_zip.unlink()
        print(f"Removed legacy zip: {legacy_zip.name}")

    print("\n--- Building Package 1: arabic.ui (Safe Profile Mode) ---")
    build_single_zip(BASE_DIR / "arabic.ui", pkgs_dir / "arabic.ui.zip")

    print("\n--- Building Package 2: arabic.full (Full Region Mod) ---")
    build_single_zip(BASE_DIR / "arabic.full", pkgs_dir / "arabic.full.zip")


def create_usb_installer_files():
    # Multi-package store selector (type=list)
    usb_data = """[nemesis]
version=1.0
type=list

[package.0]
path=packages/arabic.ui.zip

[package.1]
path=packages/arabic.full.zip
"""
    usb_data_file = USB_PKG_DIR / "NEMESIS.data"
    with open(usb_data_file, "w", newline="\n", encoding="utf-8") as f:
        f.write(usb_data)
    print(f"\nCreated USB Package Store descriptor: {usb_data_file}")


def create_emergency_recovery_files():
    USB_RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
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
GLOBAL_STOCK=/data/nemesis/build.prop.stock
BACKUP_UI=/data/nemesis/backup/arabic.ui/build.prop.stock
BACKUP_FULL=/data/nemesis/backup/arabic.full/build.prop.stock
USB_BACKUP=./build.prop
LOG=./emergency-recover.log

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

toast() {
    local _msg="$1"
    am broadcast -a com.hkmc.intent.action.TOAST \\
        -e com.hkmc.intent.extra.TOAST_MESSAGE "$_msg" \\
        --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1 || true
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

verify_prop_file() {
    local _f="$1"
    if [ ! -f "$_f" ] || [ ! -s "$_f" ]; then
        return 1
    fi
    if ! grep "ro.build." "$_f" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

log "=== EMERGENCY RESTORATION TRIGGERED ==="
toast "NEMESIS: Emergency Recovery Triggered..."

SOURCE=""
if [ -s "$USB_BACKUP" ] && verify_prop_file "$USB_BACKUP"; then
    SOURCE="$USB_BACKUP"
    log "Using USB backup: $SOURCE"
elif [ -s "$GLOBAL_STOCK" ] && verify_prop_file "$GLOBAL_STOCK"; then
    SOURCE="$GLOBAL_STOCK"
    log "Using permanent stock backup: $SOURCE"
elif [ -s "$BACKUP_UI" ] && verify_prop_file "$BACKUP_UI"; then
    SOURCE="$BACKUP_UI"
    log "Using UI package backup: $SOURCE"
elif [ -s "$BACKUP_FULL" ] && verify_prop_file "$BACKUP_FULL"; then
    SOURCE="$BACKUP_FULL"
    log "Using Full package backup: $SOURCE"
else
    log "CRITICAL: No valid factory backup file found!"
    toast "Recovery Error: No backup found!"
    exit 1
fi

if ! sys_rw; then
    log "FAIL: cannot remount /system rw"
    toast "Recovery Error: Cannot remount rw!"
    exit 1
fi

cp -f "$SOURCE" "$BP" || {
    sys_ro
    log "FAIL: cp failed"
    toast "Recovery Error: File copy failed!"
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
toast "Recovery: Stock restored! Rebooting in 3 seconds..."

sleep 2
/system/bin/reboot 2>/dev/null || reboot 2>/dev/null || true
exit 0
"""
    with open(USB_RECOVERY_DIR / "NEMESIS.sh", "w", newline="\n", encoding="utf-8") as f:
        f.write(emerg_sh)

    print(f"Created emergency recovery tools in: {USB_RECOVERY_DIR}")


if __name__ == "__main__":
    build_all_packages()
    create_usb_installer_files()
    create_emergency_recovery_files()
    print("\n--- All Builds and Assets Successfully Created ---")
