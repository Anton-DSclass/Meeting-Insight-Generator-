import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===============================
# GEMINI CONFIG
# ===============================
API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AI Video Insight Generator", layout="wide")

PDF_FILE = "AI_Video_Insights.pdf"

if "insights" not in st.session_state:
    st.session_state.insights = ""

# ===============================
# TITLE
# ===============================
st.title("🎥 AI Video Insight Generator")
st.caption("Gemini AI | YouTube Transcript Based")

# ===============================
# FIXED TRANSCRIPT FUNCTION
# ===============================
def get_youtube_transcript(url):
    video_id = url.split("v=")[-1].split("&")[0]

    api = YouTubeTranscriptApi()

    if hasattr(YouTubeTranscriptApi, "get_transcript"):
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    else:
        transcript = api.get_transcript(video_id)

    return " ".join(t["text"] for t in transcript)

def generate_insights(text):
    prompt = (
        "Generate:\n"
        "1. Short summary\n"
        "2. Topic-wise insights\n"
        "3. Actionable takeaways\n\n"
        f"Transcript:\n{text}"
    )
    response = model.generate_content(prompt)
    return response.text

# ===============================
# INPUT
# ===============================
youtube_url = st.text_input("🔗 YouTube URL")

if st.button("🚀 Generate Insights"):
    try:
        with st.spinner("Processing..."):
            transcript = get_youtube_transcript(youtube_url)
            st.session_state.insights = generate_insights(transcript)
        st.success("Done ✅")
    except Exception as e:
        st.error(str(e))

# ===============================
# OUTPUT
# ===============================
if st.session_state.insights:
    st.subheader("🎯 AI Insights")
    st.markdown(st.session_state.insights)

    if st.button("📄 Download PDF"):
        c = canvas.Canvas(PDF_FILE, pagesize=A4)
        y = 800
        for line in st.session_state.insights.split("\n"):
            if y < 50:
                c.showPage()
                y = 800
            c.drawString(40, y, line[:100])
            y -= 16
        c.save()

        with open(PDF_FILE, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name=PDF_FILE)
