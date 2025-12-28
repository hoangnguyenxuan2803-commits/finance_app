# for pip: pip instal bson
# for uv: uv add bson

from database.database_manager import DatabaseManager
from pymongo import DESCENDING, ASCENDING
from utils import handler_datetime 
import config
from datetime import datetime, date
from typing import Optional, Any, Union
from bson.objectid import ObjectId

class TransactionModel:

    def __init__(self, user_id: Optional[str]= None):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(config.COLLECTIONS["transaction"])
        self.user_id= user_id
    def set_user_id(self, user_id: Optional[str]):
        """Set or clear the current user id used to scope queries"""
        self.user_id = ObjectId(user_id) if user_id is not None else None

    def get_transaction(
            self,
            advanced_filters:dict[str, any] = None
            ) -> list[dict]:
        #build query filter
        query = self._build_query(advanced_filters)
        print("Transaction.get_transaction - query:", query)

        #Fetch transaction, sort from newest to oldest
        cursor = self.collection.find(query).sort("created_at", -1)
        return list(cursor)
    
    def _build_query(self, advanced_filter: Optional[dict]) -> dict:
        conditions = []
        if not advanced_filter:
            return self._add_user_constraint(conditions)

        # Check transaction_type
        if "transaction_type" in advanced_filter:
            conditions.append({"transaction_type": advanced_filter.get("transaction_type")})

        # Check category
        if "category" in advanced_filter:
            conditions.append({"category": advanced_filter.get("category")})

        # Check amount
        min_amount = advanced_filter.get("min_amount")
        max_amount = advanced_filter.get("max_amount")
        if min_amount or max_amount:
            amount ={}
            if min_amount is not None:
                amount['$gte']= min_amount #$gte = greater than or equal
            if max_amount is not None:
                amount['$lte'] = max_amount #$lte = less than or equal

            conditions.append({"amount": amount})

        # Check transaction_date
        start_date = advanced_filter.get("start_date")
        end_date = advanced_filter.get("end_date")
        if start_date or end_date:
            date_query = {}
            if start_date is not None:
                date_query['$gte']= handler_datetime(start_date) #$gte = greater than or equal
            if end_date is not None:
                date_query['$lte'] = handler_datetime(end_date) #$lte = less than or equal
            conditions.append({"transaction_date": date_query})
        
        # Check description
        if "search_text" in advanced_filter:
            conditions.append({
                "description": {
                    "$regex": advanced_filter.get("search_text"),
                    "$options": "i" # case-insensitive
                }
            })
        return self._add_user_constraint(conditions)

    def _add_user_constraint(self, conditions: list) -> list:
        # conditions.append({
        #     "user_id": ObjectId(self.user_id) if self.user_id else None
        # })
        # return {
        #     "$and": conditions
        # }
        if self.user_id:
            conditions.append({"user_id": self.user_id})

        if conditions:
            return {"$and": conditions}

        return {}
    
    def add_transaction(self,
                            transaction_type: str,
                            category: str,
                            amount: float,
                            transaction_date: datetime,
                            description: str = "")-> Optional[str]:
        
        """
        Add a new transaction with automatic last_modified timestamp

        Args:
            transaction_type: "Expense" or "Income"
            category: Category name
            amount: Transaction amount
            transaction_date: Transaction datet
            description: Optional description
        Returns:
            Inserted document ID as string, or None if failed
        """
        if not isinstance(transaction_date, datetime):
            transaction_date= handeler_datetime(transaction_date)

        # 2. Create transaction object
        transaction = {
            "transaction_type": transaction_type,
            "category": category,
            "amount": amount,
            "transaction_date": handler_datetime(transaction_date),
            "description": description,
            "created_at": datetime.now(),
            "last_modified": datetime.now(),
            "user_id": self.user_id ## add user_id field
            }
        try:
            result = self.collection.insert_one(transaction)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Failed to add transaction: {transaction}, error {e}")
            return None


    def update_transaction(self, transaction_id: str, data: dict) -> bool:
        try:
            data['last_modified'] = datetime.now()
            filter_ = {
                '_id': ObjectId(transaction_id),
                'user_id': self.user_id
            }
            result = self.collection.update_one(filter_, {'$set': data})
            return result.modified_count > 0
        except Exception as e:
            print(f"Failed to update transaction: {transaction_id}, error {e}")
            return False

    
    # delete transaction
    def delete_transaction(self,
                           transaction_id: str)-> bool:
        """
        Delete a transaction
        Args:
            transaction_id: Transaction ID
        Returns:
            True if delete successfully, False otherwise
        """
        try:
            filter_={'_id': ObjectId(transaction_id),
                     'user_id': self.user_id} # added user_id constraint
            
            result = self.collection.delete_one(filter_)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Failed to delete transaction: {transaction_id}, error {e}")
            return False
    
    #get transaction
    def get_transaction_by_id(self,transaction_id: Union[str, ObjectId]):
        """
        Get a single transaction by ID.
        Args:
            transaction_id: Transaction ID
        Returns:
            Transaction document or None
        """
        print("DEBUG — called get_transaction_by_id with:", transaction_id)

        try:
            obj_id = ObjectId(transaction_id)
            print("DEBUG — Converted ObjectId:", obj_id)
        except Exception as e:
            print("DEBUG — FAILED converting ObjectId:", e)
            return None
        
        filter_ = {
            "_id": obj_id,
            "user_id": self.user_id
        }

        print("DEBUG — Final filter:", filter_)

        result = self.collection.find_one(filter_)
        print("DEBUG — Query result:", result)

        return result
    def get_transaction_by_date_range(self,
                                      start_date: Union[datetime,date,str],
                                      end_date:Union[datetime,date,str]
                                      )-> list[dict]:
        """
        Legacy method: Get transactions in date range
        Args:
            start_date: Start date
            end_date: End date
        Returns:
            List of transaction documents
        
        """
        return self.get_transaction(
            advanced_filters={
                "start_date": start_date,
                "end_date": end_date       
            }
        )
    def count_transaction_by_category_id(self, category_id: Union[str, ObjectId]) -> int:
        """Count transactions that reference the given category ID (and belong to current user)"""
        try:
            cat_obj= ObjectId(category_id)
        except Exception:
            # invalid id -> zero affected
            return 0
        filter = {"category_id": cat_obj}
        if self.user_id:
            filter["user_id"] = self.user_id
        return self.collection.count_documents(filter)
    def reassign_transactions_category(self, old_catetogy_id: Union[str, ObjectId], new_category_id: Union[str, ObjectId], new_category_name: Optional[str] = None) -> int:
        """
        Reassign transactions that reference old_category_id to new_category_id
        Update both category_id and category (name) fields automically via update_many
        Returns number of modified documents
        """
        try:
            old_obj = ObjectId(old_catetogy_id)
            new_obj = ObjectId(new_category_id)
        except Exception as e:
            print("Invalid ObjectId in reassign:", e)
            return 0
        
        filter = {"category_id": old_obj}
        if self.user_id:
            filter["user_id"] = self.user_id
        
        Update_payload = {
            "$set": {
                "category_id": new_obj
            }
        }
        if new_category_name is not None:
            Update_payload["$set"]["category"] = new_category_name
        result = self.collection.update_many(filter, Update_payload)
        return result.modified_count
    
    def cascade_delete_transactions_by_category(self, category_id: Union[str, ObjectId])-> int:
        """
        Delete all trasactions that reference given category_id (and belong to current unser)
        Returns number of deleted documents
        """ 
        try:
            cat_obj = ObjectId(category_id)
        except Exception as e:
            print("Invalid ObjectId in cascade_delete:", e)
            return 0
        filter = {"category_id": cat_obj}
        if self.user_id:
            filter["user_id"] = self.user_id
        result = self.collection.delete_many(filter)
        return result.deleted_count
    def count_transactions_by_category(self, category_name:str)-> int:
        return self.collection.count_documents({
            "category": category_name,
            "user_id": self.user_id
        })
    def reassign_category(self, old_category:str, new_category: str)-> int:
        result = self.collection.update_many({
            "category": old_category,
            "user_id": self.user_id
            },
            {
            "$set": {
                "category": new_category,
                "last_modified": datetime.now()
                }
            }
        )
        return result.modified_count
    def delete_transactions_by_category(self,category_name:str)-> int:
        result = self.collection.delete_many({
            "category": category_name,
            "user_id": self.user_id
        })
        return result.deleted_count