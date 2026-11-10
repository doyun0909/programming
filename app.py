
import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Al 양극산화 피막 시뮬레이터", layout="wide")

st.title("🚀 항공우주용 Al 양극산화막 나노기공 구조 및 공력가열 내열성 시뮬레이터")
st.caption("20603 김도윤 | 황산 양극산화 문헌 기반 경험식 및 열전도 모델 적용")

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

# 1. 황산 양극산화 나노기공 구조
# 문헌 회귀식: P(%) = 0.43T + 1.28V
# 적용 범위 밖에서는 외삽에 따른 오차 가능성이 있음.

porosity_raw = 0.43 * temp_c + 1.28 * voltage

# 문헌에서 관찰된 다공도 범위(약 14~34%)를 참고해
# 물리적으로 과도한 외삽 결과를 제한
porosity_percent = float(np.clip(porosity_raw, 14.0, 34.0))
porosity = porosity_percent / 100.0

# 셀 직경: 전압에 비례하는 나노셀 경험 관계
D_cell = 2.5 * voltage

# 육각 배열을 가정하여 다공도에서 기공 직경 역산
D_pore = D_cell * np.sqrt(
    (2 * np.sqrt(3) * porosity) / np.pi
)

# 2. 패러데이 법칙을 이용한 산화막 두께 계산

F = 96485.0                  # 패러데이 상수 (C/mol)
M_Al2O3 = 0.10196            # 산화알루미늄 몰질량 (kg/mol)
rho_Al2O3 = 3200.0           # 산화알루미늄 밀도 (kg/m³)

# 황산 양극산화의 대표적인 전류밀도를 고정 가정
current_density = 1.5 * 100  # 1.5 A/dm² -> A/m²

# 실제 전류 중 산화막 형성에 사용되는 비율의 가정값
current_efficiency = 0.90

time_sec = time_min * 60

# Al2O3 1몰 형성에 필요한 전자 수: 6몰
oxide_thickness_m = (
    current_efficiency
    * current_density
    * time_sec
    * M_Al2O3
    / (6 * F * rho_Al2O3)
)

oxide_thickness_um = oxide_thickness_m * 1e6

# 장벽층 두께
barrier_thickness_nm = 1.2 * voltage

# 3. 공력가열 정체온도

T_ambient = 220.0
gamma = 1.4

T0_K = T_ambient * (
    1 + ((gamma - 1) / 2) * (mach ** 2)
)
T0_C = T0_K - 273.15

# 4. Maxwell-Eucken 모델을 이용한 유효 열전도율

k_alumina = 1.62
k_air = 0.026

k_eff = k_alumina * (
    k_air + 2 * k_alumina
    - 2 * porosity * (k_alumina - k_air)
) / (
    k_air + 2 * k_alumina
    + porosity * (k_alumina - k_air)
)

# 5. 산화막 단위 면적당 열저항

thermal_resistance = oxide_thickness_m / k_eff

# --------------------------------------------------
# 6. 종합 안정성 점수 계산 엔진
# --------------------------------------------------

# (1) 공력가열 온도 평가 (70%)

thermal_score = max(
    0,
    min(100, 100 * (1 - max(0, T0_C) / 500))
)

# (2) 산화막 다공도 평가 (30%)
# 문헌에서 관찰된 14~34% 범위를 참고한 교육용 평가 기준

if 14 <= porosity_percent <= 34:
    porosity_score = 100
else:
    porosity_score = max(
        0,
        100 - min(
            min(abs(porosity_percent - 14),
                abs(porosity_percent - 34)),
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
        st.metric("산화막 두께 (Oxide Thickness)", f"{oxide_thickness_um:.2f} um")
        st.metric("공력 가열 정체온도 (T0)", f"{T0_C:.1f} C")
        st.metric("유효 열전도율 (k)", f"{k_eff:.2f} W/mK")

    st.markdown(
        f"### 산화막 단위 면적당 열저항: **{thermal_resistance:.2e} m²K/W**"
    )

    st.info(
        "열저항은 계산된 산화막 두께와 유효 열전도율을 이용한 "
        "이론적 값입니다. 실제 항공우주 부품의 안전성을 "
        "직접 보증하는 값은 아닙니다."
    )

    st.caption(
        f"기본 알루미나 열전도율: {k_alumina:.2f} W/mK | "
        f"기공 내부 공기 열전도율: {k_air:.3f} W/mK"
    )

    st.caption(
        f"산화막 두께 계산 가정: 전류밀도 {current_density / 100:.1f} A/dm², "
        f"전류 효율 {current_efficiency * 100:.0f}%"
    )

    if voltage > 20 or temp_c < 10 or temp_c > 20:
        st.warning(
            "현재 입력 조건 중 일부가 참고 회귀식의 실험 조건 범위를 "
            "벗어날 수 있습니다. 해당 조건의 결과는 외삽에 따른 "
            "추정값으로 해석해야 합니다."
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
            "문헌에서 관찰된 다공도 범위인 14~34%를 참고하여 "
            "설정한 교육용 평가 기준입니다."
        )

        st.latex(
            r"S_P = 100 \quad (14\% \leq P \leq 34\%)"
        )

        st.write("""
        - 다공도 14~34%: 100점
        - 해당 범위를 벗어나면 범위에서 멀어질수록 점수 감소
        - 실제 소재의 최적 다공도나 안전 기준을 의미하지는 않습니다.
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
            "실제 항공우주 부품의 구조적 안정성이나 "
            "내열 안전성을 직접 인증하거나 보증하지 않습니다."
        )

        st.caption(
            "실제 안정성 검증에는 산화막의 접착력, "
            "열팽창 차이, 열충격, 기계적 강도 및 "
            "실제 온도별 재료 물성 등이 추가로 필요합니다."
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
        "양극산화 처리 시간",
        "비행 마하 수",
        "기공 크기",
        "피막 다공도",
        "산화막 두께",
        "정체온도",
        "유효 열전도율",
        "산화막 열저항",
        "열적 평가 점수",
        "다공도 평가 점수",
        "종합 안정성 점수",
        "안정성 평가 등급"
    ],
    "산출값": [
        f"{voltage} V",
        f"{temp_c} C",
        f"{time_min} min",
        f"{mach} M",
        f"{D_pore:.1f} nm",
        f"{porosity_percent:.1f} %",
        f"{oxide_thickness_um:.2f} um",
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
    "본 프로그램은 황산 양극산화 관련 문헌의 경험적 관계식, "
    "패러데이 법칙, 육각형 기공 배열 가정 및 Maxwell-Eucken "
    "열전도 모델을 결합한 교육용 시뮬레이션입니다. "
    "입력 조건에 따른 계산 결과는 문헌 기반 추정값이며 "
    "실제 실험값이나 항공우주 부품의 인증 결과를 대체하지 않습니다."
)
