import os
import shutil
from pathlib import Path

BASE_DIR = Path(r"C:\Users\k\.gemini\antigravity\scratch\nemesis-arabic-package")

# Remove obsolete directory if it exists
old_pkg = BASE_DIR / "arabic.locale"
if old_pkg.exists():
    shutil.rmtree(old_pkg)
    print(f"Removed legacy directory: {old_pkg}")

# ==============================================================================
# 1. ARABIC.UI (Safe Mode - Profile Language Only, Zero Region Conflicts)
# ==============================================================================
UI_DIR = BASE_DIR / "arabic.ui"

nemesis_data_ui = """[nemesis]
version=1.1
id=arabic.ui
name="Arabic UI Language"
type=application
package-version=1.2
short-desc="Safe Arabic UI (Profile only, zero mod conflicts)"
detailed-desc="Safe Mode: Adds Arabic to profile language settings without changing system region. 100% safe for CarPlay/AA & other regional mods. Includes auto stock backup, auto reboot, and USB unlooping."
os=any
models=any
preinstall=scripts/pre.sh
postinstall=scripts/post.sh
preuninstall=scripts/preun.sh

[app.0]
kind=sh
path=bin/status.sh
uid=root
"""

pre_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.ui.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log " DISCLAIMER / إخلاء مسؤولية "
log " Installing Arabic UI Language (Safe Profile Mode). "
log " This package modifies persist.sys.language_list only. "
log " System region and navigation engine remain untouched. "
log " Author holds no liability for device failure or damage. "
log "=========================================================="
exit 0
"""

common_sh_template = """#!/system/bin/sh
# common.sh - Helper functions for Gen5W NEMESIS package
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

PKG_ID="{PKG_ID}"
BP="/system/build.prop"
BACKUP_DIR="/data/nemesis/backup/$PKG_ID"
GLOBAL_BACKUP="/data/nemesis/build.prop.stock"
LOG="/data/nemesis/$PKG_ID.log"

log() {
    local _msg="$1"
    echo "$_msg"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$_msg" >> "$LOG" 2>/dev/null || true
}

toast() {
    local _msg="$1"
    am broadcast -a com.hkmc.intent.action.TOAST \\
        -e com.hkmc.intent.extra.TOAST_MESSAGE "$_msg" \\
        --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1 || true
}

putline() {
    print -r -- "$1" 2>/dev/null && return 0
    printf '%s\\n' "$1" 2>/dev/null && return 0
    echo "$1"
}

sys_rw() {
    /system/xbin/nemesis remount rw >/dev/null 2>&1 && return 0
    mount -o remount,rw /system 2>/dev/null && return 0
    mount -o rw,remount /system 2>/dev/null && return 0
    mount -o rw,remount / 2>/dev/null && return 0
    return 1
}

sys_ro() {
    /system/xbin/nemesis remount ro >/dev/null 2>&1 || true
    mount -o remount,ro /system 2>/dev/null || true
    mount -o ro,remount /system 2>/dev/null || true
}

# Android 4.4 toolbox compatible validation
verify_prop_file() {
    local _f="$1"
    if [ ! -f "$_f" ] || [ ! -s "$_f" ]; then
        log "FAIL: $_f does not exist or is empty"
        return 1
    fi
    if ! grep "ro.build." "$_f" >/dev/null 2>&1; then
        log "FAIL: $_f missing essential ro.build properties"
        return 1
    fi
    return 0
}

commit_tmp() {
    local _dst="$1"
    local _tmp="$2"
    
    if ! verify_prop_file "$_tmp"; then
        log "FAIL: commit aborted, temp file failed validation"
        rm -f "$_tmp" 2>/dev/null || true
        return 1
    fi
    
    cp -f "$_tmp" "$_dst" || {
        log "FAIL: cp $_tmp to $_dst failed"
        return 1
    }
    
    chmod 644 "$_dst" 2>/dev/null || true
    chown 0.0 "$_dst" 2>/dev/null || chown 0:0 "$_dst" 2>/dev/null || true
    rm -f "$_tmp" 2>/dev/null || true
    return 0
}

