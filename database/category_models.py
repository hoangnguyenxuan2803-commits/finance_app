# MỤC ĐÍCH CỦA category_models.py: Xử lý toàn bộ CRUD (Create, Read, Update, Delete) cho Category
# backend cho các nút: Add Category, Get Category, Delete Category, Update Category trên App
from database.database_manager import DatabaseManager
import config
from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId

collection_name = config.COLLECTIONS['category']

class CategoryModel:
    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(collection_name=collection_name)

        # init:
        self.user_id = user_id

    def set_user_id(self, user_id: str):
        self.user_id = ObjectId(user_id) if user_id is not None else None

        # after we have user_id, initialize their default categories
        self._initialize_user_default_categories()

    def _initialize_user_default_categories(self):
        """Initialize user categories if they dont exist"""

        # Check if there is user_id, exist earlier
        if not self.user_id:
            return
        
        # EXPENSE
        for cate in config.DEFAULT_CATEGORIES_EXPENSE:
            # # calling by params order
            # self.upsert_category("Expense", cate)

            # calling by params keywords
            self.upsert_category(category_type = "Expense", category_name= cate)

        # INCOME
        for cate in config.DEFAULT_CATEGORIES_INCOME:
            self.upsert_category(category_type = "Income", category_name = cate)

    def upsert_category(self, category_type: str, category_name: str):

        # define filter
        filter_ = {
            "type": category_type,
            "name": category_name,
            "user_id": self.user_id
        }

        # define update_doc
        update_doc = {
            "$set": {
                "last_modified": datetime.now()
            },
            "$setOnInsert": {
                "created_at": datetime.now()
            } 
        }

        result = self.collection.update_one(
            filter_,
            update_doc,
            upsert=True
        )
        return result.upserted_id

    def delete_category(self, category_type: str, category_name: str):
        result = self.collection.delete_one({"type": category_type, "name": category_name, "user_id": self.user_id}) # add user_id condition
        return result.deleted_count

    def get_categories_by_type(self, category_type: str):
        return list(self.collection.find({"type": category_type, "user_id": self.user_id}).sort("created_at", -1))  # add user_id condition
    
    def get_total(self):
        result = self.collection.find({"user_id": self.user_id})
        result = list(result)
        return result

# if __name__ == "__main__":
#     print("Init cate collection")
#     cate = CategoryModel()

#     item = {
#         "type": "Expense",
#         "name": "Rent"
#     }

#     result = cate.add_category(category_type = "Expense", category_name="Rent")
'''
if __name__== "__main__":
    print("Init category collection")
    cate = CategoryModel() 
    # gán cate chỉ dùng khi test file 1 mình, cate là 1 object (instance) của class CategoryModel, để xem class có lỗi hay không
    # gán cate để dễ debug (có thể mở Python REPL hay debug và kiểm tra) -> ví dụ lấy cate print(cate.collection) để kiểm tra
'''
