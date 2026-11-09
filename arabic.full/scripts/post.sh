#!/system/bin/sh
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
