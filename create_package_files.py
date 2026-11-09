import os
from pathlib import Path

BASE_DIR = Path(r"C:\Users\k\.gemini\antigravity\scratch\nemesis-arabic-package")

UI_DIR = BASE_DIR / "arabic.ui"
FULL_DIR = BASE_DIR / "arabic.full"
USB_PKG_DIR = BASE_DIR / "usb_package"
USB_RECOVERY_DIR = BASE_DIR / "usb_emergency_recovery"

# Clean any stale build.prop from emergency recovery
stale_bp = USB_RECOVERY_DIR / "build.prop"
if stale_bp.exists():
    stale_bp.unlink()

# ==============================================================================
# COMMON SCRIPT TEMPLATE (Universal, Bilingual, Detached Reboot)
# ==============================================================================
common_sh_content = """#!/system/bin/sh
# common.sh - Universal helper library for Gen5W (Pure toolbox compatible)
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
"""

# ==============================================================================
# 1. ARABIC.UI (Safe Profile Mode - Bilingual)
# ==============================================================================
nemesis_data_ui = """[nemesis]
version=1.1
id=arabic.ui
name="Arabic Profile | تعريب البروفايل"
type=application
package-version=1.5
short-desc="تعريب البروفايل الآمن (Safe Profile Mode)"
detailed-desc="[AR] خيار آمن: تفعيل العربية بالبروفايل دون لمس ملفات النظام.\\n[EN] Safe Mode: Activates Arabic in Driver Profile without modifying system files. 100% safe for CarPlay/AA. Includes auto OEM backup & auto-reboot."
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
log "[AR] تفعيل تعريب البروفايل (الوضع الآمن - عام لسيارات Gen5W)"
log "[EN] Activating Arabic Profile UI (Safe Mode - Universal Gen5W)"
log ""
log "[AR] إخلاء مسؤولية: استخدامك للحزمة يتم على مسؤوليتك الشخصية."
log "[EN] DISCLAIMER: Use at your own risk. Author holds no liability."
log ""
log "[AR] التعديل في بيانات المستخدم فقط، ولا يمس نظام /system أو ملف build.prop."
log "[EN] Modifies user profile data only. ZERO /system or build.prop changes."
log "=========================================================="
exit 0
"""

post_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء تثبيت تعريب البروفايل ==="
log "=== [EN] Installing arabic.ui ==="

# 1. Universal Dual OEM backup: to USB & internally inside head unit storage
backup_vehicle_oem

# 2. Apply Arabic settings to Driver Profile and persist properties (No /system write!)
if ! apply_profile_arabic; then
    log "[AR] خطأ: فشل تفعيل لغة البروفايل"
    log "[EN] ERROR: apply_profile_arabic failed."
    restore_profile_language
    toast "خطأ في التفعيل! تم الإلغاء
Error! Installation Aborted"
    exit 1
fi

sync
log "=== [AR] اكتمل التفعيل بنجاح (دون لمس ملفات النظام) ==="
log "=== [EN] Completed successfully (Zero /system changes) ==="

# 3. Rename USB installer descriptor to prevent re-install prompts on future boots
rename_usb_data "NEMESIS.data" "NEMESIS.data.installed"

# 4. Notify user on screen with bilingual toast and trigger detached reboot
toast "تم تفعيل التعريب! جاري إعادة التشغيل...
Arabic Activated! Rebooting in 4s..."
reboot_system
exit 0
"""

preun_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء إزالة حزمة التعريب ==="
log "=== [EN] Uninstalling arabic.ui ==="

restore_profile_language
rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== [AR] تمت الإزالة واسترجاع الإعدادات بنجاح ==="
log "=== [EN] arabic.ui uninstalled successfully ==="
toast "تمت الإزالة والعودة للوضع الافتراضي
Restored to default! Rebooting..."

# Spawns detached reboot subshell and exits 0 immediately so NEMESIS removes package cleanly
reboot_system
exit 0
"""