snapshot_all() {
    # If a valid global stock backup already exists, preserve it permanently!
    if [ -s "$GLOBAL_BACKUP" ] && verify_prop_file "$GLOBAL_BACKUP"; then
        log "Original factory backup already verified at $GLOBAL_BACKUP (preserved)"
        mkdir -p "$BACKUP_DIR" 2>/dev/null || true
        if [ ! -s "$BACKUP_DIR/build.prop.stock" ]; then
            cp -f "$GLOBAL_BACKUP" "$BACKUP_DIR/build.prop.stock" 2>/dev/null || true
        fi
        putline 1 > "$BACKUP_DIR/saved" 2>/dev/null || true
        return 0
    fi

    if [ -s "$BACKUP_DIR/saved" ]; then
        log "Stock backup already exists ($BACKUP_DIR) - keeping original intact"
        return 0
    fi
    
    if ! verify_prop_file "$BP"; then
        log "FAIL: Refusing to snapshot invalid $BP"
        return 1
    fi
    
    mkdir -p "$BACKUP_DIR" || return 1
    
    # Save full build.prop to package backup dir
    cp -f "$BP" "$BACKUP_DIR/build.prop.stock" || return 1
    if ! verify_prop_file "$BACKUP_DIR/build.prop.stock"; then
        log "FAIL: Snapshot build.prop.stock verification failed"
        rm -rf "$BACKUP_DIR"
        return 1
    fi
    
    # Save permanent global stock copy
    if [ ! -s "$GLOBAL_BACKUP" ]; then
        cp -f "$BP" "$GLOBAL_BACKUP" 2>/dev/null || true
    fi
    
    putline 1 > "$BACKUP_DIR/saved" || return 1
    log "Successfully created stock backup in $BACKUP_DIR"
    return 0
}

set_prop_line() {
    local _file="$1"
    local _key="$2"
    local _val="$3"
    local _tmp="$BACKUP_DIR/rewrite.tmp"
    local _line
    local _seen=0
    local _in=0
    local _out=0
    
    : > "$_tmp" || return 1
    while IFS= read -r _line || [ -n "$_line" ]; do
        _in=$((_in + 1))
        case "$_line" in
            "${_key}="*)
                putline "${_key}=${_val}" >> "$_tmp" || return 1
                _seen=1
                _out=$((_out + 1))
                ;;
            *)
                putline "$_line" >> "$_tmp" || return 1
                _out=$((_out + 1))
                ;;
        esac
    done < "$_file"
    
    if [ "$_seen" -eq 0 ]; then
        putline "${_key}=${_val}" >> "$_tmp" || return 1
        _out=$((_out + 1))
    fi
    
    if [ "$_out" -lt "$_in" ]; then
        log "FAIL: rewrite of $_file dropped lines ($_out < $_in)"
        rm -f "$_tmp" 2>/dev/null || true
        return 1
    fi
    
    commit_tmp "$_file" "$_tmp" || return 1
    log "Property set: ${_key}=${_val}"
    return 0
}

restore_all() {
    local _stock="$BACKUP_DIR/build.prop.stock"
    if [ ! -s "$_stock" ]; then
        _stock="$GLOBAL_BACKUP"
    fi
    
    if ! verify_prop_file "$_stock"; then
        log "FAIL: Cannot restore, valid stock backup not found"
        return 1
    fi
    
    if ! sys_rw; then
        log "FAIL: remount /system rw failed during restore"
        return 1
    fi
    
    cp -f "$_stock" "$BP" || {
        sys_ro
        log "FAIL: Restoring stock build.prop failed"
        return 1
    }
    
    chmod 644 "$BP" 2>/dev/null || true
    chown 0.0 "$BP" 2>/dev/null || chown 0:0 "$BP" 2>/dev/null || true
    
    # Clean runtime persist overrides
    rm -f /data/property/persist.sys.language_list 2>/dev/null || true
    
    sync
    sys_ro
    log "Restored stock build.prop successfully"
    return 0
}

