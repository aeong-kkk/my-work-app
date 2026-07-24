---
name: highlights
description: 결과/요약 텍스트에서 GPT로 핵심 항목만 뽑아 보여준다. 사소한 세부사항은 제외한다. "핵심만 뽑아줘", "중요한 것만 보여줘" 같은 요청에 사용.
---

# Highlights — 핵심 항목만 추출

## 무엇을
결과/요약 텍스트에서 사소한 세부사항은 빼고 핵심 항목만 GPT로 뽑아 보여준다.

## 입력
결과 텍스트 파일 1개. 사용자가 지정하지 않으면 연습용 샘플(`practice/sample-result-input.md`)을 사용한다. `OPENAI_API_KEY`가 `.env`에 설정돼 있어야 한다.

## 순서
1. `python feature5_extract_key_points.py [파일경로]`를 실행한다 (경로 생략 시 기본 샘플 사용).
2. 출력된 핵심 항목 목록을 사용자에게 그대로 보여준다.

## 출력
핵심 항목만 담긴 번호 목록.
