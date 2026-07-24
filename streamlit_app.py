"""Streamlit 화면 -- 발주 엑셀 드래그 앤 드롭 → "추가하기" → 샘플 발주현황 리스트

feature1_extract_order.py의 extract_order_records()를 그대로 재사용한다 (기존 기능 코드는 수정하지 않음).
지금은 브라우저 세션 안에서만 결과를 누적해서 보여준다 -- 파일로 저장/중복 제거/정렬은 아직 하지 않는다
(feature-1-spec.md "지금은 뺄 것" 범위와 동일하게, 화면도 지금은 이 범위까지만 다룬다).

실행: streamlit run streamlit_app.py
"""

import pandas as pd
import streamlit as st

from feature1_extract_order import OrderFileError, extract_order_records

st.set_page_config(page_title="샘플발주 내역 리스트화", page_icon="📦", layout="wide")

# 아래는 스타일(색·글꼴·여백·배치)만 담당 -- 화면 구조·기능 로직은 그대로다.
st.markdown(
    """
    <style>
    html, body,
    .stApp *:not([data-testid="stIconMaterial"]) {
        font-family: "Malgun Gothic", "맑은 고딕", sans-serif;
    }

    #MainMenu, header, footer { visibility: hidden; }

    .block-container {
        max-width: 1200px;
        padding-top: 4.5rem;
        padding-bottom: 4rem;
    }

    .hero-badge, .hero-title, .hero-sub {
        max-width: 640px;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .35rem .9rem;
        border-radius: 999px;
        background: #FAFAF9;
        border: 1px solid #ECECEA;
        color: #8A8D93;
        font-size: .72rem;
        font-weight: 600;
        letter-spacing: .08em;
        margin-bottom: 1.6rem;
    }
    .hero-badge .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #FF5A3C;
        display: inline-block;
    }

    .hero-title {
        font-size: 2.6rem;
        line-height: 1.18;
        font-weight: 700;
        color: #14161A;
        letter-spacing: -0.02em;
        margin: 0 0 .8rem 0;
    }
    .hero-title .accent {
        font-style: italic;
        font-weight: 600;
        color: #FF5A3C;
    }

    .hero-sub {
        color: #6B6E75;
        font-size: .95rem;
        margin: 0 0 .6rem 0;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: #FAFAF9 !important;
        border: 1.5px dashed #E3E3E1 !important;
        border-radius: 18px !important;
    }
    [data-testid="stWidgetLabel"] p {
        color: #8A8D93 !important;
        font-size: .95rem !important;
    }

    .stButton > button {
        background: #14161A;
        color: #fff;
        border: none;
        border-radius: 999px;
        padding: .55rem 1.7rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: #33353b;
        color: #fff;
    }

    .result-heading {
        font-size: 1.05rem;
        font-weight: 700;
        color: #14161A;
        margin-top: 3rem;
        margin-bottom: .9rem;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #ECECEA;
        border-radius: 14px;
        overflow: hidden;
    }
    </style>

    <div class="hero-badge"><span class="dot"></span>샘플</div>
    <div class="hero-title">발주 내역<br><span class="accent">리스트화</span></div>
    """,
    unsafe_allow_html=True,
)

if "records" not in st.session_state:
    st.session_state.records = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    '<p class="hero-sub">발주 엑셀(.xlsx) 파일을 아래에 끌어다 놓고 "추가하기"를 누르면 발주 내역이 자동으로 정리돼요.</p>',
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "수주시트를 여기에 드래그 앤 드롭하세요",
    type=["xlsx"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
)

if st.button("추가하기", type="primary"):
    messages = []
    if not uploaded_files:
        messages.append(("warning", "먼저 발주 엑셀 파일을 넣어주세요."))
        st.session_state.messages = messages
    else:
        added = 0
        for uploaded_file in uploaded_files:
            try:
                records = extract_order_records(uploaded_file)
            except OrderFileError as e:
                messages.append(("error", f"{uploaded_file.name}: {e} — 이 파일은 건너뜁니다."))
                continue
            for record in records:
                st.session_state.records.append({"파일": uploaded_file.name, **record})
                if record["비고"]:
                    messages.append(("warning", f"{uploaded_file.name}: 필수 항목이 비어 있습니다 ({record['비고']})"))
            added += len(records)
        if added:
            messages.append(("success", f"{added}건 추가했습니다."))
        st.session_state.messages = messages
        # 처리 완료 후 입력칸이 비도록 업로더를 새 key로 교체하고 다시 그린다
        st.session_state.uploader_key += 1
        st.rerun()

for level, text in st.session_state.messages:
    getattr(st, level)(text)

st.markdown('<div class="result-heading">샘플 발주현황 리스트</div>', unsafe_allow_html=True)
COLUMN_ORDER = ["파일", "구분", "발주일", "요청일", "모델명", "내부명", "층구성", "Total-T", "수량", "리드타임(일수)", "비고"]

if st.session_state.records:
    result_df = pd.DataFrame(st.session_state.records)[COLUMN_ORDER]
    st.dataframe(result_df, use_container_width=True)

    st.download_button(
        "결과 다운로드 (CSV)",
        data=result_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="샘플발주현황.csv",
        mime="text/csv",
    )
    with st.expander("표 복사하기 (엑셀에 붙여넣기)"):
        st.code(result_df.to_csv(index=False, sep="\t"), language=None)
else:
    st.caption("아직 추가된 발주 건이 없습니다.")
