#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 EasyFormStudio
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Bundle the EFS and MeasureIt extensions into a built EasyFormStudio.app
as system extensions (Resources/<version>/extensions/).

The EFS file set mirrors the official publish list (_dev/utils.ipynb).
The ``apk`` API-key file is intentionally NEVER copied: the application
ships without it and the user enters their API key on first run.

Usage:
  python3 build_files/utils/make_bundle_extensions.py \
      [--app PATH] [--efs-src PATH] [--measureit-src PATH]

Re-run this after a clean rebuild (an incremental ``make install`` keeps
already-bundled extensions in place).
"""

import argparse
import os
import re
import shutil
import sys

HOME = os.path.expanduser("~")

DEFAULT_APP = os.path.join(HOME, "build_darwin", "bin", "EasyFormStudio.app")
DEFAULT_EFS_SRC = os.path.join(
    HOME, "Library", "Application Support", "Blender", "5.0",
    "extensions", "user_default", "efs")
DEFAULT_MEASUREIT_SRC = os.path.join(
    HOME, "Library", "Application Support", "Blender", "5.0",
    "extensions", "blender_org", "measureit")

# Official EFS publish set (keep in sync with _dev/utils.ipynb).
# "wheels" is additionally required: blender_manifest.toml references the
# bundled dependency wheels (pandas, pillow, requests, reportlab, ...).
EFS_FOLDERS = [
    "element_templates", "icon", "pictures", "web_export", "assets", "hardware",
    "wheels",
]
EFS_FILES = [
    "__init__.py", "efs_cabinet_helper_functions.py", "efs_cabinet_props.py",
    "efs_cabinet_ui.py", "efs_cabinet.py", "efs_constants.py", "efs_exporter.py",
    "efs_labels.py", "efs_utils.py", "efs_parts.py", "efs_dxf.py",
    "efs_pdf_drawing.py", "efs_nesting.py", "efs_hardware.py", "efs_mpr.py",
    "efs_quote.py", "efs_label_print.py", "img_loader.py", "preferences.py",
    "efs.blend", "efs_pro", "prices.xlsx", "blender_manifest.toml",
]

JUNK = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".git")


def find_version_dir(app):
    resources = os.path.join(app, "Contents", "Resources")
    for name in sorted(os.listdir(resources)):
        if re.fullmatch(r"\d+\.\d+", name):
            return os.path.join(resources, name)
    sys.exit(f"No version folder found in {resources}")


def copy_efs(src, dest):
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for folder in EFS_FOLDERS:
        s = os.path.join(src, folder)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(dest, folder), ignore=JUNK)
        else:
            print(f"  warning: EFS folder missing: {folder}")
    for name in EFS_FILES:
        s = os.path.join(src, name)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(dest, name), ignore=JUNK)
        elif os.path.isfile(s):
            shutil.copy2(s, os.path.join(dest, name))
        else:
            print(f"  warning: EFS file missing: {name}")
    # Safety: the API key must never ship.
    apk = os.path.join(dest, "apk")
    if os.path.exists(apk):
        os.remove(apk)


def copy_measureit(src, dest):
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=JUNK)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default=DEFAULT_APP)
    parser.add_argument("--efs-src", default=DEFAULT_EFS_SRC)
    parser.add_argument("--measureit-src", default=DEFAULT_MEASUREIT_SRC)
    args = parser.parse_args()

    version_dir = find_version_dir(args.app)
    # The default "System" extensions repository reads from extensions/system.
    ext_dir = os.path.join(version_dir, "extensions", "system")
    os.makedirs(ext_dir, exist_ok=True)

    print(f"Bundling into: {ext_dir}")
    copy_efs(args.efs_src, os.path.join(ext_dir, "efs"))
    copy_measureit(args.measureit_src, os.path.join(ext_dir, "measureit"))

    for pkg in ("efs", "measureit"):
        manifest = os.path.join(ext_dir, pkg, "blender_manifest.toml")
        if not os.path.isfile(manifest):
            sys.exit(f"ERROR: manifest missing for {pkg}")
    if os.path.exists(os.path.join(ext_dir, "efs", "apk")):
        sys.exit("ERROR: apk file leaked into the bundle!")
    print("OK: efs + measureit bundled, no apk file shipped.")


if __name__ == "__main__":
    main()
