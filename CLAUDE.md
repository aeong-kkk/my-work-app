# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 명령어

이 저장소엔 빌드 시스템·린터·테스트가 없습니다 — 독립적인 파이썬 스크립트 몇 개로만 이루어져 있습니다.

- 의존성 설치 (가상환경 없이 그냥 pip 사용): `pip install -r requirements.txt` (또는 `pip install openpyxl openai pandas streamlit`) — 다른 곳에서 그대로 돌릴 수 있도록 실제 사용 중인 패키지·버전을 `requirements.txt`에 고정해둠. 새 패키지를 실제로 import해서 쓰게 되면 `requirements.txt`도 같이 업데이트할 것
- 기능 1 실행 (발주 엑셀 → 리드타임 계산): `python feature1_extract_order.py [엑셀파일경로]` — 경로를 안 주면 기본값으로 `inputs/sample-order-input.xlsx`를 읽음
- 기능 2 실행 (AI 이미지 생성): `python feature2_generate_image.py "이미지 설명"` — 인자를 안 주면 대화형으로 입력받음
- 기능 3 실행 (메모 AI 카테고리 분류): `python feature3_categorize_memos.py` — 인자 없음, `practice/memos/` 폴더의 `.md` 파일을 전부 읽음
- 기능 4 실행 (요약에서 '오늘 할 일'만 추출): `python feature4_extract_todos.py [요약파일경로]` — 경로를 안 주면 기본값으로 `practice/sample-summary-input.md`를 읽음
- 기능 5 실행 (결과에서 핵심 항목만 추출): `python feature5_extract_key_points.py [결과파일경로]` — 경로를 안 주면 기본값으로 `practice/sample-result-input.md`를 읽음
- 기능 6 실행 (결과 + 한 줄 요약): `python feature6_summarize_result.py [결과파일경로]` — 경로를 안 주면 기본값으로 `practice/sample-result-input.md`를 읽음
- 기능 7 실행 (문서 GPT 검증): `python feature7_cross_review.py <검증할 파일> [근거 파일 ...]` — GPT가 사실/논리/누락/톤형식 네 기준으로 문제점만 짚어 대상 파일과 같은 폴더에 `<파일명>-gpt-review.md`로 저장 (원본은 다시 쓰지 않음). Claude 자신의 독립 검증과 두 결과 비교는 `/cross-review` 스킬이 이어서 수행

기능 2, 3, 4, 5, 6, 7은 `OPENAI_API_KEY`가 필요합니다 (아래 참고).

- 웹 화면 실행 (Streamlit): `streamlit run streamlit_app.py` — 터미널 없이 브라우저에서 발주 엑셀을 드래그 앤 드롭(여러 개 가능)으로 넣고 "추가하기"를 누르면 기능 1(`extract_order_records`)을 그대로 호출해 결과를 아래 "샘플 발주현황 리스트" 표에 누적해서 보여줌. 브라우저 세션 안에서만 유지되고, 파일 저장·중복 제거·정렬은 하지 않음

## 아키텍처

**독립된 스크립트 6개, 공용 모듈 없음.** `feature1_extract_order.py` ~ `feature6_summarize_result.py`는 각각 그 자체로 완결되어 있고 바로 실행 가능합니다(`if __name__ == "__main__"` 진입점). `_load_dotenv()` 같은 작은 헬퍼 함수는 feature2~6에 일부러 중복 구현되어 있습니다 — 공용 모듈로 뽑아내지 않은 것은 의도된 선택이므로, 별도 요청이 없다면 새 기능 스크립트를 추가할 때도 이 패턴(중복 허용, 공용 import 지양)을 유지하세요. 각 스크립트는 같은 이름의 Claude Code 스킬(`.claude/skills/<이름>/SKILL.md`)로도 등록되어 있습니다: `/leadtime`(기능1), `/mascot`(기능2), `/categorize`(기능3), `/todos`(기능4), `/highlights`(기능5), `/summarize`(기능6), `/cross-review`(기능7 — GPT 검증 스크립트 실행 후 Claude 자신의 독립 검증·비교까지 스킬 안에서 이어서 수행하는 점이 다른 기능들과 다름).

**스펙 기반 개발:** 기획 문서는 `specs/`에 있습니다. `specs/feature-1-spec.md`는 기능 1의 명세이고, 그 안의 번호 매겨진 "동작" 단계는 `feature1_extract_order.py`의 `# N.` 인라인 주석과 1:1로 대응합니다 — 기능 1의 동작을 바꿀 때는 스펙과 코드를 같이 수정하세요. `specs/sample-order-listing-plan.md`, `specs/sample-order-listing-flow.md`는 "개발샘플현황표 자동화"라는 더 큰 전체 흐름을 설명하며, 기능 1은 그중 첫 조각일 뿐입니다 (중복 제거, 리스트 파일 누적 저장 같은 나머지 단계는 지금은 범위 밖 — feature-1-spec.md의 "지금은 뺄 것" 참고). 드래그앤드롭 화면과 다중 파일 입력은 `streamlit_app.py`로 붙였습니다 — `feature1_extract_order.py`의 `extract_order_records()`를 그대로 재사용하는 얇은 화면 레이어이고, 결과는 세션 안에서만 누적됩니다(새로고침하면 초기화, 파일 저장·중복 제거·정렬 없음). 다른 기능처럼 `feature`N 번호나 `.claude/skills/` 스킬로 등록되어 있지 않고 `streamlit run streamlit_app.py`로 직접 실행합니다. 기능 2~6은 기획서 범위 밖에서 추가로 요청받아 붙인 유틸리티 기능이라 `specs/`에 별도 명세 문서가 없습니다. `practice/repetitive-task-automation-candidates.md`(기획서 범위 밖이라 practice로 이동됨)에는 다른 자동화 후보들 대신 왜 이 프로젝트를 선택했는지가 기록돼 있습니다.

