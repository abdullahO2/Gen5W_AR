import os
from pathlib import Path

BASE_DIR = Path(r"C:\Users\k\.gemini\antigravity\scratch\nemesis-arabic-package")
PKG_DIR = BASE_DIR / "arabic.locale"

# 1. NEMESIS.data
nemesis_data = """[nemesis]
version=1.1
id=arabic.locale
name="Arabic & ME Localization"
type=application
package-version=1.1
short-desc="Arabic & ME Map Mod [Use at own risk]"
detailed-desc="DISCLAIMER: Modifies build.prop at your own risk. The author holds no liability for device failure. Minimal patch: adds Arabic locale & sets ME map region (BuildInfo.REGION=6). Includes automatic stock backup and recovery."
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

# 2. scripts/pre.sh (Disclaimer logging & pre-check)
pre_sh = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
LOG="/data/nemesis/arabic.locale.log"

log() {
    echo "$1"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$1" >> "$LOG" 2>/dev/null || true
}

log "=========================================================="
log " DISCLAIMER / إخلاء مسؤولية "
log " This package modifies system properties at user risk. "
log " Author holds no liability for device failure or damage. "
log " Proceeding with installation of minimal Arabic & ME mod. "
log "=========================================================="
exit 0
"""

# 3. scripts/common.sh
common_sh = """#!/system/bin/sh
# common.sh - Safe operations for arabic.locale package
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

BP="/system/build.prop"
BACKUP_DIR="/data/nemesis/backup/arabic.locale"
GLOBAL_BACKUP="/data/nemesis/build.prop.stock"
LOG="/data/nemesis/arabic.locale.log"

log() {
    local _msg="$1"
    echo "$_msg"
    mkdir -p /data/nemesis 2>/dev/null || true
    echo "$_msg" >> "$LOG" 2>/dev/null || true
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

# 100% Android 4.4 toolbox compatible verification (no wc/head dependency)
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
    
    # Persistent global safety copy
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
    rm -f /data/property/persist.sys.timezone 2>/dev/null || true
    
    sync
    sys_ro
    log "Restored stock build.prop successfully"
    return 0
}
"""

# 4. scripts/post.sh
post_sh = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Installing arabic.locale minimal package ==="

# 1. Safety snapshot (guaranteed never to overwrite original)
if ! snapshot_all; then
    log "ABORT: Snapshot creation failed, system untouched"
    exit 1
fi

# 2. Remount system rw
if ! sys_rw; then
    log "ABORT: Cannot remount /system rw"
    exit 1
fi

# 3. Apply MINIMAL necessary properties:
_fail=0

# A) Set Middle East region for Navigation Engine (CheckREGION -> BuildInfo.REGION = 6)
set_prop_line "$BP" ro.product.locale.region ME || _fail=1

# B) Unlock Arabic (ar_EG) in Settings -> Language list
set_prop_line "$BP" persist.sys.language_list "ko_KR,en_US,ar_EG" || _fail=1

# C) Hardware & GPS default timezone for Riyadh (GMT+3)
set_prop_line "$BP" tcc.default.timezone Asia/Riyadh || _fail=1
set_prop_line "$BP" persist.sys.timezone Asia/Riyadh || _fail=1

if [ "$_fail" -ne 0 ]; then
    log "ERROR occurred during minimal property updates. Rolling back..."
    restore_all
    sys_ro
    exit 1
fi

# 4. Set runtime persist properties
setprop persist.sys.language_list "ko_KR,en_US,ar_EG" 2>/dev/null || true
setprop persist.sys.timezone "Asia/Riyadh" 2>/dev/null || true

# 5. Lock filesystem and finish
sys_ro
sync
log "=== Minimal installation completed successfully ==="
"""

# 5. scripts/preun.sh
preun_sh = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== Uninstalling arabic.locale package ==="

if ! restore_all; then
    log "ABORT: Restore failed. Keeping backup for safety."
    exit 1
fi

rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync
log "=== arabic.locale uninstalled successfully ==="
"""

# 6. bin/status.sh
status_sh = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
echo "======================================"
echo "    NEMESIS Arabic & ME Mod Status    "
echo "======================================"
echo "Map Region (ro...region):  $(getprop ro.product.locale.region)"
echo "Language List:             $(getprop persist.sys.language_list)"
echo "Current Language:          $(getprop persist.sys.language)"
echo "Current Country:           $(getprop persist.sys.country)"
echo "Timezone:                  $(getprop persist.sys.timezone)"
echo "======================================"
exit 0
"""

# Write all package files with Unix newlines (LF)
files = {
    PKG_DIR / "NEMESIS.data": nemesis_data,
    PKG_DIR / "scripts" / "pre.sh": pre_sh,
    PKG_DIR / "scripts" / "common.sh": common_sh,
    PKG_DIR / "scripts" / "post.sh": post_sh,
    PKG_DIR / "scripts" / "preun.sh": preun_sh,
    PKG_DIR / "bin" / "status.sh": status_sh,
}

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {path}")

print("Package source files updated successfully.")
