import streamlit as st

st.title("Mongo Class Day4")
st.text("Run command: streamlit run <script_name>") #TODO: convert to display code

#TODO:
st.text("To start streamlit app:")
st.code("streamlit run <script_name>",language="bash")

st.divider()
#=========================
# Expander and Container
#=========================
st.header("Expander")
with st.expander("Click to open expand"):
    st.write("This is content hidden by default")
    st.code("print('hello world')",language="python")

st.divider()
#=========================
# Progress and Status
#=========================
st.subheader("⌛ Progress and Status ⌛") 

#progress bar:
progress = st.slider("Progress",0,100,50)
st.progress(progress)

# Spinner:
if st.button("Show spinner"):
    with st.spinner("Wait for it..."):
        import time # nhằm tránh cho việc chạy quá lâu
        time.sleep(2) # set-up khoảng thời gian 2 giây
    st.success("🌟 Done 🌟")
st.divider()

#=========================
# Metrics (Cards)
#=========================
st.subheader("📊 Metrics (Dashboard Cards) 📊")
# Single metric:
st.markdown("**Temple In Sample**")

st.metric(label="Temperature", value="20°C", delta="-6°C")

# Multiple metrics:
# Method 1:
st.markdown("**Temple In Cities**")
col1,col2,col3 = st.columns(3)
with col1:
    st.metric(
        label="Temperature Hồ Chí Minh",
        value="25°C",
        delta="6°C",
    )
with col2: 
       st.metric(
        label="Temperature Hà Nội",
        value="34°C",
        delta="-5°C",
    )
with col3:
     st.metric(
        label="Temperature Huế",
        value="14°C",
        delta="-10°C",
    ) 
# Method 3: 
CITIES = ["Hà Nội","Hồ Chí Minh","Huế"] # tạo biến CITIES bằng list
temp = ["18°C","32°C","15°C"]
delta = ["10°C","5°C","-3°C"]

cols=st.columns(len(CITIES))
for index in range(len(CITIES)):
     with cols[index]:
          st.metric(
               label=CITIES[index],
               value= temp[index],
               delta= delta[index]
          )
st.divider()

#=========================
# Sidebar
#=========================
st.header("⚙️ Sidebar")
st.sidebar.title("💻 Management")
st.sidebar.text("Put your setting down here")

#option:
sidebar_option = st.sidebar.selectbox(
     "Select your option",
     ["6 months","12 months","24 months"]
     )
st.write(f"Sidebar option selected: **{sidebar_option}**")
st.divider()

#=========================
# Form
#=========================
st.subheader("📝 Form")
st.write("Please fill out the form below")
with st.form("my_form"):
     st.write("Passport submission form")
     name = st.text_input("Name")
     email = st.text_input("Email")
     age = st.number_input("Age",min_value=0,max_value=120)
     gender = st.selectbox("Gender",["Male","Female","Other"])
     # Form sumbit button:
     submitted = st.form_submit_button("Submit")
     if submitted:
          st.success("Form submitted successfully!")
          st.write("Your Passport info:")
          st.json({
               "name": name,
               "email": email,
               "age": age,
               "gender": gender
          })
          st.write("Form submitted successfully!")

st.divider()