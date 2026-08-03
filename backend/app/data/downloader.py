# ==============================================================================
# MindShield Backend — Dataset Downloader Engine
# Phase 3.1: Dataset-Agnostic Downloader & Offline Fallback
# ==============================================================================

import logging
import os
import urllib.request
import zipfile
from pathlib import Path

from app.data.config import DatasetConfig

logger = logging.getLogger(__name__)

# Sample mock dataset used strictly for offline fallback / isolated unit runs
MOCK_UCI_SAMPLE = (
    "ham\tGo until jurong point, crazy.. Available only in bugis n great world...\n"
    "ham\tOk lar... Joking wif u oni...\n"
    "spam\tFree entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005...\n"
    "ham\tU dun say so early hor... U c already then say...\n"
    "ham\tNah I don't think he goes to usf, he lives around here though\n"
    "spam\tFreeMsg Hey there darling it's been 3 week's now and no word back!\n"
    "ham\tEven my brother is not like to speak with me.\n"
    "ham\tAs per your request 'Melle Melle' has been set as your callertune...\n"
    "spam\tWINNER!! As a valued network customer you have been selected...\n"
    "spam\tHad your mobile 11 months or more? U R entitled to Update...\n"
)


class DatasetDownloader:
    """Generic dataset download and extraction manager.

    Downloads dataset archives from configured URLs, extracts contents, handles
    retries, and provides offline fallback capabilities.
    """

    def __init__(self, config: DatasetConfig, data_raw_dir: Path):
        """Initialize the downloader with dataset configuration and path.

        Args:
            config: DatasetConfig instance.
            data_raw_dir: Path to raw data storage directory.
        """
        self.config = config
        self.raw_dir = Path(data_raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.target_filepath = self.raw_dir / self.config.raw_filename
        self.archive_filepath = self.raw_dir / self.config.archive_filename

    def download_and_extract(self, force: bool = False) -> Path:
        """Download raw archive and extract target dataset file.

        Args:
            force: If True, forces redownload even if target file exists.

        Returns:
            Path: Path to the extracted raw dataset file.
        """
        if self.target_filepath.exists() and not force:
            logger.info(
                f"Raw dataset file already present at: {self.target_filepath}"
            )
            return self.target_filepath

        if not self.config.download_url:
            logger.warning(
                f"No download URL configured for '{self.config.dataset_name}'."
            )
            return self._generate_offline_fallback()

        try:
            logger.info(
                f"Downloading {self.config.dataset_name} "
                f"from {self.config.download_url}..."
            )
            req = urllib.request.Request(
                self.config.download_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "MindShield/1.0"
                    )
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp, open(
                self.archive_filepath, "wb"
            ) as out_file:
                out_file.write(resp.read())

            logger.info(
                f"Successfully downloaded archive to {self.archive_filepath}"
            )

            if self.config.archive_filename.endswith(".zip"):
                logger.info(f"Extracting zip archive: {self.archive_filepath}")
                with zipfile.ZipFile(self.archive_filepath, "r") as zip_ref:
                    zip_ref.extractall(self.raw_dir)
                logger.info(
                    f"Successfully extracted dataset: {self.target_filepath}"
                )
            else:
                if self.archive_filepath != self.target_filepath:
                    os.rename(self.archive_filepath, self.target_filepath)

        except Exception as err:
            logger.error(
                f"Network download failed for {self.config.dataset_name}: {err}. "
                "Engaging offline fallback dataset creation."
            )
            return self._generate_offline_fallback()

        if not self.target_filepath.exists():
            possible_matches = list(self.raw_dir.glob("*SMSSpamCollection*"))
            if possible_matches:
                self.target_filepath = possible_matches[0]
                logger.info(
                    f"Resolved extracted file match: {self.target_filepath}"
                )
            else:
                logger.warning(
                    f"Extracted target file {self.config.raw_filename} "
                    "not found after download. Engaging fallback."
                )
                return self._generate_offline_fallback()

        return self.target_filepath

    def _generate_offline_fallback(self) -> Path:
        """Generate offline mock dataset file for fallback testing."""
        logger.info(
            f"Generating offline mock dataset at: {self.target_filepath}"
        )
        with open(self.target_filepath, "w", encoding=self.config.encoding) as f:
            f.write(MOCK_UCI_SAMPLE)
        return self.target_filepath
