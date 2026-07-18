from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StorageManager:
    """
    Handles every file read/write operation in VERO.

    Nothing else in the project should ever touch JSON files directly.
    """

    def __init__(self, base_path: str = "vero/data"):

        self.base = Path(base_path)

        self.raw = self.base / "raw"
        self.profiles = self.base / "profiles"
        self.analysis = self.base / "analysis"

        for folder in (
            self.raw,
            self.profiles,
            self.analysis,
        ):
            folder.mkdir(parents=True, exist_ok=True)

    # -------------------------------
    # Helpers
    # -------------------------------

    def slug(self, company: str) -> str:
        return (
            company.lower()
            .replace(" ", "_")
            .replace("/", "_")
        )

    def company_folder(self, company: str) -> Path:

        folder = self.raw / self.slug(company)

        folder.mkdir(parents=True, exist_ok=True)

        return folder

    def write_json(self, path: Path, data: dict):

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

    def read_json(self, path: Path):

        if not path.exists():
            return None

        with open(path, encoding="utf8") as f:
            return json.load(f)

    # -------------------------------
    # Raw Evidence
    # -------------------------------

    def save_raw(
        self,
        company: str,
        source: str,
        data: dict,
        source_url: str | None = None,
    ):

        folder = self.company_folder(company)

        path = folder / f"{source}.json"

        self.write_json(path, data)

        metadata = {
            "company": company,
            "source": source,
            "source_url": source_url,
            "collected_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "hash": hashlib.sha256(
                json.dumps(
                    data,
                    sort_keys=True
                ).encode()
            ).hexdigest(),
        }

        self.write_json(
            folder / f"{source}_metadata.json",
            metadata,
        )

        return path

    def load_raw(
        self,
        company: str,
        source: str,
    ):

        folder = self.company_folder(company)

        return self.read_json(
            folder / f"{source}.json"
        )

    # -------------------------------
    # Profiles
    # -------------------------------

    def save_profile(
        self,
        company: str,
        profile: dict,
    ):

        path = (
            self.profiles
            / f"{self.slug(company)}_profile.json"
        )

        self.write_json(path, profile)

        return path

    def load_profile(
        self,
        company: str,
    ):

        return self.read_json(
            self.profiles
            / f"{self.slug(company)}_profile.json"
        )

    # -------------------------------
    # AI Analysis
    # -------------------------------

    def save_analysis(
        self,
        company: str,
        analysis: dict,
    ):

        path = (
            self.analysis
            / f"{self.slug(company)}_analysis.json"
        )

        self.write_json(path, analysis)

        return path

    def load_analysis(
        self,
        company: str,
    ):

        return self.read_json(
            self.analysis
            / f"{self.slug(company)}_analysis.json"
        )

    # -------------------------------
    # Utility
    # -------------------------------

    def analysis_exists(
        self,
        company: str,
    ) -> bool:

        return (
            self.analysis
            / f"{self.slug(company)}_analysis.json"
        ).exists()