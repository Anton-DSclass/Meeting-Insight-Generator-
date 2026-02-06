import streamlit as st
import subprocess
import os
import time
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===============================
# GEMINI CLIENT
# ===============================
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

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
for key in ["transcript", "insights", "start_time"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ===============================
# STYLES
# ===============================
st.markdown("""
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
    padding: 6px;
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

.stButton>button {
    background: linear-gradient(90deg,#0072ff,#00c6ff);
    color: black;
    font-size: 18px;
    border-radius: 40px;
    padding: 10px 28px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# TITLE
# ===============================
st.markdown('<div class="big-title">AI Video Insight Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hr-line"></div>', unsafe_allow_html=True)
st.caption("⚡ Gemini AI | Processing tracker enabled")

# ===============================
# LAYOUT
# ===============================
left, right = st.columns([1, 2])

# ===============================
# INPUT
# ===============================
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    option = st.radio("Choose input source", ["YouTube Link", "Upload Video"])
    youtube_url = st.text_input("🔗 YouTube URL") if option == "YouTube Link" else None
    uploaded_file = st.file_uploader("📁 Upload Video", type=["mp4", "mkv", "mov"]) if option == "Upload Video" else None
    generate = st.button("🚀 Generate Insights")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# HELPERS
# ===============================
def get_transcript(url):
    video_id = url.split("v=")[-1].split("&")[0]
    transcript = YouTubeTranscriptApi().get_transcript(video_id)
    return " ".join(t["text"] for t in transcript)

def elapsed_time():
    return f"{int(time.time() - st.session_state.start_time)} sec"

# ===============================
# PROCESS
# ===============================
if generate:
    try:
        st.session_state.insights = ""
        st.session_state.start_time = time.time()

        with st.status("🚀 Processing started...", expanded=True) as status:
            timer_box = st.empty()

            def tick(msg):
                timer_box.info(f"{msg} | ⏱ {elapsed_time()}")

            # ---------- YOUTUBE ----------
            if option == "YouTube Link":
                if not youtube_url:
                    st.error("Please enter YouTube URL")
                    st.stop()

                tick("📝 Fetching transcript")
                transcript = get_transcript(youtube_url)

                tick("🧠 Gemini analysing transcript")
                response = model.generate_content(
                    f"""
Generate:
1. Short summary
2. Topic-wise insights
3. Actionable takeaways

Transcript:
{transcript}
"""
                )
                st.session_state.insights = response.text

            # ---------- LOCAL VIDEO ----------
            else:
                st.warning(
                    "⚠️ Direct video analysis is not supported with the public Gemini SDK.\n\n"
                    "Please upload the video to YouTube (unlisted) and use the YouTube Link option."
                )
                st.stop()

            status.update(label="✅ Processing completed", state="complete")
            timer_box.success(f"Done in ⏱ {elapsed_time()}")
            st.balloons()

    except Exception as e:
        st.error(str(e))

# ===============================
# OUTPUT
# ===============================
with right:

    if st.session_state.insights:
        st.markdown('<div class="card insight-card">', unsafe_allow_html=True)
        st.subheader("🎯 Topic-wise Insights")
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

        st.markdown('</div>', unsafe_allow_html=True)
