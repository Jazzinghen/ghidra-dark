"""Install Ghidra dark theme."""
import argparse
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.error import URLError

from tcd_browser import TCDBrowser, TCD_LIST
from preferences import preferences
from flatlaf import FlatLaf


logger = logging.getLogger(__name__)


def is_ghidra_running() -> bool:
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


def get_ghidra_install_path(install_path: Path | None = None) -> Path:
    """Find the Ghidra install path by using `which`.

    Args:
        install_path (Path, optional): Ghidra install path. Defaults to None.

    Returns:
        Path: Ghidra install path.
    """
    if install_path:
        if not install_path.exists():
            raise FileNotFoundError
        return install_path

    # Attempt to find the installation directory based on `ghidraRun`
    ghidra_run_path = shutil.which("ghidraRun")
    if not ghidra_run_path:
        raise FileNotFoundError()
    return Path(ghidra_run_path).resolve().parents[0]


def get_ghidra_config_path(version: str, user: str | None = None) -> Path:
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


def get_ghidra_version(install_path: Path) -> str:
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


def install_dark_preferences(config_path: Path):
    """Backup and modify preference files to use dark colors.

    Args:
        config_path (Path): Ghidra config path.
    """
    preferences_path = config_path / "preferences"
    if not os.path.exists(preferences_path):
        logging.error("Please open Ghidra at least once to fully install dark mode.")
        sys.exit(-1)

    # Check if the current L&f is system
    using_system = False
    with open(preferences_path, "r") as fp:
        for line in fp:
            if "LastLookAndFeel=System" in line:
                using_system = True
                break

    # Set the L&f to system
    if not using_system:
        with open(preferences_path, "a") as fp:
            fp.write("LastLookAndFeel=System\n")

    # Backup and modify the current tcd and tool files
    for tcd in TCD_LIST:
        tcd_path = config_path / "tools" / tcd
        backup_path = config_path / "tools" / f"{tcd}.bak"
        try:
            shutil.copy(tcd_path, backup_path)
            browser = TCDBrowser(tcd_path)
            browser.update(preferences)
        except FileNotFoundError as err:
            if tcd == "_code_browser.tcd":
                logging.warning(
                    "Please open Ghidra at least once to fully install dark mode."
                )
            else:
                raise err


def main(args: argparse.Namespace):
    """Install Ghidra dark theme

    Args:
        args (argparse.Namespace): Command line arguments.
    """
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    try:
        if is_ghidra_running():
            logger.error("Please close any running Ghidra instances.")
            sys.exit(-1)
    except subprocess.SubprocessError as err:
        logger.error(f"Encountered error while checking Ghidra: {err.with_traceback}")
    except OSError as err:
        logger.error(f"Encountered error: {err.strerror}")

    try:
        ghidra_install_path = get_ghidra_install_path(args.install_path)
        logging.debug("Using Ghidra install path %s", ghidra_install_path)
    except FileNotFoundError as err:
        logging.error("Could not find Ghidra installation, specify with --path")
        sys.exit(err.errno)

    ghidra_version = get_ghidra_version(ghidra_install_path)
    logging.debug("Found Ghidra v%s", ghidra_version)

    try:
        ghidra_config_path = get_ghidra_config_path(ghidra_version, args.user)
        logging.debug("Using Ghidra config path %s", ghidra_config_path)

        logging.debug("Installing FlatLaf...")
        flatlaf = FlatLaf(ghidra_install_path)
        flatlaf.install()

        logging.debug("Installing dark preferences...")
        install_dark_preferences(ghidra_config_path)
    except URLError as err:
        logger.warning(f"Encountered an error while retrieving files: {err.strerror}")
    except OSError as err:
        logger.warning(f"Encountered an OS error: {err.strerror}")
    except AssertionError as err:
        logger.error(f"Failed an assertion: {err.with_traceback}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Ghidra dark theme")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="turn on debug logging"
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="install_path",
        type=Path,
        default=None,
        help="the installation path for Ghidra",
    )
    parser.add_argument(
        "-u", "--user", type=str, default=None, help="the user to install for"
    )

    main(parser.parse_args())
