# from urlextract import URLExtract
# import pandas as pd
# from collections import Counter
# import emoji

# extract = URLExtract()

# def fetch_stats(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     num_messages = df.shape[0]
#     words = []
#     for message in df['message']:
#         words.extend(message.split())
#     num_media = df[df['message'].str.contains('<Media omitted>', case=False)].shape[0]
#     links = []
#     for message in df['message']:
#         links.extend(extract.find_urls(message))
#     return num_messages, len(words), num_media, len(links)

# def most_busy_users(df):
#     x = df['user'].value_counts().head()
#     df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
#         columns={'user': 'name', 'count': 'percent'})
#     return x, df_percent

# def most_common_words(selected_user, df):
#     with open('stop_hinglish.txt', 'r') as f:
#         stop_words = f.read()
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     temp = df[df['user'] != 'group_notification']
#     temp = temp[~temp['message'].str.contains('<Media omitted>', case=False)]
#     words = [word.lower() for message in temp['message'] for word in message.split() if word.lower() not in stop_words]
#     return pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Count'])

# def monthly_timeline(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
#     timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
#     return timeline

# def daily_timeline(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     return df.groupby('only_date').count()['message'].reset_index()

# def week_activity_map(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     return df['day_name'].value_counts()

# def month_activity_map(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     return df['month'].value_counts()

# def emoji_helper(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     emojis = [c for message in df['message'] for c in message if c in emoji.EMOJI_DATA]
#     return pd.DataFrame(Counter(emojis).most_common(20))



from urlextract import URLExtract
import pandas as pd
from collections import Counter
import emoji
import re
from textblob import TextBlob

extract = URLExtract()

# ---------------- FETCH STATS ----------------
def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    words = []
    for message in df['message']:
        if isinstance(message, str):
            words.extend(message.split())

    num_media = df[df['message'].str.contains('<Media omitted>', case=False, na=False)].shape[0]

    links = []
    for message in df['message']:
        if isinstance(message, str):
            links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media, len(links)


# ---------------- MOST BUSY USERS ----------------
def most_busy_users(df):

    x = df['user'].value_counts().head()

    df_percent = (
        (df['user'].value_counts() / df.shape[0]) * 100
    ).round(2).reset_index()

    df_percent.columns = ['name', 'percent']

    return x, df_percent


# ---------------- MOST COMMON WORDS ----------------
def most_common_words(selected_user, df):

    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().split()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', case=False, na=False)]

    words = []

    for message in temp['message']:
        if isinstance(message, str):
            for word in message.split():
                if word.lower() not in stop_words:
                    words.append(word.lower())

    return pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Count'])


# ---------------- MONTHLY TIMELINE ----------------
def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline


# ---------------- DAILY TIMELINE ----------------
def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date').count()['message'].reset_index()


# ---------------- WEEK ACTIVITY ----------------
def week_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


# ---------------- MONTH ACTIVITY ----------------
def month_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


# ---------------- EMOJI ANALYSIS ----------------
def emoji_helper(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message']:
        if isinstance(message, str):
            emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis).most_common(20))


# =====================================================
# ✅ NEW FEATURE 1: SENTIMENT ANALYSIS
# =====================================================
def sentiment_analysis(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    sentiments = []

    for message in df['message']:
        if isinstance(message, str):
            try:
                polarity = TextBlob(message).sentiment.polarity
                if polarity > 0:
                    sentiments.append("Positive")
                elif polarity < 0:
                    sentiments.append("Negative")
                else:
                    sentiments.append("Neutral")
            except:
                sentiments.append("Neutral")

    if len(sentiments) == 0:
        return pd.Series(dtype="int")

    sentiment_df = pd.DataFrame(sentiments, columns=["Sentiment"])

    return sentiment_df["Sentiment"].value_counts()


def get_punchcard_data(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Group by Day and Hour
    punchcard = df.groupby(['day_name', 'hour']).count()['message'].reset_index()
    return punchcard