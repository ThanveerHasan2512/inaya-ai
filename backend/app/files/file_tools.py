import os
import shutil
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional

RESTRICTED_DIRECTORIES = [
    r"C:\Windows",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\System Volume Information",
    r"C:\$Recycle.Bin",
]


def is_path_safe(target_path: str, for_writing: bool = True) -> (bool, str):
    """
    Validates whether a path is safe to access.
    Restricts writing to system OS directories.
    """
    try:
        resolved = os.path.abspath(target_path)
    except Exception as e:
        return False, f"Invalid path syntax: {e}"

    # Check restricted directories
    for restricted in RESTRICTED_DIRECTORIES:
        if resolved.lower().startswith(restricted.lower()):
            if for_writing:
                return False, f"Access denied: Path '{resolved}' is inside protected Windows system directory '{restricted}'."

    return True, resolved


def create_file(path: str, content: str = "") -> Dict[str, Any]:
    safe, resolved = is_path_safe(path, for_writing=True)
    if not safe:
        return {"success": False, "action": "create_file", "error": resolved, "verification_status": "failed"}

    try:
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)

        verified = os.path.isfile(resolved)
        size = os.path.getsize(resolved) if verified else 0

        return {
            "success": verified,
            "action": "create_file",
            "path": resolved,
            "size": size,
            "details": f"Successfully created file at '{resolved}' ({size} bytes).",
            "verification_status": "verified" if verified else "failed",
            "verification_details": {"file_exists": verified, "size": size},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "create_file", "error": str(exc), "verification_status": "failed"}


def read_file(path: str, max_bytes: int = 100000) -> Dict[str, Any]:
    safe, resolved = is_path_safe(path, for_writing=False)
    if not safe:
        return {"success": False, "action": "read_file", "error": resolved, "verification_status": "failed"}

    if not os.path.isfile(resolved):
        return {"success": False, "action": "read_file", "error": f"File '{resolved}' does not exist.", "verification_status": "failed"}

    try:
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)

        return {
            "success": True,
            "action": "read_file",
            "path": resolved,
            "content": content,
            "bytes_read": len(content.encode("utf-8")),
            "details": f"Read {len(content)} characters from '{resolved}'.",
            "verification_status": "verified",
            "verification_details": {"file_exists": True},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "read_file", "error": str(exc), "verification_status": "failed"}


def write_file(path: str, content: str, append: bool = False) -> Dict[str, Any]:
    safe, resolved = is_path_safe(path, for_writing=True)
    if not safe:
        return {"success": False, "action": "write_file", "error": resolved, "verification_status": "failed"}

    try:
        os.makedirs(os.path.dirname(resolved), exist_ok=True)
        mode = "a" if append else "w"
        with open(resolved, mode, encoding="utf-8") as f:
            f.write(content)

        verified = os.path.isfile(resolved)
        size = os.path.getsize(resolved) if verified else 0

        action_type = "appended to" if append else "wrote to"
        return {
            "success": verified,
            "action": "write_file",
            "path": resolved,
            "size": size,
            "details": f"Successfully {action_type} '{resolved}' (Current size: {size} bytes).",
            "verification_status": "verified" if verified else "failed",
            "verification_details": {"file_exists": verified, "size": size},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "write_file", "error": str(exc), "verification_status": "failed"}


def create_folder(path: str) -> Dict[str, Any]:
    safe, resolved = is_path_safe(path, for_writing=True)
    if not safe:
        return {"success": False, "action": "create_folder", "error": resolved, "verification_status": "failed"}

    try:
        os.makedirs(resolved, exist_ok=True)
        verified = os.path.isdir(resolved)

        return {
            "success": verified,
            "action": "create_folder",
            "path": resolved,
            "details": f"Successfully created folder at '{resolved}'.",
            "verification_status": "verified" if verified else "failed",
            "verification_details": {"directory_exists": verified},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "create_folder", "error": str(exc), "verification_status": "failed"}


def list_folder(path: str) -> Dict[str, Any]:
    safe, resolved = is_path_safe(path, for_writing=False)
    if not safe:
        return {"success": False, "action": "list_folder", "error": resolved, "verification_status": "failed"}

    if not os.path.isdir(resolved):
        return {"success": False, "action": "list_folder", "error": f"Folder '{resolved}' does not exist.", "verification_status": "failed"}

    try:
        items = []
        for entry in os.scandir(resolved):
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": entry.stat().st_size if not entry.is_dir() else 0,
            })

        # Sort directories first, then alphabetically
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        return {
            "success": True,
            "action": "list_folder",
            "path": resolved,
            "total_items": len(items),
            "items": items,
            "details": f"Found {len(items)} items in folder '{resolved}'.",
            "verification_status": "verified",
            "verification_details": {"directory_exists": True},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "list_folder", "error": str(exc), "verification_status": "failed"}


