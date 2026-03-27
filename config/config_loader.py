import yaml, os
from typing import Dict

class ConfigLoader:
    @staticmethod
    def load_database_config(config_path) -> Dict:
        """Load database configuration from YAML file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        else:
            print(f"Configuration file found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        if not config or "database" not in config:
            raise ValueError("Invalid configuration file: missing database section")

        return config["database"]

    @staticmethod
    def build_connection_string(config: Dict) -> str:
        """Build MongoDB connection string from configuration"""
        conn = config["connection"]
        host = conn["host"]
        port = conn["port"]

        # Build authentication part if credentials are provided
        auth = ""
        if conn.get("username") and conn.get("password"):
            auth = f"{conn['username']}:{conn['password']}@"

        return f"mongodb://{auth}{host}:{port}"
