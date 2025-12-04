import streamlit as st

# Tạo menu ngang
main_tabs = st.tabs(["Home", "Transactions", "Categories"])

# ------------------ HOME TAB ------------------
with main_tabs[0]:
    st.header("🏠 Home")
    st.write("Welcome to Home Page!")

# ---------------- TRANSACTIONS TAB -------------
with main_tabs[1]:
    st.header("💸 Transactions")

    # Menu con trong Transactions
    sub_choice = st.radio(
        "Choose an action:",
        ["Add Transaction", "Transaction History"],
        horizontal=True
    )

    if sub_choice == "Add Transaction":
        _render_add_transaction(transaction_model, category_model)

    elif sub_choice == "Transaction History":
        st.subheader("📜 Transaction History")
        st.write("Danh sách giao dịch...")
# ======================================================
# ===============  ADD TRANSACTION PAGE ================
# ======================================================

def _render_add_transaction(transaction_model, category_model):
    st.subheader("➕ Add Transaction")

    # tạo form
    with st.form("add_new_transaction"):
        
        # --- CHỌN LOẠI GIAO DỊCH ---
        transaction_type = st.selectbox(
            "Transaction Type",
            config.TRANSACTION_TYPES
        )

        # --- LẤY CATEGORY THEO LOẠI ---
        categories = category_model.get_category_by_type(transaction_type)
        category_names = [item['name'] for item in categories]

        if not category_names:
            st.warning(f"No category for {transaction_type}. Please add one first!")
            st.form_submit_button("Submit", disabled=True)
            return

        category = st.selectbox("Category", category_names)

        # --- NHẬP SỐ TIỀN ---
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(
                "Amount (VND)",
                min_value=1000,
                step=1
            )

        # --- NHẬP NGÀY ---
        with col2:
            transaction_date = st.date_input(
                "Transaction Date",
                value=date.today()
            )

        # --- MÔ TẢ ---
        description = st.text_input(
            "Description (Optional)",
            ""
        )

        # --- SUBMIT ---
        submitted = st.form_submit_button("Submit")

        if submitted:

            # LƯU TRANSACTION VÔ MONGO
            transaction_model.add_transaction(
                type=transaction_type,
                category=category,
                amount=amount,
                date=transaction_date,
                description=description
            )

            st.success("Transaction added successfully!")
            st.balloons()




# from database.transaction_models import TransactionModel
# from datetime import date

# if __name__ == "_main_":
#         # #init model
#         # transaction_model = TransactionModel()

#         # # define params:
#         # Transaction_type = "Income"
#         # category = "Shopping"
#         # amount = 234
#         # transaction_date = date.today()

#         # result_new = transaction_model.add_new_transaction(
#         #     Transaction_type = Transaction_type,
#         #     category = category,
#         #     amount = amount,
#         #     transaction_date = transaction_date,
#         #     description = "None" #skip
#         # )
#         # print(f"New transaction created!!{result_new}")