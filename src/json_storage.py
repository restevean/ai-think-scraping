"""JSON storage implementation."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.abstractions import IStorage
from src.config import DATA_DIR

logger = logging.getLogger(__name__)


class JsonStorage(IStorage):
    """JSON file storage implementation."""

    def __init__(self, storage_dir: Path = DATA_DIR) -> None:
        """
        Initialize JSON storage.

        Args:
            storage_dir: Directory where JSON files will be stored
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"JSON storage initialized at: {self.storage_dir}")

    def _get_filepath(self, filename: str) -> Path:
        """Get full filepath for a given filename."""
        if not filename:
            raise ValueError("Filename cannot be empty")

        if filename.endswith(".json"):
            filepath = self.storage_dir / filename
        else:
            filepath = self.storage_dir / f"{filename}.json"

        return filepath

    def save(self, data: BaseModel, filename: str) -> str:
        """
        Save Pydantic model data to JSON file.

        Args:
            data: Pydantic model instance to save
            filename: Name of the file (with or without .json extension)

        Returns:
            Path to saved file as string

        Raises:
            IOError: If save operation fails
            ValueError: If filename is invalid
        """
        if not isinstance(data, BaseModel):
            raise ValueError("Data must be a Pydantic BaseModel instance")

        filepath = self._get_filepath(filename)

        try:
            # Convert Pydantic model to dict and serialize
            data_dict = data.model_dump(mode="json")

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Data saved to: {filepath}")
            return str(filepath)

        except IOError as e:
            logger.error(f"Failed to save file {filepath}: {str(e)}")
            raise IOError(f"Failed to save data to {filepath}: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error saving {filepath}: {str(e)}")
            raise IOError(f"Unexpected error saving {filepath}: {str(e)}") from e

    def load(self, filename: str) -> dict[str, Any]:
        """
        Load data from JSON file.

        Args:
            filename: Name of the file to load (with or without .json extension)

        Returns:
            Loaded data as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        filepath = self._get_filepath(filename)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"Data loaded from: {filepath}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {filepath}: {str(e)}")
            raise ValueError(f"Invalid JSON format in {filepath}: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error loading {filepath}: {str(e)}")
            raise ValueError(f"Unexpected error loading {filepath}: {str(e)}") from e

    def exists(self, filename: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            filename: Name of the file (with or without .json extension)

        Returns:
            True if file exists, False otherwise
        """
        filepath = self._get_filepath(filename)
        exists = filepath.exists()

        if exists:
            logger.debug(f"File exists: {filepath}")
        else:
            logger.debug(f"File does not exist: {filepath}")

        return exists

    def delete(self, filename: str) -> None:
        """
        Delete a file from storage.

        Args:
            filename: Name of the file to delete (with or without .json extension)

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = self._get_filepath(filename)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            filepath.unlink()
            logger.info(f"File deleted: {filepath}")

        except Exception as e:
            logger.error(f"Failed to delete {filepath}: {str(e)}")
            raise IOError(f"Failed to delete {filepath}: {str(e)}") from e

    def list_files(self) -> list[str]:
        """
        List all JSON files in storage directory.

        Returns:
            List of filenames (without path)
        """
        files = [f.name for f in self.storage_dir.glob("*.json")]
        logger.debug(f"Found {len(files)} JSON files in storage")
        return sorted(files)