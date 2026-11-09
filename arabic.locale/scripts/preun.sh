#!/system/bin/sh
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
