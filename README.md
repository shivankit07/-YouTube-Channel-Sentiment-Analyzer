# -YouTube-Channel-Sentiment-Analyzer 🎬💬

# ## YouTube Channel Performance Analysis Based on Recent Videos

## Project Overview
Analyze the latest videos from one or more YouTube channels to understand:

- Which channels perform better.
- What factors drive views, likes, and engagement.
- How video publishing frequency affects channel growth.

---

## 1. Project Objective 🎯
This project helps you analyze YouTube channel performance by:

1. Fetching recent videos from a channel.
2. Extracting comments for those videos.
3. Performing sentiment analysis on the comments.
4. Visualizing insights to understand audience engagement.

---

## 2. Data Collection 📥
We use **YouTube Data API v3** to fetch recent videos and comments.

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable **YouTube Data API v3**.
4. Generate an **API Key**.
5. Use Python’s `google-api-python-client` library to fetch data.

**Install Required Libraries:**

pip install google-api-python-client pandas matplotlib seaborn

## 3. Tech Stack 🛠️
| Task                   | Tools / Libraries                                    |
| ---------------------- | ---------------------------------------------------- |
| Fetch video & comments | **YouTube Data API v3** + `google-api-python-client` |
| Sentiment Analysis     | **NLTK**, **TextBlob**, or **VADER**                 |
| Data Handling          | **Pandas, NumPy**                                    |
| Visualization          | **Matplotlib, Seaborn, WordCloud**                   |
| Optional Dashboard     | **Streamlit**                                        |

## 4. How It Works ⚡
1. Paste a YouTube channel link.
2. Fetch the 5 most recent videos from that channel.
3. Extract comments from these videos.
4. Perform sentiment analysis on the comments.
5. Generate visual reports & insights about the channel’s performance.

## 📸 Preview

![Analysis Screenshot]
<img width="1295" alt="preview" src="<img width="1920" height="1080" alt="Untitled design" src="https://github.com/user-attachments/assets/65a0325f-f0be-4ad1-80be-fec4ce4717d2" />

