import re
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(r"C:\Users\k\.gemini\antigravity\scratch\nemesis-arabic-package")
USB_PKG_DIR = BASE_DIR / "usb_package"
USB_RECOVERY_DIR = BASE_DIR / "usb_emergency_recovery"
RELEASES_DIR = BASE_DIR / "releases"

SHORT_MAX = 64
DETAIL_MAX = 256
VER_RE = re.compile(r"^\d+(\.\d+)*$")
ID_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]{0,63}$")


def validate_descriptor(meta_path: Path):
    text = meta_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith(("#", ";"))]
    data = {}
    sec = ""
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            sec = line[1:-1].strip()
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"')
            data[(sec, k.strip())] = v

    ver = data.get(("nemesis", "version"), "1.0")
    if not VER_RE.match(ver):
        raise ValueError(f"Invalid version: {ver}")

    pid = data.get(("nemesis", "id"), "")
    if not ID_RE.match(pid):
        raise ValueError(f"Invalid id: {pid}")

    s_desc = data.get(("nemesis", "short-desc"), "")
    if len(s_desc) > SHORT_MAX:
        raise ValueError(f"[{pid}] short-desc exceeds {SHORT_MAX} chars: ({len(s_desc)}): '{s_desc}'")

    d_desc = data.get(("nemesis", "detailed-desc"), "")
    if len(d_desc) > DETAIL_MAX:
        raise ValueError(f"[{pid}] detailed-desc exceeds {DETAIL_MAX} chars: ({len(d_desc)}): '{d_desc}'")

    print(f"Validation PASSED: {pid} v{data.get(('nemesis', 'package-version'))}")
    return pid


def build_single_zip(src_dir: Path, output_zip: Path):
    validate_descriptor(src_dir / "NEMESIS.data")
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src_dir.rglob("*")):
            if p.is_file():
                content = p.read_bytes()
                if p.suffix in (".sh", ".data", ".prop"):
                    content = content.replace(b"\r\n", b"\n")
                arcname = p.relative_to(src_dir).as_posix()
                z.writestr(arcname, content)
                print(f"  + {arcname}")

    print(f"Built: {output_zip.name} ({output_zip.stat().st_size} bytes)")


def build_all_packages():
    pkgs_dir = USB_PKG_DIR / "packages"
    pkgs_dir.mkdir(parents=True, exist_ok=True)
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n--- Building Package 1: arabic.ui (Safe Profile Mode) ---")
    ui_zip = pkgs_dir / "arabic.ui.zip"
    build_single_zip(BASE_DIR / "arabic.ui", ui_zip)
    # Also copy standalone zip to releases/ for easy upload to NEMESIS Store
    shutil.copy2(ui_zip, RELEASES_DIR / "arabic.ui.zip")
    print(f"  -> Copied standalone to releases/arabic.ui.zip")

    print("\n--- Building Package 2: arabic.full (Full Region Mod) ---")
    full_zip = pkgs_dir / "arabic.full.zip"
    build_single_zip(BASE_DIR / "arabic.full", full_zip)
    # Also copy standalone zip to releases/ for easy upload to NEMESIS Store
    shutil.copy2(full_zip, RELEASES_DIR / "arabic.full.zip")
    print(f"  -> Copied standalone to releases/arabic.full.zip")


def create_usb_installer_files():
    usb_data = """[nemesis]
version=1.0
type=list

[package.0]
path=packages/arabic.ui.zip

[package.1]
path=packages/arabic.full.zip
"""
    usb_data_file = USB_PKG_DIR / "NEMESIS.data"
    with open(usb_data_file, "w", newline="\n", encoding="utf-8") as f:
        f.write(usb_data)
    print(f"\nCreated USB Package Store descriptor: {usb_data_file}")


def create_releases_zip():
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    out_usb_pkg = RELEASES_DIR / "Gen5W_Arabic_USB_Package.zip"

    # Zip the contents of usb_package/ directly at the root of the archive
    with zipfile.ZipFile(out_usb_pkg, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(USB_PKG_DIR.rglob("*")):
            if p.is_file():
                arcname = p.relative_to(USB_PKG_DIR).as_posix()
                z.write(p, arcname)
                print(f"  + releases/Gen5W_Arabic_USB_Package.zip: {arcname}")

    print(f"\nCreated Releases ZIP archive: {out_usb_pkg} ({out_usb_pkg.stat().st_size} bytes)")

    out_recovery_pkg = RELEASES_DIR / "Gen5W_Emergency_Recovery_USB.zip"
    with zipfile.ZipFile(out_recovery_pkg, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(USB_RECOVERY_DIR.rglob("*")):
            if p.is_file():
                arcname = p.relative_to(USB_RECOVERY_DIR).as_posix()
                z.write(p, arcname)
                print(f"  + releases/Gen5W_Emergency_Recovery_USB.zip: {arcname}")

    print(f"Created Recovery ZIP archive: {out_recovery_pkg} ({out_recovery_pkg.stat().st_size} bytes)")


if __name__ == "__main__":
    # Ensure source files are up-to-date
    import create_package_files
    print("\nPackage source files generated from create_package_files.py")

    build_all_packages()
    create_usb_installer_files()
    create_releases_zip()
    print("\n--- All Builds, USB Installer, and Releases Successfully Created ---")
