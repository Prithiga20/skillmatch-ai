from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/skillmatch"))
db = client.get_default_database()

users_col = db["users"]
resumes_col = db["resumes"]
jobs_col = db["jobs"]
applications_col = db["applications"]

# Indexes
users_col.create_index("email", unique=True)
applications_col.create_index([("user_id", 1), ("job_id", 1)], unique=True)


def str_id(doc):
    """Convert ObjectId _id to string id in a document."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc
