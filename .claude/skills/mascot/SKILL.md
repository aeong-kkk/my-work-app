---
name: mascot
description: 짧은 설명을 받아 OpenAI 이미지 생성 API(gpt-image-1)로 이미지를 만들고 images/ 폴더에 PNG로 저장한다. "마스코트 만들어줘", "이미지 생성해줘" 같은 요청에 사용.
---

# Mascot — AI 이미지 생성 및 저장

## 무엇을
짧은 설명(prompt)을 받아 OpenAI 이미지 생성 API로 이미지를 만들고, `images/` 폴더에 PNG 파일로 저장한다.

## 입력
이미지 설명 텍스트 (사용자가 준 문장, 예: "물방울 모양 귀여운 캐릭터 마스코트"). 설명이 없으면 사용자에게 물어본다. `OPENAI_API_KEY`가 `.env`에 설정돼 있어야 한다.

## 순서
1. `python feature2_generate_image.py "설명"`을 실행한다.
2. 출력된 저장 경로를 확인한다.
3. 생성된 이미지를 사용자에게 보여준다 (이미지 파일 열람).

## 출력
`images/YYYYMMDD-HHMMSS_설명slug.png` 형식으로 저장된 PNG 파일 1개와 저장 경로 안내.
