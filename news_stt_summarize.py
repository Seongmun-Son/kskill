"""
Groq Whisper-large-v3 STT -> 뉴스 요약 자동화 스크립트

사용법:
    python news_stt_summarize.py <오디오파일경로>

.env(.txt) 파일에서 GROK_API_KEY 를 읽어 Groq API를 호출한다.
1) audio.transcriptions (whisper-large-v3) 로 음성을 텍스트로 변환
2) chat.completions (llama-3.3-70b-versatile) 로 변환된 텍스트를 요약
"""

import os
import sys
import json
import requests

from supabase_client import save_result

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
STT_MODEL = "whisper-large-v3"
CHAT_MODEL = "llama-3.3-70b-versatile"


def load_api_key() -> str:
    candidates = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", "04_stt", ".env.txt"),
        os.path.join(os.path.dirname(__file__), "..", "04_stt", ".env"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GROK_API_KEY="):
                        return line.split("=", 1)[1].strip()
    raise RuntimeError("GROK_API_KEY를 .env 파일에서 찾을 수 없습니다.")


def transcribe(audio_path: str, api_key: str) -> str:
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {"model": STT_MODEL, "response_format": "json"}
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.post(GROQ_STT_URL, headers=headers, files=files, data=data, timeout=300)
    resp.raise_for_status()
    return resp.json()["text"]


def summarize(text: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "당신은 회의록/뉴스 요약 전문가입니다. 주어진 음성 전사 내용을 "
                    "한국어로 아래 마크다운 형식에 '정확히' 맞춰 요약하세요. "
                    "형식 이외의 서두/맺음말은 절대 추가하지 마세요.\n\n"
                    "# (내용을 대표하는 제목)\n"
                    "## 핵심 한 문장\n"
                    "(전체 내용을 한 문장으로 요약)\n"
                    "## 회의가 끝난 다음에 해야할 일\n"
                    "- [ ] 할일 1\n"
                    "- [ ] 할일 2\n\n"
                    "'해야할 일'은 전사 내용에서 실제로 언급되거나 합리적으로 도출되는 "
                    "후속 조치/액션 아이템만 적으세요. 해당되는 내용이 없으면 "
                    "'- [ ] 해당 없음' 한 줄만 남기세요."
                ),
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.3,
    }
    resp = requests.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    if len(sys.argv) < 2:
        print("사용법: python news_stt_summarize.py <오디오파일경로>")
        sys.exit(1)

    audio_path = sys.argv[1]
    if not os.path.isfile(audio_path):
        print(f"파일을 찾을 수 없습니다: {audio_path}")
        sys.exit(1)

    api_key = load_api_key()

    print("[1/2] Groq Whisper-large-v3로 음성 인식 중...")
    transcript = transcribe(audio_path, api_key)
    transcript_path = os.path.splitext(audio_path)[0] + "_transcript.txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"  -> 전사 결과 저장: {transcript_path}")

    print("[2/2] 뉴스 내용 요약 중...")
    summary = summarize(transcript, api_key)
    summary_path = os.path.splitext(audio_path)[0] + "_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"  -> 요약 저장: {summary_path}")

    save_result(source=os.path.basename(audio_path), transcript=transcript, summary=summary)

    print("\n===== 요약 결과 =====\n")
    print(summary)


if __name__ == "__main__":
    main()
