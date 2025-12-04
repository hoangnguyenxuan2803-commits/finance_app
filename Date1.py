from pymongo import MongoClient
import random

MONGO_URI="mongodb+srv://hoangnguyenxuan2803_db_user:ydIkIUpjyMiWYNbi@cluster1.fs1mvqd.mongodb.net/?appName=Cluster1"

client = MongoClient(MONGO_URI)
db = client["First_app_finance_Hoang"]
transactions = db['transactions']
db.command("ping")

print("Data connect success")
print(f"database name {db.name}")
print(f"First collection: {transactions.name}")

print("======= insert one =======")
#my_transaction={
#    "type": "wave",
#    "amount": 1000,
#    "unit": "USD",
#}
#transactions.insert_one(my_transaction)
#print("Insert Done")

#TYPE=['in','out']
#UNIT=['VND','USD']

# multi_transactions =[]
# for i in range(10):
#     fake_trans={
#         "type": random.choice(TYPE),
#         "unit": random.choice(UNIT),
#         "amout": random.randint(10,2000),
#     }
#     multi_transactions.append(fake_trans)
# result= transactions.insert_many(multi_transactions)
# print(f"{len(result.inserted_ids)} transactions inserted!")
# print(f"Generate _ids:{result.inserted_ids}") 

# my_emb_transaction={
#     "type":"wave",
#     "amount": 1000,
#     "unit": "USD",
#     "detail": [
#         {
#             "item": "apple",
#             "quantity": 10,
#             "discount": 50
#         },
#         {
#             "item": "rice",
#             "quantity": "5 kg",
#         }
#     ]
# }
# transactions.insert_one(my_emb_transaction)
# print("Insert Done")

print("="*60)
print("Read data")
print("="*60)

# # get all docs in transaction
# all_trans = transactions.find()
# all_trans = list(all_trans)
# print(f"Retrive {len(all_trans)} docs")
# for trans in all_trans[:3]:
#     # print(f"Transaction: {trans}")
#     print(f"Transaction id: {trans.get("_id","Unknow")}")
#     print(f"Transaction type: {trans.get("type", "Others")}")
#     print(f"Transaction unit: {trans.get("unit","---")}")
#     print("-"*10)

# # get docs with type = in
# all_trans_in = transactions.find({"type": "in"})
# all_trans_in = list(all_trans_in)
# print(f"Retrive {len(all_trans_in)} docs with type = in ")

# get docs with type = out, greater than 50 USD, less than 100
all_trans_out =transactions.find({"type": "out", "amount": {"$gt": 50, "$lt": 100} , "unit":"USD"})
all_trans_out = list(all_trans_out)
print(f"Retrieve {len(all_trans_out)} docs with type = out")