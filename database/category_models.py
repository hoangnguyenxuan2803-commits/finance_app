# MỤC ĐÍCH CỦA category_models.py: Xử lý toàn bộ CRUD (Create, Read, Update, Delete) cho Category
# backend cho các nút: Add Category, Get Category, Delete Category, Update Category trên App
from database.database_manager import DatabaseManager
from database.transaction_models import TransactionModel
import config
from datetime import datetime
from typing import Optional, Tuple, Union
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
        # 🔒 TEMPORARY DISABLED - Uncomment to enable auto-init
        return  # ← Thêm dòng này để tắt auto-init
        
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

    def delete_category_safe(self,
                            transaction_model: TransactionModel,
                            category_type: str,
                            category_name: str,
                            strategy = "block",
                            reassign_to = None):
        """
        strategy: 'block' | 'cascade' | 'reassign'
        """
        try:
            affected = transaction_model.count_transactions_by_category(category_name)
            if affected > 0:
                if strategy == "block":
                    return {
                        "success": False,
                        "affected": affected,
                        "message": f"{affected} transactions will be affected"
                    }
                elif strategy == "cascade":
                    transaction_model.delete_transactions_by_category(category_name)
            
                elif strategy == "reassign":
                    if not reassign_to:
                        return {
                            "success": False,
                            "affected": affected,
                            "message": "Reassign category required"
                            }
                    transaction_model.reassign_category(category_name, reassign_to)
                else:
                    return{
                        "success": False,
                        "affected": affected,
                        "message": f"Invalid strategy: {strategy}"
                    }
            
                # Delete category
            self.collection.delete_one({
                "type": category_type,
                "name": category_name,
                "user_id": self.user_id
                })
            return {
                "success": True,
                "affected": affected,
                "message": "Category deleted successfully"
                }
        except Exception as e:
            return {
                "success": False,
                "affected": 0,
                "message": f"Error : {str(e)}"
            }

    def get_categories_by_type(self, category_type: str):
        # return list(self.collection.find({
        #     "type": category_type,
        #     "user_id": self.user_id
        #     }).sort("created_at", -1))  # add user_id condition
        #  🔍 DEBUG
        print(f"🔍 get_categories_by_type called:")
        print(f"   - user_id: {self.user_id}")
        print(f"   - category_type: {category_type}")
        
        query = {
            "type": category_type, 
            "user_id": self.user_id
        }
        print(f"   - query: {query}")
        
        result = list(self.collection.find(query).sort("created_at", -1))
        print(f"   - found: {len(result)} categories")
        
        return result
    
    def get_all_categories(self):
        """
        Get all categories of current user
        Returns:
            List of category documents
        """
        if not self.user_id:
            return []
        
        return list(
            self.collection.find({
                "user_id": self.user_id
                }).sort("created_at", -1))
    
    def get_total(self):
        result = self.collection.find({"user_id": self.user_id})
        result = list(result)
        return result  
    
    def update_category(self,
                        transaction_model: TransactionModel,
                        category_type: str,
                        old_name: str,
                        new_name: str,
                        new_type: Optional[str] = None):
        # 🚫 Không làm gì nếu tên không đổi
        if old_name == new_name and (new_type is None or new_type == category_type):
            return {
                "success": False,
                "message": "No changes detected"
                }
        # Validation: duplicate name
        current = self.collection.find_one({
            "name": old_name,
            "type": category_type,
            "user_id": self.user_id
            })
        if not current:
            return{
                "success": False,
                "message": f"Category'{old_name}' not found"
            }
        target_type = new_type or category_type
        # 3️⃣ Check trùng tên (LOẠI TRỪ CHÍNH NÓ)
        duplicate = self.collection.find_one({
            "name": new_name,
            "type": target_type,
            "user_id": self.user_id,
            "_id": {"$ne": current["_id"]}
        })
        if duplicate:
            return{
                "success": False,
                "message": "Category name already exists"
            }
        # Check transactions
        tx_count = transaction_model.count_transactions_by_category(old_name)

        #handel type change
        if new_type and new_type != category_type and tx_count > 0:
            return {
                "success": False,
                "message": f"Cannot change category type while {tx_count} transactions exist"
            }

        #update category
        result = self.collection.update_one(
            {"_id": current["_id"]},
            {
                "$set": {
                    "name": new_name,
                    "type": target_type,
                    "last_modified": datetime.now()
                    }
                }
            )
        if result.matched_count == 0:
            return {
                "success": False,
                "message": "Update failed"
            }
        # Update transactions if the name changes
        updated = 0
        if old_name != new_name:
            updated =transaction_model.reassign_category(old_name, new_name)
            
        return {
            "success": True,
            "message": f"Category updated. {updated} transaction(s) updated.",
            "updated_transactions": updated
        }
    def delete_category(self,
                        category_id: str,
                        strategy: str,
                        transaction_model,
                        reassign_to_id: Optional[str] = None):
        """
        strategy: 'block' | 'reassign' | 'cascade'
        """
        try:
            cat_obj_id = ObjectId(category_id)
        except:
            return False, 0, "Invalid category ID"

        # 1. Load category
        category = self.collection.find_one({
            "_id": cat_obj_id,
            "user_id": self.user_id
        })
        if not category:
            return False, 0, "Category not found"

        cat_name = category["name"]

        # 2. Count affected transactions (MongoDB)
        affected = transaction_model.collection.count_documents({
            "category": cat_name,
            "user_id": self.user_id
        })

        # 3. Strategy handling
        if affected > 0:
            if strategy == "block":
                return False, affected, "Deletion blocked: transactions exist"

            if strategy == "reassign":
                if not reassign_to_id:
                    return False, affected, "Reassign target required"

                target = self.collection.find_one({
                    "_id": ObjectId(reassign_to_id),
                    "user_id": self.user_id
                })
                if not target:
                    return False, affected, "Target category not found"

                # Reassign transactions
                transaction_model.collection.update_many(
                    {"category": cat_name, "user_id": self.user_id},
                    {"$set": {"category": target["name"]}}
                )

            elif strategy == "cascade":
                transaction_model.collection.delete_many({
                    "category": cat_name,
                    "user_id": self.user_id
                })

        # 4. Delete category
        self.collection.delete_one({
            "_id": cat_obj_id,
            "user_id": self.user_id
        })
        return True, affected, f"Deleted category '{cat_name}', affected {affected} transactions"
    
# if __name__ == "__main__":
#     print("Init cate collection")
#     cate = CategoryModel()

#     item = {
#         "type": "Expense",
#         "name": "Rent"
#     }

#     result = cate.add_category(category_type = "Expense", category_name="Rent")
# if __name__== "__main__":
#     print("Init category collection")
#     cate = CategoryModel()
# gán cate chỉ dùng khi test file 1 mình, cate là 1 object (instance) của class CategoryModel, để xem class có lỗi hay không
# gán cate để dễ debug (có thể mở Python REPL hay debug và kiểm tra) -> ví dụ lấy cate print(cate.collection) để kiểm tra