from database.database_manager import DatabaseManager
from datetime import datetime
import config
from bson.objectid import ObjectId

collection_name = config.COLLECTIONS['user'] # Lay ten collection tu config

# Class xử lý CRUD cho CategoryModel
class UserModel:

    # Tạo instance DatabaseManager (singleton → 1 kết nối duy nhất)
    def __init__(self):
        self.db_manager = DatabaseManager() # tạo instance DatabaseManager (instance = 1 đối tượng của Class)
        self.collection = self.db_manager.get_collection(collection_name=collection_name) # lấy collection từ DatabaseManager
    def create_user(self, email: str)-> str:
        """Create new user"""
        user = {
            "email": email,
            "created_at": datetime.now(),
            "last_modified": datetime.now(),
            "is_active": True
        }
        result = self.collection.insert_one(user)
        return str(result.inserted_id)
    
    def login(self, email:str) -> str:
        # check user exist (User find_one)
        user = self.collection.find_one({'email':email})

        #case 1: user not exit:
        #create: call create_user(email)
        if not user:
            return self.create_user(email)
        
        #case 2: user exist but deactive
        #raise Error
        if user.get("is_active") is not True:
            raise ValueError("This account is deactivated! Please connect to CS")
        
        #all check passed
        return str(user.get("_id"))
    
    def deactivated(self, user_id: str) -> bool:
        # find and update:
        user = self.collection.find_one({
            '_id':ObjectId(user_id),
            'is_active':True
            })
        #case not exit user
        if not user:
            raise ValueError("User not found")
        
        #user is validate and ready to deactivate -> update them
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )
        return result.modified_count> 0 
        