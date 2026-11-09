#!/system/bin/sh
# common.sh - Universal helper library for Gen5W (Pure toolbox compatible)
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
        log "[AR] خطأ: الملف غير موجود أو فارغ"
        log "[EN] FAIL: $_f does not exist or is empty"
        return 1
    fi
    if ! grep "ro.build." "$_f" >/dev/null 2>&1; then
        log "[AR] خطأ: الملف لا يحتوي على خصائص النظام الأساسية"
        log "[EN] FAIL: $_f missing essential ro.build properties"
        return 1
    fi
    return 0
}

find_usb_root() {
    for _u in /storage/usb0 /storage/usb1 /storage/usb2 /mnt/media_rw/usb0 /mnt/media_rw/usb1 /mnt/media_rw/usb2 /storage/usbotg; do
        if [ -d "$_u" ] && [ -w "$_u" ]; then
            echo "$_u"
            return 0
        fi
    done
    for _u in /storage/usb* /mnt/media_rw/usb*; do
        if [ -d "$_u" ] && [ -w "$_u" ]; then
            echo "$_u"
            return 0
        fi
    done
    return 1
}

# Universal per-car backup onto the connected USB drive AND inside head unit storage
backup_vehicle_oem() {
    local _src="$BP"
    if ! verify_prop_file "$_src"; then
        log "[AR] خطأ: لا يمكن عمل نسخة احتياطية لملف تالف"
        log "[EN] FAIL: Refusing to backup invalid $_src"
        return 1
    fi

    # 1. Permanent global internal backup inside the head unit (/data/nemesis/build.prop.stock)
    mkdir -p /data/nemesis 2>/dev/null || true
    mkdir -p "$BACKUP_DIR" 2>/dev/null || true

    if [ ! -s "$GLOBAL_BACKUP" ] || ! verify_prop_file "$GLOBAL_BACKUP"; then
        cp -f "$_src" "$GLOBAL_BACKUP" 2>/dev/null || true
        log "[AR] تم حفظ النسخة الاحتياطية الدائمة داخل ذاكرة الوحدة: $GLOBAL_BACKUP"
        log "[EN] Saved permanent internal backup inside head unit: $GLOBAL_BACKUP"
    fi

    # 2. Package-specific internal backup inside the head unit
    if [ ! -s "$BACKUP_DIR/build.prop.stock" ]; then
        cp -f "$_src" "$BACKUP_DIR/build.prop.stock" 2>/dev/null || true
    fi
    putline 1 > "$BACKUP_DIR/saved" 2>/dev/null || true

    # 3. Dynamic USB Backup on the user's specific flash drive
    local _usb
    _usb="$(find_usb_root)"
    if [ -n "$_usb" ] && [ -d "$_usb" ]; then
        local _usb_dir="$_usb/OEM_BACKUP"
        mkdir -p "$_usb_dir" 2>/dev/null || true
        
        # Standard filename for automatic recovery
        cp -f "$_src" "$_usb_dir/build.prop.stock" 2>/dev/null || true
        
        # Vehicle-specific informative archive filename
        local _model="$(getprop ro.product.model 2>/dev/null)"
        [ -z "$_model" ] && _model="Gen5W"
        local _sw="$(getprop ro.build.product2 2>/dev/null)"
        [ -z "$_sw" ] && _sw="$(getprop ro.build.product 2>/dev/null)"
        [ -z "$_sw" ] && _sw="SW_STOCK"

        cp -f "$_src" "$_usb_dir/build.prop.${_model}_${_sw}" 2>/dev/null || true
        sync
        log "[AR] تم إنشاء نسخة المصنع الاحتياطية بنجاح على الفلاش:"
        log "[EN] Successfully created USB OEM backup: $_usb_dir/build.prop.stock"
    else
        log "[AR] تنبيه: تعذر الكتابة على الفلاش، تم حفظ النسخة الاحتياطية في الذاكرة الداخلية للشاشة."
        log "[EN] NOTICE: USB mount not writable; internal stock backup saved inside head unit storage."
    fi
    return 0
}

