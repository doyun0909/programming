import tkinter as tk
from tkinter import messagebox

class AnodizingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("로켓 알루미늄 양극산화 피막 내구성 시뮬레이터 (20603 김도윤)")
        self.root.geometry("820x650")
        self.root.resizable(False, False)

        # 타이틀 레이블
        title_label = tk.Label(root, text="알루미늄 양극산화 피막 기공 구조 & 마찰열 내구성 시뮬레이터", 
                               font=("Arial", 14, "bold"), fg="#1E3A8A", pady=10)
        title_label.pack()

        # 프레임 구성 (좌: 컨트롤러, 우: 시각화 및 결과)
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        left_frame = tk.LabelFrame(main_frame, text=" 1. 공정 및 비행 변수 설정 ", font=("Arial", 11, "bold"), padx=15, pady=15)
        left_frame.pack(side="left", fill="y", padx=5)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        # ------------------- 좌측 슬라이더 컨트롤 -------------------
        # 1. 전압
        tk.Label(left_frame, text="양극산화 전압 (V):", font=("Arial", 10)).pack(anchor="w", pady=(5, 0))
        self.var_voltage = tk.DoubleVar(value=15.0)
        self.slider_voltage = tk.Scale(left_frame, from_=5.0, to_=30.0, resolution=0.5, 
                                       orient="horizontal", variable=self.var_voltage, length=220, command=self.update_simulation)
        self.slider_voltage.pack(pady=(0, 10))

        # 2. 온도
        tk.Label(left_frame, text="전해질 온도 (°C):", font=("Arial", 10)).pack(anchor="w")
        self.var_temp = tk.DoubleVar(value=20.0)
        self.slider_temp = tk.Scale(left_frame, from_=5.0, to_=40.0, resolution=0.5, 
                                    orient="horizontal", variable=self.var_temp, length=220, command=self.update_simulation)
        self.slider_temp.pack(pady=(0, 10))

        # 3. 비행 속도 (마하)
        tk.Label(left_frame, text="로켓 비행 속도 (Mach):", font=("Arial", 10)).pack(anchor="w")
        self.var_mach = tk.DoubleVar(value=3.0)
        self.slider_mach = tk.Scale(left_frame, from_=1.0, to_=6.0, resolution=0.1, 
                                    orient="horizontal", variable=self.var_mach, length=220, command=self.update_simulation)
        self.slider_mach.pack(pady=(0, 15))

        # 예외 처리 검증 테스트 버튼
        btn_error_test = tk.Button(left_frame, text="⚠️ 잘못된 값 예외 처리 테스트", 
                                   command=self.test_exception, bg="#EF4444", fg="white", font=("Arial", 9, "bold"))
        btn_error_test.pack(fill="x", pady=5)

        # 설명 가이드
        guide_text = "\n[화학-물리 융합 원리]\n• 전압/온도 ↑ : 기공(Pore) 크기 증가\n• 마하 수 ↑ : 마찰열 발생량 급증\n• 기공이 크면 열 침투율이 증가하여\n  피막 균열 및 내구성 저하 발생"
        tk.Label(left_frame, text=guide_text, justify="left", font=("Arial", 9), fg="#4B5563").pack(anchor="w", pady=10)

        # ------------------- 우측 Canvas 캔버스 (2D 미세구조 시각화) -------------------
        tk.Label(right_frame, text="2. 산화막 미세 단면 시각화 (나노 기공 구조)", font=("Arial", 11, "bold")).pack(anchor="w")
        
        self.canvas = tk.Canvas(right_frame, width=480, height=220, bg="#F3F4F6", highlightthickness=1, highlightbackground="#D1D5DB")
        self.canvas.pack(pady=5)

        # 결과 출력 레이블 프레임
        result_box = tk.LabelFrame(right_frame, text=" 3. 내구성 분석 및 진단 결과 ", font=("Arial", 11, "bold"), padx=10, pady=10)
        result_box.pack(fill="both", expand=True, pady=5)

        self.lbl_pore_info = tk.Label(result_box, text="기공 크기: - nm | 피막 두께: - µm", font=("Arial", 10))
        self.lbl_pore_info.pack(anchor="w")

        self.lbl_heat_info = tk.Label(result_box, text="예상 마찰열: - °C | 열 침투율: - %", font=("Arial", 10))
        self.lbl_heat_info.pack(anchor="w")

        self.lbl_score = tk.Label(result_box, text="안전 점수: - / 100", font=("Arial", 12, "bold"), fg="#2563EB")
        self.lbl_score.pack(anchor="w", pady=5)

        self.lbl_status = tk.Label(result_box, text="진단: -", font=("Arial", 10, "bold"), fg="#111827")
        self.lbl_status.pack(anchor="w")

        # 초기 계산 실행
        self.update_simulation()

    def update_simulation(self, event=None):
        try:
            # 1. 입력 값 가공
            voltage = float(self.var_voltage.get())
            temp = float(self.var_temp.get())
            mach = float(self.var_mach.get())

            # 2. 화학 수식 모델 (전압과 온도가 커질수록 기공 크기가 커지고 표면 결함 야기)
            pore_size = (voltage * 1.5) + (temp * 0.8)   # nm 단위
            thickness = (voltage * 2.2) - (temp * 0.2)  # µm 단위
            thickness = max(5.0, thickness)             # 최소 두께 보장

            # 3. 물리 수식 모델 (마하 수에 따른 대기권 마찰열 및 열 전달 산출)
            friction_heat = 150 * (mach ** 1.3)          # °C 단위
            
            # 열 침투 가중치 (기공 크기 / 피막 두께)
            heat_penetration = (pore_size / (thickness + 1e-5)) * (mach * 12.0)
            
            # 안전 점수 산출 (0 ~ 100점)
            safety_score = max(0.0, min(100.0, 100.0 - (heat_penetration * 0.8)))

            # 4. Canvas에 산화막 및 기공 시각화 렌더링
            self.draw_microstructure(pore_size, thickness, friction_heat, safety_score)

            # 5. 결과 텍스트 업데이트
            self.lbl_pore_info.config(text=f"기공 크기 (Pore Size): {pore_size:.1f} nm | 피막 두께: {thickness:.1f} µm")
            self.lbl_heat_info.config(text=f"예상 비행 마찰열: {friction_heat:.0f} °C | 열 침투 가중치: {heat_penetration:.1f}")
            self.lbl_score.config(text=f"내열 안전 점수: {safety_score:.1f} / 100점")

            if safety_score >= 80:
                self.lbl_status.config(text="진단: ✅ [안전] 치밀한 기공 구조로 마찰열을 성공적으로 차단함.", fg="#16A34A")
            elif safety_score >= 50:
                self.lbl_status.config(text="진단: ⚠️ [경고] 기공이 다소 큼. 장시간 비행 시 열 침투 위험 발생.", fg="#D97706")
            else:
                self.lbl_status.config(text="진단: ❌ [위험] 기공 과다 형성 및 열 침투로 인한 피막 균열 발생!", fg="#DC2626")

        except Exception as e:
            messagebox.showerror("계산 오류", f"시뮬레이션 처리 중 오류가 발생했습니다: {e}")

    def draw_microstructure(self, pore_size, thickness, friction_heat, safety_score):
        self.canvas.delete("all")
        width = 480
        height = 220

        # 모재 (알루미늄 합금 바탕)
        self.canvas.create_rectangle(0, 140, width, height, fill="#9CA3AF", outline="")
        self.canvas.create_text(width/2, 180, text="알루미늄 합금 모재 (Al Base Metal)", fill="#1F2937", font=("Arial", 10, "bold"))

        # 양극산화막 (Al2O3)
        film_color = "#3B82F6" if safety_score >= 70 else ("#F59E0B" if safety_score >= 40 else "#EF4444")
        self.canvas.create_rectangle(0, 40, width, 140, fill=film_color, outline="#1D4ED8")
        self.canvas.create_text(60, 55, text="양극산화막 (Al₂O₃)", fill="white", font=("Arial", 9, "bold"))

        # 기공(Micro-pore) 구멍 그리기 (기공 크기 반영)
        r = min(18, max(3, pore_size / 4))  # 기공 반지름
        gap = 45
        for x in range(30, width, gap):
            # 수직 기공 채널
            self.canvas.create_rectangle(x - r, 40, x + r, 125, fill="#F3F4F6", outline="#4B5563")
            # 기공 입구
            self.canvas.create_oval(x - r, 35, x + r, 45, fill="#D1D5DB", outline="#4B5563")

        # 상단 마찰열 화염 시각화
        heat_color = "#DC2626" if friction_heat > 400 else "#F97316"
        self.canvas.create_rectangle(0, 0, width, 40, fill=heat_color, outline="")
        self.canvas.create_text(width/2, 20, text=f"🔥 대기권 비행 마찰열 (마하 속도에 의한 공력 가열: {friction_heat:.0f}°C)", 
                                fill="white", font=("Arial", 10, "bold"))

    def test_exception(self):
        # 예외 처리 기능 검증용
        try:
            # 의도적 잘못된 타입 대입
            invalid_val = float("잘못된입력")
        except ValueError:
            messagebox.showwarning("입력 예외 처리 가동", "⚠️ [예외 처리 작동 확인]\n문자열이나 비정상적인 수치가 입력되었습니다.\n기본 안전 수치로 자동 변환합니다.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnodizingSimulator(root)
    root.mainloop()
