"""FlatLaf package handling."""
import os
from pathlib import Path
import fileinput
import logging
from urllib.request import urlopen

logger = logging.getLogger(__name__)


class FlatLaf:
    def __init__(self, version="2.5"):
        self.version = version

    def get_path(self, install_path: Path) -> Path:
        return install_path / "Ghidra" / "patch" / f"flatlaf-{self.version}.jar"

    def get_url(self):
        return (
            f"https://repo1.maven.org/maven2/com/formdev/flatlaf/{self.version}/"
            f"flatlaf-{self.version}.jar"
        )

    def install(self, install_path: Path, version: str):
        """Download (if necessary) and install FlatLaf.

        Args:
            install_path (str): Ghidra install path.
            version (str): Current Ghidra Version.
        """
        # TODO: Refactor this duplicate code
        # version_string: str = ".".join(re.findall("[0-9]+", version))
        # version_number = tuple(map(int, (version_string.split("."))))

        flatlaf_path = self.get_path(install_path)
        flatlaf_url = self.get_url()

        # Download the FlatLaf jar
        if not os.path.exists(flatlaf_path):
            logging.debug("Downloading FlatLaf")
            with urlopen(flatlaf_url) as connection:
                with open(flatlaf_path, "wb") as fp:
                    fp.write(connection.read())
        else:
            logging.debug("Flatlaf already downloaded: %s", flatlaf_path)

        launch_properties_path = install_path / "support" / "launch.properties"

        # Check if FlatLaf is the system L&f
        flatlaf_set = False
        with open(launch_properties_path, "r") as fp:
            for line in fp:
                if "flatlaf" in line:
                    flatlaf_set = True
                    break

        # Set FlatLaf as the system L&f
        if not flatlaf_set:
            with open(launch_properties_path, "a") as fp:
                logging.debug("Setting FlatLaf as system L&f")
                fp.write(
                    "\nVMARGS=-Dswing.systemlaf=com.formdev.flatlaf.FlatDarculaLaf"
                )

    def remove(self, install_path: Path):
        """Remove the flatlaf jar and remove it from launch files.

        Args:
            install_path (str): Ghidra install path.
        """

        flatlaf_path = self.get_path(install_path)
        try:
            os.remove(flatlaf_path)
            logger.debug("Removed %s", flatlaf_path)
        except FileNotFoundError:
            logger.warning("Could not remove %s", flatlaf_path)

        launch_properties_path = install_path / "support" / "launch.properties"

        with fileinput.FileInput(launch_properties_path, inplace=True) as fp:
            for line in fp:
                if (
                    "VMARGS=-Dswing.systemlaf=com.formdev.flatlaf.FlatDarculaLaf"
                    not in line
                ):
                    print(line, end="")
                else:
                    logging.debug("Restored %s", launch_properties_path)
