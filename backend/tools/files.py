import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.Files")

USER_HOME = Path.home()

@tool_registry.register(
    name="search_files",
    description="Searches for files matching a pattern or extension in standard user folders (Downloads, Documents, Desktop, or custom path).",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Search keyword or extension (e.g. '.pdf', 'report', '*.txt')"},
            "root_path": {"type": "string", "description": "Directory to search in. Defaults to User Home directory."}
        },
        "required": ["pattern"]
    }
)
def search_files(pattern: str, root_path: Optional[str] = None) -> Dict[str, Any]:
    pattern_clean = pattern.lower().replace("*", "")
    matches = []
    
    # Standard user search locations if root_path not given
    if root_path:
        search_dirs = [Path(root_path)]
    else:
        search_dirs = [
            USER_HOME / "Downloads",
            USER_HOME / "Documents",
            USER_HOME / "Desktop"
        ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        try:
            for path in search_dir.rglob("*"):
                if len(matches) >= 100:
                    break
                if path.is_file() and pattern_clean in path.name.lower():
                    matches.append({
                        "name": path.name,
                        "path": str(path),
                        "folder": path.parent.name,
                        "size_bytes": path.stat().st_size
                    })
        except Exception as e:
            logger.debug(f"Search error in {search_dir}: {e}")

    total_count = len(matches)
    summary_text = (
        f"I found {total_count} matching '{pattern}' file{'s' if total_count != 1 else ''} in your user directories, sir."
        if total_count > 0 else f"I searched your user folders but found no files matching '{pattern}', sir."
    )

    return {
        "status": "SUCCESS",
        "query_pattern": pattern,
        "count": total_count,
        "matches_found": total_count,
        "summary": summary_text,
        "files": matches[:30]
    }

@tool_registry.register(
    name="find_largest_files",
    description="Finds the largest files in a specified folder (default: Downloads).",
    parameters={
        "type": "object",
        "properties": {
            "folder_name": {"type": "string", "description": "Folder to search (e.g. 'downloads', 'documents', 'desktop')"},
            "limit": {"type": "integer", "description": "Number of files to return (default 5)"}
        },
        "required": []
    }
)
def find_largest_files(folder_name: str = "downloads", limit: int = 5) -> Dict[str, Any]:
    folder_clean = folder_name.strip().lower()
    if "download" in folder_clean:
        target = USER_HOME / "Downloads"
    elif "document" in folder_clean:
        target = USER_HOME / "Documents"
    elif "desktop" in folder_clean:
        target = USER_HOME / "Desktop"
    else:
        target = Path(folder_name)

    if not target.exists() or not target.is_dir():
        return {"status": "ERROR", "error": f"Directory '{target}' does not exist."}

    files = []
    try:
        for p in target.glob("*"):
            if p.is_file():
                files.append({
                    "name": p.name,
                    "path": str(p),
                    "size_mb": round(p.stat().st_size / (1024 * 1024), 2),
                    "size_bytes": p.stat().st_size
                })
        files.sort(key=lambda x: x["size_bytes"], reverse=True)
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

    top_files = files[:limit]
    summary_lines = [f"• {f['name']} ({f['size_mb']} MB)" for f in top_files]
    summary = f"Largest files in {target.name}:\n" + "\n".join(summary_lines) if top_files else f"No files found in {target.name}."

    return {
        "status": "SUCCESS",
        "folder": str(target),
        "files": top_files,
        "summary": summary
    }


@tool_registry.register(
    name="list_directory",
    description="Lists contents of a specified directory path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path to list."}
        },
        "required": ["path"]
    }
)
def list_directory(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"error": f"Path '{path}' does not exist.", "items": []}
    if not p.is_dir():
        return {"error": f"Path '{path}' is not a directory.", "items": []}

    items = []
    for child in p.iterdir():
        items.append({
            "name": child.name,
            "path": str(child),
            "is_dir": child.is_dir(),
            "size_bytes": child.stat().st_size if child.is_file() else 0
        })

    return {"directory": str(p), "count": len(items), "items": items[:50]}

@tool_registry.register(
    name="read_file",
    description="Reads content of a supported text file.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to text file."}
        },
        "required": ["path"]
    }
)
def read_file(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"error": f"File '{path}' does not exist."}
    
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
        return {
            "path": str(p),
            "content": content[:5000], # Max 5000 chars output
            "total_length": len(content)
        }
    except Exception as e:
        return {"error": f"Could not read file '{path}': {str(e)}"}

@tool_registry.register(
    name="create_directory",
    description="Creates a new folder at target path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "New folder path to create."}
        },
        "required": ["path"]
    }
)
def create_directory(path: str) -> Dict[str, Any]:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return {"path": str(p), "status": f"Directory '{p.name}' created successfully."}

@tool_registry.register(
    name="create_file",
    description="Creates or overwrites a text file with specified content.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target file path."},
            "content": {"type": "string", "description": "Text content to write into file."}
        },
        "required": ["path", "content"]
    }
)
def create_file(path: str, content: str) -> Dict[str, Any]:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": str(p), "status": f"File '{p.name}' written successfully.", "bytes": len(content)}

@tool_registry.register(
    name="delete_file",
    description="Deletes a file or directory.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File or folder path to delete."}
        },
        "required": ["path"]
    }
)
def delete_file(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"error": f"Path '{path}' does not exist."}
    
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()

    return {"path": str(p), "status": f"Successfully deleted '{p.name}'."}

@tool_registry.register(
    name="open_folder",
    description="Opens Windows File Explorer directly to standard user folders (Downloads, Documents, Desktop, or custom path).",
    parameters={
        "type": "object",
        "properties": {
            "folder_name": {"type": "string", "description": "Folder name (e.g. 'downloads', 'documents', 'desktop') or absolute directory path."}
        },
        "required": ["folder_name"]
    }
)
def open_folder(folder_name: str = "downloads") -> Dict[str, Any]:
    import subprocess
    name_clean = folder_name.strip().lower()
    
    if "download" in name_clean:
        target_path = USER_HOME / "Downloads"
    elif "desktop" in name_clean:
        target_path = USER_HOME / "Desktop"
    elif "document" in name_clean:
        target_path = USER_HOME / "Documents"
    else:
        target_path = Path(folder_name)

    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.Popen(f'explorer "{target_path}"', shell=True)
        return {
            "status": "SUCCESS",
            "folder": str(target_path),
            "message": f"Opened folder '{target_path.name}' in Windows File Explorer."
        }
    except Exception as e:
        return {"status": "ERROR", "error": f"Failed to open folder: {str(e)}"}

