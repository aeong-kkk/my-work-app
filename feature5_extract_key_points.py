"""기능 5 -- 결과에서 핵심 항목만 뽑아 보여주기 (OpenAI Chat Completions API)

입력: 결과/요약 텍스트 파일 1개 (중요한 항목과 사소한 항목이 섞여 있음)
동작: GPT에게 그중 핵심 항목만 골라달라고 요청 (사소한 세부사항은 제외)
출력: 핵심 항목 목록만 화면에 출력 (파일/화면 저장은 하지 않음)

API 키: OPENAI_API_KEY 환경변수 또는 이 파일과 같은 폴더의 .env 파일에서 읽음 (기능 2·3·4와 동일한 키 사용)
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


def extract_key_points(text):
    """텍스트에서 핵심 항목만 골라 목록으로 반환한다 (사소한 세부사항은 제외)."""
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
                "content": (
                    "너는 결과/요약 텍스트에서 핵심 항목만 뽑아내는 도우미야. "
                    "사소하거나 부수적인 내용은 제외해. "
                    "결과는 각 줄이 '- '로 시작하는 목록으로만 답해. 목록 외 다른 말은 하지 마."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()
    return [line.lstrip("-• ").strip() for line in answer.splitlines() if line.strip()]


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
        key_points = extract_key_points(text)
    except Exception as e:
        print(f"에러: {e}")
        sys.exit(1)

    print(f"[입력 파일] {path.name}\n")
    if not key_points:
        print("핵심 항목이 없습니다.")
    else:
        print("핵심 항목:")
        for i, point in enumerate(key_points, 1):
            print(f"{i}. {point}")
