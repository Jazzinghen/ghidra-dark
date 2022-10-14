"""Install Ghidra dark theme."""
import argparse
import logging
from pathlib import Path
import subprocess
import sys
from urllib.error import URLError


import ghidra_utils
import config_handler
from flatlaf import FlatLaf


logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> int:
    """Install Ghidra dark theme

    Args:
        args (argparse.Namespace): Command line arguments.
    """
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level, format="%(asctime)s - %(levelname)s: %(message)s", datefmt="%X"
    )

    try:
        if ghidra_utils.is_running():
            logger.error("Please close any running Ghidra instances.")
            return -1
    except subprocess.SubprocessError as err:
        logger.error(f"Encountered error while checking Ghidra: {err.with_traceback}")
        return -1
    except OSError as err:
        logger.error(f"Encountered error: {err.strerror}")
        return err.errno

    ghidra_install_path: Path = args.install_path
    if not ghidra_install_path:
        try:
            ghidra_install_path = ghidra_utils.get_install_path()
            logger.debug("Using Ghidra install path %s", ghidra_install_path)
        except FileNotFoundError as err:
            logger.error("Could not find Ghidra installation, specify with --path")
            return err.errno

    ghidra_version = ghidra_utils.get_version(ghidra_install_path)
    logger.debug("Found Ghidra v%s", ghidra_version)

    try:
        ghidra_config_path = ghidra_utils.get_config_path(ghidra_version, args.user)
        logger.debug("Using Ghidra config path %s", ghidra_config_path)

        if not args.remove:
            logger.debug("Installing FlatLaf...")
            flatlaf = FlatLaf(ghidra_install_path)
            flatlaf.install()

            logger.debug("Installing dark preferences...")
            config_handler.install_dark_preferences(ghidra_config_path)
        else:
            logger.debug("Uninstalling FlatLaf...")
            flatlaf = FlatLaf(ghidra_install_path)
            flatlaf.remove()

            logger.debug("Removing dark preferences...")
            config_handler.remove_dark_preferences(ghidra_config_path)
    except URLError as err:
        logger.warning(f"Encountered an error while retrieving files: {err.strerror}")
        return err.errno
    except OSError as err:
        logger.warning(f"Encountered an OS error: {err.strerror}")
        return err.errno
    except AssertionError as err:
        logger.error(f"Failed an assertion: {err.with_traceback}")
        return -1

    return 0


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
    parser.add_argument(
        "-r", "--remove", action="store_true", help="uninstall dark theme"
    )

    sys.exit(main(parser.parse_args()))
