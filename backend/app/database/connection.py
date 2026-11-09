
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from ..config import settings


# Connect to the local MongoDB server.
client = MongoClient(
    settings.MONGODB_URL,
    serverSelectionTimeoutMS=3000
)

# Select INAYA's database.
database = client[settings.MONGODB_DATABASE]


def check_database_connection():
    """Check whether MongoDB is reachable."""
    try:
        client.admin.command("ping")
        return {
            "connected": True,
            "database": settings.MONGODB_DATABASE,
            "message": "MongoDB connection successful."
        }

    except PyMongoError as error:
        return {
            "connected": False,
            "database": settings.MONGODB_DATABASE,
            "message": str(error)
        }


def close_database_connection():
    """Close the MongoDB client."""
    client.close()
