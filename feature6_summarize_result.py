"""기능 6 -- 결과를 한 줄 요약과 함께 보여주기 (OpenAI Chat Completions API)

입력: 결과/요약 텍스트 파일 1개
동작: GPT에게 전체 내용을 한 문장으로 요약해달라고 요청
출력: 원본 결과 내용 + 한 줄 요약을 함께 화면에 출력 (파일/화면 저장은 하지 않음)

API 키: OPENAI_API_KEY 환경변수 또는 이 파일과 같은 폴더의 .env 파일에서 읽음 (기능 2·3·4·5와 동일한 키 사용)
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

SAMPLE_INPUT = Path(__file__).parent / "practice" / "sample-result-input.md"
ENV_PATH = Path(__file__).parent / ".env"
MODEL = "gpt-4o-mini"


def _load_dotenv(path=ENV_PATH):
    """.env 파일이 있으면 KEY=VALUE 줄을 읽어 환경변수로 등록한다 (이미 설정된 값은 덮어쓰지 않음)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def summarize_one_line(text):
    """결과 텍스트 전체를 한 문장으로 요약한다."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일에 OPENAI_API_KEY=sk-... 를 넣어주세요."
        )

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "너는 결과 텍스트를 한 문장으로 요약하는 도우미야. 정확히 한 줄(한 문장)로만 답해.",
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    _load_dotenv()

    target = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_INPUT
    path = Path(target)
    if not path.is_absolute():
        path = Path(__file__).parent / target

    if not path.exists():
        print(f"에러: 파일을 찾을 수 없습니다 - {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8-sig")

    try:
        one_liner = summarize_one_line(text)
    except Exception as e:
        print(f"에러: {e}")
        sys.exit(1)

    print(f"[입력 파일] {path.name}\n")
    print(f"한 줄 요약: {one_liner}\n")
    print("원본 결과:")
    print(text)
