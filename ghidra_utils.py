import re
import shutil
import os
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def is_running() -> bool:
    """Check if `ghidrarun` is running.

    Returns:
        bool: If Ghidra is running.
    """
    if os.name == "nt":
        find_ghidra = "WMIC path win32_process get Commandline"
    else:
        find_ghidra = "ps -ax"
    out = subprocess.check_output(find_ghidra.split())
    logger.debug("Running %s", find_ghidra)
    if b"ghidrarun" in out.lower():
        return True
    return False


def get_install_path() -> Path:
    """Find the Ghidra install path by using `which`.

    Returns:
        Path: Ghidra install path.
    """

    # Attempt to find the installation directory based on `ghidraRun`
    ghidra_run_path = shutil.which("ghidraRun")
    if not ghidra_run_path:
        raise FileNotFoundError()
    return Path(ghidra_run_path).resolve().parents[0]


def get_config_path(version: str, user: str | None = None) -> Path:
    """Find the Ghidra config path based off of `version` and `user`.

    Args:
        version (str): The current version of Ghidra.
        user (str, optional): The user's home to search. Defaults to None.

    Returns:
        Path: Ghidra config path.
    """
    home: Path = Path.home() if not user else Path(os.path.expanduser(f"~{user}"))
    logger.debug("Using home: %s", home)

    # _PUBLIC was appended to the name after 9.0.4
    # The "-" after .ghidra was changed to "_" after 9.0.4
    version_number = ".".join(re.findall("[0-9]+", version))
    if tuple(map(int, (version_number.split(".")))) > (9, 0, 4):
        version_path = f".ghidra_{version}_PUBLIC"
        # _DEV when built from source, or from some repos (Arch, Kali, etc.)
        if not os.path.exists(os.path.join(home, ".ghidra", version_path)):
            version_path = f".ghidra_{version}_DEV"
    else:
        version_path = f".ghidra-{version}"

    return home / ".ghidra" / version_path


def get_version(install_path: Path) -> str:
    """Parse the version from the `application.properties` file.

    Args:
        install_path (Path): Ghidra installation path; contains `application.properties`

    Returns:
        str: Ghidra Version (e.g. 9.2, 10.0-BETA).
    """
    # Get the version from the application.properties file
    properties_path = install_path / "Ghidra" / "application.properties"
    with open(properties_path, "r") as fp:
        for line in fp:
            if "application.version=" in line:
                return line.split("=")[-1].strip()
    return ""
