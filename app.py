
import streamlit as st
import numpy as np
import pandas as pd

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
        st.success("입력값이 설정된 범위 내에 있는지 확인했습니다.")

# --------------------------------------------------
# 수식 연산 엔진
# --------------------------------------------------

# 1. 양극산화 나노기공 구조
# 문헌의 대표적인 경험적 비례 관계
# 셀 간격: 약 2.5 nm/V
# 기공 직경: 약 0.9 nm/V
# 전해질 및 공정 조건에 따라 실제 값은 달라질 수 있음

D_cell = 2.5 * voltage
D_pore = 0.9 * voltage

# 이상적인 육각 배열을 가정한 기공률
porosity = (
    np.pi / (2 * np.sqrt(3))
) * ((D_pore / D_cell) ** 2)

porosity_percent = porosity * 100.0

# 2. 산화알루미늄 장벽층 두께
# 장벽형 산화막 두께의 대표적인 비례 관계
# 약 1.0~1.4 nm/V 범위 중 1.2 nm/V 사용
# 전체 다공성 산화막 두께가 아닌 장벽층의 이론적 추정값

barrier_thickness_nm = 1.2 * voltage
thickness = barrier_thickness_nm / 1000.0  # um 단위 변환

# 3. 공력가열 정체온도
# 이상기체, 공기 비열비 gamma = 1.4 가정
# T0 = T∞ * (1 + (gamma-1)/2 * M²)

T_ambient = 220.0  # 외부 대기 온도 (K)
gamma = 1.4

T0_K = T_ambient * (
    1 + ((gamma - 1) / 2) * (mach ** 2)
)
T0_C = T0_K - 273.15

# 4. 양극산화 알루미나의 열전도도
# 문헌 측정 범위:
# 황산 전해질: 0.53~1.01 W/mK
# 옥살산 전해질: 1.31~1.62 W/mK
# 전해질을 별도로 선택하지 않으므로 문헌 전체 범위 표시
# 대표 비교값은 두 범위의 바깥쪽 평균이 아닌 전체 범위의 중간값으로 설정

k_min = 0.53
k_max = 1.62
k_eff = (k_min + k_max) / 2

# 5. 장벽층의 단위 면적당 열저항
# R'' = d / k
# d는 m 단위로 변환

thickness_m = barrier_thickness_nm * 1e-9
thermal_resistance = thickness_m / k_eff

# --------------------------------------------------
# 결과 출력
# --------------------------------------------------

with col2:
    st.subheader("2. 미세구조 및 열역학 해석 결과")

    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.metric("셀 직경 (Cell Size, Dc)", f"{D_cell:.1f} nm")
        st.metric("기공 직경 (Pore Size, Dp)", f"{D_pore:.1f} nm")
        st.metric("산화막 다공도 (Porosity)", f"{porosity_percent:.1f} %")

    with res_col2:
        st.metric("장벽층 두께 (Barrier Layer)", f"{thickness:.3f} um")
        st.metric("공력 가열 정체온도 (T0)", f"{T0_C:.1f} C")
        st.metric("대표 열전도율 (k)", f"{k_eff:.2f} W/mK")

    st.markdown(
        f"### 장벽층 단위 면적당 열저항: **{thermal_resistance:.2e} m²K/W**"
    )

    st.info(
        "위 열저항은 장벽층만을 대상으로 계산한 이론적 값입니다. "
        "전체 다공성 산화막의 열저항이나 실제 항공우주 부품의 안전성을 "
        "직접 나타내는 값은 아닙니다."
    )

    st.caption(
        f"문헌상 양극산화 알루미나 열전도도 범위: "
        f"{k_min:.2f}~{k_max:.2f} W/mK"
    )

    st.caption(
        "전해질 반응 온도는 입력 조건으로 표시하지만, "
        "전해질별 실험 자료 없이 임의의 온도 보정 계수를 적용하지 않았습니다."
    )

st.divider()

# --------------------------------------------------
# 시각화 영역
# --------------------------------------------------

st.subheader("3. 비행 속도별 마찰열 정체점 온도 프로파일")

mach_range = np.linspace(1.0, 6.0, 50)

T0_range = (
    T_ambient
    * (1 + ((gamma - 1) / 2) * (mach_range ** 2))
) - 273.15

chart_data = pd.DataFrame({
    "Mach Number": mach_range,
    "Stagnation Temp (C)": T0_range
})

chart_data = chart_data.set_index("Mach Number")

st.line_chart(
    chart_data,
    use_container_width=True
)

st.caption(
    f"📍 현재 설정 비행 속도: Mach {mach:.1f} | "
    f"정체온도: {T0_C:.1f} °C"
)

st.divider()

# --------------------------------------------------
# 요약 표
# --------------------------------------------------

st.subheader("4. 주요 정량 데이터 요약")

summary_data = {
    "파라미터": [
        "인가 전압",
        "반응 온도",
        "비행 마하 수",
        "기공 크기",
        "피막 다공도",
        "정체온도",
        "대표 열전도율",
        "장벽층 열저항"
    ],
    "산출값": [
        f"{voltage} V",
        f"{temp_c} C",
        f"{mach} M",
        f"{D_pore:.1f} nm",
        f"{porosity_percent:.1f} %",
        f"{T0_C:.1f} C",
        f"{k_eff:.2f} W/mK",
        f"{thermal_resistance:.2e} m²K/W"
    ]
}

st.table(summary_data)
