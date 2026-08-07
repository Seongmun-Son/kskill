"""mp3 파일을 텍스트로 전사(transcribe)하는 프로그램.

사용법:
    python transcribe.py <mp3_경로> [--model small]
"""

import argparse
from pathlib import Path

from faster_whisper import WhisperModel


def transcribe(audio_path: str, model_size: str = "small") -> str:
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, language="ko", vad_filter=True)

    print(f"감지 언어: {info.language} (확률 {info.language_probability:.2f})")

    lines = []
    for seg in segments:
        line = f"[{seg.start:7.2f}s -> {seg.end:7.2f}s] {seg.text.strip()}"
        print(line)
        lines.append(seg.text.strip())

    return " ".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="mp3 파일 경로")
    parser.add_argument("--model", default="small", help="whisper 모델 크기 (tiny/base/small/medium/large)")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    text = transcribe(str(audio_path), args.model)

    out_path = audio_path.with_suffix(".txt")
    out_path.write_text(text, encoding="utf-8")
    print(f"\n[전사 완료] 저장 위치: {out_path}")


if __name__ == "__main__":
    main()
