from manim import *

from manim import *

class SquareToCircle(Scene):
    def construct(self):
        # Create a square
        square = Square()
        # Create a circle
        circle = Circle()

        # Transform square into circle
        self.play(Create(square))
        self.wait(0.5)
        self.play(Transform(square, circle))
        self.wait(0.5)
