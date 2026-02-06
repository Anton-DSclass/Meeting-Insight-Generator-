import streamlit as st
import os
import time
import subprocess
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===============================
# GEMINI CONFIG (CLOUD SAFE)
# ===============================
API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ GEMINI_API_KEY not found. Add it in Streamlit → Settings → Secrets")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="AI Video Insight Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# FILE PATHS
# ===============================
VIDEO_FILE = "input_video.mp4"
PDF_FILE = "AI_Video_Insights.pdf"

# ===============================
# SESSION STATE
# ===============================
if "insights" not in st.session_state:
    st.session_state.insights = ""

# ===============================
# STYLES
# ===============================
st.markdown(
    """
<style>
.stApp { background: linear-gradient(135deg, #e3f2fd, #f8fbff); }

.big-title {
    text-align: center;
    font-size: 88px;
    font-weight: 900;
    background: linear-gradient(100deg,#0020ff,#00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hr-line {
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg,#0072ff,#00c6ff);
    margin: 10px auto 30px auto;
}

.card {
    background: white;
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #e0e7ff;
    box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    margin-bottom: 16px;
}

.insight-card {
    border: 3px solid #0066ff;
    background: linear-gradient(135deg,#f0f9ff,#ffffff);
    padding: 22px;
    border-radius: 24px;
    box-shadow: 0 10px 24px rgba(0,102,255,0.2);
}
</style>
""",
    unsafe_allow_html=True
)

# ===============================
# TITLE
# ===============================
st.markdown('<div class="big-title">AI Video Insight Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hr-line"></div>', unsafe_allow_html=True)
st.caption("⚡ Gemini AI | YouTube Transcript Based")

# ===============================
# HELPER FUNCTIONS
# ===============================
def get_youtube_transcript(url):
    video_id = url.split("v=")[-1].split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
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
# LAYOUT
# ===============================
left, right = st.columns([1, 2])

# ===============================
# INPUT SECTION
# ===============================
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    option = st.radio("Choose input source", ["YouTube Link", "Upload Video"])
    youtube_url = st.text_input("🔗 YouTube URL") if option == "YouTube Link" else None
    uploaded_file = st.file_uploader("📁 Upload Video", type=["mp4", "mkv", "mov"]) if option == "Upload Video" else None

    generate = st.button("🚀 Generate Insights")

    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# PROCESSING
# ===============================
if generate:
    try:
        with st.status("⏳ Processing...", expanded=True):

            if option == "YouTube Link":
                if not youtube_url:
                    st.error("Please enter a YouTube URL")
                    st.stop()

                st.write("📝 Fetching transcript...")
                transcript = get_youtube_transcript(youtube_url)

                st.write("🤖 Generating AI insights...")
                st.session_state.insights = generate_insights(transcript)

            else:
                st.warning(
                    "⚠️ Direct video analysis is NOT supported in Gemini stable SDK.\n\n"
                    "Please use a YouTube link with captions."
                )
                st.stop()

        st.success("✅ Done")
        st.balloons()

    except Exception as e:
        st.error(str(e))

# ===============================
# OUTPUT SECTION
# ===============================
with right:
    if st.session_state.insights:
        st.markdown('<div class="card insight-card">', unsafe_allow_html=True)
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
                st.download_button(
                    "⬇️ Download PDF",
                    f,
                    file_name=PDF_FILE
                )

        st.markdown('</div>', unsafe_allow_html=True)
