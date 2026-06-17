import tkinter as tk
from tkinter import ttk, messagebox

from calculations.preload import PreloadCalculator
from calculations.vector_load import VectorLoadCalculator


class DimensioningView(tk.Frame):
    """
    Result screen for the bolted joint application.
    Combines preload checks with friction-based joint safety.
    """

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.bolt_props = controller.bolt_props
        self.bolts = controller.bolt_group.bolts
        self.centroid = controller.centroid
        self.load = controller.load

        self.build()

    def build(self):
        ttk.Label(self, text="Dimensionamento da Junta Parafusada",
                  font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # torque input
        torque_frame = tk.Frame(self)
        torque_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(torque_frame, text="Torque de aperto [N·m]").pack(side="left")
        self.torque_entry = ttk.Entry(torque_frame, width=12)
        self.torque_entry.pack(side="left", padx=5)

        ttk.Button(torque_frame, text="Sugerir torque",
                   command=self.suggest_torque).pack(side="left", padx=2)

        ttk.Button(torque_frame, text="?",
                   command=self.show_torque_explanation, width=3).pack(side="left", padx=2)

        # friction inputs
        ttk.Label(self, text="Coeficiente de atrito da junta μ").grid(row=2, column=0, sticky="w", padx=10)
        self.mu_entry = ttk.Entry(self)
        self.mu_entry.insert(0, "0.15")
        self.mu_entry.grid(row=2, column=1, sticky="ew", padx=10)

        ttk.Label(self, text="Coeficiente K (torque)").grid(row=3, column=0, sticky="w", padx=10)
        self.k_entry = ttk.Entry(self)
        self.k_entry.insert(0, "0.20")
        self.k_entry.grid(row=3, column=1, sticky="ew", padx=10)

        ttk.Label(self, text="Dica: μ ≈ 0.15 para aço seco, K ≈ 0.20 para torque típico.", foreground="blue").grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(0,6))

        # calculate button
        row = 5
        ttk.Button(self, text="Calcular",
                   command=self.calculate).grid(row=row, column=0, columnspan=2, pady=10)

        # ---- RESULTADOS ----
        result_frame = tk.Frame(self)
        result_frame.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.result_box = tk.Text(result_frame, height=16, width=85, yscrollcommand=scrollbar.set)
        self.result_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.result_box.yview)

        # action buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=row + 2, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Forças por parafuso",
                   command=self.show_bolt_details).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Exemplo de cálculo",
                   command=self.show_example_steps).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Como os resultados são gerados",
                   command=self.show_results_explanation).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Mudar propriedades do parafuso",
                   command=self.change_bolt_properties).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Voltar",
                   command=self.controller.show_bolt_layout).pack(side="left", padx=5)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(row + 1, weight=1)

    def show_torque_explanation(self):
        """Show how the torque suggestion is calculated."""
        msg = (
            "Torque sugerido\n\n"
            "A pré-carga estimada usa 70% do limite de escoamento:\n"
            "  Fp = 0.70 × Sy × At\n\n"
            "O torque de aperto é calculado por:\n"
            "  T = K × Fp × d\n\n"
            "Onde:\n"
            "  K = coeficiente de atrito do parafuso\n"
            "  d = diâmetro nominal do parafuso (mm)\n"
            "  T = torque em N·mm"
        )
        messagebox.showinfo("Cálculo do torque", msg)

    def show_results_explanation(self):
        """Explain how the two calculation methods work."""
        msg = (
            "Como os resultados são gerados:\n\n"
            "Método 1 - Shigley:\n"
            "  Avalia a tensão no parafuso usando σeq = sqrt(σ² + 3τ²).\n"
            "  O fator de segurança do parafuso é Sy / σeq.\n\n"
            "Método 2 - COEMI:\n"
            "  Usa a pré-carga total e o atrito na junta para avaliar a capacidade.\n"
            "  FS_junta = (μ × ΣFp) / F_aplicada.\n\n"
            "O app mostra os resultados para os dois casos e ajuda a comparar:\n"
            "  - se o torque informado é suficiente\n"
            "  - se o torque ótimo para atrito é mais adequado\n"
        )
        messagebox.showinfo("Como os resultados são calculados", msg)

    def show_bolt_details(self):
        result = getattr(self, 'last_result', None)
        if not result:
            messagebox.showwarning("Aviso", "Calcule antes de ver os detalhes por parafuso.")
            return

        window = tk.Toplevel(self)
        window.title("Forças por Parafuso")
        window.geometry("860x420")

        text = tk.Text(window, wrap="none", font=("Arial", 10))
        text.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(window, orient="vertical", command=text.yview)
        scroll_y.pack(side="right", fill="y")
        text.configure(yscrollcommand=scroll_y.set)

        is_example = self._is_coemi_example()
        reference_values = {
            'B1': {'Vb_kN': 42.12, 'Pf_kN': 4.06},
            'B2': {'Vb_kN': 32.92, 'Pf_kN': 16.24},
            'B3': {'Vb_kN': 26.63, 'Pf_kN': 16.24}
        } if is_example else {}

        text.insert(tk.END, "DETALHES DE FORÇAS E MOMENTOS POR PARAFUSO\n")
        text.insert(tk.END, "="*140 + "\n")
        if is_example:
            text.insert(tk.END, "Este é o exemplo COEMI. Os valores de referência estão ao final de cada linha.\n")
            text.insert(tk.END, "O valor Pf_ref refere-se à força axial de momento no parafuso, não à pré-carga total.\n\n")
        else:
            text.insert(tk.END, "Tabela: Fx, Fy, Fxy, Fz_moment, pré-carga efetiva, σeq e FS.\n\n")

        header = f"{'Bolt':<5}{'Fx [N]':>12}{'Fy [N]':>12}{'Fxy [N]':>12}{'Fz_mom [N]':>14}{'Fp_tot [N]':>14}{'σeq [MPa]':>12}{'FS':>8}{'Status':>12}"
        if is_example:
            header += f"{'Vb_ref [kN]':>14}{'Pf_ref [kN]':>14}"
        text.insert(tk.END, header + "\n")
        text.insert(tk.END, "-"*150 + "\n")

        for bolt in result.get("per_bolt", []):
            Fx = bolt.get("Fx", 0.0)
            Fy = bolt.get("Fy", 0.0)
            Fxy = bolt.get("Fxy", 0.0)
            Fz_moment = bolt.get("Fz_moment", 0.0)
            Fp = bolt.get("Fp", 0.0)
            sigma_eq = bolt.get("sigma_eq", 0.0)
            fs_bolt = bolt.get("fs_bolt", 0.0)
            sep = bolt.get("separated", False)
            status = "SEPARADO" if sep else "OK"
            line = f"{bolt['label']:<5}{Fx:12.1f}{Fy:12.1f}{Fxy:12.1f}{Fz_moment:14.1f}{Fp:13.1f}{sigma_eq:12.2f}{fs_bolt:8.3f}{status:>12}"
            if is_example:
                ref = reference_values.get(bolt['label'], {'Vb_kN': 0.0, 'Pf_kN': 0.0})
                line += f"{ref['Vb_kN']:14.2f}{ref['Pf_kN']:14.2f}"
            text.insert(tk.END, line + "\n")

        text.insert(tk.END, "\nComparação rápida:\n")
        text.insert(tk.END, "  Fxy = sqrt(Fx² + Fy²) para cada parafuso.\n")
        if is_example:
            text.insert(tk.END, "  Valores de referência COEMI: Vb_ref e Pf_ref. Compare com os valores obtidos na tabela.\n")
        else:
            text.insert(tk.END, "  Se você estiver usando o exemplo COEMI, compare estes valores com os Vb esperados.\n")

        text.insert(tk.END, "\nLegenda das colunas:\n")
        text.insert(tk.END, "  Bolt: identificação do parafuso.\n")
        text.insert(tk.END, "  Fx, Fy: componentes da força plana no parafuso.\n")
        text.insert(tk.END, "  Fxy: magnitude da força de cisalhamento no plano XY.\n")
        text.insert(tk.END, "  Fz_mom: componente axial Z devido ao momento da carga.\n")
        text.insert(tk.END, "  Fp_tot: pré-carga total efetiva do parafuso (Torque + efeito axial).\n")
        text.insert(tk.END, "  σeq: tensão equivalente von Mises usada para verificar o parafuso.\n")
        text.insert(tk.END, "  FS: fator de segurança do parafuso.\n")
        text.insert(tk.END, "  Status: indica se o parafuso permanece comprimido (OK) ou se perdeu\n")
        text.insert(tk.END, "          pré-carga axial (SEPARADO), ou seja, se não contribui com preload.\n")
        text.insert(tk.END, "  Vb_ref: valor de cisalhamento de referência do exemplo COEMI.\n")
        text.insert(tk.END, "  Pf_ref: valor de tração de referência do momento COEMI.\n")
        text.insert(tk.END, "\nNotas sobre atrito:\n")
        text.insert(tk.END, "  μ_junta: coeficiente de atrito entre as superfícies da junta (usado no cálculo de FS da junta).\n")
        text.insert(tk.END, "  K: coeficiente empírico usado na relação torque→pré-carga (T = K·Fp·d).\n")
        text.insert(tk.END, "  Sugestões: μ_junta (aço-aço seco) ≈ 0.15; K (torque) ≈ 0.20 — ajuste conforme lubrificação e acabamento.\n")
        text.configure(state="disabled")

    def _is_coemi_example(self):
        if not hasattr(self, 'load') or self.load is None:
            return False
        return (
            len(self.bolts) == 3 and
            abs(self.load.Fx) < 1e-3 and
            abs(self.load.Fz) < 1e-3 and
            abs(self.load.Fy + 13400.0) < 1.0 and
            abs(self.load.x - 381.0) < 1.0 and
            abs(self.load.y - 127.0) < 1.0 and
            abs(self.load.z - 254.0) < 1.0
        )

    def show_example_steps(self):
        window = tk.Toplevel(self)
        window.title("Exemplo passo a passo")
        window.geometry("760x520")

        text = tk.Text(window, wrap="word", font=("Arial", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)

        example_text = (
            "EXEMPLO PASSO A PASSO (baseado no exemplo COEMI)\n\n"
            "1) Defina o carregamento vetorial:\n"
            "   Fx = 0 N, Fy = -13.400 N, Fz = 0 N\n"
            "   Ponto de aplicação: X = 381 mm, Y = 127 mm, Z = 254 mm\n\n"
            "2) Defina a posição dos parafusos e calcule o centroide:\n"
            "   Parafuso 1: (63.5, 25.4) mm\n"
            "   Parafuso 2: (88.9, 101.6) mm\n"
            "   Parafuso 3: (38.1, 101.6) mm\n\n"
            "3) Calcule o momento da carga em relação ao centroide:\n"
            "   M = r × F\n"
            "   Mx = ry·Fz - rz·Fy\n"
            "   My = rz·Fx - rx·Fz\n"
            "   Mz = rx·Fy - ry·Fx\n\n"
            "4) Distribua o momento in-plane (Mz) entre os parafusos:\n"
            "   F_momento = (Mz · r) / Σr²\n"
            "   A direção é perpendicular ao raio de cada parafuso\n\n"
            "5) Distribua o momento fora do plano (Mx, My) como força axial Z:\n"
            "   Fz_moment = (Mx · Δy) / ΣΔy² + (-My · Δx) / ΣΔx²\n\n"
            "6) Calcule a força direta por parafuso:\n"
            "   Fx_dir = Fx / n, Fy_dir = Fy / n, Fz_dir = Fz / n\n\n"
            "7) Some as componentes diretas e os efeitos de momento:\n"
            "   Fx_bolt = Fx_dir + F_momento_x\n"
            "   Fy_bolt = Fy_dir + F_momento_y\n"
            "   Fz_bolt = Fz_dir + Fz_moment\n\n"
            "8) Calcule a pré-carga de aperto pelo torque:\n"
            "   Fi = T / (K · d)\n"
            "   Aqui K = 0.20 e d é o diâmetro do parafuso em mm\n\n"
            "9) Determine a pré-carga eficaz do parafuso:\n"
            "   Fp_efetivo = max(Fi + Fz_bolt, 0)\n"
            "   Se o parafuso se separar, Fp_efetivo = 0\n\n"
            "10) Calcule a tensão equivalente von Mises:\n"
            "   σeq = sqrt((Fp_efetivo / At)² + 3·(Vb / At)²)\n"
            "   onde Vb é a força de cisalhamento resultante no plano XY\n\n"
            "11) FS do parafuso = Sy / σeq\n"
            "12) FS da junta COEMI = (μ · ΣFp_efetivo) / |F_xy|\n"
            "   onde |F_xy| é a magnitude da força de cisalhamento no plano XY:\n"
            "   |F_xy| = sqrt(Fx² + Fy²)\n"
            "13) O objetivo do COEMI é garantir que a força de atrito disponível na junta\n"
            "   seja igual ou maior que a força de cisalhamento aplicada, isto é, FS_junta\n"
            "   maior ou igual a 1.0.\n\n"
            "DETALHES DE FORÇAS E MOMENTOS POR PARAFUSO\n"
            "============================================================================================================================================\n"
            "Tabela: Fx, Fy, Fxy, Fz_moment, pré-carga efetiva, σeq e FS.\n\n"
            "Bolt       Fx [N]      Fy [N]     Fxy [N]    Fz_mom [N]    Fp_tot [N]   σeq [MPa]      FS      Status\n"
            "------------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "B1       -41875.0     -4466.7     42112.5         406.1     272216.1      798.35   1.378          OK\n"
            "B2        20937.5    -25404.2     32920.4        1624.2     273434.2      791.26   1.390          OK\n"
            "B3        20937.5     16470.8     26639.6        1624.2     273434.2      785.55   1.400          OK\n\n"
            "Comparação rápida:\n"
            "  Fxy = sqrt(Fx² + Fy²) para cada parafuso.\n"
            "  Se você estiver usando o exemplo COEMI, compare estes valores com os Vb esperados.\n\n"
            "Legenda das colunas:\n"
            "  Bolt: identificação do parafuso.\n"
            "  Fx, Fy: componentes da força plana no parafuso.\n"
            "  Fxy: magnitude da força de cisalhamento no plano XY.\n"
            "  Fz_mom: componente axial Z devido ao momento da carga.\n"
            "  Fp_tot: pré-carga total efetiva do parafuso (Torque + efeito axial).\n"
            "  σeq: tensão equivalente von Mises usada para verificar o parafuso.\n"
            "  FS: fator de segurança do parafuso.\n"
            "  Status: indica se o parafuso permanece comprimido (OK) ou se perdeu\n"
            "          pré-carga axial (SEPARADO), ou seja, se não contribui com preload.\n"
            "  Vb_ref: valor de cisalhamento de referência do exemplo COEMI.\n"
            "  Pf_ref: valor de tração de referência do momento COEMI.\n\n"
            "Notas sobre atrito:\n"
            "  μ_junta: coeficiente de atrito entre as superfícies da junta (usado no cálculo de FS da junta).\n"
            "  K: coeficiente empírico usado na relação torque→pré-carga (T = K·Fp·d).\n"
            "  Sugestões: μ_junta (aço-aço seco) ≈ 0.15; K (torque) ≈ 0.20 — ajuste conforme lubrificação e acabamento.\n\n"
            "Este é o fluxo usado pelo cálculo unificado para cada parafuso: distribuir carregamento direto, distribuir momentos e somar o efeito axial.\n"
        )

        text.insert(tk.END, example_text)
        text.configure(state="disabled")

    def suggest_torque(self):
        """Sugestão: 70% de Sy * At"""
        if not self.bolt_props:
            messagebox.showerror("Erro", "Propriedades do parafuso não definidas")
            return

        At = self.bolt_props.area_tracao  # mm²
        Sy = self.bolt_props.sy  # MPa
        d = self.bolt_props.nominal_diameter  # mm

        # Pré-carga em N: Fp = 0.7 * Sy(MPa) * At(mm²) = 0.7 * Sy * At (N)
        Fp = 0.7 * Sy * At
        # Torque em N·mm = K * Fp * d (com d em mm e Fp em N)
        T_Nmm = 0.20 * Fp * d
        # UI uses N·m: convert
        T_Nm = T_Nmm / 1000.0

        self.torque_entry.delete(0, tk.END)
        self.torque_entry.insert(0, f"{T_Nm:.3f}")

    def change_bolt_properties(self):
        """Go back to bolt properties selection without losing other settings"""
        # indicate we want to return to dimensioning after editing
        self.controller.return_to = 'dimensioning'
        self.controller.show_bolt_properties()

    def calculate(self):
        try:
            if not self.bolt_props:
                messagebox.showerror("Erro", "Propriedades do parafuso não definidas")
                return

            # torque entry is in N·m (UI). Convert to N·mm for calculators
            torque_Nm = float(self.torque_entry.get())
            torque = torque_Nm * 1000.0  # N·mm for internal calculators
            mu = float(self.mu_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Torque e atrito devem ser numéricos")
            return

        try:
            calc = VectorLoadCalculator(
                self.bolts, self.load, self.centroid,
                self.bolt_props, torque, mu
            )
            result = calc.calculate()
            optimal_torque = calc.optimal_torque()

            result['T_optimal_Nm'] = optimal_torque / 1000.0
            result['T_optimal_Nmm'] = optimal_torque
            result['load_value'] = self.load.P
            self.last_result = result

        except ValueError as e:
            messagebox.showerror("Erro de cálculo", str(e))
            return

        self.show_results_dual(result)

    def show_results_dual(self, result):
        """Display results comparing user-provided and optimal COEMI torque"""
        self.result_box.delete("1.0", tk.END)

        T_user = result.get('T_user_Nm', 0)
        T_optimal = result.get('T_optimal_Nm', 0)
        F_load = result.get('load_value', 0)
        
        # Header
        self.result_box.insert(tk.END, "-"*85 + "\n")
        self.result_box.insert(tk.END, "Resultados do dimensionamento\n")
        self.result_box.insert(tk.END, f"Carregamento: {self.load.description()}\n")
        self.result_box.insert(tk.END, "-"*85 + "\n\n")

        # Torque comparison
        self.result_box.insert(tk.END, "Comparação de torques:\n")
        self.result_box.insert(tk.END, "-"*85 + "\n")
        self.result_box.insert(tk.END, f"Torque aplicado (entrada):      {T_user:10.3f} N·m\n")
        self.result_box.insert(tk.END, f"Torque ótimo COEMI (atrito):  {T_optimal:10.3f} N·m\n")
        self.result_box.insert(
            tk.END,
            f"Recomendação:                  Use um torque entre {min(T_user, T_optimal):.3f} e {max(T_user, T_optimal):.3f} N·m para manter margem de segurança, favorecendo o valor mais alto quando a junta de atrito for o critério dominante.\n\n"
        )

        # MÉTODO 1: SHIGLEY
        self.result_box.insert(tk.END, "="*85 + "\n")
        self.result_box.insert(tk.END, f"MÉTODO 1: SHIGLEY (Tensão combinada von Mises) - Torque: {T_user:.3f} N·m\n")
        self.result_box.insert(tk.END, "="*85 + "\n")
        self.result_box.insert(tk.END, f"Parafuso crítico: {result['critical_bolt']}\n")
        self.result_box.insert(tk.END, f"FS mínimo do parafuso:        {result['fs_bolt_min']:.3f} {'OK' if result['fs_bolt_min'] >= 1.0 else 'CRÍTICO'}\n")
        self.result_box.insert(tk.END, f"FS da junta (atrito):         {result['fs_joint']:.3f} {'OK' if result['fs_joint'] >= 1.0 else 'CRÍTICO'}\n")
        moment = result.get('moment_vector', (0.0, 0.0, 0.0))
        self.result_box.insert(tk.END, f"Momento resultante:           Mx={moment[0]:.1f} N·mm, My={moment[1]:.1f} N·mm, Mz={moment[2]:.1f} N·mm\n")
        self.result_box.insert(tk.END, f"FS crítico (mínimo):          {min(result['fs_bolt_min'], result['fs_joint']):.3f}\n\n")

        # MÉTODO 2: COEMI com torque ótimo
        if T_optimal > 0:
            calc_opt = VectorLoadCalculator(
                self.bolts, self.load, self.centroid,
                self.bolt_props, result.get('T_optimal_Nmm', 0.0), float(self.mu_entry.get())
            )
            result_opt = calc_opt.calculate()

            self.result_box.insert(tk.END, "="*85 + "\n")
            note = " (ajustado para FS_junta>=1)" if result_opt.get('fs_joint', 0) >= 1.0 else ""
            self.result_box.insert(tk.END, f"MÉTODO 2: COEMI (Junta de atrito){note} - Torque: {T_optimal:.3f} N·m\n")
            self.result_box.insert(tk.END, "="*85 + "\n")
            self.result_box.insert(tk.END, f"Parafuso crítico: {result_opt['critical_bolt']}\n")
            self.result_box.insert(tk.END, f"FS mínimo do parafuso:        {result_opt['fs_bolt_min']:.3f} {'OK' if result_opt['fs_bolt_min'] >= 1.0 else 'CRÍTICO'}\n")
            self.result_box.insert(tk.END, f"FS da junta (atrito):         {result_opt['fs_joint']:.3f}\n")
            self.result_box.insert(tk.END, f"FS crítico (mínimo):          {min(result_opt['fs_bolt_min'], result_opt['fs_joint']):.3f}\n\n")

        # Detalhes por parafuso (com torque do usuário)
        self.result_box.insert(tk.END, "DETALHES POR PARAFUSO (Torque do usuário em N·m):\n")
        self.result_box.insert(tk.END, "-"*85 + "\n")
        for b in result["per_bolt"]:
            sep_status = " SEPARADO" if b.get("separated") else ""
            self.result_box.insert(tk.END, 
                f"{b['label']:<5} | FS parafuso: {b['fs_bolt']:>7.3f} | Fp: {b.get('Fp', 0):>9.1f} N | "
                f"σeq: {b.get('sigma_eq', 0):>8.1f} MPa{sep_status}\n"
            )

        # Recomendação final
        self.result_box.insert(tk.END, "\n" + "="*85 + "\n")
        fs_shigley = min(result['fs_bolt_min'], result['fs_joint'])
        
        if T_optimal > 0:
            fs_coemi = min(result_opt['fs_bolt_min'], result_opt['fs_joint'])
            self.result_box.insert(tk.END, f"COMPARAÇÃO FINAL:\n")
            self.result_box.insert(tk.END, f"  Shigley (T={T_user:.1f}): FS={fs_shigley:.3f}\n")
            self.result_box.insert(tk.END, f"  COEMI ótimo (T={T_optimal:.1f}): FS={fs_coemi:.3f}\n\n")
            
            if fs_shigley >= 1.0 and fs_coemi >= 1.0:
                self.result_box.insert(tk.END, "RECOMENDAÇÃO: DESIGN VIÁVEL - Use o maior torque entre {:.1f} e {:.1f} N·mm\n".format(T_user, T_optimal))
            elif fs_shigley >= 1.0:
                self.result_box.insert(tk.END, f"RECOMENDAÇÃO: Use torque {T_user:.1f} N·mm (Shigley OK, considerar torque ótimo)\n")
            elif fs_coemi >= 1.0:
                self.result_box.insert(tk.END, f"RECOMENDAÇÃO: Use torque {T_optimal:.1f} N·mm (COEMI viável, Shigley revisar)\n")
            else:
                self.result_box.insert(tk.END, "RECOMENDAÇÃO: REVISÃO NECESSÁRIA - Ambos os métodos críticos\n")
        else:
            if fs_shigley >= 1.0:
                self.result_box.insert(tk.END, f"RECOMENDAÇÃO: DESIGN VIÁVEL - Torque OK (FS={fs_shigley:.3f})\n")
            else:
                self.result_box.insert(tk.END, "RECOMENDAÇÃO: REVISÃO NECESSÁRIA - FS crítico\n")
        
        self.result_box.insert(tk.END, "="*85 + "\n")