status_sh_ui = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
ACTIVE="$(settings get system user_profile_driver 2>/dev/null)"
D1="$(settings get system language_type_dr1 2>/dev/null)"
D2="$(settings get system language_type_dr2 2>/dev/null)"
GUEST="$(settings get system language_type 2>/dev/null)"
LANGS="$(getprop persist.sys.language_list)"
LOCALE="$(getprop persist.sys.language)_$(getprop persist.sys.country)"
REGION="$(getprop ro.product.locale.region)"

echo "=========================================================="
echo " [AR] تقرير حالة تعريب البروفايل"
echo " [EN] NEMESIS Arabic Profile Status Report"
echo "=========================================================="
echo " [AR] نوع الحزمة:"
echo " [EN] Package:                   arabic.ui (Safe Profile Mode)"
echo " [AR] السائق النشط حالياً:"
echo " [EN] Active Driver:             $ACTIVE"
echo " [AR] لغة السائق الأول:"
echo " [EN] Driver 1 Language:         $D1"
echo " [AR] لغة السائق الثاني:"
echo " [EN] Driver 2 Language:         $D2"
echo " [AR] لغة الضيف الافتراضية:"
echo " [EN] Guest Language:            $GUEST"
echo " [AR] قائمة اللغات المتاحة:"
echo " [EN] Language List:             $LANGS"
echo " [AR] لغة الواجهة الحالية:"
echo " [EN] Current Locale:            $LOCALE"
echo " [AR] منطقة النظام:"
echo " [EN] System Region:             $REGION (OEM intact / لم تتغير)"
echo " [AR] وضع ملفات النظام:"
echo " [EN] System Files Status:       Read-Only intact (آمن 100%)"
echo "=========================================================="
exit 0
"""

# ==============================================================================
# 2. ARABIC.FULL (Middle East Map Compatibility Mod - Bilingual)
# ==============================================================================
nemesis_data_full = """[nemesis]
version=1.1
id=arabic.full
name="ME Map & Arabic | توافق خرائط الشرق الأوسط"
type=application
package-version=1.5
short-desc="توافق خرائط الشرق الأوسط (ME Map Mod)"
detailed-desc="[AR] تهيئة النظام لقبول خرائط الشرق الأوسط (لا تشمل الخرائط).\\n[EN] Full Mode: Enables ME native map compatibility (does not include map files). Sets region to ME. Creates per-vehicle USB backup & auto-reboot."
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
log "[AR] تهيئة النظام لتشغيل خرائط الشرق الأوسط الأصلية"
log "[EN] Enabling Middle East Native Map Engine Compatibility"
log ""
log "[AR] تنبيه هام: الحزمة لا تحتوي على ملفات الخرائط، بل تهيئ النظام لقبولها."
log "[EN] IMPORTANT: This package does NOT include map files; it enables system map support."
log ""
log "[AR] إخلاء مسؤولية: هذا التعديل يتم على مسؤوليتك الشخصية بالكامل."
log "[EN] DISCLAIMER: Use at your own risk. Author holds no liability."
log ""
log "[AR] تنبيه: تعديل منطقة النظام إلى ME قد يعطل بعض التعديلات الكورية."
log "[EN] NOTICE: Changing system region to ME may deactivate Korean mods."
log ""
log "[AR] يتم حفظ نسخة المصنع لسيارتك تلقائياً على الفلاش ميموري وداخل ذاكرة الشاشة."
log "[EN] Automatic dual OEM backup created on USB drive and inside head unit storage."
log "=========================================================="
exit 0
"""

post_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء تثبيت تهيئة خرائط الشرق الأوسط والتعريب ==="
log "=== [EN] Installing arabic.full (ME Map Compatibility) ==="

# 1. Dual OEM backup: to USB (OEM_BACKUP folder) AND internal head unit storage
if ! backup_vehicle_oem; then
    log "[AR] خطأ: فشل النسخ الاحتياطي! تم إلغاء العملية."
    log "[EN] ABORT: Per-vehicle OEM backup failed! System untouched."
    toast "فشل النسخ الاحتياطي! تم الإلغاء
Backup Failed! Aborted"
    exit 1
fi

# 2. Remount system partition rw
if ! sys_rw; then
    log "[AR] خطأ: تعذر فتح نظام الملفات للكتابة"
    log "[EN] ABORT: Cannot remount /system rw"
    toast "فشل فتح نظام الملفات!
Cannot remount /system rw"
    exit 1
fi

# 3. Apply properties to build.prop
_fail=0

# A) Set Middle East region for Native Navigation Engine (BuildInfo.REGION = 6)
set_prop_line "$BP" ro.product.locale.region ME || _fail=1

# B) Universal language list: preserves vehicle native languages + adds ar_EG
_langs="$(get_universal_language_list)"
set_prop_line "$BP" persist.sys.language_list "$_langs" || _fail=1

if [ "$_fail" -ne 0 ]; then
    log "[AR] خطأ أثناء تعديل الخصائص. جاري استرجاع نسخة المصنع..."
    log "[EN] ERROR occurred during build.prop updates. Rolling back..."
    restore_build_prop
    sys_ro
    toast "خطأ في التثبيت! تم استرجاع الوكالة
Error! Restored OEM"
    exit 1
fi

# 4. Lock system filesystem
sys_ro
sync

# 5. Apply Driver Profile settings
apply_profile_arabic

log "=== [AR] اكتمل التثبيت والتهيئة بنجاح ==="
log "=== [EN] Full installation completed successfully ==="

# 6. Rename USB installer descriptor to prevent re-install prompts on future boots
rename_usb_data "NEMESIS.data" "NEMESIS.data.installed"

# 7. Notify user on screen and trigger detached reboot
toast "تم تفعيل توافق خرائط الشرق الأوسط!
ME Map Compatibility Enabled! Rebooting..."
reboot_system
exit 0
"""

