import os
import logging
import shutil
from tcd_browser import TCDBrowser, TCD_LIST
from pathlib import Path
import fileinput
from preferences import preferences

logger = logging.getLogger(__name__)


def remove_dark_preferences(config_path: Path):
    """Restore preference files from backups.

    Args:
        config_path (Path): Ghidra config path.
    """
    for tcd in TCD_LIST:
        tcd_path: Path = config_path / "tools" / tcd
        tcd_extension: str = tcd_path.suffix
        backup_path: Path = tcd_path.with_suffix(tcd_extension + ".bak")
        if not backup_path.exists():
            if tcd_path.exists():
                logger.warning(f"No backup of {tcd} found, cannot restore!")
        else:
            try:
                os.remove(tcd_path)
            except FileNotFoundError:
                logger.warning(f"File {tcd} not found, will restore backup anyway")

            os.rename(backup_path, tcd_path)
            logger.debug("Restored %s", tcd_path)


def install_dark_preferences(config_path: Path):
    """Backup and modify preference files to use dark colors.

    Args:
        config_path (Path): Ghidra config path.
    """
    preferences_path = config_path / "preferences"
    if not os.path.exists(preferences_path):
        logger.error("Please open Ghidra at least once to fully install dark mode.")
        raise FileNotFoundError

    # Check if the current L&f is system
    logger.debug("Checking for look and feel configuration")
    with fileinput.FileInput(
        preferences_path, inplace=True, backup=".bak", mode="r", encoding="utf-8"
    ) as config_fp:
        for line in config_fp:
            if "LastLookAndFeel" not in line:
                print(line, end="")
            else:
                split_line = line.split("=")
                if len(split_line) == 2:
                    split_line[1] = "System"

                print("=".join(split_line), end="")

        logger.debug("Set the correct Look and Feel")

    # Backup and modify the current tcd and tool files
    logger.debug("Injecting preferences in TCD files")
    for tcd in TCD_LIST:
        tcd_path = config_path / "tools" / tcd
        tcd_extension = tcd_path.suffix
        backup_path = tcd_path.with_suffix(tcd_extension + ".bak")
        if tcd_path.exists():
            logger.debug(f"Backing {tcd_path} up...")
            shutil.copy(tcd_path, backup_path)
            browser = TCDBrowser(tcd_path)
            logger.debug("\tInjecting preferences")
            browser.update(preferences)
        elif tcd == "_code_browser.tcd":
            logger.warning(
                "Please open Ghidra at least once to fully install dark mode."
            )
