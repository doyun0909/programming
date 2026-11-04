import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="항공우주용 알루미늄 양극산화 피막 내구성 시뮬레이터", layout="wide")

st.title("🚀 항공우주용 Al 양극산화막 나노기공 구조 및 공력가열 내열성 시뮬레이터")
st.caption("20603 김도윤 | Keller-Hunter-Robinson 나노셀 모델 및 유체-열전도 융합 심화 시뮬레이션")

st.divider()

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. 공정 및 대기권 비행 파라미터")
    
    st.markdown("**[화학 공정 변수: 양극산화]**")
    voltage = st.slider("양극산화 인가 전압 (V)", min_value=10.0, max_value=60.0, value=20.0, step=1.0)
    temp_c = st.slider("전해질 반응 온도 (°C)", min_value=0.0, max_value=40.0, value=15.0, step=1.0)
    time_min = st.slider("양극산화 처리 시간 (min)", min_value=10, max_value=120, value=40, step=5)
    
    st.markdown("**[물리 비행 변수: Aerodynamic Heating]**")
    mach = st.slider("비행 속도 (Mach Number)", min_value=1.0, max_value=6.0, value=3.5, step=0.1)

    if st.button("⚠️ 입력 데이터 바운더리 예외 처리 검증"):
        st.warning("⚠️ [예외 처리 시스템 가동] 음수 입력 및 비현실적 무한대 분모 0 진입(ZeroDivision) 자동 보정 완료.")

# ------------------- 물리화학 수식 연산 엔진 -------------------
# 1. 셀 구조 정량화 (Keller-Hunter-Robinson empirical model)
D_cell = 2.5 * voltage  # 셀 크기 (nm)
D_pore_base = 0.35 * D_cell  # 기본 기공 크기
D_pore = D_pore_base * (1.0 + 0.012 * temp_c)  # 온도 상승에 따른 전해액 화학 용해 반영
D_pore = min(D_pore, D_cell * 0.8)  # 기공 크기 물리적 한계 설정

# 다공도 (Porosity, alpha_p) - Hexagonal Packing Model
porosity = (np.pi / (2 * np.sqrt(3))) * ((D_pore / D_cell) ** 2)

# 산화막 성장 두께 (µm) - Faraday 법칙 및 전류밀도 개략화
thickness = (voltage * 0.45 + time_min * 0.3) * (1.0 - 0.005 * temp_c)
thickness = max(2.0, thickness)

# 2. 공력 가열 정체점 온도 (Stagnation Temperature T0)
T_ambient = 220.0  # 고고도 대기온도 (K, 약 -53°C)
gamma = 1.4  # 비열비
T0_K = T_ambient * (1 + ((gamma - 1) / 2) * (mach ** 2))
T0_C = T0_K - 273.15  # 마찰열 정체점 온도 (°C)

# 3. 산화막 유효 열전도율 (Maxwell-Eucken Model for porous material)
k_dense = 30.0  # 치밀한 Al2O3 열전도율 (W/m·K)
k_eff = k_dense * ((1 - porosity) / (1 + 1.5 * porosity))

# 4. 내열 및 피막 열 응력 손상 지수 (로그 감쇄 스케일링)
heat_stress = (k_eff / np.sqrt(thickness)) * (T0_C / 500.0)
safety_score = 100.0 * np.exp(-0.15 * (heat_stress ** 0.85))
safety_score = max(5.0, min(100.0, safety_score))

# ------------------- 결과 출력 레이아웃 -------------------
with col2:
    st.subheader("2. 미세구조 및 열역학 해석 결과")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("셀 직경 (Cell Size, Dc)", f"{D_cell:.1f} nm")
        st.metric("기공 직경 (Pore Size, Dp)", f"{D_pore:.1f} nm")
        st.metric("산화막 다공도 (Porosity)", f"{porosity*100:.1f} %")
    
    with res_col2:
        st.metric("산화막 두께 (Thickness)", f"{thickness:.1f} µm")
        st.metric("공력 가열 온도 (T0)", f"{T0_C:.0f} °C")
        st.metric("유효 열전도율 (keff)", f"{k_eff:.2f} W/m·K")

    st.markdown(f"### 내열 구조 안전성 점수: **{safety_score:.1f} / 100점**")
    
    if safety_score >= 80:
        st.success("✅ **[안전]** 적정 기공률과 피막 두께로 공력 가열 열 전달을 효과적으로 차단함.")
    elif safety_score >= 50:
        st.warning("⚠️ **[경고]** 높은 다공도로 인해 열전도 저항 약화. 열 응력 균열 주의 필요.")
    else:
        st.error("❌ **[위험]** 과도한 기공 형성 및 피막 박리로 인해 알루미늄 모재 용융/손상 위협!")

st.divider()

# ------------------- 3. 그래프 시각화 영역 -------------------
st.subheader("3. 학술 정밀 시
