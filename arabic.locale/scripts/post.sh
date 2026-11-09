#!/system/bin/sh
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