# Universal language list builder: preserves any car's native languages (KR, US, EU, etc.) and appends ar_EG
get_universal_language_list() {
    local _curr="$(getprop persist.sys.language_list 2>/dev/null)"
    if [ -z "$_curr" ]; then
        if [ -f "$BP" ]; then
            _curr="$(grep '^persist.sys.language_list=' "$BP" 2>/dev/null | cut -d= -f2-)"
        fi
    fi
    [ -z "$_curr" ] && _curr="ko_KR,en_US"

    case "$_curr" in
        *ar_EG*)
            echo "$_curr"
            ;;
        *)
            echo "${_curr},ar_EG"
            ;;
    esac
}

# Apply profile settings directly in user data partition (settings.db & persist)
apply_profile_arabic() {
    log "[AR] جاري تفعيل اللغة العربية في إعدادات البروفايل..."
    log "[EN] Applying Arabic localization to Driver Profile..."
    
    # Update settings provider for Driver 1, Driver 2, and Guest
    settings put system language_type_dr1 ar_EG 2>/dev/null || true
    settings put system language_type_dr2 ar_EG 2>/dev/null || true
    settings put system language_type ar_EG 2>/dev/null || true

    # Append ar_EG to language list in /data/property/ (without touching /system/build.prop!)
    local _langs="$(get_universal_language_list)"
    setprop persist.sys.language_list "$_langs" 2>/dev/null || true

    # Set current locale to Arabic
    setprop persist.sys.language ar 2>/dev/null || true
    setprop persist.sys.country EG 2>/dev/null || true

    # Trigger locale change broadcast
    settings put system settings.locale.change 1 2>/dev/null || true
    am broadcast -a android.intent.action.LOCALE_CHANGED >/dev/null 2>&1 || true

    log "[AR] تم تفعيل لغة البروفايل بنجاح"
    log "[EN] Profile language set to ar_EG (language_list: $_langs)"
    return 0
}

restore_profile_language() {
    log "[AR] جاري استرجاع لغة البروفايل للوضع الافتراضي..."
    log "[EN] Restoring Driver Profile language to default..."
    settings put system language_type_dr1 en_US 2>/dev/null || true
    settings put system language_type_dr2 Unknown 2>/dev/null || true
    settings put system language_type Unknown 2>/dev/null || true

    # Remove runtime persist overrides
    rm -f /data/property/persist.sys.language_list 2>/dev/null || true
    rm -f /data/property/persist.sys.language 2>/dev/null || true
    rm -f /data/property/persist.sys.country 2>/dev/null || true

    settings put system settings.locale.change 1 2>/dev/null || true
    am broadcast -a android.intent.action.LOCALE_CHANGED >/dev/null 2>&1 || true
    return 0
}

commit_tmp() {
    local _dst="$1"
    local _tmp="$2"
    
    if ! verify_prop_file "$_tmp"; then
        log "[AR] فشل التحقق من صحة الملف المؤقت"
        log "[EN] FAIL: commit aborted, temp file failed validation"
        rm -f "$_tmp" 2>/dev/null || true
        return 1
    fi
    
    cp -f "$_tmp" "$_dst" || {
        log "[AR] فشل نسخ الملف إلى مسار النظام"
        log "[EN] FAIL: cp $_tmp to $_dst failed"
        return 1
    }
    
    chmod 644 "$_dst" 2>/dev/null || true
    chown 0.0 "$_dst" 2>/dev/null || chown 0:0 "$_dst" 2>/dev/null || true
    rm -f "$_tmp" 2>/dev/null || true
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
        log "[AR] خطأ: سقطت أسطر أثناء تعديل الملف"
        log "[EN] FAIL: rewrite of $_file dropped lines ($_out < $_in)"
        rm -f "$_tmp" 2>/dev/null || true
        return 1
    fi
    
    commit_tmp "$_file" "$_tmp" || return 1
    log "[AR] تم ضبط الخاصية: ${_key}=${_val}"
    log "[EN] Property set: ${_key}=${_val}"
    return 0
}

