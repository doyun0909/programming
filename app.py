
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

D_cell = 2.5 * voltage
D_pore = 0.9 * voltage

# 이상적인 육각 배열을 가정한 기공률
porosity = (
    np.pi / (2 * np.sqrt(3))
) * ((D_pore / D_cell) ** 2)

porosity_percent = porosity * 100.0

# 2. 산화알루미늄 장벽층 두께

barrier_thickness_nm = 1.2 * voltage
thickness = barrier_thickness_nm / 1000.0

# 3. 공력가열 정체온도

T_ambient = 220.0
gamma = 1.4

T0_K = T_ambient * (
    1 + ((gamma - 1) / 2) * (mach ** 2)
)
T0_C = T0_K - 273.15

# 4. 양극산화 알루미나의 열전도도

k_min = 0.53
k_max = 1.62
k_eff = (k_min + k_max) / 2

# 5. 장벽층의 단위 면적당 열저항

thickness_m = barrier_thickness_nm * 1e-9
thermal_resistance = thickness_m / k_eff

# --------------------------------------------------
# 6. 종합 안정성 점수 계산 엔진
# --------------------------------------------------

# (1) 공력가열 온도 평가 (70%)
# 참고 평가 구간: 0~500°C

thermal_score = max(
    0,
    min(100, 100 * (1 - max(0, T0_C) / 500))
)

# (2) 산화막 다공도 평가 (30%)
# 참고 평가 구간: 5~20%

if 5 <= porosity_percent <= 20:
    porosity_score = 100
else:
    porosity_score = max(
        0,
        100 - min(
            abs(porosity_percent - 12.5) - 7.5,
            20
        ) * 5
    )

# (3) 종합 안정성 점수

stability_score = (
    thermal_score * 0.7
    + porosity_score * 0.3
)

stability_score = round(stability_score, 1)

# (4) 점수 등급

if stability_score >= 80:
    stability_grade = "우수"
elif stability_score >= 60:
    stability_grade = "양호"
elif stability_score >= 40:
    stability_grade = "보통"
else:
    stability_grade = "낮음"

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
    # 7. 종합 안정성 평가 결과
    # --------------------------------------------------

    st.subheader("3. 종합 안정성 평가")

    score_col1, score_col2 = st.columns([1.5, 1])

    with score_col1:
        st.metric(
            "산화막 구조 및 열적 안정성 점수",
            f"{stability_score:.1f} / 100점"
        )

    with score_col2:
        st.metric(
            "종합 평가 등급",
            stability_grade
        )

    st.progress(stability_score / 100)

    st.caption(
        f"열적 평가: {thermal_score:.1f}점 | "
        f"다공도 평가: {porosity_score:.1f}점"
    )

    # 점수 산정 기준 더보기

    with st.expander("📖 안정성 점수 산정 기준 더보기"):

        st.markdown("### ① 공력가열 온도 평가 (70%)")

        st.write(
            "비행 중 공력가열로 발생하는 정체온도를 기준으로 "
            "열적 조건을 평가합니다."
        )

        st.latex(
            r"S_T = 100 \times "
            r"\left(1-\frac{\max(0,T_0)}{500}\right)"
        )

        st.write("""
        - 정체온도 0°C 이하: 100점
        - 정체온도 500°C 이상: 0점
        - 0~500°C: 온도 상승에 따라 선형적으로 점수 감소
        """)

        st.divider()

        st.markdown("### ② 산화막 다공도 평가 (30%)")

        st.write(
            "양극산화 피막의 기공률을 기준으로 "
            "설정된 참고 평가 구간과의 일치도를 평가합니다."
        )

        st.latex(
            r"S_P = 100 \quad (5\% \leq P \leq 20\%)"
        )

        st.write("""
        - 다공도 5~20%: 100점
        - 해당 범위를 벗어나면 기준 구간에서 멀어질수록 점수 감소
        - 다공도 5~20%는 이 시뮬레이터에서 설정한 참고 평가 구간입니다.
        """)

        st.divider()

        st.markdown("### ③ 종합 안정성 점수 계산")

        st.latex(
            r"S = 0.7S_T + 0.3S_P"
        )

        st.write("""
        | 평가 항목 | 가중치 |
        |---|---:|
        | 공력가열 온도 평가 | 70% |
        | 산화막 다공도 평가 | 30% |
        | 합계 | 100% |
        """)

        st.divider()

        st.markdown("### ④ 점수별 평가 등급")

        grade_data = pd.DataFrame({
            "점수 범위": [
                "80~100점",
                "60~79.9점",
                "40~59.9점",
                "0~39.9점"
            ],
            "평가 등급": [
                "우수",
                "양호",
                "보통",
                "낮음"
            ],
            "의미": [
                "설정된 평가 기준에서 높은 점수",
                "설정된 평가 기준에서 양호한 점수",
                "설정된 평가 기준에서 중간 수준",
                "설정된 평가 기준에서 낮은 점수"
            ]
        })

        st.table(grade_data)

        st.divider()

        st.markdown("### ⑤ 평가 지표의 한계")

        st.warning(
            "본 안정성 점수는 교육 및 시뮬레이션을 위한 "
            "모델 기반 상대 평가 지표입니다. "
            "실제 항공우주 부품의 구조적 안정성, "
            "열충격 저항성 또는 내열 안전성을 "
            "직접 인증하거나 보증하지 않습니다."
        )

        st.caption(
            "실제 안정성 검증에는 산화막의 접착력, "
            "열팽창 차이, 열충격, 기계적 강도, "
            "실제 온도별 재료 물성 및 실험 데이터가 추가로 필요합니다."
        )

st.divider()

# --------------------------------------------------
# 시각화 영역
# --------------------------------------------------

st.subheader("4. 비행 속도별 마찰열 정체점 온도 프로파일")

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

st.subheader("5. 주요 정량 데이터 요약")

summary_data = {
    "파라미터": [
        "인가 전압",
        "반응 온도",
        "비행 마하 수",
        "기공 크기",
        "피막 다공도",
        "정체온도",
        "대표 열전도율",
        "장벽층 열저항",
        "열적 평가 점수",
        "다공도 평가 점수",
        "종합 안정성 점수",
        "안정성 평가 등급"
    ],
    "산출값": [
        f"{voltage} V",
        f"{temp_c} C",
        f"{mach} M",
        f"{D_pore:.1f} nm",
        f"{porosity_percent:.1f} %",
        f"{T0_C:.1f} C",
        f"{k_eff:.2f} W/mK",
        f"{thermal_resistance:.2e} m²K/W",
        f"{thermal_score:.1f} 점",
        f"{porosity_score:.1f} 점",
        f"{stability_score:.1f} 점",
        stability_grade
    ]
}

st.table(summary_data)

st.divider()

st.caption(
    "본 프로그램은 Keller-Hunter-Robinson 나노셀 구조의 "
    "기하학적 관계와 이상기체 정체온도 관계를 참고한 "
    "교육용 융합 시뮬레이션입니다. "
    "실제 실험값과 항공우주 부품의 인증 결과를 대체하지 않습니다."
)
