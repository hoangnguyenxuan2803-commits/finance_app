import streamlit as st
import config
from database.category_models import CategoryModel
from database.transaction_models import TransactionModel

# function to render category list
def _render_category_list(category_model: CategoryModel,
                          transaction_model: TransactionModel,
                          category_type: str
                          ):
    # Initialize session state
    if "delete_warning" not in st.session_state:
        st.session_state.delete_warning = None
    
    if "edit_result" not in st.session_state:
        # Lưu kết quả edit category theo cat_id
        st.session_state.edit_result = {}

    # ✅ FIX: Proper indentation
    st.subheader(f"{category_type} Categories")
    
    # 🔍 DEBUG: Check user_id
    print(f"🔍 DEBUG: category_model.user_id = {category_model.user_id}")
    print(f"🔍 DEBUG: category_type = {category_type}")
    
    # Fetch categories
    expense_lst = category_model.get_categories_by_type(category_type=category_type)
    
    print(f"🔍 DEBUG: Found {len(expense_lst)} categories")

    if expense_lst:
        st.write(f"Total: {len(expense_lst)} categories")
        st.write("")
        with st.spinner("Calculating transactions..."):
            cat_counts = {}
            for item in expense_lst:
                name = item["name"]
                cat_counts[name] = transaction_model.count_transactions_by_category(name)
        cols = st.columns(3)

        for idx, item in enumerate(expense_lst):
            col_idx = idx % 3 # remaining fraction
            cat_name = item["name"]
            cat_id = str(item["_id"])
            tx_count = cat_counts.get(cat_name, 0)

            with cols[col_idx]:
                with st.container():
                    subcol_a, subcol_b = st.columns([4, 1])

                    with subcol_a:
                        st.write(f"📌{item.get('name')}")
                        st.caption(f"Transactions: {tx_count}")
                        st.caption(f"{item.get('created_at').strftime('%d-%m-%Y')}")

                    with subcol_b:
                        # ===== EDIT CATEGORY =====
                        with st.popover("✏️", use_container_width=True):
                            st.markdown("### ✏️ Edit Category")
                            new_name = st.text_input(
                                "New category name",
                                value=cat_name,
                                key=f"edit_name_{cat_id}"
                            )
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button("💾 Save", key=f"save_cat_{cat_id}"):
                                    result = category_model.update_category(
                                        transaction_model=transaction_model,
                                        category_type=category_type,
                                        old_name=cat_name,
                                        new_name=new_name)
                                    st.session_state.need_refresh = True
                                    st.rerun()
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_edit_cat_{cat_id}"):
                                    if st.session_state.get("need_refresh_{cat_id}"):
                                        del st.session_state[f"need_refresh_{cat_id}"]
                                        st.rerun()
                        # ===== DELETE CATEGORY =====
                        delete_button = st.button("🗑", key = f"del_exp_{cat_id}")
                        if delete_button:
                            affected = transaction_model.count_transactions_by_category(cat_name)
                            st.session_state.delete_warning = {
                                "category_type": category_type,
                                "category_name": cat_name,
                                "category_id": cat_id,
                                "affected": affected
                            }
                            st.rerun()
        # ======== pop-up area ==========
        ctx = st.session_state.delete_warning
        if ctx and ctx["category_type"] == category_type:
            with st.expander("⚠️ Delete Category Warning", expanded=True):
                if ctx["affected"] == 0:
                    st.info(
                        f"No transactions are using category "
                        f"'{ctx['category_name']}'. You can safely delete it. "
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancel", key=f"cancel_{ctx['category_type']}_{ctx['category_id']}"):
                            st.session_state.delete_warning = None
                            st.rerun()
                    with col2:
                        if st.button("🗑 Delete Category", key=f"delete_{ctx['category_type']}_{ctx['category_id']}"):
                            category_model.delete_category_safe(
                                transaction_model,
                                ctx["category_type"],
                                ctx["category_name"],
                                "block"
                                )
                            st.session_state.delete_warning = None
                            st.rerun()
                else:
                    # Affected > 0 
                    st.warning(
                        f"{ctx['affected']} transaction(s) are using category "
                        f"'{ctx['category_name']}'.\n\n"
                        "Please reassign or delete those transactions before deleting this category"
                    )
                    strategy_label = st.radio(
                        "Choose delete strategy",
                        ["Cancel", "Cascade(delete transactions)", "Reassign"],
                        key=f"delete_strategy_{ctx['category_type']}_{ctx['category_id']}"
                    )
                    strategy_map ={
                        "Cancel": "block",
                        "Cascade(delete transactions)": "cascade",
                        "Reassign": "reassign"
                    }
                    strategy = strategy_map[strategy_label]
                    target = None
                    can_submit = True

                    if strategy == "reassign":
                        options = [
                            c["name"]
                            for c in category_model.get_categories_by_type(category_type)
                            if c["name"] != ctx["category_name"]
                        ]
                        if not options:
                            st.warning("No category available to reassign")
                            can_submit = False
                        else:
                            target = st.selectbox(
                                "Reassign to category",
                                options,
                                key=f"reassign_{ctx['category_type']}_{ctx['category_id']}"
                                )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancel", key=f"cancel_{ctx['category_type']}_{ctx['category_id']}"):
                            st.session_state.delete_warning = None
                            st.rerun()
                    with col2:
                        if can_submit and st.button( "Confirm Delete",
                                                    key=f"confirm_{ctx['category_type']}_{ctx['category_id']}",
                                                    type = "primary"):
                            result = category_model.delete_category_safe(
                                transaction_model,
                                ctx["category_type"],
                                ctx["category_name"],
                                strategy.lower(),
                                target
                            )
                            st.session_state.delete_warning = None
                            if result.get("message", "Operation completed"):
                                st.success(result.get("message", "Operation completed successfully"))
                                st.rerun()
                            else:
                                st.warning(result.get("message", "Operation failed"))
                            st.rerun()
                               
def _render_category_detail(category_model, transaction_model):
    st.subheader("Category detail")
    tab1, tab2 = st.tabs(config.TRANSACTION_TYPES)

    with tab1:
        _render_category_list(category_model, transaction_model, "Expense")

    with tab2:
        _render_category_list(category_model, transaction_model , "Income")
def _render_add_category(category_model):
    st.subheader("Add category")
    with st.form("add_category_name"):
        col1, col2, col3 = st.columns([2, 2, 1]) # col1 and col2 is double size of col1

    # category type
    with col1:
        category_type = st.selectbox(
            "Category Type",
            config.TRANSACTION_TYPES # ["Expense", "Income"]
        )
    
    # category input
    with col2:
        category_name = st.text_input(
            "Category Name",
            placeholder="e.g., Groceries, Rent, Bonus"
        )
    
    with col3:
        st.write("")  # Spacing
        st.write("")
        submitted = st.form_submit_button("Submit", use_container_width=True)
    
    if submitted:
        if not category_name:
            st.error("❌ Please enter a category name")
        elif not category_type:
            st.error("❌ Please choose a category type")          
        else:
            result = category_model.upsert_category(category_type = category_type, category_name = category_name)
            if result:
                st.success(f"✅ Category '{category_name}' added successfully!")
                st.balloons()
                st.rerun()  # Refresh the page to show new category
            else:
                st.error("❌ Error adding category")
def _render_category_card(category_model: CategoryModel, transaction_model: TransactionModel, category_doc: dict):
    # Category_doc must contain _id and name fields
    cat_id = str(category_doc['_id'])
    cat_name = category_doc.get('name') or category_doc.get("category") or "Unknown"

    st.write(f"**(cat_name)**")
    st.write(f"**ID:** {cat_id}")
    
    col1, col2 = st.columns([1,1])
    with col2:
        if st.button(" Delete", key=f"delete_cat_{cat_id}"):
            #Count affecter transactions
            affected = transaction_model.count_transaction_by_category_id(cat_id)
            if affected == 0:
                #direct confirm delete
                if st.confirm(f"Delete category '{cat_name}'? No transactions will be affected. Confirm?"):
                    ok, _, msg = category_model.delete_category_safe(cat_id, "block", 
                                                                strategy="block",
                                                                transaction_model=transaction_model)
                    if ok:
                        st.success(f"Deleted category '{cat_name}'")
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to delete category '{cat_name}': {msg}")
            else:
                # Show warning & strategy
                st.warning(f"{affected} transaction(s) will be affected by deleting '{cat_name}'. Choose strategy:")
                strat = st.radio("Strategy", ("Reassign", "Cascade(delete transactions)", "Block (cancel delete)"), key=f"strat_{cat_id}")
                if strat == "Reassign":
                    # Choose target category to reassign to (exclude current)
                    cats = category_model.get_all_categories()
                    options = [ c for c in cats if str(c["_id"]) != cat_id]
                    if not options:
                        st.info("No other category to reassign to. Choose another strategy.")
                    else:
                        names = [o.get("name") or o.get("category") or str(o["_id"]) for o in options]
                        sel = st.selectbox("Reassign transactions to:", names, key=f"reassign_{cat_id}")
                        # map selected name -> id
                        sel_idx = names.index(sel)
                        target_id = str(options[sel_idx]["_id"])
                        ok, modified, msp = category_model.delete_category(cat_id, "reassign", reassign_to_id = target_id)
                        if ok:
                            st.success(msg)
                            st.experimental_rerun()
                        else:
                            st.error(msg)
                elif strat == "Cascade (delete transactions)":
                    if st.button("Confirm Cascade Delete", key=f"confirm_cascade_{cat_id}"):
                        ok, deleted, msp = category_model.delete_category_safe(cat_id, "cascade")
                        if ok:
                            st.success(msg)
                            st.experimental_rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("Deletion blocked. Choose another strategy or cancel.")
def _render_danger_zone(category_model, transaction_model):
    """Danger zone - delete all categories"""
    st.divider()
    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning("**Delete all categories** - This action cannot be undone!")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("This will delete ALL categories and their transactions")
        with col2:
            if st.button("🗑️ Delete All", type="primary"):
                # Count total
                all_cats = category_model.get_all_categories()
                
                # Confirm
                if len(all_cats) > 0:
                    # Delete all transactions first
                    tx_deleted = transaction_model.collection.delete_many({
                        "user_id": transaction_model.user_id
                    }).deleted_count
                    
                    # Delete all categories
                    cat_deleted = category_model.collection.delete_many({
                        "user_id": category_model.user_id
                    }).deleted_count
                    
                    st.success(f"✅ Deleted {cat_deleted} categories and {tx_deleted} transactions")
                    st.rerun()
                else:
                    st.info("No categories to delete")

# public function
def render_categories(category_model : CategoryModel, 
                      transaction_model : TransactionModel):
    # 🔍 DEBUG: Check if user_id is set
    print(f"🔍 DEBUG render_categories: category_model.user_id = {category_model.user_id}")
    print(f"🔍 DEBUG render_categories: transaction_model.user_id = {transaction_model.user_id}")
    
    st.title("🏷️ Category Management")

    # Display existing category list
    _render_category_detail(category_model, transaction_model)

    st.divider()

    # Add category section
    _render_add_category(category_model)
    _render_danger_zone(category_model, transaction_model) 