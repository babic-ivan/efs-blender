#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 EasyFormStudio
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Codesign Mach-O binaries inside macOS .whl files bundled in the app.

Notarization unpacks wheels (they are ZIPs) and rejects unsigned .so/.dylib
inside them. This re-signs those binaries with the Developer ID identity and
updates each wheel's RECORD hashes so wheel installation stays valid.

Usage: sign_wheel_binaries.py <app-or-dir> "<identity>"
"""

import base64
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

MACHO_MAGICS = (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe",
                b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca")


def _is_macho(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) in MACHO_MAGICS
    except OSError:
        return False


def _record_hash(path):
    digest = hashlib.sha256(open(path, "rb").read()).digest()
    encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"sha256={encoded}", os.path.getsize(path)


def sign_wheel(wheel_path, identity):
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(wheel_path) as zf:
            zf.extractall(tmp)

        signed = []
        for root, _dirs, files in os.walk(tmp):
            for name in files:
                full = os.path.join(root, name)
                if _is_macho(full):
                    subprocess.run(
                        ["codesign", "--force", "--timestamp", "--options", "runtime",
                         "--sign", identity, full],
                        check=True, capture_output=True)
                    signed.append(os.path.relpath(full, tmp))

        if not signed:
            return 0

        # update RECORD hashes for the re-signed files
        for root, _dirs, files in os.walk(tmp):
            for name in files:
                if name != "RECORD" or not root.endswith(".dist-info"):
                    continue
                record_path = os.path.join(root, name)
                lines = open(record_path, encoding="utf-8").read().splitlines()
                out = []
                for line in lines:
                    rel = line.split(",", 1)[0]
                    if rel in signed:
                        h, size = _record_hash(os.path.join(tmp, rel))
                        out.append(f"{rel},{h},{size}")
                    else:
                        out.append(line)
                open(record_path, "w", encoding="utf-8").write("\n".join(out) + "\n")

        # rebuild the wheel zip
        new_wheel = wheel_path + ".new"
        with zipfile.ZipFile(new_wheel, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmp):
                for name in sorted(files):
                    full = os.path.join(root, name)
                    zf.write(full, os.path.relpath(full, tmp))
        os.replace(new_wheel, wheel_path)
        return len(signed)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    target, identity = sys.argv[1], sys.argv[2]
    total_wheels = 0
    total_bins = 0
    for root, _dirs, files in os.walk(target):
        for name in files:
            if name.endswith(".whl") and "macosx" in name:
                count = sign_wheel(os.path.join(root, name), identity)
                if count:
                    total_wheels += 1
                    total_bins += count
                    print(f"  {name}: {count} binarija potpisano")
    print(f"Wheelova promijenjeno: {total_wheels}, binarija: {total_bins}")


if __name__ == "__main__":
    main()