def rename_file(old_path: str, new_path: str) -> Dict[str, Any]:
    safe_old, resolved_old = is_path_safe(old_path, for_writing=True)
    safe_new, resolved_new = is_path_safe(new_path, for_writing=True)
    if not safe_old: return {"success": False, "action": "rename_file", "error": resolved_old, "verification_status": "failed"}
    if not safe_new: return {"success": False, "action": "rename_file", "error": resolved_new, "verification_status": "failed"}

    if not os.path.exists(resolved_old):
        return {"success": False, "action": "rename_file", "error": f"Source '{resolved_old}' does not exist.", "verification_status": "failed"}

    try:
        os.rename(resolved_old, resolved_new)
        verified = os.path.exists(resolved_new) and not os.path.exists(resolved_old)
        return {
            "success": verified,
            "action": "rename_file",
            "old_path": resolved_old,
            "new_path": resolved_new,
            "details": f"Renamed '{resolved_old}' to '{resolved_new}'.",
            "verification_status": "verified" if verified else "failed",
            "verification_details": {"renamed": verified},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "rename_file", "error": str(exc), "verification_status": "failed"}


def copy_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    safe_src, res_src = is_path_safe(source_path, for_writing=False)
    safe_dst, res_dst = is_path_safe(destination_path, for_writing=True)
    if not safe_src: return {"success": False, "action": "copy_file", "error": res_src, "verification_status": "failed"}
    if not safe_dst: return {"success": False, "action": "copy_file", "error": res_dst, "verification_status": "failed"}

    if not os.path.exists(res_src):
        return {"success": False, "action": "copy_file", "error": f"Source '{res_src}' does not exist.", "verification_status": "failed"}

    try:
        if os.path.isdir(res_src):
            shutil.copytree(res_src, res_dst, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(res_dst), exist_ok=True)
            shutil.copy2(res_src, res_dst)

        verified = os.path.exists(res_dst)
        return {
            "success": verified,
            "action": "copy_file",
            "source": res_src,
            "destination": res_dst,
            "details": f"Copied '{res_src}' to '{res_dst}'.",
            "verification_status": "verified" if verified else "failed",
            "verification_details": {"destination_exists": verified},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "copy_file", "error": str(exc), "verification_status": "failed"}


def move_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    safe_src, res_src = is_path_safe(source_path, for_writing=True)
    safe_dst, res_dst = is_path_safe(destination_path, for_writing=True)
    if not safe_src: return {"success": False, "action": "move_file", "error": res_src, "verification_status": "failed"}
    if not safe_dst: return {"success": False, "action": "move_file", "error": res_dst, "verification_status": "failed"}

    if not os.path.exists(res_src):
        return {"success": False, "action": "move_file", "error": f"Source '{res_src}' does not exist.", "verification_status": "failed"}

    try:
        os.makedirs(os.path.dirname(res_dst), exist_ok=True)
        shutil.move(res_src, res_dst)
        verified = os.path.exists(res_dst) and not os.path.exists(res_src)
        return {
            "success": verified,
            "action": "move_file",
            "source": res_src,
            "destination": res_dst,
            "details": f"Moved '{res_src}' to '{res_dst}'.",
            "verification_status": "verified" if verified else "failed",
            "verification_details": {"moved": verified},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "move_file", "error": str(exc), "verification_status": "failed"}


def search_files(directory: str, query: str = "*", recursive: bool = True) -> Dict[str, Any]:
    safe, resolved = is_path_safe(directory, for_writing=False)
    if not safe:
        return {"success": False, "action": "search_files", "error": resolved, "verification_status": "failed"}

    if not os.path.isdir(resolved):
        return {"success": False, "action": "search_files", "error": f"Directory '{resolved}' does not exist.", "verification_status": "failed"}

    try:
        pattern = os.path.join(resolved, "**" if recursive else "", query)
        matches = glob.glob(pattern, recursive=recursive)
        file_matches = [os.path.abspath(m) for m in matches[:100]]

        return {
            "success": True,
            "action": "search_files",
            "directory": resolved,
            "query": query,
            "count": len(file_matches),
            "matches": file_matches,
            "details": f"Found {len(file_matches)} matches for '{query}' in '{resolved}'.",
            "verification_status": "verified",
            "verification_details": {"count": len(file_matches)},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "search_files", "error": str(exc), "verification_status": "failed"}


def open_path(path: str) -> Dict[str, Any]:
    """
    Opens a file or folder in the Windows desktop environment using the default handler.
    """
    safe, resolved = is_path_safe(path, for_writing=False)
    if not safe:
        return {"success": False, "action": "open_path", "error": resolved, "verification_status": "failed"}

    if not os.path.exists(resolved):
        return {"success": False, "action": "open_path", "error": f"Path '{resolved}' does not exist.", "verification_status": "failed"}

    try:
        if hasattr(os, "startfile"):
            os.startfile(resolved)
        else:
            subprocess.Popen(["explorer.exe", resolved], shell=False)

        return {
            "success": True,
            "action": "open_path",
            "path": resolved,
            "details": f"Opened '{resolved}' in Windows.",
            "verification_status": "verified",
            "verification_details": {"path_exists": True},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "open_path", "error": str(exc), "verification_status": "failed"}
