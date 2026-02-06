import streamlit as st
import time
import subprocess


from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===============================
# GEMINI CLIENT
# ===============================
import os
import google.generativeai as genai

genai.configure(
    api_key=os.environ["GEMINI_API_KEY"]
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "Summarize this news in simple points"
)

print(response.text)


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
for key in ["insights", "start_time"]:
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
st.caption("⚡ Gemini AI | YouTube & Video Upload Supported")

# ===============================
# HELPER FUNCTIONS
# ===============================

def is_youtube_url(url):
    return url and ("youtube.com" in url or "youtu.be" in url)

def get_youtube_transcript(url):
    video_id = url.split("v=")[-1].split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t["text"] for t in transcript])

def download_youtube_video(url):
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o", VIDEO_FILE, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

def upload_video(file_path, status):
    status.write("⬆️ Uploading video to Gemini")
    video_file = client.files.upload(file=file_path)

    while True:
        file_info = client.files.get(name=video_file.name)
        if file_info.state.name == "ACTIVE":
            break
        time.sleep(3)

    return file_info

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
        with st.status("⏳ Processing video...", expanded=True) as status:
            st.session_state.start_time = time.time()

            # ---------- YOUTUBE ----------
            if option == "YouTube Link":
                try:
                    status.write("📝 Fetching transcript")
                    transcript = get_youtube_transcript(youtube_url)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            f"""
Generate:
1. Short summary
2. Topic-wise insights
3. Actionable takeaways

Transcript:
{transcript}
"""
                        ]
                    )
                    st.session_state.insights = response.text

                except:
                    status.write("⬇️ Transcript failed, downloading video")
                    download_youtube_video(youtube_url)

                    file_info = upload_video(VIDEO_FILE, status)

                    status.write("🎥 Gemini analysing video")
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[file_info, "Generate summary, insights and takeaways"]
                    )
                    st.session_state.insights = response.text

            # ---------- LOCAL VIDEO ----------
            else:
                if uploaded_file is None:
                    st.error("Please upload a video")
                    st.stop()

                with open(VIDEO_FILE, "wb") as f:
                    f.write(uploaded_file.read())

                file_info = upload_video(VIDEO_FILE, status)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[file_info, "Generate summary, insights and takeaways"]
                )
                st.session_state.insights = response.text

            status.update(label="✅ Processing completed", state="complete")
            st.balloons()

    except Exception as e:
        st.error(str(e))

# ===============================
# OUTPUT
# ===============================
with right:
    if os.path.exists(VIDEO_FILE):
        st.subheader("🎬 Video Preview")
        st.video(VIDEO_FILE)

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
                st.download_button("⬇️ Download PDF", f, file_name=PDF_FILE)

        st.markdown('</div>', unsafe_allow_html=True)
