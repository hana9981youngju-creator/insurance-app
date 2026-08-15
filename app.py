import io
from PIL import Image
from pypdf import PdfReader
import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="AI 스마트 보험 보장분석", page_icon="📑", layout="centered")

st.title("📑 AI 스마트 보험 보장분석")
st.write("보험 가입현황표 **이미지(JPG/PNG)** 또는 **PDF 파일**을 업로드하면 전문 분석 리포트를 생성합니다.")

# 사이드바 API Key 입력
api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")
st.sidebar.markdown("[👉 API Key 무료 발급받기](https://aistudio.google.com/apikey)")

# 파일 업로더
uploaded_file = st.file_uploader("가입현황표 파일을 올려주세요 (PNG, JPG, PDF)", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    pdf_text = ""
    image_list = []

    if file_type == 'pdf':
        st.success(f"📄 PDF 문서가 업로드되었습니다: {uploaded_file.name}")
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
    else:
        image = Image.open(uploaded_file)
        image_list.append(image)
        st.image(image, caption="업로드된 가입현황표", use_container_width=True)

    if st.button("🚀 보장분석 리포트 생성하기", type="primary"):
        if not api_key:
            st.error("좌측 사이드바에 Gemini API Key를 먼저 입력해 주세요!")
        else:
            with st.spinner("AI가 보험 가입 내역을 정밀 분석하고 있습니다... (약 10~20초 소요)"):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")

                    prompt = """
                    당신은 대한민국 20년 경력의 베테랑 독립보험대리점(GA) 수석 보험설계사이자 보장분석 전문가입니다.
                    제공된 보험 가입현황 데이터를 정밀 분석하여 아래 양식에 맞춘 마크다운 리포트를 작성해주세요.

                    [리포트 출력 형식]
                    ## 📊 1. 종합 총평 및 핵심 요약
                    - 고객 기본 정보 (성함, 연령, 성별, 총 보험료, 정상 계약 건수)
                    - 핵심 요약 3~4줄 (과다/부족/핵심 특징)

                    ## 🔍 2. 영역별 상세 보장 진단
                    - **사망/장해**: 가입금액 및 연령 대비 적정성
                    - **3대 질병 진단비**: 일반암/유사암, 뇌혈관/뇌졸중/뇌출혈, 허혈성/급성심근경색 범위 및 금액 평가
                    - **실손의료비**: 세대 판별 및 유지 권장 여부
                    - **수술비 및 치료비**: 질병/상해 종수술비, 최신 표적항암/비급여 방사선 치료비 여부

                    ## 📋 3. 가입 상품별 진단 및 관리 전략
                    (표 형태로 정리: 상품명/가입시기 | 월 보험료 | 권장 방향(유지/감액/정리/실손분리) 및 이유)

                    ## 💡 4. 전문가의 리모델링 추천 방향
                    (구체적인 실천 권장사항 3가지)
                    """

                    contents = [prompt]
                    if file_type == 'pdf':
                        contents.append(f"다음은 고객의 보험 가입내역 데이터입니다:\n\n{pdf_text}")
                    else:
                        contents.extend(image_list)

                    response = model.generate_content(contents)
                    st.success("✅ 분석이 완료되었습니다!")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
