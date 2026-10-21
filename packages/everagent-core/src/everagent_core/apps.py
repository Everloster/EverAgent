"""Host application metadata from the exact caller ancestry; never a global app inventory."""
from __future__ import annotations

import os
from pathlib import Path
import plistlib
from .identity import processes

DESKTOP_APPS = {
    "kimi-desktop": {"name": "Kimi", "bundle_id": "com.moonshot.kimichat"},
    "zcode": {"name": "ZCode", "bundle_id": "dev.zcode.app"},
    "minimax-code": {"name": "MiniMax Code", "bundle_id": "com.minimax.agent.cn"},
}


def app_for_process(row: dict, *, windows: bool | None = None) -> str | None:
    windows = os.name == "nt" if windows is None else windows
    image = row.get("image", "")
    name = row.get("name", "")
    if not isinstance(image, str) or not isinstance(name, str):
        return None
    for app_id, app in DESKTOP_APPS.items():
        if not windows and app["name"] + ".app/Contents/" in image:
            return app_id
        if windows:
            # Windows filenames are case insensitive. Product directory and
            # executable must agree; a bare Kimi.exe cannot identify Desktop.
            parts = image.replace("\\", "/").split("/")
            product = app["name"].casefold().replace(" ", "")
            directories = {part.casefold().replace(" ", "") for part in parts[:-1]}
            executable = name.casefold().removesuffix(".exe").replace(" ", "")
            if product in directories and (executable == product or executable.startswith(product + "helper")):
                return app_id
    return None


def inspect_host() -> dict:
    for row in processes.process_chain():
        image = row.get("image", "")
        app_id = app_for_process(row)
        if app_id:
            app = DESKTOP_APPS[app_id]
            marker = app["name"] + ".app/Contents/"
            is_mac = marker in image
            result = {"id": app_id, "kind": "desktop", "verified": True,
                      "source": "caller-process-image", "model_api": "unavailable"}
            if is_mac:
                path = Path(image.split(marker, 1)[0]) / (app["name"] + ".app/Contents/Info.plist")
                try:
                    if path.stat().st_size <= 131072:
                        with path.open("rb") as handle:
                            metadata = plistlib.load(handle)
                        if metadata.get("CFBundleIdentifier") != app["bundle_id"]:
                            return {"id": app_id, "kind": "desktop", "verified": False,
                                    "source": "caller-process-image", "status": "bundle-mismatch"}
                        result["version"] = str(metadata.get("CFBundleShortVersionString", ""))[:64]
                except (OSError, ValueError, TypeError, plistlib.InvalidFileException):
                    result["metadata_status"] = "unavailable"
            return result
    return {"id": None, "kind": "terminal", "verified": False, "source": "unresolved"}