restore_build_prop() {
    local _stock=""
    local _usb="$(find_usb_root)"

    if [ -n "$_usb" ] && [ -s "$_usb/OEM_BACKUP/build.prop.stock" ] && verify_prop_file "$_usb/OEM_BACKUP/build.prop.stock"; then
        _stock="$_usb/OEM_BACKUP/build.prop.stock"
        log "[AR] تم العثور على نسخة المصنع في الفلاش:"
        log "[EN] Found USB OEM backup: $_stock"
    elif [ -s "$BACKUP_DIR/build.prop.stock" ] && verify_prop_file "$BACKUP_DIR/build.prop.stock"; then
        _stock="$BACKUP_DIR/build.prop.stock"
        log "[AR] تم العثور على نسخة المصنع في مجلد الحزمة:"
        log "[EN] Found package backup: $_stock"
    elif [ -s "$GLOBAL_BACKUP" ] && verify_prop_file "$GLOBAL_BACKUP"; then
        _stock="$GLOBAL_BACKUP"
        log "[AR] تم العثور على نسخة المصنع الدائمة داخل الوحدة:"
        log "[EN] Found global backup inside head unit: $_stock"
    fi

    if [ -z "$_stock" ]; then
        log "[AR] خطأ: تعذر العثور على نسخة احتياطية صالحة لمصنع السيارة"
        log "[EN] FAIL: Cannot restore build.prop, valid stock backup not found"
        return 1
    fi

    if ! sys_rw; then
        log "[AR] خطأ: تعذر فتح نظام الملفات للكتابة"
        log "[EN] FAIL: remount /system rw failed during restore"
        return 1
    fi

    cp -f "$_stock" "$BP" || {
        sys_ro
        log "[AR] خطأ: فشل استرجاع ملف build.prop الأصلي"
        log "[EN] FAIL: Restoring stock build.prop failed"
        return 1
    }

    chmod 644 "$BP" 2>/dev/null || true
    chown 0.0 "$BP" 2>/dev/null || chown 0:0 "$BP" 2>/dev/null || true

    # Preserve internal stock backup on unit if missing
    mkdir -p /data/nemesis 2>/dev/null || true
    if [ ! -s "$GLOBAL_BACKUP" ] || ! verify_prop_file "$GLOBAL_BACKUP"; then
        cp -f "$_stock" "$GLOBAL_BACKUP" 2>/dev/null || true
    fi

    sync
    sys_ro
    log "[AR] تم استرجاع ملف build.prop الأصلي للوكالة بنجاح"
    log "[EN] Restored stock build.prop successfully from $_stock"
    return 0
}

rename_usb_data() {
    local _src="$1"
    local _dst="$2"
    for _u in /storage/usb* /mnt/media_rw/usb* /storage/usbotg*; do
        if [ -d "$_u" ] && [ -f "$_u/$_src" ]; then
            mv "$_u/$_src" "$_u/$_dst" 2>/dev/null && {
                log "[AR] تم تغيير اسم ملف التهيئة على الفلاش:"
                log "[EN] Renamed $_u/$_src -> $_u/$_dst"
                sync
            }
        fi
    done
}

# Spawns detached reboot subshell so script exits 0 immediately.
reboot_system() {
    log "[AR] جاري جدولة إعادة التشغيل التلقائي خلال 4 ثوان..."
    log "[EN] Reboot scheduled in 4 seconds (detached)..."
    sync
    ( sleep 4; sync; /system/bin/reboot 2>/dev/null || reboot 2>/dev/null ) >/dev/null 2>&1 &
}
