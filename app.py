# mkdir .streamlit cách tạo thư mục
# touch .streamlit/secrets.toml cách tạo file
# create app new file by touch <name>.py
import streamlit as st
import config

#import analytics
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinananceVisualizer

# import Model
from database.transaction_models import TransactionModel
from database.category_models import CategoryModel
from database.user_model import UserModel

#import view model
from Views.categories_view import render_categories
from Views.transaction_view import render_transaction
from Views.user_view import render_user_profile
from Views.home_views import render_dashboard


# initialize models
@st.cache_resource
def init_models():
    """Initialize and cached models"""
    return {
        "category": CategoryModel(),
        "transaction": TransactionModel(),
        "user": UserModel(),
        "visualizer": FinananceVisualizer()
    }

# initialize session per user
if "models" not in st.session_state:
    # initialize models
    st.session_state['models'] = init_models()


models = st.session_state['models']

# Page configuration
st.set_page_config(
    page_title = "Finance Tracker",
    page_icon = "🤑",
    layout = "wide"
)
# =========================
# INIT SESSION STATE
# =========================
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None
# =============================================
# 1. Authen User
# =============================================

def login_screen():
    with st.container():
        st.header("This app is private")
        st.subheader("Please login to continue")
        st.button("Login with Google", on_click = st.login)
if not st.session_state.is_logged_in:

    # chưa login → show login UI
    login_screen()

    # 🔴 CHỈ check st.user SAU KHI OAuth xong
    if st.user is not None and st.user.get("email"):
        user_model: UserModel = models["user"]

        try:
            mongo_user_id = user_model.login(st.user["email"])
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.stop()

        st.session_state.is_logged_in = True
        st.session_state.user_id = mongo_user_id
        st.rerun()

    st.stop()
else:
    # Get mongo_user
    user_model: UserModel = models['user']
    try:
        mongo_user_id = user_model.login(st.user.email)
    except Exception as e:
        st.error(f"Error during user login: {e}")
        st.stop()

    # set user_id for models
    # currently we have category and transaction models
    # you can optimize this by doing it in the model init function
    models['category'].set_user_id(mongo_user_id)
    models['transaction'].set_user_id(mongo_user_id)


    user = st.user.to_dict() # convert google_user to dict
    user.update({
        "id": mongo_user_id
    })

    # Display user profile after update user with mongo_user_id
    render_user_profile(user_model, user)

    # init analyzer
    # because transaction_model has set user_id already in line 74
    analyzer_model = FinanceAnalyzer(models['transaction'])

    # =============================================
    # 2. Navigation
    # =============================================

    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Category", "Transaction"]
    )
    
    # =============================================
    # Router
    # =============================================

    if page == "Home":
        st.title("Home")
        render_dashboard(analyzer_model = analyzer_model,
                        transaction_model = models['transaction'],
                        visualizer_model=models['visualizer'])
    elif page == "Category":
        # get category_model from models
        category_model = models['category']
        transaction_model = models['transaction']

        # display category views
        render_categories(category_model=category_model, transaction_model= transaction_model)

    elif page == "Transaction":
        # get category_model and transaction from models
        category_model = models['category']
        transaction_model = models['transaction']

        # display transaction views
        render_transaction(transaction_model=transaction_model, category_model=category_model)