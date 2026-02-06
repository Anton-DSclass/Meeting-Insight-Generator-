# 🎬 AI Video Insight Generator

An AI-powered Streamlit application that generates **topic-wise insights, summaries, and actionable takeaways** from:
- 📺 YouTube videos  
- 📁 Local uploaded videos  

Powered by **Google Gemini 2.5 Flash** with live processing tracker and PDF export.

---

## 🚀 Features

- 🔗 Accepts **YouTube links** and **local video uploads**
- 📝 Automatically fetches **YouTube transcripts**
- 🎥 Falls back to **video-based analysis** if transcript is unavailable
- ⏱️ **Live processing tracker** with elapsed time
- 🎯 Generates:
  - Short summary  
  - Topic-wise insights  
  - Actionable takeaways
- 📄 **Download insights as PDF**
- 🌐 Fully deployed & accessible via **public URL**
- ❌ No local setup required for judges

---

## 🧠 Tech Stack

- **Frontend:** Streamlit  
- **AI Model:** Google Gemini 2.5 Flash  
- **Video Handling:** yt-dlp  
- **Transcript:** youtube-transcript-api  
- **PDF Export:** reportlab  

---

## 📦 Installation (Local Setup – Optional)

```bash
git clone https://github.com/your-username/ai-video-insight-generator.git
cd ai-video-insight-generator
pip install -r requirements.txt
streamlit run app.py
--------------------------------------------------------------------------------



---

## 📦 `requirements.txt`

```txt
streamlit
google-generativeai
youtube-transcript-api
yt-dlp
reportlab
