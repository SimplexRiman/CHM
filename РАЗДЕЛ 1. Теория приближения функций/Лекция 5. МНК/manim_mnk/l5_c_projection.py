"""C: МНК как проекция вектора b на образ Col(A). Чистый вариант."""
import numpy as np
import manimgx as m

# A = [[1,0],[0,1],[1,1]] (столбцы a1, a2), b = (0,0,3) на оси z.
# Col(A) — плоскость z = x + y. Решение целое: x^ = (1,1), p = (1,1,2).
A1 = np.array([1.0, 0.0, 1.0])
A2 = np.array([0.0, 1.0, 1.0])
B = np.array([0.0, 0.0, 3.0])
XHAT = np.array([1.0, 1.0])
P = np.array([1.0, 1.0, 2.0])
E = B - P  # (-1,-1,1), длина sqrt(3)


class LeastSquaresProjection(m.ThreeDScene):
    def construct(self) -> None:
        self.set_camera_orientation(phi=70 * m.DEGREES, theta=-60 * m.DEGREES)

        title = m.Text("МНК — проекция вектора b на образ Col(A)", font_size=28)
        title.to_corner(m.UL, buff=0.4)
        self.add_fixed_in_frame_mobjects(title)

        axes = m.ThreeDAxes(
            x_range=[-1, 3, 1],
            y_range=[-1, 3, 1],
            z_range=[-1, 4, 1],
            x_length=5.0,
            y_length=5.0,
            z_length=3.8,
        )

        def plane_uv(u: float, v: float) -> np.ndarray:
            return axes.c2p(u, v, u + v)

        plane = m.Surface(
            plane_uv, u_range=[-0.5, 2.5], v_range=[-0.5, 2.5],
            fill_opacity=0.35, stroke_width=1,
        )
        try:
            plane.set_color(m.BLUE_E)
            plane.set_opacity(0.30)
        except Exception:
            pass

        o = axes.c2p(0, 0, 0)
        a1_arrow = m.Arrow(o, axes.c2p(*A1), buff=0, color=m.GREEN, stroke_width=8)
        a2_arrow = m.Arrow(o, axes.c2p(*A2), buff=0, color=m.GREEN, stroke_width=8)
        b_arrow = m.Arrow(o, axes.c2p(*B), buff=0, color=m.RED, stroke_width=10)
        p_arrow = m.Arrow(o, axes.c2p(*P), buff=0, color=m.YELLOW, stroke_width=10)
        e_line = m.DashedLine(
            axes.c2p(*P), axes.c2p(*B),
            color=m.PINK, stroke_width=6, dash_length=0.1,
        )
        p_dot = m.Dot(axes.c2p(*P), radius=0.13, color=m.YELLOW)
        b_dot = m.Dot(axes.c2p(*B), radius=0.13, color=m.RED)

        # маркер прямого угла в точке p: квадрат на (d_inplane, e_dir)
        d_in = (A1 + A2) / np.linalg.norm(A1 + A2) * 0.28
        e_dir = E / np.linalg.norm(E) * 0.28
        q0 = P
        q1 = P + d_in
        q2 = P + d_in + e_dir
        q3 = P + e_dir
        elbow = m.Polygon(
            axes.c2p(*q0), axes.c2p(*q1), axes.c2p(*q2), axes.c2p(*q3),
            color=m.PINK, stroke_width=4, fill_opacity=0.0,
        )

        # подписи у стрелок (в 3D, с выносом от концов)
        lab_b = m.MathTex(r"\mathbf{b}", font_size=52, color=m.RED)
        lab_b.move_to(axes.c2p(0.0, -0.35, 3.25))
        lab_p = m.MathTex(r"\mathbf{p}=A\hat{\mathbf{x}}", font_size=44, color=m.YELLOW)
        lab_p.move_to(axes.c2p(1.75, 1.35, 2.0))
        lab_e = m.MathTex(r"\mathbf{e}", font_size=48, color=m.PINK)
        lab_e.move_to(axes.c2p(-0.15, 0.05, 2.75))
        lab_col = m.MathTex(r"\mathrm{Col}(A)", font_size=44, color=m.BLUE_B)
        lab_col.move_to(axes.c2p(2.35, 2.35, 4.7))

        # легенда + формулы (фиксированы на экране, не ездят с камерой)
        leg_b = m.Text("b — вне плоскости", font_size=24, color=m.RED)
        leg_p = m.Text("p = Ax^ — проекция", font_size=24, color=m.YELLOW)
        leg_e = m.Text("e = b − p ⊥ Col(A)", font_size=24, color=m.PINK)
        f1 = m.MathTex(r"\hat{x} = (A^T A)^{-1} A^T b", font_size=36)
        f2 = m.MathTex(r"A^T(b - A\hat{x}) = 0", font_size=36, color=m.PINK)
        panel = m.VGroup(leg_b, leg_p, leg_e, f1, f2).arrange(
            m.DOWN, buff=0.18, aligned_edge=m.LEFT
        )
        panel.to_corner(m.DR, buff=0.5)
        self.add_fixed_in_frame_mobjects(panel)
        # сначала показываем только первые две строки легенды? проще: всё сразу в конце.
        # Чтобы не спойлерить: держим panel скрытой до нужного момента.
        panel.save_state()
        panel.scale(0.01)
        panel.set_opacity(0)

        step1 = m.Text("Шаг 1: плоскость Col(A) и её базис", font_size=26)
        step1.to_corner(m.DL, buff=0.5)
        step2 = m.Text("Шаг 2: вектор b — вне плоскости", font_size=26, color=m.RED)
        step2.to_corner(m.DL, buff=0.5)
        step3 = m.Text("Шаг 3: опускаем перпендикуляр", font_size=26, color=m.PINK)
        step3.to_corner(m.DL, buff=0.5)
        step4 = m.Text("МНК = ближайшая точка образа", font_size=26, color=m.GREEN)
        step4.to_corner(m.DL, buff=0.5)
        for s in (step1, step2, step3, step4):
            self.add_fixed_in_frame_mobjects(s)
            s.save_state()
            s.scale(0.01)
            s.set_opacity(0)

        def show_step(s: m.Mobject) -> None:
            s.restore()
        # --- действие ---
        self.add(axes)
        show_step(step1)
        self.play(m.Create(plane), run_time=1.5)
        self.play(
            m.GrowArrow(a1_arrow), m.GrowArrow(a2_arrow),
            m.FadeIn(lab_col),
            run_time=1.4,
        )
        self.wait(0.6)

        step1.save_state(); step1.scale(0.01); step1.set_opacity(0)
        show_step(step2)
        self.play(m.GrowArrow(b_arrow), m.FadeIn(b_dot), m.Write(lab_b), run_time=1.4)
        self.wait(0.8)

        # смена ракурса: вид сбоку, чтобы было видно, что b висит над плоскостью
        self.move_camera(phi=68 * m.DEGREES, theta=-30 * m.DEGREES, run_time=1.6)
        self.wait(0.4)

        step2.save_state(); step2.scale(0.01); step2.set_opacity(0)
        show_step(step3)
        self.play(m.Create(e_line), m.Write(lab_e), run_time=1.4)
        self.play(
            m.GrowArrow(p_arrow), m.FadeIn(p_dot),
            m.Write(lab_p),
            m.Create(elbow),
            a1_arrow.animate.set_opacity(0.35),
            a2_arrow.animate.set_opacity(0.35),
            run_time=1.6,
        )
        self.wait(0.6)

        step3.save_state(); step3.scale(0.01); step3.set_opacity(0)
        show_step(step4)
        panel.restore()
        self.play(m.FadeIn(panel), run_time=1.4)
        # медленный облёт для объёма — короткий, подписи уже стоят
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)
