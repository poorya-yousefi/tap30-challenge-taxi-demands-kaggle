from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

from src.logger import get_logger

logger = get_logger(__name__)

"""
This module is responsible for training the model using the processed data.
It includes loading the data, creating the model, training it,
evaluating its performance, and saving the trained model.
The model used is a Random Forest Regressor.
"""


class ModelTraining:
    def __init__(self, config):
        self.model_training_config = config["model_training"]
        artifact_dir = Path(config["data_ingestion"]["artifact_dir"])
        self.processed_dir = artifact_dir / "processed"
        self.model_output_dir = artifact_dir / "models"
        self.model_output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        logger.info("Model training process started...")
        logger.info("mlflow operation started.")

        mlflow.set_experiment("tap30-challenge-taxi-demands")
        with mlflow.start_run():
            mlflow.set_tag("model_type", "RandomForestRegressor")

            train_data, val_data = self.load_data()
            mlflow.log_artifact(self.train_data_path, "datasets")
            mlflow.log_artifact(self.val_data_path, "datasets")

            model = self.create_model()
            self.train_model(model, train_data)
            self.evaluate_model(model, val_data)
            mlflow.log_metric("oob_score", self.oob_score)
            mlflow.log_metric("rmse", self.rmse)

            self.save_model(model)

            mlflow.log_artifact(self.model_output_path, "models")

            params = model.get_params()
            mlflow.log_params(params)

            logger.info("mlflow operation ended successfully.")
            logger.info("Model training ended successfully!")

    def load_data(self):
        self.train_data_path = self.processed_dir / "train.csv"
        self.val_data_path = self.processed_dir / "validation.csv"
        train_data = pd.read_csv(self.train_data_path)
        val_data = pd.read_csv(self.val_data_path)

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

    def save_model(self, model):
        self.model_output_path = self.model_output_dir / "rf.joblib"
        joblib.dump(model, self.model_output_path, compress=("gzip", 3))
