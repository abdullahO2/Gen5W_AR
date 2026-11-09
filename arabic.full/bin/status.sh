#!/system/bin/sh
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
