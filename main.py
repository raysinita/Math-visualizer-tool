from manim import *
import numpy as np

class PowerOfPoint(Scene):
    """Power of a Point — both inside and outside cases."""

    def construct(self):
        circle = Circle(radius=2.5, color=TEAL)
        self.play(Create(circle))
        self.wait(0.3)

        # ── CASE 1: P inside the circle (intersecting chords) ──────────
        title1 = Text("Case 1: P inside — intersecting chords",
                      font_size=28).to_edge(UP)
        self.play(Write(title1))

        P_in = Dot(point=LEFT * 0.6 + DOWN * 0.3, color=PURPLE)
        P_lbl = MathTex(r"P").next_to(P_in, UL, buff=0.1)
        self.play(FadeIn(P_in), Write(P_lbl))

        # Chord 1: angle ~20 deg
        A, B = self._chord_pts(P_in.get_center(), np.radians(20), 2.5)
        chord1 = Line(A, B, color=BLUE)
        dA = Dot(A, color=BLUE); lA = MathTex(r"A").next_to(dA, UL, buff=0.08)
        dB = Dot(B, color=BLUE); lB = MathTex(r"B").next_to(dB, DR, buff=0.08)

        # Chord 2: angle ~110 deg
        C, D = self._chord_pts(P_in.get_center(), np.radians(110), 2.5)
        chord2 = Line(C, D, color=RED)
        dC = Dot(C, color=RED); lC = MathTex(r"C").next_to(dC, UL, buff=0.08)
        dD = Dot(D, color=RED); lD = MathTex(r"D").next_to(dD, DR, buff=0.08)

        self.play(Create(chord1), FadeIn(dA, lA, dB, lB))
        self.play(Create(chord2), FadeIn(dC, lC, dD, lD))

        # Measure segments
        PA = np.linalg.norm(P_in.get_center() - A)
        PB = np.linalg.norm(P_in.get_center() - B)
        PC = np.linalg.norm(P_in.get_center() - C)
        PD = np.linalg.norm(P_in.get_center() - D)

        eq1 = MathTex(
            r"PA \cdot PB", r"=", r"PC \cdot PD",
            r"\quad\Rightarrow\quad",
            rf"{PA:.2f}" + r"\times" + rf"{PB:.2f}",
            r"=",
            rf"{PC:.2f}" + r"\times" + rf"{PD:.2f}",
        ).scale(0.7).to_edge(DOWN)
        eq1[0].set_color(BLUE)
        eq1[2].set_color(RED)

        self.play(Write(eq1))
        self.wait(2)

        # Power = d² - r²
        d_in = np.linalg.norm(P_in.get_center())
        pow_in = abs(d_in**2 - 2.5**2)
        pow_label = MathTex(
            rfr"\text{{Power}} = |d^2 - r^2| = {pow_in:.2f}"
        ).scale(0.65).next_to(eq1, UP, buff=0.15)
        self.play(FadeIn(pow_label))
        self.wait(1.5)

        # ── Animate P moving to show invariance ───────────────────────
        self.play(FadeOut(eq1, pow_label, title1))
        title2 = Text("PA·PB stays constant as chords rotate",
                      font_size=26).to_edge(UP)
        self.play(Write(title2))

        angle_tracker = ValueTracker(20)

        def update_chord1(mob):
            ang = np.radians(angle_tracker.get_value())
            A2, B2 = self._chord_pts(P_in.get_center(), ang, 2.5)
            mob.put_start_and_end_on(A2, B2)

        chord1.add_updater(update_chord1)
        self.play(angle_tracker.animate.set_value(160), run_time=3, rate_func=there_and_back)
        chord1.remove_updater(update_chord1)
        self.wait(1)

        # ── CASE 2: P outside (secant-secant) ─────────────────────────
        self.play(FadeOut(*self.mobjects))
        circle2 = Circle(radius=2.5, color=TEAL)
        self.play(Create(circle2))

        title3 = Text("Case 2: P outside — secant-secant",
                      font_size=28).to_edge(UP)
        self.play(Write(title3))

        P_out = Dot(point=RIGHT * 4.2, color=PURPLE)
        P_lbl2 = MathTex(r"P").next_to(P_out, RIGHT, buff=0.1)
        self.play(FadeIn(P_out), Write(P_lbl2))

        A2, B2 = self._secant_pts(P_out.get_center(), np.radians(170), 2.5)
        C2, D2 = self._secant_pts(P_out.get_center(), np.radians(195), 2.5)

        s1 = Line(P_out.get_center(), A2, color=BLUE)
        s2 = Line(P_out.get_center(), C2, color=RED)
        dA2=Dot(A2,color=BLUE); lA2=MathTex(r"A").next_to(dA2,UL,buff=0.08)
        dB2=Dot(B2,color=BLUE); lB2=MathTex(r"B").next_to(dB2,LEFT,buff=0.08)
        dC2=Dot(C2,color=RED);  lC2=MathTex(r"C").next_to(dC2,DL,buff=0.08)
        dD2=Dot(D2,color=RED);  lD2=MathTex(r"D").next_to(dD2,LEFT,buff=0.08)

        self.play(Create(s1), FadeIn(dA2,lA2,dB2,lB2))
        self.play(Create(s2), FadeIn(dC2,lC2,dD2,lD2))

        PA2=np.linalg.norm(P_out.get_center()-A2)
        PB2=np.linalg.norm(P_out.get_center()-B2)
        PC2=np.linalg.norm(P_out.get_center()-C2)
        PD2=np.linalg.norm(P_out.get_center()-D2)

        eq2 = MathTex(
            r"PA \cdot PB = PC \cdot PD",
            rfr"\approx {PA2*PB2:.2f}"
        ).scale(0.75).to_edge(DOWN)
        self.play(Write(eq2))
        self.wait(2.5)

        self.play(FadeOut(*self.mobjects))
        outro = Text("Power of a Point: d² − r² = constant",
                     font_size=32, gradient=(BLUE, TEAL))
        self.play(Write(outro))
        self.wait(2)

    def _chord_pts(self, P, angle, R):
        """Intersections of the line through P at `angle` with circle of radius R centered at origin."""
        dx, dy = np.cos(angle), np.sin(angle)
        px, py = P[0], P[1]
        a = dx**2 + dy**2
        b = 2*(px*dx + py*dy)
        c = px**2 + py**2 - R**2
        disc = b**2 - 4*a*c
        t1 = (-b - np.sqrt(disc)) / (2*a)
        t2 = (-b + np.sqrt(disc)) / (2*a)
        A = np.array([px+dx*t1, py+dy*t1, 0])
        B = np.array([px+dx*t2, py+dy*t2, 0])
        return A, B

    def _secant_pts(self, P, angle, R):
        return self._chord_pts(P, angle, R)
