import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
from pathlib import Path
from src.utils.logger import setup_logger

logger = setup_logger("data_loader")


class DataLoader:
    def __init__(self, raw_path: str):
        self.raw_path = Path(raw_path)

    def load(self):
        logger.info("Loading raw datasets...")

        students_path = self.raw_path / "indian_engineering_student_placement.csv"
        placement_path = self.raw_path / "placement_targets.csv"

        if not students_path.exists():
            logger.error(f"File not found: {students_path}")
            raise FileNotFoundError(f"Missing: {students_path}")

        if not placement_path.exists():
            logger.error(f"File not found: {placement_path}")
            raise FileNotFoundError(f"Missing: {placement_path}")

        students = pd.read_csv(students_path)
        placement = pd.read_csv(placement_path)

        logger.info(f"Students: {students.shape}")
        logger.info(f"Placement: {placement.shape}")

        df = students.merge(placement, on="Student_ID")
        logger.info(f"Merged shape: {df.shape}")

        return df