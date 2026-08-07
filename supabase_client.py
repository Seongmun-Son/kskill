"""Supabase 클라이언트 연결 및 전사/요약 결과 저장 헬퍼.

.env 파일에서 SUPABASE_URL, SUPABASE_KEY 를 읽어 클라이언트를 생성한다.
값이 비어 있으면 get_client() 가 None 을 반환하므로, 호출부에서 이를
확인하고 저장을 건너뛰도록 처리한다 (Supabase 미설정 상태에서도
기존 스크립트가 그대로 동작해야 하기 때문).
"""

import os
from typing import Optional

from supabase import create_client, Client


def _load_env(key: str) -> str:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
    return os.environ.get(key, "")


def get_client() -> Optional[Client]:
    url = _load_env("SUPABASE_URL")
    key = _load_env("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def save_result(source: str, transcript: str, summary: str) -> None:
    """transcripts 테이블에 전사/요약 결과를 저장한다.

    Supabase 설정이 없으면 조용히 건너뛴다.
    """
    client = get_client()
    if client is None:
        print("  (Supabase 미설정: DB 저장을 건너뜁니다. .env 의 SUPABASE_URL/SUPABASE_KEY 를 채워주세요.)")
        return

    client.table("transcripts").insert(
        {
            "source": source,
            "transcript": transcript,
            "summary": summary,
        }
    ).execute()
    print("  -> Supabase 'transcripts' 테이블에 저장 완료")
