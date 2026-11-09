#!/system/bin/sh
# common.sh - Helper functions for Gen5W NEMESIS package
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

PKG_ID="arabic.full"
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
    am broadcast -a com.hkmc.intent.action.TOAST \
        -e com.hkmc.intent.extra.TOAST_MESSAGE "$_msg" \
        --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1 || true
}

putline() {
    print -r -- "$1" 2>/dev/null && return 0
    printf '%s\n' "$1" 2>/dev/null && return 0
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
