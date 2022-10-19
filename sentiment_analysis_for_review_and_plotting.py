from statistics import mode
import streamlit as st
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment?text=I+like+you.+I+love+you

tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

from scipy.special import softmax
# open txt file
file_ = open('reviews.txt', 'r')
# read all lines
lines = file_.readlines()
import pandas as pd

dates = pd.read_csv('covers_2019.csv')
dates = dates['Date']
# keep only date
dates = dates.str.split(' ').str[0]
dates = dates.to_numpy()
# remove duplicates
dates = np.unique(dates)

# add random date to each review
dates = np.random.choice(dates, len(lines))
# add date to each review as a dataframe
df = pd.DataFrame({'Date': dates, 'Review': lines})
print(df)

# sort by dates
df = df.sort_values(by=['Date'])

# get all reviews
reviews = df['Review'].to_numpy()
n = 100
for review in reviews[:n]:
    text = review[10:]
    print(text)

    text = preprocess(text)
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    # return index of the highest score
    pred = np.argmax(scores)
    labels = ['negative', 'neutral', 'positive']
    print(labels[pred])
    print(scores)
    # add sentiment to dataframe in one of the three columns
    if labels[pred] == 'negative':
        df.loc[df['Review'] == review, 'Negative'] = scores[pred]
    elif labels[pred] == 'neutral':
        df.loc[df['Review'] == review, 'Neutral'] = scores[pred]
    else:
        df.loc[df['Review'] == review, 'Positive'] = scores[pred]

# fill NaN with 0
# lambda function to take off the first 10 characters of the review
df['Review'] = df['Review'].apply(lambda x: x[10:])
st.write(df)

# plot positive, negative and neutral sentiment
import plotly.express as px
df = df[:n]
fig = px.bar(df, x='Date', y=['Positive', 'Negative', 'Neutral'], barmode='group')
st.plotly_chart(fig)