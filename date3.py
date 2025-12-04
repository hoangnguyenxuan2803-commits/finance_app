# installs streamlit:
# pip install streamlit
# uv add streamlit
import streamlit as st
from datetime import datetime, date
import pandas as pd
import random

#=================================
# streamlit base text and title
#=================================
# cách chạy lên: streamlit run hands-on/date3.py => Dùng hands-on/ để trỏ tới nếu trường hợp nó có nhiều thư mục
# streamlit run date3.py 
st.title("Welcome to our finance-tracker app") # Show the bigger title
st.header("This is header")
st.subheader("this is subheader")
st.text("This is simple text")
st.markdown("** this is bold text **")
st.markdown("* this is bold text *")

st.divider() #add horizontal line
#=================================
# display date
#=================================
st.header("this is section to display data")

#Display dictionary
st.subheader("Display dictionary")
category ={
    "type":"Income",
    "category": "Shopping",
    "amount": "5$"
}
st.write(category)

#Display list
st.subheader("Display list")
colections = ['categories','users','budgets']
st.write(colections)

#Display Dataframe

st.subheader("Display dataframe")
data=[]
for i in range(10):
    item={
        "id": i+1,
        "sex": random.choice(['F',"M"]),
        "age": random.randint(3,50)
    }
    data.append(item)
df =pd.DataFrame(data)
st.markdown("**Interactive table**")
st.dataframe(df)

st.markdown("**Static table**")
st.table(df) # Không có tương tác

#=================================
# User widget input
#=================================
# text input
st.subheader("1. Text input")
name = st.text_input("What is your name?", placeholder="Enter your name")
if name:
    st.write(f"Hello {name}")

# Number input
st.subheader("2. Numb input")
number = st.number_input("How old are you?", placeholder="Enter the positive number")
if number:
    st.write(f"You are {number} years old")

#slider
st.subheader("3. Slider input")
my_slide = st.slider("Select a current temperature", min_value= -10, max_value= 50, value = 20)
st.write(f"Current temperature is {my_slide} celsius")

#option
option = st.selectbox("Choose your interest?", ["Education","Technology","Marketing"])
if option:
    st.write(f"Your option is {option}")