# ⚙️ Slotted Timing Belt Pulley Calculator & Kinematic Simulator

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Tkinter%20%7C%20Matplotlib-orange.svg)](#)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](#)

An interactive desktop application built in Python for calculating engineering parameters, chordal action geometry, and simulating the kinematics of **Slotted Timing Belt Pulleys**.

Specifically engineered for timing belt transmission mechanisms carrying **brackets / carrier attachments** on the belt, where pulleys require precision U-shaped slots to allow brackets to pass through without collision (*collision-free clearance*).

---

## 📸 Interface Overview

The application features a sleek dark-mode UI (Catppuccin theme) divided into three synchronized panels:
1. **Design Parameter & Control Panel** (Left) — Input geometry, tolerances, speed, and manual inspection sliders.
2. **Real-Time Kinematic Simulation** (Center) — Matplotlib canvas rendering continuous rotation, belt tracking, and chordal trajectories.
3. **Engineering Report & Validation** (Right) — Instant validation banners and comprehensive mechanical telemetry.

---

## ✨ Key Features

- 📐 **High-Precision Geometry & Kinematics**:
  - Exact Pitch Diameter ($D_p$) and Outer Diameter ($D_o$) calculations.
  - Closed-loop Center Distance ($C$) solved analytically via Newton-Raphson iteration.
  - Contact wrap angles ($\theta_{\text{wrap}}$) and tangent belt span lengths.
- 🎯 **Chordal Action & Slot Sizing Analysis**:
  - **Chordal Dip ($\Delta_{\text{dip}}$)**: Sinking depth calculation as the rigid bracket spans across pulley curvature.
  - **Lead-in / Exit Swing ($\delta_{\text{swing}}$)**: Angular offset dynamic clearance during belt meshing.
  - Recommended U-slot dimensions (width & depth) incorporating custom safety clearance.
- 🔄 **Automatic Synchronization Verification**:
  - Mathematical proof to verify if pulley slots and belt attachments align consistently across infinite cycles:
    $$\text{Slot Period} = \frac{Z}{\text{slots}} \quad \text{and} \quad Z_{\text{belt}} \pmod{\frac{Z}{\text{slots}}} = 0$$
- 🛡️ **Mechanical Strength & Shaft Safety Checks**:
  - Working belt tension ($F_t$) estimation from target torque ($T$).
  - Effective tooth engagement count (*remaining active teeth*).
  - Residual wall thickness between the slot base and motor/drive shaft bore.
- 🎬 **Kinematic Animation & Frame-by-Frame Inspection**:
  - Smooth real-time animation with adjustable speed.
  - **Manual Inspection Slider** ($0 - 3$ full belt cycles) for micro-stepping the bracket into and out of the pulley slot.

---

## 🧮 Theoretical Background & Engineering Formulas

| Parameter | Formula / Method | Description |
| :--- | :--- | :--- |
| **Pitch Diameter ($D_p$)** | $D_p = \frac{Z \cdot p}{\pi}$ | Standard timing belt pitch circle diameter |
| **Outer Diameter ($D_o$)** | $D_o = 2 \times (r_p - \Delta_{\text{ded}})$ | Pulley outer diameter minus tooth dedendum |
| **Center Distance ($C$)** | $L \approx 2C + \pi(r_1+r_2) + \frac{(r_2-r_1)^2}{C}$ *(Iterative)* | Closed-loop belt center-to-center distance |
| **Chordal Dip** | $\Delta_{\text{dip}} = r_p - \sqrt{r_p^2 - (w/2)^2}$ | Sagitta drop due to straight-line bracket chord |
| **Lead-in Swing** | $\delta_{\text{swing}} = h \cdot \left(\frac{w/2}{r_p}\right)$ | Corner displacement as bracket enters radius |
| **Slot Depth ($d_{\text{slot}}$)** | $d_{\text{slot}} = (h - (r_p - r_o)) + \Delta_{\text{dip}} + c$ | Minimum safe cutting depth for U-slot |
| **Slot Width ($w_{\text{slot}}$)** | $w_{\text{slot}} = 2 \cdot (w/2 + \delta_{\text{swing}} + c)$ | Minimum clearance width for bracket passage |

---

## 🛠️ System Requirements & Installation

### Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### Dependencies
Install the required scientific packages via `pip`:

```bash
pip install numpy matplotlib
```

*(Note for Linux users: ensure Tkinter is installed via `sudo apt install python3-tk`)*

---

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/ReAN25/Calculator-Slotted-Pulley.git
   cd Calculator-Slotted-Pulley
   ```
2. Run the application:
   ```bash
   python slotted_pulley_calculator.py
   ```

---

## 📖 Usage Guide

1. **Enter Parameters** (Left Panel):
   - Belt Pitch (e.g. `3.0` mm for GT2 / HTD 3M)
   - Driver ($Z_1$) and Driven ($Z_2$) tooth count
   - Belt tooth count ($Z_{\text{belt}}$)
   - Number of slots on driver/driven pulleys
   - Bracket Dimensions: Width ($b_{\text{width}}$) and Height ($b_{\text{height}}$)
   - Clearance margin & Driver shaft diameter ($D_{\text{shaft}}$)
   - Operating torque
2. **Update & Recalculate**: Click **`Update Konfigurasi & Grafik`** to recompute math and re-render the visual geometry.
3. **Verify Status Banner** (Right Panel):
   - 🟢 **STATUS: SINKRON & AMAN**: System is fully synchronized; clearances and shaft wall thickness are safe.
   - 🔴 **PERINGATAN: TIDAK SINKRON**: Bracket will collide with pulley teeth on subsequent cycles.
   - 🟠 **PERINGATAN: CEK DINDING / JARAK C**: Structural wall is too thin ($< 1.5$ mm) or center distance is invalid.
4. **Inspect Motion**: Use **Play/Pause** or slide the **Manual Inspection Slider** to scrutinize entry/exit trajectory points.

---

## 📂 Project Structure

```text
Calculator-Slotted-Pulley/
├── slotted_pulley_calculator.py   # Main application, GUI, & kinematic math
├── README.md                      # English technical documentation
└── .gitignore                     # Git ignore rules for Python / IDE artifacts
```

---

## 📄 License

This project is open-source and distributed under the **[MIT License](LICENSE)**. Feel free to use, modify, and integrate it into your robotics or mechanical design projects.
