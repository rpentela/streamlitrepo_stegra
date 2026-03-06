# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.title("My Streamlit Dashboard")

# Example dataframe
df = pd.DataFrame(
    np.random.randn(10, 3),
    columns=['A', 'B', 'C']
)

st.write("Here's a sample dataframe:")
st.dataframe(df)
