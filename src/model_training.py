from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

from logger import get_logger

logger = get_logger(__name__)


class ModelTraining:
    def __init__(self, config):
        self.model_training_config = config["model_training"]
        artifact_dir = Path(config["data_ingestion"]["artifact_dir"])
        self.processed_dir = artifact_dir / "processed"
        self.model_output_dir = artifact_dir / "models"
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Model training process started...")

    def run(self):
        train_data, val_data = self.load_data()
        model = self.create_model()
        self.train_model(model, train_data)
        self.evaluate_model(model, val_data)
        logger.info("Model training ended successfully!")

    def load_data(self):
        train_data_dir = self.processed_dir / "train.csv"
        val_data_dir = self.processed_dir / "validation.csv"
        train_data = pd.read_csv(train_data_dir)
        val_data = pd.read_csv(val_data_dir)

        return train_data, val_data

    def create_model(self):
        n_estimators = self.model_training_config["n_estimators"]
        max_samples = self.model_training_config["max_samples"]
        n_jobs = self.model_training_config["n_jobs"]

        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_samples=max_samples,
            n_jobs=n_jobs,
            oob_score=root_mean_squared_error,
        )
        logger.info(f"n_estimators: {n_estimators}, max_samples: {max_samples}")
        return model

    def train_model(self, model: RandomForestRegressor, train_data: pd.DataFrame):
        X_train, y_train = train_data.drop(columns=["demand"]), train_data["demand"]
        model.fit(X_train, y_train)
        logger.info("Model is trained successfully.")

    def evaluate_model(self, model: RandomForestRegressor, val_data: pd.DataFrame):
        X_val, y_val = val_data.drop(columns=["demand"]), val_data["demand"]
        y_pred = model.predict(X_val)
        self.rmse = root_mean_squared_error(y_val, y_pred)
        self.oob_score = model.oob_score_

        logger.info(f"Out-of-Bag Score: {self.oob_score}")
        logger.info(f"Root Mean Squared Error for validation data: {self.rmse}")
