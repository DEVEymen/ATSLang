"""Builds editor/atslang.vsix from editor/vscode without any external tool.

A .vsix is a zip file with a manifest; VS Code installs it with
"Install from VSIX..." or `code --install-extension`.

    python tools/build_vsix.py
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "editor" / "vscode"
OUTPUT = ROOT / "editor" / "atslang.vsix"

CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
  <Default Extension=".md" ContentType="text/markdown"/>
</Types>
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}"/>
    <DisplayName>{display}</DisplayName>
    <Description xml:space="preserve">{description}</Description>
    <Categories>Programming Languages</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{engine}"/>
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="workspace"/>
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"/>
  </Assets>
</PackageManifest>
"""


def build(output: Path = OUTPUT) -> Path:
    package = json.loads((SOURCE / "package.json").read_text(encoding="utf-8"))
    manifest = MANIFEST.format(
        name=escape(package["name"]), version=escape(package["version"]),
        publisher=escape(package["publisher"]), display=escape(package["displayName"]),
        description=escape(package["description"]), engine=escape(package["engines"]["vscode"]),
    )
    # Fixed timestamps keep the file identical between builds.
    def add(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, data)

    with zipfile.ZipFile(output, "w") as zf:
        add(zf, "[Content_Types].xml", CONTENT_TYPES.encode("utf-8"))
        add(zf, "extension.vsixmanifest", manifest.encode("utf-8"))
        for path in sorted(SOURCE.rglob("*")):
            if path.is_file():
                add(zf, "extension/" + path.relative_to(SOURCE).as_posix(), path.read_bytes())
    return output


if __name__ == "__main__":
    print(build(Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT))
