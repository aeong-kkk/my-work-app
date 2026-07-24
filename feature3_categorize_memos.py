"""기능 3 -- 메모에 AI로 카테고리 붙이기 (OpenAI Chat Completions API)

입력: memos/ 폴더의 메모 파일들 (.md)
동작: 각 메모 내용을 GPT에 보내 정해진 카테고리 중 하나로 분류
출력: 파일명 + 제목 + 분류된 카테고리를 표로 보여줌 (파일/화면 저장은 하지 않음)

API 키: OPENAI_API_KEY 환경변수 또는 이 파일과 같은 폴더의 .env 파일에서 읽음 (기능 2와 동일한 키 사용)
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

MEMOS_DIR = Path(__file__).parent / "practice" / "memos"
ENV_PATH = Path(__file__).parent / ".env"
MODEL = "gpt-4o-mini"

CATEGORIES = ["회의", "아이디어", "할일", "리서치", "피드백", "기타"]


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


def _read_memo(path):
    text = path.read_text(encoding="utf-8-sig").strip()
    lines = text.splitlines()
    title = lines[0].lstrip("#").strip() if lines else path.stem
    return title, text


def classify_memo(client, content):
    """메모 내용을 GPT에 보내 정해진 카테고리 중 하나로 분류한다."""
    prompt = (
        "다음 메모를 아래 카테고리 중 하나로 분류해줘. 카테고리 이름만 정확히 답해줘.\n"
        f"카테고리: {', '.join(CATEGORIES)}\n\n"
        f"메모:\n{content}"
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "너는 업무 메모를 정해진 카테고리로 분류하는 도우미야. 카테고리 이름 하나만 답해."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()
    for category in CATEGORIES:
        if category in answer:
            return category
    return "기타"


def categorize_memos(memos_dir=MEMOS_DIR):
    """memos 폴더의 모든 메모를 읽어 (파일명, 제목, 카테고리) 리스트로 반환한다."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일에 OPENAI_API_KEY=sk-... 를 넣어주세요."
        )

    client = OpenAI()
    memo_files = sorted(Path(memos_dir).glob("*.md"))

    results = []
    for path in memo_files:
        title, content = _read_memo(path)
        category = classify_memo(client, content)
        results.append({"파일명": path.name, "제목": title, "카테고리": category})
    return results


def print_results(records):
    columns = ["파일명", "제목", "카테고리"]
    widths = {
        c: max([len(c)] + [len(str(r[c])) for r in records]) if records else len(c)
        for c in columns
    }

    header = " | ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-+-".join("-" * widths[c] for c in columns))
    for r in records:
        print(" | ".join(str(r[c]).ljust(widths[c]) for c in columns))


if __name__ == "__main__":
    _load_dotenv()

    try:
        records = categorize_memos()
    except Exception as e:
        print(f"에러: {e}")
        sys.exit(1)

    if not records:
        print(f"{MEMOS_DIR.name} 폴더에 메모 파일(.md)이 없습니다.")
        sys.exit(0)

    print_results(records)
