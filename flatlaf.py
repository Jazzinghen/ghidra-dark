"""FlatLaf package handling."""
import os
from typing import Tuple
from pathlib import Path
import fileinput
import logging
import hashlib
import shutil
from urllib.request import urlopen

logger = logging.getLogger(__name__)


class FlatLaf:
    theme: str = "com.formdev.flatlaf.intellijthemes.FlatDraculaIJTheme"

    def __init__(self, ghidra_path: Path, version="2.5"):
        self.version = version
        self.ghidra_path = ghidra_path
        self.launch_properties_path = self.ghidra_path / "support" / "launch.properties"

    def get_paths(self) -> Tuple[Path, Path]:
        return (
            self.ghidra_path / "Ghidra" / "patch" / f"flatlaf-{self.version}.jar",
            self.ghidra_path
            / "Ghidra"
            / "patch"
            / f"flatlaf-intellij-themes-{self.version}.jar",
        )

    def get_urls(self) -> Tuple[str, str]:
        return (
            f"https://repo1.maven.org/maven2/com/formdev/flatlaf/{self.version}/"
            f"flatlaf-{self.version}.jar",
            f"https://repo1.maven.org/maven2/com/formdev/flatlaf-intellij-themes/"
            f"{self.version}/flatlaf-intellij-themes-{self.version}.jar",
        )

    def verify_jars(self) -> bool:
        (flatlaf_path, themes_path) = self.get_paths()
        (flatlaf_hash_url, themes_hash_url) = self.get_urls()
        flatlaf_hash_url += ".sha512"
        themes_hash_url += ".sha512"

        logger.debug("Checking retrieved files")
        with urlopen(flatlaf_hash_url) as response:
            logger.debug("Checking FlatLAF hash")
            flatlaf_hash_data: str = response.read().decode("utf-8")
            with open(flatlaf_path, "rb") as flatlaf_jar:
                flatlaf_hash = hashlib.sha512()
                while jar_chunk := flatlaf_jar.read(8192):
                    flatlaf_hash.update(jar_chunk)
                hex_hash = flatlaf_hash.hexdigest()
                if hex_hash != flatlaf_hash_data:
                    logger.warning("FlatLAF jar has the wrong hash!")
                    return False
                else:
                    logger.debug(f"\tHash valid: {hex_hash}")

        with urlopen(themes_hash_url) as response:
            logger.debug("Checking themes hash")
            themes_hash_data: str = response.read().decode("utf-8")
            with open(themes_path, "rb") as themes_jar:
                themes_hash = hashlib.sha512()
                while jar_chunk := themes_jar.read(8192):
                    themes_hash.update(jar_chunk)
                hex_hash = themes_hash.hexdigest()
                if hex_hash != themes_hash_data:
                    logger.warning("FlatLAF themes jar has the wrong hash!")
                    return False
                else:
                    logger.debug(f"\tHash valid: {hex_hash}")

        return True

    def install(self):
        """Download (if necessary) and install FlatLaf."""

        (flatlaf_path, themes_path) = self.get_paths()
        (flatlaf_url, themes_url) = self.get_urls()

        # Download the FlatLaf jar
        if not os.path.exists(flatlaf_path):
            logger.debug("Downloading FlatLaf")
            with urlopen(flatlaf_url) as connection:
                with open(flatlaf_path, "wb") as fp:
                    shutil.copyfileobj(connection, fp)
        else:
            logger.debug("Flatlaf already downloaded: %s", flatlaf_path)

        # Download the FlatLaf tar jar
        if not os.path.exists(themes_path):
            logger.debug("Downloading FlatLaf themes")
            with urlopen(themes_url) as connection:
                with open(themes_path, "wb") as fp:
                    shutil.copyfileobj(connection, fp)
        else:
            logger.debug("Flatlaf themes already downloaded: %s", themes_path)

        assert self.verify_jars()

        # Check if FlatLaf is the system L&f
        flatlaf_set: bool = False
        with fileinput.FileInput(
            self.launch_properties_path, inplace=True, backup=".bak", mode="r"
        ) as input:
            for line in input:
                if "flatlaf" not in line:
                    print(line, end="")
                else:
                    split_line = line.split("=")
                    if len(split_line) == 3:
                        split_line[2] = self.theme

                    print("=".join(split_line), end="")
                    flatlaf_set = True

        # Set FlatLaf as the system L&f
        if not flatlaf_set:
            with open(self.launch_properties_path, "a") as fp:
                logger.debug("Setting FlatLaf as system L&f")
                fp.write(f"\nVMARGS=-Dswing.systemlaf={self.theme}")

    def remove(self):
        """Remove the flatlaf jar and remove it from launch files."""

        (flatlaf_path, themes_path) = self.get_paths()
        try:
            os.remove(flatlaf_path)
            logger.debug("Removed %s", flatlaf_path)
        except FileNotFoundError:
            logger.warning("FlatLAF jar not found")
        try:
            os.remove(themes_path)
            logger.debug("Removed %s", themes_path)
        except FileNotFoundError:
            logger.warning("FlatLAF Themes jar not found")

        with fileinput.FileInput(
            self.launch_properties_path, inplace=True, backup=".bak"
        ) as fp:
            for line in fp:
                write_line = True
                if "flatlaf" in line:
                    split_line = line.split("=")
                    if len(split_line) == 3:
                        write_line = False

                if write_line:
                    print(line, end="")

            logger.debug("Restored %s", self.launch_properties_path)