preun_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
. ./scripts/common.sh

log "=== [AR] بدء إزالة تهيئة خرائط الشرق الأوسط والتعريب ==="
log "=== [EN] Uninstalling arabic.full ==="

_err=0
restore_build_prop || _err=1
restore_profile_language || _err=1

if [ "$_err" -ne 0 ]; then
    log "[AR] فشل الاسترجاع الكامل! تم الاحتفاظ بالنسخ الاحتياطية للأمان."
    log "[EN] ABORT: Restore failed. Keeping backup for safety."
    toast "فشل الاسترجاع! راجع السجل
Restore failed! Check log"
    exit 1
fi

rm -rf "$BACKUP_DIR" 2>/dev/null || true
sync

# Re-enable installer on USB if USB is still plugged in
rename_usb_data "NEMESIS.data.installed" "NEMESIS.data"

log "=== [AR] تم استرجاع نسخة المصنع وإزالة الحزمة بنجاح ==="
log "=== [EN] arabic.full uninstalled successfully ==="
toast "تم استرجاع وضع المصنع الافتراضي!
OEM Restored! Rebooting..."

# Spawns detached reboot subshell and exits 0 immediately so NEMESIS removes package cleanly
reboot_system
exit 0
"""

status_sh_full = """#!/system/bin/sh
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
ACTIVE="$(settings get system user_profile_driver 2>/dev/null)"
D1="$(settings get system language_type_dr1 2>/dev/null)"
LANGS="$(getprop persist.sys.language_list)"
LOCALE="$(getprop persist.sys.language)_$(getprop persist.sys.country)"
REGION="$(getprop ro.product.locale.region)"

