import os
import time
import subprocess
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# ===============================
# 1. GEMINI CLIENT
# ===============================

client = genai.Client()

# ===============================
# 2. HELPER FUNCTIONS
# ===============================

def is_youtube_url(path: str) -> bool:
    return path.startswith("http") and "youtube.com" in path or "youtu.be" in path


def download_youtube_video(url, output_name="temp_video.mp4"):
    print("⬇️ Downloading YouTube video...")
    subprocess.run([
        "yt-dlp",
        "-f", "mp4",
        "-o", output_name,
        url
    ], check=True)
    return output_name


def get_youtube_transcript(url):
    video_id = url.split("v=")[-1].split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([i["text"] for i in transcript])


def upload_and_wait(file_path):
    print("⬆️ Uploading video to Gemini...")
    video_file = client.files.upload(file=file_path)

    while True:
        file_info = client.files.get(name=video_file.name)
        print("⏳ Current state:", file_info.state.name)

        if file_info.state.name == "ACTIVE":
            break

        time.sleep(5)

    print("✅ Video ready")
    return file_info


# ===============================
# 3. MAIN FUNCTION (MAGIC 🔥)
# ===============================

def summarize_video(source):
    """
    source:
      - Local video path  (C:/video/news.mp4)
      - OR YouTube link   (https://youtube.com/...)
    """

    # -------------------------------
    # CASE 1: YOUTUBE LINK
    # -------------------------------
    if is_youtube_url(source):
        print("🌐 Detected YouTube link")

        try:
            transcript_text = get_youtube_transcript(source)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "Summarize this news in simple bullet points:\n",
                    transcript_text
                ]
            )

            return response.text

        except Exception as e:
            print("⚠️ Transcript failed, falling back to video download...")
            local_video = download_youtube_video(source)
            file_info = upload_and_wait(local_video)

    # -------------------------------
    # CASE 2: LOCAL FILE
    # -------------------------------
    else:
        if not os.path.isfile(source):
            raise FileNotFoundError("❌ Invalid local file path")

        print("📁 Detected local video file")
        file_info = upload_and_wait(source)

    # -------------------------------
    # VIDEO → GEMINI SUMMARY
    # -------------------------------
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            file_info,
            "Summarize this news video in simple bullet points"
        ]
    )

    return response.text


# ===============================
# 4. USAGE EXAMPLES
# ===============================

# 👉 Example 1: YouTube link
video_source = "https://www.youtube.com/watch?v=gP4ki8m8EZg"

# 👉 Example 2: Local file
# video_source = r"C:\Users\ANTON\news.mp4"

summary = summarize_video(video_source)

print("\n📌 VIDEO SUMMARY:\n")
print(summary)
