---
name: summarize
description: 결과/요약 텍스트를 GPT로 한 줄 요약하고, 원본 내용과 함께 보여준다. "한 줄로 요약해줘" 같은 요청에 사용.
---

# Summarize — 결과 + 한 줄 요약

## 무엇을
결과 텍스트 전체를 GPT로 한 문장 요약하고, 원본 내용과 함께 보여준다.

## 입력
결과 텍스트 파일 1개. 사용자가 지정하지 않으면 연습용 샘플(`practice/sample-result-input.md`)을 사용한다. `OPENAI_API_KEY`가 `.env`에 설정돼 있어야 한다.

## 순서
1. `python feature6_summarize_result.py [파일경로]`를 실행한다 (경로 생략 시 기본 샘플 사용).
2. 출력된 "한 줄 요약"과 "원본 결과"를 사용자에게 그대로 보여준다.

## 출력
한 줄 요약 + 원본 결과 전체.