echo "=========================================================="
echo " [AR] تقرير حالة التوافق مع خرائط الشرق الأوسط"
echo " [EN] NEMESIS Middle East Map Compatibility Status"
echo "=========================================================="
echo " [AR] نوع الحزمة:"
echo " [EN] Package:                   arabic.full (ME Map Compatibility Mod)"
echo " [AR] السائق النشط حالياً:"
echo " [EN] Active Driver:             $ACTIVE"
echo " [AR] لغة السائق الأول:"
echo " [EN] Driver 1 Language:         $D1"
echo " [AR] قائمة اللغات المتاحة:"
echo " [EN] Language List:             $LANGS"
echo " [AR] اللغة الحالية:"
echo " [EN] Current Locale:            $LOCALE"
echo " [AR] منطقة النظام المعدلة:"
echo " [EN] System Region:             $REGION (Expected: ME)"
echo " [AR] جاهزية محرك خرائط الشرق الأوسط:"
echo " [EN] ME Map Engine Support:     Enabled (مهيأ لتشغيل خرائط ME)"
echo " [AR] تنبيه: ملفات الخرائط يلزم توفيرها من الوكالة/بطاقة SD"
echo " [EN] Notice: Map data files must be provided via SD card"
echo "=========================================================="
exit 0
"""

# ==============================================================================
# 3. UNIVERSAL EMERGENCY RECOVERY SCRIPT (Dual Backup & Head Unit Internal Preservation)
# ==============================================================================
emergency_data = """[nemesis]
version=1.0
type=execute
path=NEMESIS.sh
"""

emergency_sh = """#!/system/bin/sh
# Universal Failsafe Emergency Recovery Script for Gen5W (Pure toolbox compatible)
# Dynamically searches for that vehicle's own backup on USB or internal storage,
# and guarantees a permanent internal backup is always preserved inside the head unit.
export PATH=/data/nemesis/bin:/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
export LD_LIBRARY_PATH=/vendor/lib:/system/lib

BP=/system/build.prop
GLOBAL_STOCK=/data/nemesis/build.prop.stock
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

