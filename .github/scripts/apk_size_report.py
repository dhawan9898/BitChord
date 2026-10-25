#!/usr/bin/env python3
"""Prints where an APK's bytes are, as GitHub-flavoured Markdown.

Usage: apk_size_report.py <apk> [top-n]

Sizes are the compressed sizes stored in the APK (what the download costs),
not what is unpacked on the device. Files are grouped so the biggest levers
are obvious: native libraries, dex (code), the embedded watch APK, resources
and assets.
"""
import sys
import zipfile
from collections import defaultdict


def group(name: str) -> str:
    if name.startswith("lib/"):
        return "Native libraries (lib/)"
    if name.endswith(".dex"):
        return "Code (classes*.dex)"
    if name == "resources.arsc":
        return "Compiled resources (resources.arsc)"
    if name.startswith("assets/") and name.endswith(".onnx"):
        return "ONNX models (assets/)"
    if name.endswith(".apk") or "wear" in name.lower() and name.endswith((".apk", ".bin")):
        return "Embedded watch app"
    if name.startswith("assets/"):
        return "Other assets"
    if name.startswith("res/"):
        return "Resources (res/)"
    if name.startswith("META-INF/"):
        return "META-INF"
    return "Other"


def mb(n: int) -> str:
    return f"{n / 1048576:.2f} MB"


def main() -> None:
    apk = sys.argv[1]
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    with zipfile.ZipFile(apk) as z:
        infos = z.infolist()
    total = sum(i.compress_size for i in infos)
    groups = defaultdict(int)
    for i in infos:
        groups[group(i.filename)] += i.compress_size

    print(f"## APK size report: `{apk.split('/')[-1]}`\n")
    print(f"**Download size (sum of compressed entries): {mb(total)}**\n")
    print("| Group | Size | Share |")
    print("|---|---:|---:|")
    for name, size in sorted(groups.items(), key=lambda kv: -kv[1]):
        print(f"| {name} | {mb(size)} | {size * 100 / total:.1f}% |")
    print(f"\n### Largest {top} files\n")
    print("| File | Compressed | Uncompressed |")
    print("|---|---:|---:|")
    for i in sorted(infos, key=lambda x: -x.compress_size)[:top]:
        print(f"| `{i.filename}` | {mb(i.compress_size)} | {mb(i.file_size)} |")


if __name__ == "__main__":
    main()
