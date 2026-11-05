
import streamlit as st
import numpy as np
import pandas as pd

# ==========================================
# 1. 기본 페이지 설정
# ==========================================

st.set_page_config(
    page_title="AAO 열적 특성 시뮬레이터",
    layout="wide"
)

st.title("🚀 항공우주용 양극산화 알루미나 열적 특성 시뮬레이터")

st.caption(
    "20603 | 문헌 기반 AAO 나노구조 및 공력가열 이론 모델"
)

st.info(
    "이 프로그램은 문헌 기반의 이상화된 이론 시뮬레이터입니다. "
    "실제 시료의 실측값이나 비행체의 구조 안전성을 보증하지 않습니다."
)

st.divider()


# ==========================================
# 2. 학술 상수 및 문헌 데이터
# ==========================================

# Faraday constant
F = 96485.33212       # C/mol

# Alumina (Al2O3)
M_AL2O3 = 0.10196      # kg/mol
RHO_AL2O3 = 3950.0     # kg/m^3 (bulk density)
N_ELECTRONS = 6

# Air properties (ideal calorically perfect gas approximation)
GAMMA = 1.4
PR = 0.72

# AAO empirical proportionality constants
LAMBDA_CELL = 2.5     # nm/V
LAMBDA_PORE = 0.9     # nm/V


# Literature thermal conductivity ranges
# Lee et al., Materials Chemistry and Physics (2013)

THERMAL_DATA = {
    "황산": (0.53, 1.01),
    "옥살산": (1.31, 1.62)
}


# ==========================================
# 3. 사용자 입력
# ==========================================

col1, col2 = st.columns([1, 1.2])

with col1:

    st.subheader("1. 공정 및 비행 조건")

    st.markdown("### [화학] 양극산화 조건")

    electrolyte = st.selectbox(
        "전해질 종류",
        ["옥살산", "황산", "인산"]
    )

    voltage_ranges = {
        "황산": (15, 30, 25),
        "옥살산": (20, 60, 40),
        "인산": (160, 195, 195)
    }

    v_min, v_max, v_default = voltage_ranges[electrolyte]

    voltage = st.slider(
        "인가 전압 (V)",
        min_value=v_min,
        max_value=v_max,
        value=v_default,
        step=1,
        key=f"voltage_{electrolyte}"
    )

    time_min = st.slider(
        "양극산화 시간 (min)",
        min_value=10,
        max_value=120,
        value=40,
        step=5
    )

    current_density = st.slider(
        "전류 밀도 (mA/cm²)",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5
    )

    st.caption(
        "전류 밀도는 이론적 산화막 성장량 계산을 위한 가정 입력값입니다."
    )

    st.divider()

    st.markdown("### [물리] 비행 조건")

    mach = st.slider(
        "비행 마하 수",
        min_value=1.0,
        max_value=6.0,
        value=3.5,
        step=0.1
    )

    ambient_temp = st.slider(
        "자유류 대기 온도 (K)",
        min_value=180.0,
        max_value=280.0,
        value=220.0,
        step=1.0
    )

    flow_type = st.selectbox(
        "경계층 유동 가정",
        ["층류", "난류"]
    )


# ==========================================
# 4. 화학적 나노구조 계산
# ==========================================

# 4-1. Interpore distance
D_cell = LAMBDA_CELL * voltage

# 4-2. Pore diameter
D_pore = LAMBDA_PORE * voltage

# 4-3. Ideal hexagonal porosity
porosity = (
    np.pi / (2 * np.sqrt(3))
    * (D_pore / D_cell) ** 2
)

porosity_percent = porosity * 100


# ==========================================
# 5. 패러데이 법칙을 이용한 이론적 두께
# ==========================================

# Current density:
# 1 mA/cm² = 10 A/m²

j = current_density * 10.0

# Time conversion
time_sec = time_min * 60.0

# Charge per unit area (C/m²)
charge_density = j * time_sec

# Theoretical compact-equivalent oxide thickness
# d = M * Q / (n * F * rho)

thickness_m = (
    M_AL2O3 * charge_density
    / (N_ELECTRONS * F * RHO_AL2O3)
)

thickness_um = thickness_m * 1e6


# ==========================================
# 6. 문헌 기반 열전도율
# ==========================================

thermal_available = electrolyte in THERMAL_DATA

if thermal_available:

    k_min, k_max = THERMAL_DATA[electrolyte]

    k_mean = (k_min + k_max) / 2

    # Areal thermal resistance range
    R_min = thickness_m / k_max
    R_max = thickness_m / k_min

else:

    k_min = None
    k_max = None
    k_mean = None
    R_min = None
    R_max = None


# ==========================================
# 7. 공력가열 계산
# ==========================================

# Stagnation temperature
T0_K = ambient_temp * (
    1 + ((GAMMA - 1) / 2) * mach**2
)

T0_C = T0_K - 273.15

# Recovery factor
if flow_type == "층류":
    recovery_factor = np.sqrt(PR)

else:
    recovery_factor = PR ** (1 / 3)

# Adiabatic recovery wall temperature
T_aw_K = ambient_temp * (
    1 + recovery_factor
    * ((GAMMA - 1) / 2)
    * mach**2
)

T_aw_C = T_aw_K - 273.15


# ==========================================
# 8. 결과 출력
# ==========================================

