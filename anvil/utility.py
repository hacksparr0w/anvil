import shutil
import subprocess
import sys
import urllib.request

from pathlib import Path
from typing import Dict, List, Optional


__all__ = [
    "clone_git_repository",
    "download_file",
    "pythonify_name",
    "run",
    "untar"
]


DEFAULT_HTTP_USER_AGENT = "anvil"


def run(
    command: List[str],
    working_directory: Path = None,
    environment: Dict = {}
):
    with subprocess.Popen(
        command,
        cwd=str(working_directory) if working_directory else None,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=environment
    ) as process:
        process.communicate()
        code = process.wait()

        if code != 0:
            raise RuntimeError(
                f"'{' '.join(command)}' failed, return code {code}"
            )


def clone_git_repository(
    url: str,
    path: Path,
    branch: Optional[str] = None,
    depth: Optional[int] = None
):
    command = ["git", "clone"]

    if branch:
        command.extend(["-b", branch])

    if depth:
        command.extend(["--depth", str(depth)])

    command.extend([url, str(path)])

    run(command)


def download_file(url: str, path: Path):
    request = urllib.request.Request(url)
    request.add_header("User-Agent", DEFAULT_HTTP_USER_AGENT)

    with urllib.request.urlopen(request) as response:
        with path.open("wb") as output:
            shutil.copyfileobj(response, output)


def pythonify_name(name: str) -> str:
    return name.replace("-", "_")


def untar(file: Path, strip_components: Optional[int] = None):
    command = ["tar", "-zxvf"]

    if strip_components:
        command.append(f"--strip-components={strip_components}")

    command.append(str(file))
