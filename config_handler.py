import os
import logging
import sys
import shutil
from tcd_browser import TCDBrowser, TCD_LIST
from pathlib import Path
import fileinput
from preferences import preferences

logger = logging.getLogger(__name__)


def remove_dark_preferences(config_path: Path):
    """Restore preference files from backups.

    Args:
        config_path (str): Ghidra config path.
    """
    preferences_path = os.path.join(config_path, "preferences")
    if not os.path.exists(preferences_path):
        logging.error("Please open Ghidra at least once to fully install dark mode.")
        sys.exit(-1)

    with fileinput.FileInput(preferences_path, inplace=True) as fp:
        for line in fp:
            if "LastLookAndFeel=System" not in line:
                print(line, end="")
            else:
                logging.debug("Restored %s", preferences_path)

    for tcd in TCD_LIST:
        tcd_path = os.path.join(config_path, "tools", tcd)
        backup_path = os.path.join(config_path, "tools", f"{tcd}.bak")
        if os.path.exists(tcd_path) and not os.path.exists(backup_path):
            logger.warning("Could not restore %s", tcd_path)
        elif os.path.exists(backup_path):
            os.remove(tcd_path)
            os.rename(backup_path, tcd_path)
            logger.debug("Restored %s", tcd_path)
        else:
            logger.debug("Could not restore %s", tcd_path)


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