with col2:

    st.subheader("2. 나노구조 및 물리 계산 결과")

    st.markdown("### [화학] 나노기공 구조")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "셀 간격",
            f"{D_cell:.2f} nm"
        )

        st.metric(
            "기공 직경",
            f"{D_pore:.2f} nm"
        )

    with c2:

        st.metric(
            "이상적 기하학적 다공도",
            f"{porosity_percent:.2f}%"
        )

        st.metric(
            "이론적 산화막 두께",
            f"{thickness_um:.2f} μm"
        )

    st.warning(
        "산화막 두께는 패러데이 법칙에 따른 치밀한 Al2O3의 "
        "이론적 등가 두께입니다. 실제 다공성 피막 두께와 다를 수 있습니다."
    )

    st.divider()

    st.markdown("### [물리] 열역학 계산")

    c3, c4 = st.columns(2)

    with c3:

        st.metric(
            "정체온도",
            f"{T0_C:.2f} °C"
        )

        st.metric(
            "회복온도",
            f"{T_aw_C:.2f} °C"
        )

    with c4:

        st.metric(
            "회복계수",
            f"{recovery_factor:.4f}"
        )

        st.metric(
            "비열비 γ",
            f"{GAMMA:.2f}"
        )

    st.caption(
        "회복온도는 이상화된 경계층 모델의 단열 벽면 온도 추정치입니다."
    )

    st.divider()

    st.markdown("### [재료] 열전도 특성")

    if thermal_available:

        st.metric(
            "문헌 열전도율 범위",
            f"{k_min:.2f} ~ {k_max:.2f} W/(m·K)"
        )

        st.metric(
            "문헌 범위 중간값",
            f"{k_mean:.3f} W/(m·K)"
        )

        st.metric(
            "단위 면적당 열저항 범위",
            f"{R_min:.6f} ~ {R_max:.6f} m²·K/W"
        )

        st.caption(
            "열전도율은 Lee et al. (2013)의 전해질별 "
            "실측 범위를 표시한 것입니다. 중간값은 대표 비교값이지 "
            "현재 입력 조건에서의 실측 예측값은 아닙니다."
        )

    else:

        st.warning(
            "선택한 인산 전해질에 대해서는 이 코드에 연결한 "
            "문헌의 열전도율 측정값이 없습니다. "
            "임의의 열전도율을 만들어 계산하지 않습니다."
        )


# ==========================================
# 9. 마하 수에 따른 온도 변화 그래프
# ==========================================

st.divider()

st.subheader("3. 마하 수에 따른 공력 온도 변화")

mach_range = np.linspace(1.0, 6.0, 100)

T0_range = ambient_temp * (
    1 + ((GAMMA - 1) / 2) * mach_range**2
) - 273.15

Taw_range = ambient_temp * (
    1 + recovery_factor
    * ((GAMMA - 1) / 2)
    * mach_range**2
) - 273.15

chart_data = pd.DataFrame({
    "Mach Number": mach_range,
    "Stagnation Temperature (°C)": T0_range,
    "Recovery Temperature (°C)": Taw_range
})

chart_data = chart_data.set_index("Mach Number")

st.line_chart(
    chart_data,
    use_container_width=True
)


# ==========================================
# 10. 주요 계산 데이터
# ==========================================

st.divider()

st.subheader("4. 주요 정량 데이터 요약")

summary = {
    "항목": [
        "전해질",
        "인가 전압",
        "양극산화 시간",
        "전류 밀도",
        "셀 간격",
        "기공 직경",
        "기하학적 다공도",
        "이론적 등가 두께",
        "비행 마하 수",
        "정체온도",
        "회복온도"
    ],

    "계산값": [
        electrolyte,
        f"{voltage} V",
        f"{time_min} min",
        f"{current_density} mA/cm²",
        f"{D_cell:.2f} nm",
        f"{D_pore:.2f} nm",
        f"{porosity_percent:.2f} %",
        f"{thickness_um:.2f} μm",
        f"Mach {mach:.1f}",
        f"{T0_C:.2f} °C",
        f"{T_aw_C:.2f} °C"
    ]
}

st.table(pd.DataFrame(summary))


# ==========================================
# 11. 모델의 한계
# ==========================================

st.divider()

with st.expander("모델의 학술적 가정 및 한계 확인"):

    st.markdown("""
    **1. 나노구조 모델**

    - 셀 간격과 기공 직경은 문헌의 전압 비례 경험식을 사용합니다.
    - 균일한 육각형 기공 배열을 가정합니다.
    - 실제 기공의 불균일성과 결함은 반영하지 않습니다.

    **2. 산화막 성장 모델**

    - 패러데이 법칙으로 이론적 산화물 생성량을 계산합니다.
    - 전류 효율을 100%로 가정합니다.
    - 산화물의 화학적 용해와 기공 형성에 따른 부피 변화는 반영하지 않습니다.

    **3. 열전도 모델**

    - 전해질별 문헌 측정 범위를 사용합니다.
    - 실제 시료의 온도와 다공도에 따른 열전도율 변화를 직접 계산하지 않습니다.
    - Maxwell-Eucken 모델의 유효 열전도율 예측값과는 구분합니다.

    **4. 공력가열 모델**

    - 공기를 비열비 1.4의 이상기체로 가정합니다.
    - 층류와 난류의 회복계수를 구분합니다.
    - 고온에서 발생할 수 있는 공기 해리 및 실가스 효과는 반영하지 않습니다.

    **5. 안전성 평가**

    - 실제 열응력이나 파손 여부를 계산하지 않습니다.
    - 안전성 점수를 출력하지 않습니다.
    - 실제 항공우주 구조 설계용 검증 모델이 아닙니다.
    """)
