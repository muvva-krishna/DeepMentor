import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API client setup
class AnimationGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_animation_plan(self, studybot_response: str) -> str:
        """Generate the animation plan for a given math concept."""
        system_prompt = (
            "You are a math animation director. Given a math concept, generate a sequence of visual explanation steps "
            "that would help a student understand it clearly. Think like a teacher and an animator combined. "
            "Break the explanation into logical, visual steps that build understanding progressively.\n\n"
            "Note: Some mathematical concepts require **deriving the formula**, not just stating it. So include that in your thinking. "
            "Also, think graphically—consider how shapes, graphs, labels, and transformations can convey the concept visually. "
            "Explain what appears on screen in each step. Be intuitive and pedagogical."
        )
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": studybot_response}
            ],
            model="llama3-70b-8192",
            temperature=0.4
        )
        return response.choices[0].message.content.strip()

    def generate_manim_code_from_plan(self, animation_plan: str) -> str:
        """Generate the Manim code based on the animation plan."""
        system_prompt = (
            "You are a math visualization assistant. Generate Manim Community Edition Python code based on the following animation plan. "
            "Use clear class structure and appropriate animations. Return only the code, no explanation.STRICLTY ONLY CODE, start with - from manim import *"
        )
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": animation_plan}
            ],
            model="llama3-70b-8192",
            temperature=0.4
        )
        return response.choices[0].message.content.strip()

    def clean_code(self, code: str) -> str:
        """Clean the Manim code by removing unnecessary markdown and formatting."""
        if code.strip().startswith("```"):
            code = code.strip().split("```")[1]
            if code.strip().startswith("python"):
                code = "\n".join(code.strip().split("\n")[1:])
        return code.strip()

    def fix_code(self, code: str) -> str:
        """Fix syntax or structural errors in the Manim code."""
        fix_prompt = (
            "You are a Python expert familiar with ManimCE. "
            "Fix any syntax or structural errors in the following Manim code. "
            "Do not add explanations or comments. Return corrected code only.\n\n"
            f"{code}"
        )
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You fix Manim Python code."},
                {"role": "user", "content": fix_prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.2
        )
        return self.clean_code(response.choices[0].message.content)

    def generate_final_manim_code(self, user_prompt: str) -> tuple:
        """Generate the full animation plan and Manim code from the user prompt."""
        # Step 1: Generate animation steps
        plan = self.generate_animation_plan(user_prompt)

        # Step 2: Generate Manim code based on plan
        raw_code = self.generate_manim_code_from_plan(plan)

        # Step 3: Clean and fix the code
        cleaned = self.clean_code(raw_code)
        fixed = self.fix_code(cleaned)

        return plan, fixed
