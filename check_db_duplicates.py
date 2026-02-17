import os
from pymongo import MongoClient

def check_db():
    uri = os.environ.get('DATABASE_URL', 'mongodb://root:example@192.168.1.134:27017/')
    client = MongoClient(uri)
    db = client['garden_db']
    collection = db['core_machine']
    
    print("Checking indexes...")
    for index in collection.list_indexes():
        print(index)
        
    print("\nChecking for duplicate serials...")
    pipeline = [
        {"$group": {"_id": "$serial", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(collection.aggregate(pipeline))
    if duplicates:
        print(f"Found {len(duplicates)} serials with duplicates:")
        for dup in duplicates:
            print(f"Serial: {dup['_id']}, Count: {dup['count']}")
    else:
        print("No duplicate serials found.")

if __name__ == "__main__":
    check_db()