# Automatically rename NEMESIS.data on USB drives to prevent repeated prompts on boot
rename_usb_data() {
    local _src="$1"
    local _dst="$2"
    for _usb in /storage/usb* /mnt/media_rw/usb* /storage/usbotg*; do
        if [ -d "$_usb" ] && [ -f "$_usb/$_src" ]; then
            mv "$_usb/$_src" "$_usb/$_dst" 2>/dev/null && {
                log "Renamed $_usb/$_src -> $_usb/$_dst"
                sync
            }
        fi
    done
}

reboot_system() {
    log "Reboot triggered. Syncing disks and restarting..."
    sync
    sleep 2
    /system/bin/reboot 2>/dev/null || reboot 2>/dev/null || true
}
"""

common_sh_ui = common_sh_template.replace("{PKG_ID}", "arabic.ui")

post_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Installing arabic.ui (Safe Profile Mode) ==="

# 1. Safety snapshot of OEM build.prop
if ! snapshot_all; then
    log "ABORT: Snapshot creation failed, system untouched"
    toast "Arabic Mod: Backup failed! Aborted."
    exit 1
fi

# 2. Remount system partition rw
if ! sys_rw; then
    log "ABORT: Cannot remount /system rw"
    toast "Arabic Mod: Cannot remount system rw."
    exit 1
fi

# 3. Apply ONLY UI language list (leaves system region and timezone completely untouched)
_fail=0
set_prop_line "$BP" persist.sys.language_list "ko_KR,en_US,ar_EG" || _fail=1

if [ "$_fail" -ne 0 ]; then
    log "ERROR occurred during property update. Rolling back..."
    restore_all
    sys_ro
    toast "Arabic Mod: Failed! Rolled back to stock."
    exit 1
fi

# 4. Set runtime persist property
setprop persist.sys.language_list "ko_KR,en_US,ar_EG" 2>/dev/null || true

# 5. Lock filesystem and sync
sys_ro
sync
log "=== Arabic UI installation completed successfully ==="

# 6. Rename USB installer descriptor to prevent re-install prompts on future boots
rename_usb_data "NEMESIS.data" "NEMESIS.data.installed"

# 7. Notify user on screen and reboot automatically
toast "Arabic UI: Installed! Rebooting in 3 seconds..."
reboot_system
exit 0
"""

preun_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Uninstalling arabic.ui package ==="

if ! restore_all; then
    log "ABORT: Restore failed. Keeping backup for safety."
    toast "Arabic Mod: Restore failed! Check log."
    exit 1
fi

rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== arabic.ui uninstalled successfully ==="
toast "Arabic UI: Restored to stock OEM! Rebooting in 3 seconds..."
reboot_system
exit 0
"""

status_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
echo "======================================"
echo "    NEMESIS Arabic UI Status          "
echo "======================================"
echo "Package:          arabic.ui (Safe Mode)"
echo "Language List:    $(getprop persist.sys.language_list)"
echo "Current Language: $(getprop persist.sys.language)"
echo "Current Country:  $(getprop persist.sys.country)"
echo "System Region:    $(getprop ro.product.locale.region)"
echo "======================================"
exit 0
"""

# ==============================================================================
# 2. ARABIC.FULL (Full Mode - Arabic UI + Middle East Region for Native Maps)
# ==============================================================================
FULL_DIR = BASE_DIR / "arabic.full"

nemesis_data_full = """[nemesis]
version=1.1
id=arabic.full
name="Arabic & ME Region (Full)"
type=application
package-version=1.2
short-desc="Arabic UI + Middle East Region for Native Maps"
detailed-desc="Full Mode: Adds Arabic UI and sets ME region (ro.product.locale.region=ME) for offline native maps. NOTE: May conflict with Korean-market mods (Wireless CarPlay/AA). Includes auto backup, auto reboot, and USB unlooping."
os=any
models=any
preinstall=scripts/pre.sh
postinstall=scripts/post.sh
preuninstall=scripts/preun.sh

[app.0]
kind=sh
path=bin/status.sh
uid=root
"""

pre_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.full.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log " DISCLAIMER / إخلاء مسؤولية "
log " Installing Arabic & Middle East Region (Full Mod). "
log " NOTICE: Modifies system region to ME for native map engine. "
log " May deactivate Korean-market specific features/mods. "
log " Author holds no liability for device failure or damage. "
log "=========================================================="
exit 0
"""

common_sh_full = common_sh_template.replace("{PKG_ID}", "arabic.full")

post_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Installing arabic.full (Full Region Mod) ==="

# 1. Safety snapshot of OEM build.prop
if ! snapshot_all; then
    log "ABORT: Snapshot creation failed, system untouched"
    toast "Arabic Mod: Backup failed! Aborted."
    exit 1
fi

# 2. Remount system partition rw
if ! sys_rw; then
    log "ABORT: Cannot remount /system rw"
    toast "Arabic Mod: Cannot remount system rw."
    exit 1
fi

# 3. Apply properties (Language list + Middle East Region)
_fail=0

# A) Set Middle East region for Native Navigation Engine (BuildInfo.REGION = 6)
set_prop_line "$BP" ro.product.locale.region ME || _fail=1

# B) Unlock Arabic (ar_EG) in Settings -> Language list
set_prop_line "$BP" persist.sys.language_list "ko_KR,en_US,ar_EG" || _fail=1

if [ "$_fail" -ne 0 ]; then
    log "ERROR occurred during property updates. Rolling back..."
    restore_all
    sys_ro
    toast "Arabic Mod: Failed! Rolled back to stock."
    exit 1
fi

# 4. Set runtime persist property
setprop persist.sys.language_list "ko_KR,en_US,ar_EG" 2>/dev/null || true

# 5. Lock filesystem and sync
sys_ro
sync
log "=== Arabic Full installation completed successfully ==="

# 6. Rename USB installer descriptor to prevent re-install prompts on future boots
rename_usb_data "NEMESIS.data" "NEMESIS.data.installed"

# 7. Notify user on screen and reboot automatically
toast "Arabic Full: Installed! Rebooting in 3 seconds..."
reboot_system
exit 0
"""

preun_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Uninstalling arabic.full package ==="

if ! restore_all; then
    log "ABORT: Restore failed. Keeping backup for safety."
    toast "Arabic Mod: Restore failed! Check log."
    exit 1
fi

rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== arabic.full uninstalled successfully ==="
toast "Arabic Full: Restored to stock OEM! Rebooting in 3 seconds..."
reboot_system
exit 0
"""

status_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
echo "======================================"
echo "    NEMESIS Arabic Full Status        "
echo "======================================"
echo "Package:          arabic.full (Full Region Mod)"
echo "Language List:    $(getprop persist.sys.language_list)"
echo "Current Language: $(getprop persist.sys.language)"
echo "Current Country:  $(getprop persist.sys.country)"
echo "System Region:    $(getprop ro.product.locale.region) (Expected: ME)"
echo "======================================"
exit 0
"""

# ==============================================================================
# Write Files with LF Line Endings
# ==============================================================================
all_files = {
    # UI package
    UI_DIR / "NEMESIS.data": nemesis_data_ui,
    UI_DIR / "scripts" / "pre.sh": pre_sh_ui,
    UI_DIR / "scripts" / "common.sh": common_sh_ui,
    UI_DIR / "scripts" / "post.sh": post_sh_ui,
    UI_DIR / "scripts" / "preun.sh": preun_sh_ui,
    UI_DIR / "bin" / "status.sh": status_sh_ui,
    # Full package
    FULL_DIR / "NEMESIS.data": nemesis_data_full,
    FULL_DIR / "scripts" / "pre.sh": pre_sh_full,
    FULL_DIR / "scripts" / "common.sh": common_sh_full,
    FULL_DIR / "scripts" / "post.sh": post_sh_full,
    FULL_DIR / "scripts" / "preun.sh": preun_sh_full,
    FULL_DIR / "bin" / "status.sh": status_sh_full,
}

for path, content in all_files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

print("\nAll package files created successfully.")