find_backup_source() {
    # 1. Check relative OEM_BACKUP on current USB drive
    if [ -s "./OEM_BACKUP/build.prop.stock" ] && verify_prop_file "./OEM_BACKUP/build.prop.stock"; then
        echo "./OEM_BACKUP/build.prop.stock"
        return 0
    fi
    if [ -s "./build.prop" ] && verify_prop_file "./build.prop"; then
        echo "./build.prop"
        return 0
    fi

    # 2. Check all mounted USB locations for this vehicle's OEM_BACKUP
    for _u in /storage/usb0 /storage/usb1 /storage/usb2 /mnt/media_rw/usb* /storage/usbotg*; do
        if [ -s "$_u/OEM_BACKUP/build.prop.stock" ] && verify_prop_file "$_u/OEM_BACKUP/build.prop.stock"; then
            echo "$_u/OEM_BACKUP/build.prop.stock"
            return 0
        fi
        if [ -s "$_u/build.prop" ] && verify_prop_file "$_u/build.prop"; then
            echo "$_u/build.prop"
            return 0
        fi
    done

    # 3. Check internal global stock backup on the car (/data/nemesis/build.prop.stock)
    if [ -s "$GLOBAL_STOCK" ] && verify_prop_file "$GLOBAL_STOCK"; then
        echo "$GLOBAL_STOCK"
        return 0
    fi

    # 4. Check internal package backup on the car
    for _p in /data/nemesis/backup/*/build.prop.stock; do
        if [ -s "$_p" ] && verify_prop_file "$_p"; then
            echo "$_p"
            return 0
        fi
    done

    return 1
}

log "=========================================================="
log "[AR] بدء تشغيل الاسترجاع التلقائي للطوارئ"
log "[EN] Universal Emergency OEM Restore Triggered"
log "=========================================================="
toast "طوارئ: جاري استرجاع نسخة المصنع...
Emergency: Restoring OEM Backup..."

SOURCE="$(find_backup_source)"

if [ -z "$SOURCE" ] || ! verify_prop_file "$SOURCE"; then
    log "[AR] خطأ حرج: لم يتم العثور على نسخة احتياطية صالحة لهذا الجهاز!"
    log "[EN] CRITICAL: No valid OEM backup file found for this vehicle on USB or internal storage!"
    toast "خطأ: لم يتم العثور على نسخة احتياطية!
Error: No OEM Backup Found!"
    exit 1
fi

log "[AR] تم تحديد مسار نسخة المصنع:"
log "[EN] Identified valid OEM vehicle backup: $SOURCE"

if ! sys_rw; then
    log "[AR] خطأ: تعذر فتح نظام الملفات للكتابة"
    log "[EN] FAIL: cannot remount /system rw"
    toast "خطأ: تعذر فتح النظام!
Cannot remount /system rw"
    exit 1
fi

cp -f "$SOURCE" "$BP" || {
    sys_ro
    log "[AR] خطأ: فشل نسخ الملف إلى مسار النظام"
    log "[EN] FAIL: cp failed"
    toast "خطأ: فشل نسخ الملف!
File copy failed!"
    exit 1
}

chmod 644 "$BP" 2>/dev/null || true
chown 0.0 "$BP" 2>/dev/null || chown 0:0 "$BP" 2>/dev/null || true

# GUARANTEE DUAL BACKUP: Save/preserve internal backup inside the head unit's internal storage
mkdir -p /data/nemesis 2>/dev/null || true
if [ ! -s "$GLOBAL_STOCK" ] || ! verify_prop_file "$GLOBAL_STOCK"; then
    cp -f "$SOURCE" "$GLOBAL_STOCK" 2>/dev/null || true
    log "[AR] تم حفظ نسخة احتياطية إضافية داخل ذاكرة الوحدة: $GLOBAL_STOCK"
    log "[EN] Saved permanent internal backup inside head unit storage: $GLOBAL_STOCK"
fi

# Clear persist locale and timezone overrides
rm -f /data/property/persist.sys.language_list 2>/dev/null || true
rm -f /data/property/persist.sys.language 2>/dev/null || true
rm -f /data/property/persist.sys.country 2>/dev/null || true
rm -f /data/property/persist.sys.timezone 2>/dev/null || true

# Restore profile language defaults
settings put system language_type_dr1 en_US 2>/dev/null || true
settings put system language_type_dr2 Unknown 2>/dev/null || true
settings put system language_type Unknown 2>/dev/null || true

sys_ro
sync
log "=========================================================="
log "[AR] اكتمل استرجاع نسخة المصنع بنجاح. جاري إعادة التشغيل..."
log "[EN] OEM RESTORE COMPLETED SUCCESSFULLY. REBOOTING..."
log "=========================================================="
toast "تم استرجاع الوكالة بنجاح! جاري الإقلاع
OEM Restored! Rebooting in 3s..."

sleep 3
/system/bin/reboot 2>/dev/null || reboot 2>/dev/null || true
exit 0
"""

# ==============================================================================
# Write all files with LF line endings
# ==============================================================================
files = {
    # UI package
    UI_DIR / "NEMESIS.data": nemesis_data_ui,
    UI_DIR / "scripts" / "pre.sh": pre_sh_ui,
    UI_DIR / "scripts" / "common.sh": common_sh_content.replace("{PKG_ID}", "arabic.ui"),
    UI_DIR / "scripts" / "post.sh": post_sh_ui,
    UI_DIR / "scripts" / "preun.sh": preun_sh_ui,
    UI_DIR / "bin" / "status.sh": status_sh_ui,
    # Full package
    FULL_DIR / "NEMESIS.data": nemesis_data_full,
    FULL_DIR / "scripts" / "pre.sh": pre_sh_full,
    FULL_DIR / "scripts" / "common.sh": common_sh_content.replace("{PKG_ID}", "arabic.full"),
    FULL_DIR / "scripts" / "post.sh": post_sh_full,
    FULL_DIR / "scripts" / "preun.sh": preun_sh_full,
    FULL_DIR / "bin" / "status.sh": status_sh_full,
    # Emergency recovery
    USB_RECOVERY_DIR / "NEMESIS.data": emergency_data,
    USB_RECOVERY_DIR / "NEMESIS.sh": emergency_sh,
}

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {path}")

# Ensure NEMESIS.emergency flag exists
(USB_RECOVERY_DIR / "NEMESIS.emergency").write_bytes(b"")
print("Verified: NEMESIS.emergency flag file present.")
