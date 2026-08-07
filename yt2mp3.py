"""유튜브 링크를 입력하면 mp3로 다운로드하는 프로그램.

사용법:
    python yt2mp3.py <유튜브 URL> [<유튜브 URL> ...]
    또는 인자 없이 실행하면 링크를 입력하라는 프롬프트가 뜬다.
"""

import shutil
import sys
from pathlib import Path

import yt_dlp

DOWNLOAD_DIR = Path(__file__).parent / "downloads"


def find_ffmpeg() -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return str(Path(ffmpeg).parent)

    winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget_root.exists():
        for exe in winget_root.glob("Gyan.FFmpeg_*/**/ffmpeg.exe"):
            return str(exe.parent)
    return None


def download_mp3(url: str) -> None:
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "noplaylist": True,
    }

    ffmpeg_dir = find_ffmpeg()
    if ffmpeg_dir:
        ydl_opts["ffmpeg_location"] = ffmpeg_dir

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main() -> None:
    urls = sys.argv[1:]
    if not urls:
        url = input("유튜브 링크를 입력하세요: ").strip()
        if not url:
            print("링크가 입력되지 않았습니다.")
            return
        urls = [url]

    for url in urls:
        print(f"\n[다운로드 시작] {url}")
        try:
            download_mp3(url)
            print("[완료]")
        except Exception as e:
            print(f"[오류] {url} 다운로드 실패: {e}")


if __name__ == "__main__":
    main()
