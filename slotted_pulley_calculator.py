import math
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation


class TimingBeltSlotSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Slotted Timing Belt Pulley Simulation")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1e1e2e")

        self.is_playing = True
        self.s_total = 0.0  # Continuous travel distance (mm) so pulley rotation does not reset
        self.params = {}

        self._build_ui()

        if self.recalculate_and_redraw():
            self.ani = FuncAnimation(
                self.fig, self._update_animation, interval=30, blit=False, cache_frame_data=False
            )

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#252536")
        style.configure("TLabel", background="#252536", foreground="#e0e0e0", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), foreground="#89b4fa")
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=5)

        main_container = tk.Frame(self.root, bg="#1e1e2e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ================= LEFT PANEL: INPUTS & CONTROLS =================
        left_frame = ttk.Frame(main_container, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_frame.pack_propagate(False)

        ttk.Label(left_frame, text="DESIGN PARAMETERS", style="Header.TLabel").pack(
            anchor="w", padx=10, pady=(10, 6)
        )

        self.inputs = {
            "pitch": tk.StringVar(value="3.0"),
            "z1": tk.StringVar(value="40"),
            "z2": tk.StringVar(value="80"),
            "z_belt": tk.StringVar(value="120"),
            "slots1": tk.StringVar(value="1"),
            "slots2": tk.StringVar(value="2"),
            "b_width": tk.StringVar(value="15.0"),
            "b_height": tk.StringVar(value="10.0"),
            "clearance": tk.StringVar(value="1.2"),
            "shaft_d1": tk.StringVar(value="6.0"),
            "torque": tk.StringVar(value="1.0"),
        }

        fields = [
            ("Belt Pitch (mm):", "pitch"),
            ("Driver Pulley Teeth (Z1):", "z1"),
            ("Driven Pulley Teeth (Z2):", "z2"),
            ("Total Belt Teeth (Zb):", "z_belt"),
            ("Driver Slot Count:", "slots1"),
            ("Driven Slot Count:", "slots2"),
            ("Bracket Width (mm):", "b_width"),
            ("Bracket Protrusion Height (mm):", "b_height"),
            ("Slot Clearance (mm):", "clearance"),
            ("Driver Shaft Diameter (mm):", "shaft_d1"),
            ("Operating Torque (kg.cm):", "torque"),
        ]

        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill=tk.X, padx=10)

        for row_idx, (label_text, key) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=row_idx, column=0, sticky="w", pady=3)
            entry = ttk.Entry(form_frame, textvariable=self.inputs[key], width=10, justify="right")
            entry.grid(row=row_idx, column=1, sticky="e", pady=3, padx=(5, 0))
        form_frame.columnconfigure(0, weight=1)

        btn_update = ttk.Button(
            left_frame, text="Update Configuration & Plot", command=self.recalculate_and_redraw
        )
        btn_update.pack(fill=tk.X, padx=10, pady=(12, 6))

        ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(left_frame, text="SIMULATION CONTROLS", style="Header.TLabel").pack(
            anchor="w", padx=10, pady=(0, 6)
        )

        ctrl_row = ttk.Frame(left_frame)
        ctrl_row.pack(fill=tk.X, padx=10, pady=4)

        self.btn_play = ttk.Button(ctrl_row, text="Pause", command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        btn_reset = ttk.Button(ctrl_row, text="Reset", command=self.reset_sim)
        btn_reset.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        ttk.Label(left_frame, text="Rotation Speed:").pack(anchor="w", padx=10, pady=(8, 0))
        self.speed_var = tk.DoubleVar(value=2.5)
        ttk.Scale(
            left_frame, from_=0.2, to=8.0, variable=self.speed_var, orient=tk.HORIZONTAL
        ).pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(left_frame, text="Manual Inspection (0 - 3 Belt Revolutions):").pack(
            anchor="w", padx=10, pady=(8, 0)
        )
        self.manual_pos_var = tk.DoubleVar(value=0.0)
        ttk.Scale(
            left_frame,
            from_=0.0,
            to=300.0,
            variable=self.manual_pos_var,
            orient=tk.HORIZONTAL,
            command=self.on_manual_slide,
        ).pack(fill=tk.X, padx=10, pady=2)

        legend_frame = ttk.Frame(left_frame)
        legend_frame.pack(fill=tk.X, padx=10, pady=(15, 5))
        ttk.Label(legend_frame, text="Visual Legend:", style="Header.TLabel").pack(anchor="w")
        ttk.Label(legend_frame, text="■ Blue: Pulley Body & Slot").pack(anchor="w")
        ttk.Label(legend_frame, text="■ Red: Bracket (Chordal Path)").pack(anchor="w")
        ttk.Label(legend_frame, text="■ Yellow: Timing Belt Pitch Line").pack(anchor="w")

        # ================= CENTER PANEL: MATPLOTLIB CANVAS =================
        center_frame = tk.Frame(main_container, bg="#181825")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.fig, self.ax = plt.subplots(figsize=(7.5, 7), dpi=100)
        self.fig.patch.set_facecolor("#181825")
        self.ax.set_facecolor("#181825")

        self.canvas = FigureCanvasTkAgg(self.fig, master=center_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ================= RIGHT PANEL: TECHNICAL OUTPUT PARAMETERS =================
        right_frame = ttk.Frame(main_container, width=360)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        ttk.Label(right_frame, text="TECHNICAL CALCULATION RESULTS", style="Header.TLabel").pack(
            anchor="w", padx=10, pady=(10, 6)
        )

        self.status_banner = tk.Label(
            right_frame,
            text="STATUS: SYNCHRONIZED",
            bg="#a6e3a1",
            fg="#11111b",
            font=("Segoe UI", 10, "bold"),
            pady=6,
        )
        self.status_banner.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.report_text = tk.Text(
            right_frame,
            bg="#1e1e2e",
            fg="#cdd6f4",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD,
        )
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # ==================== GEOMETRY & KINEMATICS CALCULATION ====================
    def _solve_center_distance(self, r1, r2, L_belt):
        b = 4 * L_belt - 2 * math.pi * (2 * r2 + 2 * r1)
        disc = b**2 - 32 * (2 * r2 - 2 * r1) ** 2
        if disc <= 0:
            raise ValueError("Belt length is too short for these pulley sizes!")
        C = (b + math.sqrt(disc)) / 16.0

        for _ in range(50):
            if C <= abs(r2 - r1) + 1e-4:
                C = abs(r2 - r1) + 0.5
            sin_a = (r2 - r1) / C
            alpha = math.asin(max(-0.9999, min(0.9999, sin_a)))
            L_calc = (
                2 * math.sqrt(C**2 - (r2 - r1) ** 2)
                + r2 * (math.pi + 2 * alpha)
                + r1 * (math.pi - 2 * alpha)
            )
            err = L_calc - L_belt
            if abs(err) < 1e-10:
                break
            C -= err / (2 * math.cos(alpha))
        return C

    def recalculate_and_redraw(self):
        try:
            pitch = float(self.inputs["pitch"].get())
            z1 = int(self.inputs["z1"].get())
            z2 = int(self.inputs["z2"].get())
            z_belt = int(self.inputs["z_belt"].get())
            slots1 = int(self.inputs["slots1"].get())
            slots2 = int(self.inputs["slots2"].get())
            b_width = float(self.inputs["b_width"].get())
            b_height = float(self.inputs["b_height"].get())
            clearance = float(self.inputs["clearance"].get())
            shaft_d1 = float(self.inputs["shaft_d1"].get())
            torque = float(self.inputs["torque"].get())

            if any(v <= 0 for v in [pitch, z1, z2, z_belt, slots1, slots2, b_width, b_height, shaft_d1]):
                raise ValueError("All parameter values must be greater than 0.")

            dp1 = (z1 * pitch) / math.pi
            dp2 = (z2 * pitch) / math.pi
            rp1 = dp1 / 2.0
            rp2 = dp2 / 2.0

            tooth_ded = 0.38 if pitch <= 3.0 else 0.55
            ro1 = rp1 - tooth_ded
            ro2 = rp2 - tooth_ded

            L_belt = z_belt * pitch
            C = self._solve_center_distance(rp1, rp2, L_belt)

            alpha = math.asin((rp2 - rp1) / C)
            L_tan = math.sqrt(C**2 - (rp2 - rp1) ** 2)
            L_arc2 = rp2 * (math.pi + 2 * alpha)
            L_arc1 = rp1 * (math.pi - 2 * alpha)

            half_c = b_width / 2.0
            if half_c >= rp1 or half_c >= rp2:
                raise ValueError("Bracket width exceeds pulley radius!")

            dip1 = rp1 - math.sqrt(rp1**2 - half_c**2)
            dip2 = rp2 - math.sqrt(rp2**2 - half_c**2)

            swing1 = b_height * (half_c / rp1)
            swing2 = b_height * (half_c / rp2)

            slot_depth1 = (b_height - (rp1 - ro1)) + dip1 + clearance
            slot_depth2 = (b_height - (rp2 - ro2)) + dip2 + clearance

            slot_width1 = 2 * (half_c + swing1 + clearance)
            slot_width2 = 2 * (half_c + swing2 + clearance)

            r_base1 = ro1 - slot_depth1
            r_base2 = ro2 - slot_depth2
            wall_thick1 = r_base1 - (shaft_d1 / 2.0)

            sync1 = (z1 % slots1 == 0) and (z_belt % (z1 // slots1) == 0)
            sync2 = (z2 % slots2 == 0) and (z_belt % (z2 // slots2) == 0)
            is_sync = sync1 and sync2

            torque_nm = torque * 0.0980665
            ft = torque_nm / (rp1 / 1000.0)
            wrap_deg1 = math.degrees(math.pi - 2 * alpha)
            teeth_in_wrap1 = z1 * (wrap_deg1 / 360.0)
            teeth_removed1 = slot_width1 / pitch
            remaining_teeth1 = max(0.0, teeth_in_wrap1 - teeth_removed1)

            self.params = {
                "pitch": pitch,
                "z1": z1,
                "z2": z2,
                "z_belt": z_belt,
                "slots1": slots1,
                "slots2": slots2,
                "b_width": b_width,
                "b_height": b_height,
                "clearance": clearance,
                "shaft_d1": shaft_d1,
                "torque": torque,
                "dp1": dp1,
                "dp2": dp2,
                "rp1": rp1,
                "rp2": rp2,
                "ro1": ro1,
                "ro2": ro2,
                "L_belt": L_belt,
                "C": C,
                "alpha": alpha,
                "L_tan": L_tan,
                "L_arc1": L_arc1,
                "L_arc2": L_arc2,
                "dip1": dip1,
                "dip2": dip2,
                "swing1": swing1,
                "swing2": swing2,
                "slot_depth1": slot_depth1,
                "slot_depth2": slot_depth2,
                "slot_width1": slot_width1,
                "slot_width2": slot_width2,
                "r_base1": r_base1,
                "r_base2": r_base2,
                "wall_thick1": wall_thick1,
                "is_sync": is_sync,
                "ft": ft,
                "wrap_deg1": wrap_deg1,
                "remaining_teeth1": remaining_teeth1,
            }

            self._update_report_panel()
            self._init_plot_artists()
            self._render_frame(self.s_total)
            self.canvas.draw_idle()
            return True

        except Exception as e:
            messagebox.showerror("Parameter Error", str(e))
            return False

    def _update_report_panel(self):
        p = self.params
        if p["is_sync"] and p["wall_thick1"] > 1.5 and p["C"] < 100.0:
            self.status_banner.config(text="STATUS: SYNCHRONIZED & SAFE", bg="#a6e3a1", fg="#11111b")
        elif not p["is_sync"]:
            self.status_banner.config(
                text="WARNING: NOT SYNCHRONIZED!", bg="#f38ba8", fg="#11111b"
            )
        else:
            self.status_banner.config(
                text="WARNING: CHECK WALL / C DISTANCE", bg="#fab387", fg="#11111b"
            )

        ratio_str = f"1 : {p['z2']/p['z1']:.2f}"
        report = (
            f"1. SYNCHRONIZATION & RATIO\n"
            f"   Transmission Ratio : {ratio_str}\n"
            f"   Driver Period      : {p['z1']/p['slots1']:.1f} teeth/slot\n"
            f"   Driven Period      : {p['z2']/p['slots2']:.1f} teeth/slot\n"
            f"   Synchronization    : {'YES (Matched)' if p['is_sync'] else 'NO (Collision!)'}\n"
            f"{'-'*36}\n"
            f"2. PULLEY & BELT GEOMETRY\n"
            f"   Dp / Do Driver     : {p['dp1']:.2f} / {p['ro1']*2:.2f} mm\n"
            f"   Dp / Do Driven     : {p['dp2']:.2f} / {p['ro2']*2:.2f} mm\n"
            f"   Belt Length        : {p['z_belt']} teeth ({p['L_belt']:.1f} mm)\n"
            f"   Center Distance (C): {p['C']:.2f} mm\n"
            f"   Driver Slot Angles : {[round(360*i/p['slots1'],1) for i in range(p['slots1'])]}°\n"
            f"   Driven Slot Angles : {[round(360*i/p['slots2'],1) for i in range(p['slots2'])]}°\n"
            f"{'-'*36}\n"
            f"3. CHORDAL ACTION & SLOT DIMENSIONS\n"
            f"   [Driver Pulley]\n"
            f"   - Chordal Dip      : {p['dip1']:.2f} mm\n"
            f"   - Entry Swing      : ±{p['swing1']:.2f} mm\n"
            f"   - Slot Width       : {p['slot_width1']:.2f} mm\n"
            f"   - Slot Depth       : {p['slot_depth1']:.2f} mm\n"
            f"   - Base Radius      : {p['r_base1']:.2f} mm\n\n"
            f"   [Driven Pulley]\n"
            f"   - Chordal Dip      : {p['dip2']:.2f} mm\n"
            f"   - Entry Swing      : ±{p['swing2']:.2f} mm\n"
            f"   - Slot Width       : {p['slot_width2']:.2f} mm\n"
            f"   - Slot Depth       : {p['slot_depth2']:.2f} mm\n"
            f"   - Base Radius      : {p['r_base2']:.2f} mm\n"
            f"{'-'*36}\n"
            f"4. STRENGTH & WALL THICKNESS\n"
            f"   Belt Tensile Force : {p['ft']:.2f} N ({p['ft']/9.81:.2f} kgf)\n"
            f"   Driver Wrap Angle  : {p['wrap_deg1']:.1f}°\n"
            f"   Remaining Teeth    : {p['remaining_teeth1']:.1f} teeth (Min: 6)\n"
            f"   Wall Thickness     : {p['wall_thick1']:.2f} mm\n"
        )

        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)
        self.report_text.config(state=tk.DISABLED)

    # ==================== SIMPLE PULLEY POLYGON (WITHOUT TEETH) ====================
    def _create_simple_slotted_pulley(self, ro, num_slots, slot_w, slot_d):
        """Creates a smooth outer pulley circle with defined U-slot cutouts."""
        half_w = min(slot_w / 2.0, ro * 0.92)
        r_base = max(1.0, ro - slot_d)
        phi_open = math.asin(half_w / ro)
        x_rim = math.sqrt(max(0.0, ro**2 - half_w**2))

        xs, ys = [], []
        slot_angles = [2 * math.pi * k / num_slots for k in range(num_slots)]

        for k in range(num_slots):
            sa_curr = slot_angles[k]
            sa_next = slot_angles[(k + 1) % num_slots]

            # 4 U-Slot corner points at angle sa_curr (local coordinates facing +X)
            c, s = math.cos(sa_curr), math.sin(sa_curr)
            local_slot = [
                (x_rim, -half_w),   # Slot entry lip
                (r_base, -half_w),  # Right base corner
                (r_base, half_w),   # Left base corner
                (x_rim, half_w),    # Slot exit lip
            ]
            for lx, ly in local_slot:
                xs.append(lx * c - ly * s)
                ys.append(lx * s + ly * c)

            # Smooth circular arc to next slot
            arc_start = sa_curr + phi_open
            arc_end = (sa_next - phi_open) if (k + 1 < num_slots) else (2 * math.pi - phi_open)
            if arc_end > arc_start:
                arc_angles = np.linspace(arc_start, arc_end, 40)
                xs.extend(ro * np.cos(arc_angles))
                ys.extend(ro * np.sin(arc_angles))

        return np.array(xs), np.array(ys)

    def _get_belt_point(self, s):
        """(x, y) coordinates on the closed belt path for position s (clockwise)."""
        p = self.params
        L = p["L_belt"]
        s = s % L

        rp1, rp2, C, alpha = p["rp1"], p["rp2"], p["C"], p["alpha"]
        s1_a = rp1 * (math.pi / 2.0 - alpha)
        s2_top = s1_a + p["L_tan"]
        s3_arc2 = s2_top + p["L_arc2"]
        s4_bot = s3_arc2 + p["L_tan"]

        if s < s1_a:
            ang = math.pi - (s / rp1)
            return rp1 * math.cos(ang), rp1 * math.sin(ang)
        elif s < s2_top:
            u = (s - s1_a) / p["L_tan"]
            ang = math.pi / 2.0 + alpha
            x0, y0 = rp1 * math.cos(ang), rp1 * math.sin(ang)
            x1, y1 = C + rp2 * math.cos(ang), rp2 * math.sin(ang)
            return x0 + u * (x1 - x0), y0 + u * (y1 - y0)
        elif s < s3_arc2:
            ds = s - s2_top
            ang = (math.pi / 2.0 + alpha) - (ds / rp2)
            return C + rp2 * math.cos(ang), rp2 * math.sin(ang)
        elif s < s4_bot:
            u = (s - s3_arc2) / p["L_tan"]
            ang = -math.pi / 2.0 - alpha
            x0, y0 = C + rp2 * math.cos(ang), rp2 * math.sin(ang)
            x1, y1 = rp1 * math.cos(ang), rp1 * math.sin(ang)
            return x0 + u * (x1 - x0), y0 + u * (y1 - y0)
        else:
            ds = s - s4_bot
            ang = (-math.pi / 2.0 - alpha) - (ds / rp1)
            return rp1 * math.cos(ang), rp1 * math.sin(ang)

    def _init_plot_artists(self):
        self.ax.clear()
        p = self.params

        # Simple polygon with clean U-slot cutout
        self.poly1_x, self.poly1_y = self._create_simple_slotted_pulley(
            p["ro1"], p["slots1"], p["slot_width1"], p["slot_depth1"]
        )
        self.poly2_x, self.poly2_y = self._create_simple_slotted_pulley(
            p["ro2"], p["slots2"], p["slot_width2"], p["slot_depth2"]
        )

        # Belt pitch line
        s_samples = np.linspace(0, p["L_belt"], 400)
        belt_pts = np.array([self._get_belt_point(sv) for sv in s_samples])
        self.ax.plot(belt_pts[:, 0], belt_pts[:, 1], color="#f9e2af", lw=2.0)

        # Driver & Driven pulley bodies
        (self.pulley1_patch,) = self.ax.fill([], [], color="#89b4fa", alpha=0.88, ec="#cdd6f4", lw=1.5)
        (self.pulley2_patch,) = self.ax.fill([], [], color="#74c7ec", alpha=0.88, ec="#cdd6f4", lw=1.5)

        # Auxiliary spoke lines to easily observe pulley rotation
        (self.spoke1_line,) = self.ax.plot([], [], color="#1e1e2e", lw=1.5, ls="--")
        (self.spoke2_line,) = self.ax.plot([], [], color="#1e1e2e", lw=1.5, ls="--")

        # Center shafts
        shaft1 = plt.Circle((0, 0), p["shaft_d1"] / 2.0, color="#181825", ec="#f38ba8", lw=1.5, zorder=5)
        shaft2 = plt.Circle((p["C"], 0), p["shaft_d1"] / 2.0, color="#181825", ec="#f38ba8", lw=1.5, zorder=5)
        self.ax.add_patch(shaft1)
        self.ax.add_patch(shaft2)

        # Center Distance line
        self.ax.plot([0, p["C"]], [0, 0], color="#a6adc8", ls=":", lw=1.0)
        self.ax.text(
            p["C"] / 2.0,
            -5.0,
            f"C = {p['C']:.2f} mm",
            color="#cdd6f4",
            ha="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#313244", edgecolor="none"),
        )

        # Moving bracket
        (self.bracket_patch,) = self.ax.fill([], [], color="#f38ba8", ec="#ffffff", lw=1.5, zorder=10)

        margin = 14.0
        self.ax.set_xlim(-p["rp1"] - margin, p["C"] + p["rp2"] + margin)
        y_lim = max(p["rp1"], p["rp2"]) + margin + 8.0
        self.ax.set_ylim(-y_lim, y_lim)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.grid(True, color="#313244", linestyle="--", linewidth=0.5)
        self.ax.tick_params(colors="#a6adc8", labelsize=8)
        self.ax.set_title(
            f"Slotted Pulley Kinematics Simulation (Z1={p['z1']}, Z2={p['z2']}, Belt={p['z_belt']}T)",
            color="#cdd6f4",
            fontsize=11,
            fontweight="bold",
            pad=10,
        )

    def _render_frame(self, s_total):
        p = self.params

        # 1. Driver pulley rotation directly based on linear belt travel s_total
        theta1 = math.pi - (s_total / p["rp1"])
        c1, s1 = math.cos(theta1), math.sin(theta1)
        x1_rot = self.poly1_x * c1 - self.poly1_y * s1
        y1_rot = self.poly1_x * s1 + self.poly1_y * c1
        self.pulley1_patch.set_xy(np.column_stack([x1_rot, y1_rot]))

        # Spoke line opposite slot direction (theta1 + pi)
        self.spoke1_line.set_data([0, -p["ro1"] * c1], [0, -p["ro1"] * s1])

        # 2. Driven pulley rotation directly based on s_total (ratio 1 : Z2/Z1)
        theta2 = (p["L_belt"] / (2.0 * p["rp2"])) - (s_total / p["rp2"])
        c2, s2 = math.cos(theta2), math.sin(theta2)
        x2_rot = p["C"] + (self.poly2_x * c2 - self.poly2_y * s2)
        y2_rot = self.poly2_x * s2 + self.poly2_y * c2
        self.pulley2_patch.set_xy(np.column_stack([x2_rot, y2_rot]))

        # Spoke line perpendicular to slot direction (theta2 + pi/2)
        self.spoke2_line.set_data(
            [p["C"], p["C"] - p["ro2"] * s2], [0, p["ro2"] * c2]
        )

        # 3. Rigid bracket position along belt path (s_total % L_belt)
        half_c = p["b_width"] / 2.0
        p_rear = np.array(self._get_belt_point(s_total - half_c))
        p_front = np.array(self._get_belt_point(s_total + half_c))

        tangent = p_front - p_rear
        norm_t = np.linalg.norm(tangent)
        t_hat = tangent / norm_t if norm_t > 1e-6 else np.array([1.0, 0.0])
        inward_n = np.array([t_hat[1], -t_hat[0]])

        c_rear_out = p_rear - inward_n * 2.0
        c_front_out = p_front - inward_n * 2.0
        c_front_tip = p_front + inward_n * p["b_height"]
        c_rear_tip = p_rear + inward_n * p["b_height"]

        self.bracket_patch.set_xy(np.array([c_rear_out, c_front_out, c_front_tip, c_rear_tip]))

    def _update_animation(self, frame):
        if self.is_playing and self.params:
            self.s_total += self.speed_var.get()
            pct = ((self.s_total / self.params["L_belt"]) * 100.0) % 300.0
            self.manual_pos_var.set(pct)
            self._render_frame(self.s_total)
        return []

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.config(text="Pause" if self.is_playing else "Play")

    def reset_sim(self):
        self.s_total = 0.0
        self.manual_pos_var.set(0.0)
        self._render_frame(self.s_total)
        self.canvas.draw_idle()

    def on_manual_slide(self, val):
        if not self.is_playing and self.params:
            pct = float(val)
            self.s_total = (pct / 100.0) * self.params["L_belt"]
            self._render_frame(self.s_total)
            self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = TimingBeltSlotSimulator(root)
    root.mainloop()
