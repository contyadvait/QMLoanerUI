import streamlit as st
import pandas as pd
import pymongo
import secret
import certifi

client = pymongo.MongoClient(secret.mongo_host_connection("", "", default=True), tlsCAFile=certifi.where())
db = client["inventory"]
collection = db["inventory"]
items = list(collection.find())

data = []

for key in items:
    del key["_id"]

st.write(pd.DataFrame(items))