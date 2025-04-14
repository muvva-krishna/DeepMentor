from manim import *

class ConcentricCircles(Scene):
    def construct(self):
        # Step 1: Introduction
        self.camera.background_color = "#f0f0f0"
        grid = NumberPlane(
            x_range=[-10, 10],
            y_range=[-10, 10],
            background_line_style={"stroke_color": GRAY, "stroke_opacity": 0.5},
        )
        self.add(grid)

        title = Text("Concentric Circles", font_size=48)
        title.add(MathTex("\\circ", font_size=48))
        title.arrange(RIGHT, buff=0.1)
        title.to_edge(UP)
        self.play(Write(title))

        # Step 2: Define a Circle
        circle1 = Circle(radius=2, color="#87CEEB", stroke_width=2)
        circle1.set_z_index(1)
        self.play(Create(circle1, run_time=2))
        label1 = Text("Circle", font_size=24)
        label1.next_to(circle1, UR, buff=0.2)
        arrow1 = Arrow(start=label1.get_right(), end=circle1.get_center())
        label1.add(arrow1)
        self.play(Write(label1))

        # Step 3: Introduce a Second Circle
        circle2 = Circle(radius=3, color="#FFC107", stroke_width=2)
        circle2.set_z_index(0)
        self.play(Create(circle2, run_time=2))

        # Step 4: Emphasize Concentricity
        dashed_line = DashedLine(circle1.get_center(), circle2.get_center())
        dashed_line.add_tip(tip_length=0.2)
        self.play(Write(dashed_line))
        label2 = Text("Concentric", font_size=24)
        label2.next_to(dashed_line, UP, buff=0.2)
        arrow2 = Arrow(start=label2.get_bottom(), end=dashed_line.get_center())
        label2.add(arrow2)
        self.play(Write(label2))

        # Step 5: Highlight the Relationship
        self.camera.frame.save_state()
        self.play(self.camera.frame.animate.scale(1.2), run_time=2)
        arc1 = Arc(angle=PI / 3, radius=2, color=YELLOW)
        arc1.move_to(circle1.get_center())
        arc2 = Arc(angle=PI / 3, radius=3, color=YELLOW)
        arc2.move_to(circle2.get_center())
        self.play(Create(arc1), Create(arc2), run_time=2)
        self.wait()
        self.play(Restore(self.camera.frame))
