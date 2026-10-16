"""D: Чаша Phi(a0, a1) — спуск к минимуму МНК. Обзор сверху, затем пике ко дну."""
import numpy as np
import manimgx as m

XS = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
YS = np.array([1.1, 1.9, 3.1, 3.6, 4.6])
AM = np.vstack([np.ones_like(XS), XS]).T
XOPT = np.linalg.lstsq(AM, YS, rcond=None)[0]


def phi(a0: float, a1: float) -> float:
    return float(np.sum((a0 + a1 * XS - YS) ** 2))


def descent_path(start: np.ndarray = np.array([-0.6, -0.1]), lr: float = 0.02, n: int = 400):
    p = np.array(start, dtype=float)
    pts = []
    for _ in range(n):
        pts.append((float(p[0]), float(p[1]), phi(float(p[0]), float(p[1]))))
        r = AM @ p - YS
        g = 2.0 * (AM.T @ r)
        p = p - lr * g
    pts.append((float(XOPT[0]), float(XOPT[1]), phi(float(XOPT[0]), float(XOPT[1]))))
    return pts


PATH = descent_path()
TRAIL_PTS = PATH[::5]


class LeastSquaresBowl(m.ThreeDScene):
    def construct(self) -> None:
        self.set_camera_orientation(phi=68 * m.DEGREES, theta=-55 * m.DEGREES, zoom=0.55)

        title = m.Text("Чаша Φ(a₀, a₁): минимум — это МНК", font_size=30)
        title.to_corner(m.UL, buff=0.4)
        self.add_fixed_in_frame_mobjects(title)

        axes = m.ThreeDAxes(
            x_range=[-1.5, 2.5, 1],
            y_range=[-0.5, 2.0, 0.5],
            z_range=[0, 110, 20],
            x_length=4.6,
            y_length=4.6,
            z_length=4.6,
        )
        lab_a0 = m.MathTex("a_0", font_size=36)
        lab_a0.move_to(axes.c2p(2.75, -0.5, 0))
        lab_a1 = m.MathTex("a_1", font_size=36)
        lab_a1.move_to(axes.c2p(-1.5, 2.2, 0))

        def bowl_uv(u: float, v: float) -> np.ndarray:
            return axes.c2p(u, v, phi(u, v))

        bowl = m.Surface(
            bowl_uv, u_range=[-1.5, 2.5], v_range=[-0.5, 2.0],
            resolution=(36, 36),
            fill_opacity=0.85, stroke_width=0.5,
        )
        try:
            bowl.set_fill_by_checkerboard(m.BLUE_D, m.TEAL, opacity=0.85)
        except Exception:
            try:
                bowl.set_color(m.TEAL)
            except Exception:
                pass

        # след спуска — цепочка отрезков БЕЗ заливки
        segs = m.VGroup()
        for (a0a, a1a, za), (a0b, a1b, zb) in zip(TRAIL_PTS[:-1], TRAIL_PTS[1:]):
            segs.add(m.Line(
                axes.c2p(a0a, a1a, za + 0.4), axes.c2p(a0b, a1b, zb + 0.4),
                color=m.YELLOW, stroke_width=5,
            ))

        t = m.ValueTracker(0.0)

        def make_ball() -> m.Dot:
            k = int(t.get_value() * (len(TRAIL_PTS) - 1))
            k = max(0, min(k, len(TRAIL_PTS) - 1))
            a0, a1, z = TRAIL_PTS[k]
            return m.Dot(axes.c2p(a0, a1, z + 0.4), radius=0.13, color=m.RED)

        ball = m.always_redraw(make_ball)
        zmin = phi(float(XOPT[0]), float(XOPT[1]))
        opt_dot = m.Dot(
            axes.c2p(float(XOPT[0]), float(XOPT[1]), zmin),
            radius=0.14, color=m.GREEN,
        )

        cap1 = m.Text("Шаг 1: вся чаша Φ — видно дно", font_size=26)
        cap1.to_corner(m.DL, buff=0.5)
        cap2 = m.Text("Шаг 2: шарик катится вниз по градиенту", font_size=26)
        cap2.to_corner(m.DL, buff=0.5)
        cap3 = m.Text("Дно чаши — решение МНК", font_size=26, color=m.GREEN)
        cap3.to_corner(m.DL, buff=0.5)
        for s in (cap1, cap2, cap3):
            self.add_fixed_in_frame_mobjects(s)
            s.save_state()
            s.scale(0.01)
            s.set_opacity(0)

        f1 = m.MathTex(r"\nabla\Phi = 0", font_size=44, color=m.GREEN)
        f2 = m.MathTex(r"A^T A x = A^T b", font_size=38)
        panel = m.VGroup(f1, f2).arrange(m.DOWN, buff=0.2, aligned_edge=m.LEFT)
        panel.to_corner(m.DR, buff=0.5)
        self.add_fixed_in_frame_mobjects(panel)
        panel.save_state()
        panel.scale(0.01)
        panel.set_opacity(0)

        self.add(axes)
        cap1.restore()
        self.play(m.Create(bowl), m.FadeIn(lab_a0), m.FadeIn(lab_a1), run_time=2.0)
        self.wait(0.6)
        cap1.save_state(); cap1.scale(0.01); cap1.set_opacity(0)
        cap2.restore()
        self.play(m.Create(segs), m.FadeIn(ball), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=0.12)
        self.play(t.animate.set_value(1.0), run_time=6.0)
        self.stop_ambient_camera_rotation()
        cap2.save_state(); cap2.scale(0.01); cap2.set_opacity(0)
        cap3.restore()
        # пике ко дну
        self.move_camera(
            phi=62 * m.DEGREES, theta=-35 * m.DEGREES, zoom=1.5,
            frame_center=axes.c2p(float(XOPT[0]), float(XOPT[1]), zmin),
            run_time=2.0,
        )
        panel.restore()
        self.play(m.FadeIn(opt_dot), m.Write(f1), run_time=1.0)
        self.play(m.Write(f2), run_time=1.0)
        self.wait(2.0)
