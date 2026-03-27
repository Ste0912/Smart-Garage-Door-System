from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from datetime import datetime
from src.virtualization.digital_replica.schema_registry import SchemaRegistry
import os

class DatabaseService:
    def __init__(
        self, connection_string: str, db_name: str, schema_registry: SchemaRegistry
    ):
        self.connection_string = connection_string
        self.db_name = db_name
        self.schema_registry = schema_registry
        self.client = None
        self.db = None

    def connect(self) -> None:
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        return self.client is not None and self.db is not None

    def save_dr(self, collection_name: str, dr_data: Dict) -> str:
        """Save a Digital Replica"""
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        try:
            collection = self.db[collection_name]
            collection.insert_one(dr_data)
            return str(dr_data["_id"])
        except Exception as e:
            raise Exception(f"Failed to save Digital Replica: {str(e)}")

    def get_dr(self, dr_type: str, dr_id: str) -> Optional[Dict]:
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")

        try:
            collection_name = self.schema_registry.get_collection_name(dr_type)
            return self.db[collection_name].find_one({"_id": dr_id})
        except Exception as e:
            raise Exception(f"Failed to get Digital Replica: {str(e)}")

    def query_drs(self, dr_type: str, query: Dict = None) -> List[Dict]:
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")

        try:
            collection_name = self.schema_registry.get_collection_name(dr_type)
            return list(self.db[collection_name].find(query or {}))
        except Exception as e:
            raise Exception(f"Failed to query Digital Replicas: {str(e)}")

    def update_dr(self, dr_type: str, dr_id: str, update_data: Dict) -> None:
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")

        try:
            collection_name = self.schema_registry.get_collection_name(dr_type)

            # Let SchemaRegistry handle validation through MongoDB schema
            result = self.db[collection_name].update_one(
                {"_id": dr_id}, {"$set": update_data}
            )

            if result.matched_count == 0:
                raise ValueError(f"Digital Replica not found: {dr_id}")

        except Exception as e:
            raise Exception(f"Failed to update Digital Replica: {str(e)}")

    def delete_dr(self, collection_name: str, dr_id: str) -> None:
        if not self.is_connected():
            raise ConnectionError("Not connected to MongoDB")
        try:
            self.db[collection_name].delete_one({"_id": dr_id})
        except Exception as e:
            raise Exception(f"Failed to delete Digital Replica: {str(e)}")