**기능 1은 엑셀 템플릿의 셀 위치를 하드코딩해서 읽습니다** (Info 시트 1개뿐 — 예전엔 별도 Packing 시트가 있었지만 지금은 Info 시트 안 "Shipping Information" 구역으로 통합됨): `G1`=발주일, `F3`=구분(New/Repeat), `F5`=모델명(Customer Model Name), `F6`=내부명(Internal Model Name), `G18`=Total-T(板厚), `G19`=층구성(层构成), 수량·요청일은 항상 "Shipping Information" 구역의 `I`열(수량)/`M`열(요청일), 3행부터(단일 발주든 분할 발주든 구분 없이 이 구역 하나로 처리 — 행이 1개면 단일, 여러 개면 분할). 리드타임은 `요청일 - 발주일`로 계산합니다. 행이 여러 개인데 요청일이 서로 다르면, 그중 가장 늦은 요청일인 행만 구분 값을 "분할입고"로 덮어씁니다(원래 신규발주/재발주였는지와 무관). 원본 엑셀 양식이 바뀌면 `feature1_extract_order.py`의 셀 상수(`SHIPPING_INFO_START_ROW`/`SHIPPING_QTY_COL`/`SHIPPING_DATE_COL` 및 `G1`/`F3`/`F5`/`F6`/`G19`)와 `specs/sample-order-listing-flow.md`의 매핑 표를 같이 업데이트해야 합니다. `inputs/New-2.xlsx`가 현재 기준이 되는 참고 양식(파일)입니다. 이 저장소 밖에 이보다 오래된 양식 파일(`New.xlsx`, `New-1.xlsx` 등 — Packing 시트가 별도로 있거나 층구성이 `G21`인 버전)이 남아있을 수 있는데, 그건 템플릿으로 쓰면 안 됩니다.

**OpenAI API 키 로딩:** `python-dotenv` 없이, 키가 필요한 각 스크립트가 자체 `_load_dotenv()`로 옆에 있는 `.env` 파일을 직접 파싱합니다. 이때 `utf-8-sig`로 읽는데, PowerShell의 `Out-File`이 UTF-8 BOM을 붙여서 저장하기 때문에 일반 `utf-8`로 읽으면 첫 번째 키 이름 앞에 BOM이 붙어버리는 문제가 있었습니다. `.env.example`이 형식 예시이고, 실제 `.env`엔 진짜 키가 들어있으니 절대 공유하거나 커밋하면 안 됩니다.

**폴더 구성:**
- `inputs/` — 기능 1용 테스트 엑셀 파일 (기획서에 나오는 "진짜 App" 입력만)
- `specs/` — 기획/명세 문서 (기획서 본문에 해당하는 것만)
- `outputs/` — 앞으로 결과를 저장할 자리로 미리 만들어둠, 지금은 비어 있음 (기능 1이 아직 데이터를 반환/출력만 하고 파일로 저장하진 않기 때문)
- `images/` — 기능 2가 생성한 이미지, 파일명 형식은 `YYYYMMDD-HHMMSS_<설명을 slug화한 값>.png`
- `practice/` — 기획서 범위 밖의 연습/데모 자료 모음 (아래 참고)

**`practice/` 안의 예외 — 이름은 연습용이지만 실제로 코드가 참조함:** `practice/memos/`는 기능 3(`/categorize`)이 기본으로 읽는 폴더이고, `practice/sample-summary-input.md`는 기능 4(`/todos`), `practice/sample-result-input.md`는 기능 5·6(`/highlights`, `/summarize`)의 기본 입력입니다. 각 스크립트의 `MEMOS_DIR`/`SAMPLE_INPUT` 상수가 이 경로를 가리키므로, `practice/`를 통째로 지우거나 옮기면 해당 스킬이 멈춥니다.

**그 외 `practice/`는 완전히 무관한 자료:** `practice/inbox/`, `practice/organized/`, `practice/weekly-report-2.md`, `practice/d2_*.txt`/`.xlsx`, `practice/sales-report.*`는 이 파이썬 앱과 별개인 메모 정리·주간보고 워크플로 데모입니다. 카테고리별 하위 폴더(`meeting`/`ideas`/`todo`/`research`/`feedback`)로 정리되며, 관련 Claude Code 스킬 `.claude/skills/weekly-summary/SKILL.md`는 (`.claude`는 옮기지 않는다는 규칙 때문에) 여전히 루트에 남아 있습니다 — 이 역시 기획서와 무관한 워크플로입니다.

## 작업 규칙

**절대 규칙 (항상 지킬 것):**
- 항상 한국어로, 공손하고 간결하게 답하고, 추측하지 말고 모르면 모른다고 말할 것.
- 실명·실제 사내 자료는 절대 넣지 않기 — 연습/테스트는 항상 가짜 데이터로.

**세부 규칙 인덱스:**
- 역할 규칙 → `rules/role.md`
- 말투 규칙 → `rules/tone.md`
- 결과 형식 규칙 → `rules/format.md`
- 하지 말 것 규칙 → `rules/dont.md`

**우선순위:** 규칙이 서로 부딪치면 `dont.md` → `format.md` → `tone.md` → `role.md` 순으로 따릅니다.
