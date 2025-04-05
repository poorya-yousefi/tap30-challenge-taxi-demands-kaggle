from config_reader import read_config
from data_ingestion import DataIngestion

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_config("config/config.yaml"))
    data_ingestion.run()
