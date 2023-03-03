import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt
import seaborn as sns
import re
import emoji
from collections import Counter
import warnings
from wordcloud import WordCloud, STOPWORDS
warnings.filterwarnings("ignore")
from datetime import datetime

## Function to find mobile number and names
def find_sender(x):
    # type: ignore
    pattern = "^\s-\s([\w\s\d+]+):"
    res = re.search(pattern, x)
    if res == None:
        return ""
    else:
        return res[1]

## Function to preprocess the data
def data_preprocessing(data):
    # ## Loading chat data
    # type: ignore
    pattern = "\d{1,2}/\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s.M"

    message = re.split(pattern, data)[1:]

    dates = re.findall(pattern, data)

    df = pd.DataFrame({'date':dates, "message":message})

    df['date'] = pd.to_datetime(df['date'].str.replace(',',''))

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    df['sender'] = df['message'].apply(lambda x : find_sender(x))

    indices = df[df['sender'] == ""].index
    df.drop(indices, inplace = True)

    pattern = "^\s-\s[\w\s\d+]+:"
    df['text'] = df['message'].apply(lambda x : re.split(pattern, x)[1])\
                .str.replace('\\n','').str.strip().str.lower()

    df.drop('message', axis=1, inplace=True)
    return df

def member_count(df):
    return len(df['sender'].unique())

def total_media(df):
    id = "<media omitted>"
    return df['text'].apply(lambda x  : x.count(id)).sum()

def emoji_table(df):
    emj = []
    emoji_dict = emoji.get_emoji_unicode_dict('en')
    for row in df['text']:
        for c in row:
            # type: ignore
            if emoji.demojize(c) in emoji_dict:
                emj.append(c)
    
    emj = dict(Counter(emj).most_common(10))
    return pd.DataFrame({'Emoji':emj.keys(), 'Frequency':emj.values()})

def total_links(df):
    pattern = "https?:"
    return df['text'].apply(lambda x : len(re.findall(pattern, x))).sum()

def total_words(df):
    words = []
    for row in df['text']:
        for word in row.split():
            if word != '<media' and word != 'omitted>':
                words.append(word)
    return words

def top_busy_user(df):
    return df['sender'].value_counts().head(5)

def top_busy_user_percentage(df):
    busy_user = round(df['sender'].value_counts()/df.shape[0] * 100, 2).reset_index()
    return busy_user.rename(columns={'index':'Sender','sender':'Percentage'})

def create_wordcloud(words):
    return WordCloud(width = 600, height =400,
                background_color ='white',
                stopwords = set(STOPWORDS),
                min_font_size = 10).generate(" ".join(words))

def most_freq_words(words):
    words = [w for w in words if w not in set(STOPWORDS) and len(w) > 2]
    return pd.DataFrame(Counter(words).most_common(20), columns=['Words', 'Frequency'])

def busy_month(df):
    busy_month = df[['year', 'month']].value_counts(sort=False)
    busy_month_index = sorted(busy_month.index, key=lambda x : datetime.strptime(x[1], "%B"))
    busy_month_index = sorted(busy_month_index, key=lambda x : x[0])
    return busy_month[busy_month_index]

def daily_timeline(df):
    daily_timeline = df['date'].dt.strftime("%Y-%m-%d").value_counts(sort=False)
    return pd.to_datetime(daily_timeline.index), daily_timeline.values

def most_busy_month(df):
    return df['month'].value_counts()

def most_busy_week(df):
    return df['day_name'].value_counts()

def get_spammer(df):
    spammer = df[(df['text'] == 'this message was deleted') | (df['text'] == 'you deleted this message')]['sender'].value_counts()
    return spammer.reset_index().rename({"index":"Sender","sender":"Frequency"}, axis=1)