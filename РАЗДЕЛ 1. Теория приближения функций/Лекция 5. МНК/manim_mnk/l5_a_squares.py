"""A: MNK — прямая, невязки и квадраты ошибок. Phi = сумма площадей."""
import numpy as np
import manimgx as m

XS = np.array([0.5, 1.5, 2.5, 3.5, 4.5])
YS = np.array([1.1, 1.9, 3.1, 3.6, 4.6])
# точное решение МНК для y = a0 + a1*x
A_MAT = np.vstack([np.ones_like(XS), XS]).T
A0_OPT, A1_OPT = np.linalg.lstsq(A_MAT, YS, rcond=None)[0]


class LeastSquaresSquares(m.Scene):
    def construct(self) -> None:
        title = m.Text("МНК: прямая и квадраты ошибок", font_size=30)
        title.to_corner(m.UL, buff=0.4)
        formula = m.MathTex(
            r"\Phi(a_0, a_1) = \sum e_i^2 \to \min",
            font_size=38,
        )
        formula.next_to(title, m.DOWN, buff=0.15).align_to(title, m.LEFT)

        axes = m.Axes(
            x_range=[0, 5.5, 1],
            y_range=[0, 5.5, 1],
            x_length=6.2,
            y_length=4.2,
        ).shift(2.8 * m.LEFT + 0.8 * m.DOWN)
        axes.add_coordinates()

        dots = m.VGroup(*(
            m.Dot(axes.c2p(float(x), float(y)), radius=0.09, color=m.YELLOW)
            for x, y in zip(XS, YS)
        ))

        a0 = m.ValueTracker(2.5)
        a1 = m.ValueTracker(0.2)

        def line_func(x: float) -> float:
            return float(a0.get_value() + a1.get_value() * x)

        def make_line() -> m.VMobject:
            return axes.plot(line_func, x_range=[0, 5.5], color=m.BLUE, stroke_width=6)

        def make_residuals() -> m.VGroup:
            g = m.VGroup()
            for x, y in zip(XS, YS):
                yp = float(a0.get_value() + a1.get_value() * float(x))
                p_pred = axes.c2p(float(x), yp)
                p_real = axes.c2p(float(x), float(y))
                g.add(m.Line(p_pred, p_real, color=m.RED, stroke_width=4))
            return g

        def make_squares() -> m.VGroup:
            g = m.VGroup()
            for x, y in zip(XS, YS):
                yp = float(a0.get_value() + a1.get_value() * float(x))
                p_pred = axes.c2p(float(x), yp)
                p_real = axes.c2p(float(x), float(y))
                side = p_real - p_pred
                h = float(np.linalg.norm(side))
                if h < 1e-3:
                    continue
                # квадрат в сторону от прямой (вправо по экрану)
                ux = np.array([h, 0.0, 0.0])
                c1 = p_pred
                c2 = p_real
                c3 = p_real + ux
                c4 = p_pred + ux
                sq = m.Polygon(
                    c1, c2, c3, c4,
                    color=m.RED, fill_opacity=0.25, stroke_width=2,
                )
                g.add(sq)
            return g

        def phi_val() -> float:
            pred = a0.get_value() + a1.get_value() * XS
            return float(np.sum((pred - YS) ** 2))

        phi_num = m.DecimalNumber(phi_val(), num_decimal_places=2, font_size=40, color=m.RED)
        phi_label = m.MathTex(r"\Phi =", font_size=40)
        phi_row = m.VGroup(phi_label, phi_num).arrange(m.RIGHT, buff=0.2)
        phi_row.move_to([4.2, 1.5, 0])

        line = m.always_redraw(make_line)
        resids = m.always_redraw(make_residuals)
        squares = m.always_redraw(make_squares)
        phi_num.add_updater(lambda d: d.set_value(phi_val()))

        self.play(m.Write(title), m.Write(formula), run_time=1.5)
        self.play(m.Create(axes), m.FadeIn(dots), run_time=1.5)
        self.play(m.Create(line), m.Create(resids), run_time=1.2)
        self.play(m.FadeIn(squares), m.FadeIn(phi_row), run_time=1.2)
        self.wait(0.5)
        # плавный совместный переход к решению МНК — Phi монотонно тает
        self.play(
            a0.animate.set_value(float(A0_OPT)),
            a1.animate.set_value(float(A1_OPT)),
            run_time=4.5,
        )
        self.wait(0.5)
        opt_text = m.MathTex(
            r"\hat{a}_0 \approx %.2f,\ \hat{a}_1 \approx %.2f" % (A0_OPT, A1_OPT),
            font_size=38, color=m.GREEN,
        )
        opt_text.move_to([4.2, -0.5, 0])
        extra = m.Text("сумма площадей минимальна", font_size=26, color=m.GREEN)
        extra.next_to(opt_text, m.DOWN, buff=0.15)
        self.play(m.Write(opt_text), m.FadeIn(extra), run_time=1.2)
        self.wait(1.5)
