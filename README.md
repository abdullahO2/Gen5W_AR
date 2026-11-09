# NEMESIS Arabic Localization Mod for Gen5W
### حزم تفعيل اللغة العربية لشاشات هيونداي وكيا وجينيسيس (Gen5W) عبر نظام NEMESIS

[![Platform](https://img.shields.io/badge/Platform-Gen5W%20(Android%204.4.2)-blue.svg)](#)
[![Compatibility](https://img.shields.io/badge/Framework-NEMESIS%20v1.1+-green.svg)](#)
[![License: Unlicense](https://img.shields.io/badge/License-Unlicense%20(Public%20Domain)-lightgrey.svg)](LICENSE)

---

## 🇸🇦 نظرة عامة ودليل الاستخدام (العربية)

يوفر هذا المستودع حزم تثبيت رسمية ونظيفة وقابلة للإلغاء بنسبة 100% لنظام **NEMESIS** على شاشات **Gen5W** (هيونداي، كيا، وجينيسيس). تم تصميم الحزم وفق مبدأ **الحد الأدنى الحتمي والآمن للتعديلات (Minimal Safe Modifications)** دون المساس باستقرار النظام أو كسر التعديلات الأخرى.

تتضمن الحزمة خيارين مستقلين يستطيع المستخدم الاختيار بينهما مباشرة من شاشة السيارة:

---

### 📦 مقارنة بين الخيارين المتاحين (اختر الأنسب لك)

| وجه المقارنة | الخيار الأول: تعريب الواجهة فقط (الموصى به) | الخيار الثاني: تعريب كامل + خرائط الشرق الأوسط |
| :--- | :--- | :--- |
| **اسم الحزمة** | `arabic.ui` | `arabic.full` |
| **التعديلات في النظام** | تعديل خاصية واحدة فقط: `persist.sys.language_list` | تعديل خاصيتين: `persist.sys.language_list` + `ro.product.locale.region=ME` |
| **مستوى الأمان** | **آمن 100% (أعلى درجات الأمان)** | **آمن مع ملاحظة لاحتمال تأثر بعض الإضافات** |
| **دعم لغة الواجهة** | نعم، يتيح اختيار العربية في إعدادات البروفايل | نعم، يتيح اختيار العربية في إعدادات البروفايل |
| **التوافق مع التعديلات الكورية** | **متوافق تماماً** (لا يؤثر إطلاقاً على تفعيل CarPlay/AA اللاسلكي أو Tilepad) | **قد يعطل بعض التعديلات** المخصصة للنسخ الكورية فقط (REGION=0) |
| **خرائط الملاحة الأصلية (Offline)** | تظل خرائط الوكالة كما هي (مثالي لمن يعتمد على خرائط Google أو Waze عبر CarPlay/AA) | يهيئ محرك الملاحة لقبول خرائط الشرق الأوسط الأصلية |
| **من نوصي به له؟** | **لجميع المستخدمين عموماً ومستخدمي CarPlay و Android Auto** | لمن يرغب بتشغيل الخرائط الأصلية للشرق الأوسط على الشاشة مباشرة |

---

### 🌟 مميزات وتقنيات مدمجة في الحزم

1. **متجر حزم مدمج على الفلاش (Package Store):**
   - بمجرد وضع الفلاش في الشاشة، تفتح واجهة NEMESIS لتخيرك مباشرة بين الحزمتين مع شرح وافٍ لكل خيار.
2. **منع تكرار شاشة التثبيت (USB Auto-Rename):**
   - بعد اكتمال التثبيت، يقوم النظام بتغيير اسم ملف التهيئة على الفلاش تلقائياً إلى `NEMESIS.data.installed` حتى لا تظهر لك رسالة التثبيت المزعجة في كل مرة تشغل فيها السيارة إذا نسيت الفلاش موصولاً.
3. **إشعارات فورية على شاشة السيارة (On-Screen Native Toasts):**
   - إشعارات منبثقة رسمية على واجهة الشاشة لإعلامك بنجاح التثبيت أو الاسترجاع.
4. **إعادة تشغيل تلقائية (Auto-Reboot):**
   - فور الانتهاء من التثبيت أو الحذف، تقوم الحزمة بعمل مزامنة كاملة للملفات (`sync`) وإعادة تشغيل الشاشة تلقائياً بعد 3 ثوانٍ لتطبيق التغييرات.
5. **نسخ احتياطي واسترجاع فوري (100% OEM Rollback):**
   - أخذ نسخة احتياطية مطابقة للوكالة قبل أي تعديل وحفظها بشكل دائم في مسار محمي، مع إمكانية حذف الحزمة بضغطة زر والعودة لحالة المصنع.

---

### 🚀 خطوات التثبيت (Installation Steps)

#### المتطلبات
1. شاشة Gen5W تدعم وتعمل بنظام **NEMESIS**.
2. فلاش ميموري (USB Flash Drive) بنظام تهيئة **FAT32** أو **exFAT**.

#### الطريقة المباشرة:
1. حمّل ملفات مجلد [`usb_package`](usb_package/) وانسخها مباشرة إلى جذر الفلاش ميموري (Root):
   ```text
   USB Drive (الجذر)
   ├── NEMESIS.data
   └── packages/
       ├── arabic.ui.zip         (خيار تعريب الواجهة - الموصى به)
       └── arabic.full.zip       (خيار التعريب الكامل مع الملاحة)
   ```
2. شغّل السيارة حتى تكتمل إقلاع الشاشة.
3. أدخل الفلاش ميموري في منفذ USB الخاص بنظام الوسائط.
4. ستظهر على الشاشة نافذة **NEMESIS Package Store** تعرض الحزمتين:
   - اضغط على **Arabic UI Language** إذا كنت تريد تعريب الواجهة الآمن.
   - أو اضغط على **Arabic & ME Region (Full)** إذا كنت تريد تفعيل خرائط الشرق الأوسط الأصلية.
5. اضغط **Install**.
6. ستظهر رسالة Toast على الشاشة لتأكيد النجاح، وستقوم الشاشة بإعادة التشغيل تلقائياً.
7. بعد إعادة التشغيل، اذهب إلى:
   **الإعدادات (Settings) ⬅️ عام (General) ⬅️ لغة النظام (Language)**، واختر **العربية**.

---

### 🔄 إزالة الحزمة والعودة لحالة المصنع (Uninstallation)

إذا رغبت في أي وقت بحذف التعديل والعودة لحالة الوكالة:
1. افتح تطبيق **NEMESIS Manager** من شاشة السيارة.
2. اذهب إلى قائمة الحزم المثبتة (**My Packages**).
3. اختر الحزمة المثبتة (`arabic.ui` أو `arabic.full`).
4. اضغط **Uninstall**.
5. ستقوم الحزمة باسترجاع ملف `build.prop` الأصلي للوكالة، وحذف الإعدادات، وإعادة تشغيل الشاشة تلقائياً.

---

### 🆘 فلاشة الطوارئ المستقلة (Emergency Recovery Kit)

في حال حدوث أي انقطاع كهربائي مفاجئ أثناء التثبيت أو رغبت في استرجاع النظام دون الدخول للواجهة:
1. انسخ محتويات مجلد [`usb_emergency_recovery`](usb_emergency_recovery/) إلى فلاش ميموري مفرمت FAT32.
2. ضع الفلاش في منفذ USB بالسيارة.
3. بفضل ملف `NEMESIS.emergency`، سيقوم النظام بتشغيل سكربت الطوارئ واسترجاع نسخة المصنع الأصلية المخزنة فوراً وإعادة تشغيل الشاشة تلقائياً.

---

## 📖 English Overview & Guide

This repository contains community-ready, safe, and completely reversible **NEMESIS packages** designed to enable **Arabic language** and optional **Middle East regional support** on **Hyundai, Kia, and Genesis Gen5W** head units (running Android 4.4.2 KitKat).

### Modes Available

1. **`arabic.ui` (Safe Profile Mode - Recommended):**
   - Modifies **only** `persist.sys.language_list=ko_KR,en_US,ar_EG`.
   - Leaves system region (`ro.product.locale.region`) untouched.
   - Zero side-effects: 100% compatible with Korean-market modifications (such as Wireless CarPlay/AA, Tilepad).
   - Ideal for drivers using Apple CarPlay (Google Maps, Waze) or Android Auto.
2. **`arabic.full` (Full Region & Offline Map Engine):**
   - Configures both `persist.sys.language_list` and `ro.product.locale.region=ME`.
   - Enables native offline Middle East navigation map loading (`BuildInfo.REGION = 6`).
   - Notice: may disable regional-locked Korean modifications.

### Key Enhancements

- **USB Auto-Rename:** Automatically renames `NEMESIS.data` to `NEMESIS.data.installed` on the USB drive upon successful install to prevent re-install prompts on vehicle startup.
- **On-Screen Toasts:** Broadcasts native system toast messages via `com.hkmc.intent.action.TOAST` on the head unit display.
- **Auto-Reboot:** Disks are cleanly synchronized (`sync`) and the system reboots 3 seconds after install or uninstall.
- **Fail-safe OEM Rollback:** Preserves original factory `build.prop` permanently and restores it cleanly on uninstallation.
- **Offline Emergency Recovery Kit:** Standalone emergency USB setup with `NEMESIS.emergency` trigger.

---

## 📁 Repository Structure / هيكل المستودع

```text
nemesis-arabic-package/
├── usb_package/                      <-- Ready to copy directly to USB flash drive (FAT32)
│   ├── NEMESIS.data                  (Package Store multi-installer descriptor)
│   └── packages/
│       ├── arabic.ui.zip             (Safe Profile Mode: UI Language Only)
│       └── arabic.full.zip           (Full Mode: UI + Middle East Region)
│
├── arabic.ui/                        <-- Source code for arabic.ui package
│   ├── NEMESIS.data                  (Package descriptor)
│   ├── bin/status.sh                 (Diagnostic script for NEMESIS Manager)
│   └── scripts/
│       ├── pre.sh                    (Pre-install verification)
│       ├── common.sh                 (Safe Android 4.4 toolbox utility functions)
│       ├── post.sh                   (Install script with toast, USB unloop, & reboot)
│       └── preun.sh                  (Uninstall script with OEM restore & reboot)
│
├── arabic.full/                      <-- Source code for arabic.full package
│   ├── NEMESIS.data                  (Package descriptor)
│   ├── bin/status.sh                 (Diagnostic script)
│   └── scripts/
│       ├── pre.sh                    (Pre-install verification)
│       ├── common.sh                 (Safe utility functions)
│       ├── post.sh                   (Full install script)
│       └── preun.sh                  (Full uninstall script)
│
├── usb_emergency_recovery/           <-- Standalone emergency recovery drive
│   ├── NEMESIS.emergency             (Direct execution trigger)
│   ├── NEMESIS.data                  (Execute descriptor)
│   ├── NEMESIS.sh                    (Automatic OEM restore script)
│   └── build.prop                    (Reference OEM backup)
│
├── build_package.py                  <-- Build & validation automation script
├── create_package_files.py           <-- Package source generator
├── README.md                         <-- Full documentation (Ar/En)
└── LICENSE                           <-- The Unlicense (Public Domain)
```

---

## ⚠️ Disclaimer / إخلاء مسؤولية

> [!CAUTION]
> هذا العمل متاح للجميع بشكل مجاني وحر تماماً كمنفعة عامة دون أي حقوق ملكية أو احتكار.
> استخدامك لهذه الحزمة يتم على مسؤوليتك الشخصية الكاملة دون أي مسؤولية أو ضمان من أي نوع على المطورين أو المساهمين في حال حدوث أي عطل أو تلف للشاشة نتيجة سوء الاستخدام. احرص دائماً على الاحتفاظ بنسخة احتياطية لملف نظامك الأصلي.

---

## 📄 License / الترخيص

هذا المشروع متاح ومصنف تحت رخصة **[The Unlicense](LICENSE)** (ملكية عامة بالكامل - Public Domain)، مما يتيح لأي شخص نسخه أو تعديله أو نشره أو استخدامه بأي شكل تجاري أو غير تجاري بحرية تامة وبدون أي قيود أو حقوق.
