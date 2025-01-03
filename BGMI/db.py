from pymongo import MongoClient

# MongoDB connection setup
MONGO_URI = "mongodb+srv://sufyan532011:2011@cluster0.rhff7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["Testing"]
users_col = db["users"]
group_col = db["groups"]
active_games_col = db["games"]

MONGO_URI = "mongodb+srv://sufyan532011:2011@cluster0.rhff7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
try:
    client = MongoClient(MONGO_URI)
    client.server_info()  # This will raise an error if the connection fails
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
