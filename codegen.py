import os
from groq import Groq
from dotenv import load_dotenv
from asset import manim_code_prompt_template,animation_plan_prompt
# Load environment variables
load_dotenv()

# Groq API client setup
class AnimationGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def generate_animation_plan(self, studybot_response: str) -> str:
        """Generate the animation plan for a given math concept."""
        system_prompt = animation_plan_prompt

        response = self.client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": studybot_response}
        ],
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.4
        )
        return response.choices[0].message.content.strip()

    def generate_manim_code_from_plan(self, animation_plan: str) -> str:
        """Generate the Manim code based on the animation plan."""
        system_prompt = manim_code_prompt_template


        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": animation_plan}
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
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
            "You are a Python and Manim Community Edition (ManimCE) expert. "
            "Your job is to review and fix the following Manim Python code. "
            "Cross-check all methods, class names, and animation logic against the latest ManimCE documentation . "
            "Fix any syntax errors, deprecated method usage, structural issues, or logic mistakes that may cause the animation to fail or behave incorrectly.\n\n"
            "Guidelines:\n"
            "- Return only the corrected Python code — no explanations, no comments.\n"
            "- Ensure correct usage of Scene, construct method, and animation functions (e.g., Create, Write, FadeIn, Transform, etc).\n"
            "- Ensure the code uses valid Manim syntax and logic: for example, objects must be added to the scene with self.add(), animations must be passed to self.play(), and so on.\n"
            "- Ensure variables are consistently used if created (e.g., use the same MathTex or Circle object across steps).\n"
            "- Maintain modular and readable code.\n\n"
            "Here is the Manim code to fix:\n\n"
            f"{code}"
        )

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You fix Manim Python code."},
                {"role": "user", "content": fix_prompt}
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
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
