"""기능 2 -- AI로 이미지를 만들어 저장 (OpenAI 이미지 생성 API)

입력: 이미지 설명 텍스트 (프롬프트)
동작: OpenAI 이미지 생성 API(gpt-image-1) 호출 -> 받은 이미지를 PNG로 디코딩
출력: images/ 폴더에 PNG 파일로 저장 (저장된 경로 반환)

API 키: OPENAI_API_KEY 환경변수 또는 이 파일과 같은 폴더의 .env 파일에서 읽음
        (.env 예시는 .env.example 참고 -- 실제 키가 든 .env는 절대 공유/커밋하지 말 것)
"""

import base64
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

IMAGES_DIR = Path(__file__).parent / "images"
ENV_PATH = Path(__file__).parent / ".env"


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


def _slugify(text, max_len=40):
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", text).strip("-")
    return slug[:max_len] or "image"


def generate_image(prompt, output_dir=IMAGES_DIR, size="1024x1024"):
    """설명(prompt)으로 이미지를 생성해 PNG로 저장하고, 저장된 파일 경로를 반환한다."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. "
            "환경변수로 설정하거나 이 파일과 같은 폴더에 .env 파일을 만들어 "
            "OPENAI_API_KEY=sk-... 형태로 넣어주세요."
        )

    client = OpenAI()

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        n=1,
    )

    image_bytes = base64.b64decode(response.data[0].b64_json)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}_{_slugify(prompt)}.png"
    path = output_dir / filename
    path.write_bytes(image_bytes)

    return path


if __name__ == "__main__":
    _load_dotenv()

    prompt = " ".join(sys.argv[1:]).strip()
    if not prompt:
        prompt = input("이미지 설명을 입력하세요: ").strip()

    if not prompt:
        print("에러: 설명(prompt)이 비어 있습니다.")
        sys.exit(1)

    try:
        saved_path = generate_image(prompt)
    except Exception as e:
        print(f"에러: 이미지 생성 실패 - {e}")
        sys.exit(1)

    print(f"이미지 저장됨: {saved_path}")
