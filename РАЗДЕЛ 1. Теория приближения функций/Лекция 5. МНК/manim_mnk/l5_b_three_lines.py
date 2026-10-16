"""B: Tri pryamye bez obshchey tochki (primer 10.3 iz lektsii)."""
import numpy as np
import manimgx as m

# (a, b, c) dlya a*x1 + b*x2 = c
L1 = (1.0, 2.0, 8.5)
L2 = (2.0, 1.0, 6.7)
L3 = (1.0, 3.0, 11.1)
X_OPT = np.array([1.8, 3.1714285714])  # reshenie normalnyh uravneniy


def foot(a: float, b: float, c: float, p: np.ndarray) -> np.ndarray:
    d = (a * p[0] + b * p[1] - c) / (a * a + b * b)
    return np.array([p[0] - a * d, p[1] - b * d])


def resid(a: float, b: float, c: float, p: np.ndarray) -> float:
    return float(a * p[0] + b * p[1] - c)


class ThreeLinesLS(m.Scene):
    def construct(self) -> None:
        title = m.Text("Три прямые без общей точки", font_size=30)
        title.to_corner(m.UL, buff=0.4)
        # уравнения в цветах своих прямых
        eq1 = m.MathTex(r"x_1+2x_2=8.5", font_size=34, color=m.BLUE)
        eq2 = m.MathTex(r"2x_1+x_2=6.7", font_size=34, color=m.GREEN)
        eq3 = m.MathTex(r"x_1+3x_2=11.1", font_size=34, color=m.YELLOW)
        sys = m.VGroup(eq1, eq2, eq3).arrange(m.DOWN, buff=0.12, aligned_edge=m.LEFT)
        sys.next_to(title, m.DOWN, buff=0.25).align_to(title, m.LEFT)

        axes = m.Axes(
            x_range=[0, 5, 1], y_range=[0, 5, 1],
            x_length=5.2, y_length=4.4,
        ).shift(3.0 * m.LEFT + 1.0 * m.DOWN)
        axes.add_coordinates()

        def f1(x: float) -> float:
            return (L1[2] - L1[0] * x) / L1[1]

        def f2(x: float) -> float:
            return (L2[2] - L2[0] * x) / L2[1]

        def f3(x: float) -> float:
            return (L3[2] - L3[0] * x) / L3[1]

        l1g = axes.plot(f1, x_range=[0.5, 5], color=m.BLUE, stroke_width=6)
        l2g = axes.plot(f2, x_range=[0.9, 3.2], color=m.GREEN, stroke_width=6)
        l3g = axes.plot(f3, x_range=[0.5, 5], color=m.YELLOW, stroke_width=6)

        # треугольник попарных пересечений — «треугольник ошибок»
        T12 = np.array([1.6333333, 3.4333333])
        T13 = np.array([3.3, 2.6])
        T23 = np.array([1.8, 3.1])
        tri = m.Polygon(
            axes.c2p(*T12), axes.c2p(*T13), axes.c2p(*T23),
            color=m.RED, fill_opacity=0.15, stroke_width=3,
        )
        tri_label = m.Text("треугольник ошибок", font_size=22, color=m.RED)
        tri_label.move_to([4.3, -2.2, 0])

        px = m.ValueTracker(0.3)
        py = m.ValueTracker(0.5)

        def p_now() -> np.ndarray:
            return np.array([px.get_value(), py.get_value()])

        def make_pdot() -> m.Dot:
            p = p_now()
            return m.Dot(axes.c2p(p[0], p[1]), radius=0.1, color=m.RED)

        def make_perps() -> m.VGroup:
            p = p_now()
            g = m.VGroup()
            for (aa, bb, cc), col in [(L1, m.BLUE), (L2, m.GREEN), (L3, m.YELLOW)]:
                f = foot(aa, bb, cc, p)
                g.add(m.DashedLine(
                    axes.c2p(p[0], p[1]), axes.c2p(f[0], f[1]),
                    color=col, stroke_width=3, dash_length=0.08,
                ))
                g.add(m.Dot(axes.c2p(f[0], f[1]), radius=0.06, color=col))
            return g

        def phi_now() -> float:
            p = p_now()
            return float(sum(resid(a, b, c, p) ** 2 for (a, b, c) in (L1, L2, L3)))

        phi_num = m.DecimalNumber(phi_now(), num_decimal_places=2, font_size=40, color=m.RED)
        phi_lab = m.MathTex(r"\Phi =", font_size=40)
        phi_row = m.VGroup(phi_lab, phi_num).arrange(m.RIGHT, buff=0.2)
        phi_row.move_to([4.3, 1.8, 0])
        phi_num.add_updater(lambda d: d.set_value(phi_now()))

        pdot = m.always_redraw(make_pdot)
        perps = m.always_redraw(make_perps)

        self.play(m.Write(title), m.Write(sys), run_time=1.5)
        self.play(m.Create(axes), run_time=1.0)
        self.play(m.Create(l1g), m.Create(l2g), m.Create(l3g), run_time=1.8)
        self.play(m.FadeIn(tri), m.FadeIn(tri_label), run_time=1.0)
        warn = m.Text("общей точки нет", font_size=28, color=m.RED)
        warn.move_to([4.3, 2.6, 0])
        self.play(m.FadeIn(warn), m.FadeIn(pdot), m.FadeIn(perps), m.FadeIn(phi_row), run_time=1.2)
        self.wait(0.4)
        # vedem tochku k resheniyu MNK
        self.play(px.animate.set_value(float(X_OPT[0])),
                  py.animate.set_value(float(X_OPT[1])), run_time=3.5)
        self.wait(0.4)
        self.play(m.FadeOut(tri), m.FadeOut(tri_label), run_time=0.6)
        ans = m.MathTex(
            r"x_1^* \approx 1.80,\ x_2^* \approx 3.17",
            font_size=38, color=m.GREEN,
        )
        ans.move_to([4.3, 0.6, 0])
        norm = m.MathTex(
            r"\begin{cases} 6x_1+7x_2=33 \\ 7x_1+14x_2=57 \end{cases}",
            font_size=32,
        )
        norm.move_to([4.3, -0.9, 0])
        tag = m.Text("нормальные уравнения", font_size=24, color=m.GREY_B)
        tag.next_to(norm, m.DOWN, buff=0.15)
        self.play(m.Write(ans), run_time=1.2)
        self.play(m.Write(norm), m.FadeIn(tag), run_time=1.5)
        final_dot = m.Dot(axes.c2p(float(X_OPT[0]), float(X_OPT[1])), radius=0.12, color=m.GREEN)
        self.play(m.FadeIn(final_dot), m.Circumscribe(final_dot, color=m.GREEN), run_time=1.2)
        self.wait(1.5)
