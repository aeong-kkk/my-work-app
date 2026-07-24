"""기능 7 -- 문서 GPT 검증 (OpenAI Chat Completions API)

입력: 검증할 파일 1개 + (선택) 근거/참고 파일 여러 개
동작: GPT에게 사실/논리/누락/톤형식 네 기준으로 문제점만 짚어달라고 요청 (문서를 다시 쓰지는 않음)
출력: 검증 대상 파일과 같은 폴더에 `<파일명>-gpt-review.md`로 저장

이 스크립트는 GPT 쪽 검증만 담당한다. Claude 자신의 독립 검증 및 두 결과 비교는
`/cross-review` 스킬(.claude/skills/cross-review/SKILL.md)이 이어서 수행한다.

API 키: OPENAI_API_KEY 환경변수 또는 이 파일과 같은 폴더의 .env 파일에서 읽음 (기능 2~6과 동일한 키 사용)
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

ENV_PATH = Path(__file__).parent / ".env"
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """\
너는 사내 문서를 검수하는 깐깐한 리뷰어야.
검증 대상 문서를 아래 네 가지 기준으로만 점검해.

- 사실: 숫자·이름·날짜·인용 중 근거 자료로 뒷받침되지 않거나 근거 자료와 다른, 지어낸 것으로 의심되는 부분
- 논리: 문서 안에서 주장과 근거가 맞지 않거나, 단계·설명 사이 흐름이 앞뒤가 안 맞는 부분
- 누락: 이 문서의 목적상 꼭 있어야 하는데 빠진 내용
- 톤·형식: 이 문서를 읽을 사람 기준으로 어색하거나 부적절한 표현·형식

절대 문서를 다시 쓰거나 수정안을 제시하지 마. 오직 문제점 지적만 해.
문제가 없는 항목은 언급하지 마. 근거 자료가 주어졌다면 그것과 비교해서 검증 대상 문서 자체에 있는 문제만 짚어.

출력은 마크다운으로, 다음 형식을 지켜:

## 사실
- **문장**: (문제라고 본 검증 대상 문서의 문장/구절 그대로 인용)
  **문제**: (왜 문제인지 1~2문장)

(논리/누락/톤·형식도 동일한 형식. 해당 기준에서 지적할 게 없으면 "지적 사항 없음"이라고 적어.)

각 지적은 간결하게, 최대 2문장 이내로 "왜 문제인지"를 설명해.
"""


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


def _resolve(path_str):
    path = Path(path_str)
    if not path.is_absolute():
        path = Path(__file__).parent / path
    return path


def build_user_content(target_path, reference_paths):
    parts = [
        f"# 검증 대상 문서 ({target_path.name})\n\n",
        target_path.read_text(encoding="utf-8-sig"),
    ]
    for i, ref in enumerate(reference_paths, start=1):
        parts.append(f"\n\n# 근거 자료 {i} — {ref.name}\n")
        parts.append(ref.read_text(encoding="utf-8-sig"))
    return "".join(parts)


def review(target_path, reference_paths):
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일에 OPENAI_API_KEY=sk-... 를 넣어주세요."
        )
    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_content(target_path, reference_paths)},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    _load_dotenv()

    if len(sys.argv) < 2:
        print("사용법: python feature7_cross_review.py <검증할 파일> [근거 파일 ...]")
        sys.exit(1)

    target = _resolve(sys.argv[1])
    if not target.exists():
        print(f"에러: 파일을 찾을 수 없습니다 - {target}")
        sys.exit(1)

    references = []
    for arg in sys.argv[2:]:
        ref = _resolve(arg)
        if not ref.exists():
            print(f"에러: 근거 파일을 찾을 수 없습니다 - {ref}")
            sys.exit(1)
        references.append(ref)

    try:
        result = review(target, references)
    except Exception as e:
        print(f"에러: {e}")
        sys.exit(1)

    output = target.parent / f"{target.stem}-gpt-review.md"
    header = (
        f"# GPT 검증 결과 — {target.name}\n\n"
        "> 검증 기준: 사실 / 논리 / 누락 / 톤·형식. GPT("
        + MODEL
        + ")가 지적한 문제점만 정리한 결과이며, 문서 자체를 다시 쓴 것은 아닙니다.\n\n"
    )
    output.write_text(header + result + "\n", encoding="utf-8")
    print(f"저장 완료: {output}")
    print()
    print(result)
