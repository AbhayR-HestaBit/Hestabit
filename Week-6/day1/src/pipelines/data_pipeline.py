import hashlib
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.utils.logger import setup_logger
from src.pipelines.data_loader import DataLoader

logger = setup_logger("data_pipeline")


class DataPipeline:

    def __init__(self):
        self.raw_path = Path("src/data/raw")
        self.processed_path = Path("src/data/processed")
        self.models_path = Path("src/models")

        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)

    

    def clean(self, df):
        logger.info("Cleaning dataset...")

        logger.info(f"Missing before: {df.isnull().sum().sum()}")
        logger.info(f"Duplicates before: {df.duplicated().sum()}")

        df = df.drop_duplicates()

        df["extracurricular_involvement"] = \
            df["extracurricular_involvement"].fillna("None")

        df["placement_status"] = \
            df["placement_status"].map({"Placed": 1, "Not Placed": 0})

        logger.info(f"Missing after: {df.isnull().sum().sum()}")
        logger.info(
            f"Target distribution: {df['placement_status'].value_counts().to_dict()}"
        )

        imbalance_ratio = df["placement_status"].value_counts(normalize=True).to_dict()
        logger.info(f"Class imbalance ratio: {imbalance_ratio}")

        return df



    def detect_outliers(self, df):
        logger.info("Detecting outliers (IQR)...")

        num_cols = df.select_dtypes(include=np.number).columns
        total_outliers = 0

        for col in num_cols:
            if col not in ["Student_ID", "placement_status", "salary_lpa"]:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                count = len(df[
                    (df[col] < Q1 - 1.5 * IQR) |
                    (df[col] > Q3 + 1.5 * IQR)
                ])

                if count > 0:
                    logger.info(f"{col}: {count} outliers")
                    total_outliers += count

        logger.info(f"Total outliers detected: {total_outliers} (kept)")
        return df

    
    def dataset_hash(self, df):
        hash_id = hashlib.md5(
            pd.util.hash_pandas_object(df).values
        ).hexdigest()
        return hash_id

    def save_versioned_dataset(self, df):
        hash_id = self.dataset_hash(df)
        filename = f"final_{hash_id}.csv"

        output_path = self.processed_path / filename
        df.to_csv(output_path, index=False)

        logger.info(f"Saved versioned dataset: {filename}")
        return output_path

    
    def split(self, df):
        logger.info("Splitting dataset (70/15/15)...")

        X = df.select_dtypes(include=np.number).drop(
            ["Student_ID", "placement_status", "salary_lpa"],
            axis=1,
            errors="ignore"
        )
        y = df["placement_status"]

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, stratify=y, random_state=42
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
        )

        logger.info(
            f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}"
        )

        # Save splits
        pd.concat([X_train, y_train], axis=1).to_csv(
            self.processed_path / "train.csv", index=False
        )
        pd.concat([X_val, y_val], axis=1).to_csv(
            self.processed_path / "val.csv", index=False
        )
        pd.concat([X_test, y_test], axis=1).to_csv(
            self.processed_path / "test.csv", index=False
        )

        logger.info("Saved train.csv, val.csv, test.csv")

        return X_train, X_val, X_test, y_train, y_val, y_test

    

    def scale(self, X_train, X_val, X_test):
        logger.info("Scaling features (StandardScaler)...")

        scaler = StandardScaler()

        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)

        joblib.dump(scaler, self.models_path / "scaler.pkl")
        logger.info("Saved scaler.pkl")

        logger.info(
            f"Mean after scaling: {X_train_scaled.mean():.4f}"
        )
        logger.info(
            f"Std after scaling: {X_train_scaled.std():.4f}"
        )

        return X_train_scaled, X_val_scaled, X_test_scaled

    

    def run(self):
        try:
            logger.info("DATA PIPELINE STARTING")

            loader = DataLoader(self.raw_path)
            df = loader.load()

            df = self.clean(df)
            df = self.detect_outliers(df)

            self.save_versioned_dataset(df)

            X_train, X_val, X_test, y_train, y_val, y_test = self.split(df)
            self.scale(X_train, X_val, X_test)

            logger.info("DATA PIPELINE COMPLETE")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run()
