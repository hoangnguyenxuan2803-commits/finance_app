import streamlit as st
from datetime import datetime, date
import pandas as pd
import random

st.subheader("---------My Calculation---------")
number_1 = st.number_input("Enter your first number")
number_2 = st.number_input("Enter your second number")
operation = st.selectbox("Choose your operation?",['+','-',"x",":"])
if operation == "+":
    result = number_1 + number_2
elif operation == "-":
    result = number_1 - number_2
elif operation == "x":
    result = number_1 * number_2
elif operation == ":" and number_2 != 0 :
    result = number_1/number_2
else:
    result = "Invalid operation"

st.write(f"Result {number_1} {operation} {number_2} = {result}")

#=================================
#  Buttons and Actions
#=================================
st.header("Button and Actions")
# divide pafe into three column
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Click Me"):
        st.success("You Clicked")
        st.balloons() # funny effect

with col2:
    if st.button("Show failed"):
        st.error("Message Error !")

with col3:
    if st.button("Show Warning"):
        st.warning("Message warning !")
st. divider()