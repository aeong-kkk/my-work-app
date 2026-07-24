"""Streamlit 화면 -- 발주 엑셀 드래그 앤 드롭 → "추가하기" → 샘플 발주현황 리스트

feature1_extract_order.py의 extract_order_records()를 그대로 재사용한다 (기존 기능 코드는 수정하지 않음).
지금은 브라우저 세션 안에서만 결과를 누적해서 보여준다 -- 파일로 저장/중복 제거/정렬은 아직 하지 않는다
(feature-1-spec.md "지금은 뺄 것" 범위와 동일하게, 화면도 지금은 이 범위까지만 다룬다).

화면 위쪽 탭 네비게이션: 지금은 "발주 리스트" 탭 하나뿐이지만, 다른 기능(feature2~7)을
화면에 추가할 때 같은 자리에 탭만 더 넣으면 되도록 구조만 미리 잡아뒀다.

실행: streamlit run streamlit_app.py
"""

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from openai import OpenAI

from feature1_extract_order import OrderFileError, extract_order_records

ENV_PATH = Path(__file__).parent / ".env"
CHAT_MODEL = "gpt-4o-mini"
CONTEXT_PATHS = [Path(__file__).parent / "CLAUDE.md", *sorted((Path(__file__).parent / "specs").glob("*.md"))]

CHATBOT_SYSTEM_PROMPT = """\
너는 이 App(개발샘플현황표 자동화 서비스) 화면에 방문한 사람의 질문에 답하는 안내 챗봇이야.
아래는 이 서비스의 기획 문서와 개발 가이드 전문이야. 이 내용만 근거로 이 서비스가 무엇을 하는지,
어떤 기능이 있는지, 어떻게 쓰는지를 친절하고 간결하게 answer해.
문서에 없는 내용은 추측하지 말고 모른다고 답해. 실제 사내 자료·개인정보는 언급하지 마.

# 참고 문서
{context}
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


_load_dotenv()


@st.cache_resource
def _load_service_context():
    parts = []
    for path in CONTEXT_PATHS:
        if path.exists():
            parts.append(f"## {path.name}\n\n{path.read_text(encoding='utf-8-sig')}")
    return "\n\n---\n\n".join(parts)


def _get_chat_reply(chat_history):
    """chat_history: [{"role": "user"/"assistant", "content": str}, ...]"""
    if not os.environ.get("OPENAI_API_KEY"):
        return "챗봇을 쓰려면 OPENAI_API_KEY가 설정되어 있어야 해요. .env 파일을 확인해주세요."
    try:
        client = OpenAI()
        system_prompt = CHATBOT_SYSTEM_PROMPT.format(context=_load_service_context())
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + chat_history,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"답변을 가져오지 못했어요: {e}"


st.set_page_config(page_title="개발샘플현황표 자동화", page_icon="📦", layout="wide")

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

    [data-testid="stTabs"] {
        margin-top: 1.2rem;
    }
    [data-testid="stTabs"] [data-testid="stTab"] p {
        font-size: 1.15rem;
        font-weight: 600;
        color: #9CA0A8;
        padding: .2rem 0;
    }
    [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p {
        color: #FF5A3C;
        font-weight: 700;
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

    .st-key-floating_chat {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
    }
    .st-key-floating_chat .stButton > button {
        border-radius: 999px;
    }
    </style>

    <div class="hero-badge"><span class="dot"></span>개발샘플</div>
    <div class="hero-title">현황표<br><span class="accent">자동화</span></div>
    """,
    unsafe_allow_html=True,
)

if "records" not in st.session_state:
    st.session_state.records = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기능을 고르는 탭
order_tab, analysis_tab = st.tabs(["발주 리스트", "리드타임 분석"])

with order_tab:
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

with analysis_tab:
    st.markdown(
        '<p class="hero-sub">엑셀 파일을 아래에 끌어다 놓으면 층구성·구분별 리드타임 평균/최대/최소를 요약해서 보여줘요.</p>',
        unsafe_allow_html=True,
    )

    analysis_file = st.file_uploader(
        "분석할 엑셀 파일을 여기에 드래그 앤 드롭하세요",
        type=["xlsx"],
        key="analysis_uploader",
    )

    if analysis_file is None:
        st.caption("아직 업로드된 파일이 없습니다.")
    else:
        try:
            sheets = pd.read_excel(analysis_file, sheet_name=None)
        except Exception as e:
            st.error(f"엑셀 파일을 읽지 못했습니다: {e}")
        else:
            sheet_names = list(sheets.keys())
            sheet_name = sheet_names[0]
            if len(sheet_names) > 1:
                sheet_name = st.selectbox("시트 선택", sheet_names)
            df = sheets[sheet_name]

            if df.empty:
                st.caption("이 시트에는 데이터가 없습니다.")
            else:
                lead_col = "리드타임(일수)" if "리드타임(일수)" in df.columns else None
                group_cols = [c for c in ["층구성", "구분"] if c in df.columns]
                if lead_col and group_cols:
                    st.markdown('<div class="result-heading">리드타임 요약</div>', unsafe_allow_html=True)
                    for group_col in group_cols:
                        lead_summary = (
                            df.groupby(group_col)[lead_col]
                            .agg(건수="count", 평균=lambda s: round(s.mean(), 1), 최대="max", 최소="min")
                            .sort_values("평균", ascending=False)
                        )
                        st.markdown(f"**{group_col}별 리드타임(일수)**")
                        st.dataframe(lead_summary, use_container_width=True)
                        st.bar_chart(lead_summary["평균"])

                with st.expander("원본 데이터 미리보기"):
                    st.dataframe(df, use_container_width=True)

# 화면 우측 아래 떠 있는 챗봇 -- 탭과 무관하게 항상 노출.
# 이 서비스가 뭘 하는 앱인지는 CLAUDE.md·specs/*.md를 읽어서 스스로 파악한 내용을 GPT에게 근거로 준다.
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if st.session_state.chat_open:
    st.markdown(
        """
        <style>
        .st-key-floating_chat {
            width: 360px;
            max-width: 92vw;
            background: #fff;
            border: 1px solid #ECECEA;
            border-radius: 16px;
            box-shadow: 0 12px 32px rgba(0,0,0,.16);
            padding: .9rem .9rem .5rem .9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .st-key-floating_chat {
            width: fit-content;
        }
        .st-key-floating_chat .stButton > button {
            width: 56px;
            height: 56px;
            padding: 0;
            font-size: 1.5rem;
            box-shadow: 0 6px 16px rgba(0,0,0,.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

with st.container(key="floating_chat"):
    if not st.session_state.chat_open:
        if st.button("💬", key="chat_fab_open"):
            st.session_state.chat_open = True
            st.rerun()
    else:
        header_col, close_col = st.columns([5, 1])
        with header_col:
            st.markdown("**무엇이든 물어보세요**")
        with close_col:
            if st.button("✕", key="chat_fab_close"):
                st.session_state.chat_open = False
                st.rerun()

        history_box = st.container(height=300)
        with history_box:
            if not st.session_state.chat_messages:
                st.caption("이 서비스에 대해 궁금한 걸 물어보세요. (예: 이 앱은 뭘 하는 앱이야?)")
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_question = st.chat_input("메시지를 입력하세요", key="chat_input_widget")
        if user_question:
            st.session_state.chat_messages.append({"role": "user", "content": user_question})
            with st.spinner("답변 준비 중..."):
                reply = _get_chat_reply(st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()
