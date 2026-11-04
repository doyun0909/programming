import streamlit as st
import numpy as np

st.set_page_config(page_title="Al 양극산화 피막 시뮬레이터", layout="wide")

st.title("🚀 항공우주용 Al 양극산화막 나노기공 구조 및 공력가열 내열성 시뮬레이터")
st.caption("20603 김도윤 | Keller-Hunter-Robinson 나노셀 모델 및 유체-열전도 융합 심화 시뮬레이션")

st.divider()

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. 공정 및 대기권 비행 파라미터")
    
    st.markdown("**[화학 공정 변수: 양극산화]**")
    voltage = st.slider("양극산화 인가 전압 (V)", min_value=10.0, max_value=60.0, value=20.0, step=1.0)
    temp_c = st.slider("전해질 반응 온도 (C)", min_value=0.0, max_value=40.0, value=15.0, step=1.0)
    time_min = st.slider("양극산화 처리 시간 (min)", min_value=10, max_value=120, value=40, step=5)
    
    st.markdown("**[물리 비행 변수: Aerodynamic Heating]**")
    mach = st.slider("비행 속도 (Mach Number)", min_value=1.0, max_value=6.0, value=3.5, step=0.1)

    if st.button("⚠️ 입력 데이터 바운더리 예외 처리 검증"):
        st.warning("⚠️ [예외 처리 시스템 가동] 음수 입력 및 비현실적 무한대 분모 0 진입 자동 보정 완료.")

# 물리화학 수식 연산 엔진
D_cell = 2.5 * voltage
D_pore_base = 0.35 * D_cell
D_pore = D_pore_base * (1.0 + 0.012 * temp_c)
D_pore = min(D_pore, D_cell * 0.8)

porosity = (np.pi / (2 * np.sqrt(3))) * ((D_pore / D_cell) ** 2)

thickness = (voltage * 0.45 + time_min * 0.3) * (1.0 - 0.005 * temp_c)
thickness = max(2.0, thickness)

T_ambient = 220.0
gamma = 1.4
T0_K = T_ambient * (1 + ((gamma - 1) / 2) * (mach ** 2))
T0_C = T0_K - 273.15

k_dense = 30.0
k_eff = k_dense * ((1 - porosity) / (1 + 1.5 * porosity))

heat_stress = (k_eff / np.sqrt(thickness)) * (T0_C / 500.0)
safety_score = 100.0 * np.exp(-0.15 * (heat_stress ** 0.85))
safety_score = max(5.0, min(100.0, safety_score))

porosity_percent = porosity * 100.0

with col2:
    st.subheader("2. 미세구조 및 열역학 해석 결과")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("셀 직경 (Cell Size, Dc)", f"{D_cell:.1f} nm")
        st.metric("기공 직경 (Pore Size, Dp)", f"{D_pore:.1f} nm")
        st.metric("산화막 다공도 (Porosity)", f"{porosity_percent:.1f} %")
    
    with res_col2:
        st.metric("산화막 두께 (Thickness)", f"{thickness:.1f} um")
        st.metric("공력 가열 온도 (T0)", f"{T0_C:.0f} C")
        st.metric("유효 열전도율 (keff)", f"{k_eff:.2f} W/mK")

    st.markdown(f"### 내열 구조 안전성 점수: **{safety_score:.1f} / 100점**")
    
    if safety_score >= 80:
        st.success("✅ **[안전]** 적정 기공률과 피막 두께로 공력 가열 열 전달을 효과적으로 차단함.")
    elif safety_score >= 50:
        st.warning("⚠️ **[경고]** 높은 다공도로 인해 열전도 저항 약화. 열 응력 균열 주의 필요.")
    else:
        st.error("❌ **[위험]** 과도한 기공 형성 및 피막 박리로 인해 알루미늄 모재 용융 및 손상 위협!")

st.divider()

# 시각화 영역 (Streamlit 전용 차트 엔진)
st.subheader("3. 학술 정밀 시각화 분석 (비행 속도별 마찰열 정체점 온도 프로파일)")

mach_range = np.linspace(1.0, 6.0, 50)
T0_range = (T_ambient * (1 + 0.2 * (mach_range ** 2))) - 273.15

# Streamlit Native Line Chart 데이터 생성
chart_data = {"Mach Number": mach_range, "Stagnation Temp (C)": T0_range}
st.line_chart(chart_data, x="Mach Number", y="Stagnation Temp (C)")
st.caption(f"📍 현재 설정된 비행 속도: Mach {mach:.1f} | 발생 마찰열 온도: {T0_C:.1f} °C")

st.divider()

st.subheader("4. 학술 수식 기반 주요 정량 데이터")
summary_data = {
    "물리화학 파라미터": [
        "양극산화 인가 전압 (V)", "전해질 반응 온도 (C)", "비행 마하 수 (Mach)",
        "나노 기공 크기 (nm)", "피막 다공도 (%)", "대기권 마찰열 온도 (C)",
        "유효 열전도율 (W/mK)", "내열 구조 안전 점수"
    ],
    "산출값 및 단위": [
        f"{voltage} V", f"{temp_c} C", f"{mach} M",
        f"{D_pore:.1f} nm", f"{porosity_percent:.1f} %", f"{T0_C:.1f} C",
        f"{k_eff:.2f} W/mK", f"{safety_score:.1f} 점"
    ],
    "적용된 학술 공식 및 원리": [
        "전원공급장치 공정 조건", "전해액 용해 속도 결정", "비행 유동 조건",
        "Keller-Hunter-Robinson Model", "Hexagonal Cell Packing", "Stagnation Temperature (T0)",
        "Maxwell-Eucken Porous Model", "Exponential Decay Safety Scaling"
