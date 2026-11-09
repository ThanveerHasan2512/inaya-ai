import os
import sys
import subprocess
from typing import Dict, Any, Optional

DEFAULT_WORKSPACE = r"D:\INAYA\scratch"


def create_python_project(project_name: str, directory: Optional[str] = None) -> Dict[str, Any]:
    """
    Scaffolds a clean Python project with main.py, requirements.txt, and README.md.
    """
    clean_name = "".join(c for c in project_name if c.isalnum() or c in ("-", "_")).strip()
    if not clean_name:
        clean_name = "sample_project"

    base_dir = os.path.abspath(directory) if directory else DEFAULT_WORKSPACE
    target_dir = os.path.join(base_dir, clean_name)

    try:
        os.makedirs(target_dir, exist_ok=True)

        main_py = os.path.join(target_dir, "main.py")
        with open(main_py, "w", encoding="utf-8") as f:
            f.write(f'"""\nProject: {clean_name}\nCreated by INAYA Autonomous AI\n"""\n\ndef main():\n    print("Hello from {clean_name}!")\n\nif __name__ == "__main__":\n    main()\n')

        req_txt = os.path.join(target_dir, "requirements.txt")
        with open(req_txt, "w", encoding="utf-8") as f:
            f.write("# Project dependencies\n")

        readme_md = os.path.join(target_dir, "README.md")
        with open(readme_md, "w", encoding="utf-8") as f:
            f.write(f"# {clean_name}\n\nAutomated project created by INAYA.\n\n## Usage\n```bash\npython main.py\n```\n")

        verified = os.path.isfile(main_py) and os.path.isfile(readme_md)
        return {
            "success": verified,
            "action": "create_python_project",
            "project_name": clean_name,
            "project_path": target_dir,
            "files_created": ["main.py", "requirements.txt", "README.md"],
            "verification_status": "verified" if verified else "failed",
            "details": f"Successfully created Python project '{clean_name}' at '{target_dir}'.",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "create_python_project", "error": str(exc), "verification_status": "failed"}


def create_java_file(class_name: str, directory: Optional[str] = None, package_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Creates a clean Java source file with a main method.
    """
    clean_class = "".join(c for c in class_name if c.isalnum() or c == "_").strip()
    if not clean_class or not clean_class[0].isalpha():
        clean_class = "MainApp"

    base_dir = os.path.abspath(directory) if directory else DEFAULT_WORKSPACE
    os.makedirs(base_dir, exist_ok=True)
    java_file = os.path.join(base_dir, f"{clean_class}.java")

    try:
        pkg_header = f"package {package_name};\n\n" if package_name else ""
        content = (
            f"{pkg_header}"
            f"public class {clean_class} {{\n"
            f"    public static void main(String[] args) {{\n"
            f'        System.out.println("Hello from {clean_class}!");\n'
            f"    }}\n"
            f"}}\n"
        )
        with open(java_file, "w", encoding="utf-8") as f:
            f.write(content)

        verified = os.path.isfile(java_file)
        return {
            "success": verified,
            "action": "create_java_file",
            "class_name": clean_class,
            "path": java_file,
            "verification_status": "verified" if verified else "failed",
            "details": f"Successfully created Java source file at '{java_file}'.",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "create_java_file", "error": str(exc), "verification_status": "failed"}


def run_program(script_path: str, timeout: int = 15) -> Dict[str, Any]:
    """
    Safely executes a Python program inside the project virtual environment,
    capturing standard output, errors, and execution time with a strict timeout.
    """
    resolved = os.path.abspath(script_path)
    if not os.path.isfile(resolved):
        return {"success": False, "action": "run_program", "error": f"Script '{resolved}' not found.", "verification_status": "failed"}

    # Use project python interpreter
    python_exe = sys.executable

    try:
        proc = subprocess.run(
            [python_exe, resolved],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(resolved),
        )

        success = proc.returncode == 0
        return {
            "success": success,
            "action": "run_program",
            "script_path": resolved,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "verification_status": "verified" if success else "failed",
            "details": f"Executed '{os.path.basename(resolved)}' (Exit Code: {proc.returncode}). Output: {proc.stdout.strip()[:200]}",
            "error": proc.stderr.strip() if proc.stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "action": "run_program",
            "script_path": resolved,
            "error": f"Execution timed out after {timeout} seconds.",
            "verification_status": "failed",
        }
    except Exception as exc:
        return {"success": False, "action": "run_program", "error": str(exc), "verification_status": "failed"}
