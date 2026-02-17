import os
import certifi
from pymongo import MongoClient

def cleanup_indexes():
    uri = os.environ.get('DATABASE_URL', 'mongodb://root:example@192.168.1.134:27017/')
    print(f"Connecting to: {uri.split('@')[-1]}") # Hide credentials
    
    tls_ca_file = certifi.where() if 'mongodb+srv' in uri else None
    
    try:
        client = MongoClient(uri, tlsCAFile=tls_ca_file)
        db = client['garden_db']
        collection = db['core_machine']
        
        print("Listing current indexes for 'core_machine':")
        for index in collection.list_indexes():
            print(f"- {index['name']}")
            
        print("\nChecking for any index that includes 'serial' field...")
        for index in collection.list_indexes():
            if 'serial' in index['key'] and index['name'] != '_id_':
                print(f"Dropping index: {index['name']} (Key: {index['key']})")
                try:
                    collection.drop_index(index['name'])
                    print(f"Successfully dropped {index['name']}")
                except Exception as e:
                    print(f"Error dropping {index['name']}: {e}")
                    
        print("\nCleanup finished. You can now run migrations.")
            
    except Exception as e:
        print(f"Critical error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_indexes()
