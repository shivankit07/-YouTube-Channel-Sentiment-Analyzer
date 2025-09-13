import os
import streamlit as st
import pandas as pd
import re
from googleapiclient.discovery import build
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# -------------------------------
# NLTK Setup
# -------------------------------
nltk_data_dir = os.path.expanduser('~/nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
nltk.data.path.append(nltk_data_dir)
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', download_dir=nltk_data_dir)

# -------------------------------
# YouTube API Setup
# -------------------------------
API_KEY = "Enter YOUR YOUTUBE API KEY HERE"  # Replace with your API key
youtube = build("youtube", "v3", developerKey=API_KEY)

# -------------------------------
# Helper Functions
# -------------------------------
def extract_channel_id(channel_url):
    if "channel/" in channel_url:
        return channel_url.split("channel/")[-1].strip("/")
    elif "@" in channel_url:
        handle = channel_url.split("@")[-1].strip("/")
        request = youtube.search().list(
            part="snippet", q=f"@{handle}", type="channel", maxResults=1
        )
        response = request.execute()
        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]["snippet"]["channelId"]
        else:
            st.error("❌ Could not resolve handle. Try /channel/ link.")
            return None
    else:
        st.error("❌ Invalid URL format.")
        return None

def get_recent_videos(channel_id, max_results=5):
    channel_req = youtube.channels().list(part="contentDetails", id=channel_id)
    channel_res = channel_req.execute()
    playlist_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos_req = youtube.playlistItems().list(
        part="snippet,contentDetails", playlistId=playlist_id, maxResults=max_results
    )
    videos_res = videos_req.execute()
    videos = []
    for item in videos_res.get("items", []):
        videos.append({
            "video_id": item["contentDetails"]["videoId"],
            "title": item["snippet"]["title"],
            "publishedAt": item["snippet"]["publishedAt"]
        })
    return pd.DataFrame(videos)

def get_video_comments(video_id, max_results=50):
    comments = []
    req = youtube.commentThreads().list(
        part="snippet", videoId=video_id, maxResults=max_results, textFormat="plainText"
    )
    res = req.execute()
    for item in res.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    df = pd.DataFrame(comments, columns=["comment"])
    df["sentiment_score"] = df["comment"].apply(lambda x: analyzer.polarity_scores(x)["compound"])
    def get_sentiment(score):
        if score >= 0.05: return "Positive"
        elif score <= -0.05: return "Negative"
        else: return "Neutral"
    df["sentiment"] = df["sentiment_score"].apply(get_sentiment)
    return df

def generate_wordcloud(comments):
    text = " ".join(comments)
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    return wc

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📊 YouTube Channel Sentiment Analyzer")
st.write("Paste YouTube channel link** to analyze recent videos and comments.")

channel_urls = st.text_input("Enter YouTube Channel Link:")

max_videos = st.number_input("Number of recent videos per channel:", min_value=1, max_value=10, value=5)

if st.button("Analyze"):
    if not channel_urls.strip():
        st.warning("Please enter at least one channel link.")
    else:
        urls = [url.strip() for url in channel_urls.split(",")]
        for url in urls:
            channel_id = extract_channel_id(url)
            if not channel_id:
                continue
            st.info(f"Fetching latest {max_videos} videos for channel: {url}")
            videos_df = get_recent_videos(channel_id, max_results=max_videos)
            if videos_df.empty:
                st.warning("No videos found.")
                continue
            st.write(f"### Recent Videos for {url}", videos_df)

            all_comments = []
            video_sentiments = []
            for _, row in videos_df.iterrows():
                comments = get_video_comments(row["video_id"], max_results=50)
                all_comments.extend(comments)
                df_vid = analyze_sentiment(comments)
                pos = (df_vid["sentiment"]=="Positive").sum()
                neg = (df_vid["sentiment"]=="Negative").sum()
                neu = (df_vid["sentiment"]=="Neutral").sum()
                total = len(df_vid)
                score = (pos - neg)/total*100 if total>0 else 0
                video_sentiments.append({
                    "video_id": row["video_id"],
                    "title": row["title"],
                    "positive": pos,
                    "negative": neg,
                    "neutral": neu,
                    "score": score
                })

            if not all_comments:
                st.warning("No comments found.")
                continue

            # Overall Sentiment
            df_comments = analyze_sentiment(all_comments)
            st.write("### Sample Comments with Sentiment", df_comments.head(10))

            # Word Cloud
            st.write("### Word Cloud of Comments")
            wc = generate_wordcloud(all_comments)
            plt.figure(figsize=(10,5))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            st.pyplot(plt)

            # Sentiment Distribution
            st.write("### Sentiment Distribution")
            fig, ax = plt.subplots(figsize=(6,4))
            sns.countplot(data=df_comments, x="sentiment", palette="coolwarm", ax=ax)
            st.pyplot(fig)

            # Video-level Sentiment
            st.write("### Video-level Sentiment Score")
            video_df = pd.DataFrame(video_sentiments)
            st.bar_chart(video_df.set_index("title")["score"])

            # Summary Report
            pos = (df_comments["sentiment"]=="Positive").sum()
            neg = (df_comments["sentiment"]=="Negative").sum()
            neu = (df_comments["sentiment"]=="Neutral").sum()
            total = len(df_comments)
            overall_score = (pos - neg)/total*100

            if overall_score > 30:
                status = "🌟 Channel is performing well — strong positive audience response!"
            elif overall_score < -10:
                status = "⚠️ Channel performance is declining — many negative comments."
            else:
                status = "😐 Channel has mixed audience feedback."

            st.write("### 📌 Channel Performance Report")
            st.markdown(f"""
            - Total Comments Analyzed: **{total}**
            - Positive: **{pos}**
            - Negative: **{neg}**
            - Neutral: **{neu}**
            - Overall Sentiment Score: **{overall_score:.2f}%**
            - **Status:** {status}
            """)
