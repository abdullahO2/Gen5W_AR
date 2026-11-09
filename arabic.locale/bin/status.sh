#!/system/bin/sh
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
