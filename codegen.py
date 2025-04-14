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
    "You are a math animation director. Your job is to visually explain mathematical concepts to students in a clear, "
    "progressive, and intuitive way — like a great teacher who also thinks like an animator.\n\n"
    "Given a response from a math tutor, your goal is to create a sequence of animation steps that help learners understand "
    "the underlying logic, derivations, and mathematical relationships.\n\n"
    "Rules:\n\n"
    "1. Focus only on the **core mathematical logic**, derivations, and equations.\n"
    "2. Ignore greetings, conversational fluff, or unrelated narrative — only extract what needs to be visualized.\n"
    "3. Use LaTeX math expressions if available (e.g., $$a^2 + b^2 = c^2$$).\n"
    "4. Derivations should be prioritized. If the formula or result is presented, also show how it was reached.\n"
    "5. Break the explanation into short, visually intuitive steps that follow a teacher’s flow of instruction.\n"
    "6. Think graphically — explain what appears on the screen in each step:\n"
    "   - equations building up\n"
    "   - variables highlighted\n"
    "   - graphs forming\n"
    "   - shapes transforming\n"
    "   - substitutions being animated\n\n"
    "Example:\n"
    "Step 1: Display the definition of the area of a circle: $$A = \\pi r^2$$\n"
    "Step 2: Show a circle with radius labeled, and highlight the radius.\n"
    "Step 3: Visually derive the formula using small sectors being rearranged...\n\n"
    "Be intuitive and pedagogical, always thinking: \"What would help a student *see* and understand this better?\"\n"
        )


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
        system_prompt = (
    "You are a math visualization assistant. Given the animation plan below, generate **clear, structured Manim Community Edition Python code**. "
    "The code should be logically organized, keeping in mind each step of the animation.\n\n"
    "Follow these guidelines:\n"
    "1. **Use classes and methods** to ensure the code is modular, and each step of the animation is represented clearly in the structure.\n"
    "2. **Retain context between steps** — the previous steps should build towards the next. For example, if you introduce a circle or variable, it should persist across the animation until it's no longer relevant.\n"
    "3. **Use Manim’s standard objects and animations**. Start with the appropriate imports (`from manim import *`), and use standard Manim methods like `FadeIn`, `Create`, `Write`, `Transform`, etc.\n"
    "4. Break the animation into logical sequences. For example:\n"
    "   - **Step 1:** Set up the scene.\n"
    "   - **Step 2:** Introduce the concept (e.g., draw a circle, write an equation).\n"
    "   - **Step 3:** Animate transformations, transitions, and effects based on the animation plan.\n"
    "5. **Be efficient and concise**. Avoid unnecessary steps. Only include animations that directly contribute to explaining the concept.\n"
    "6. **Return only the code** — no explanations or descriptions.\n"
    "7. The code should be **easy to follow** for someone working with Manim for the first time.\n"
    "8. Return strictly the Manim code, starting with:\n"
    "   from manim import *\n"
    "9. No other markdown content other than the code should be present\n"
    "Animation Plan:\n\n"
    "Example of expected behavior:\n"
    "- In a step explaining the area of a circle: Draw the circle, label the radius, animate the formula building with text, then show the area formula with transformations.\n\n"
    "Return strictly the Manim code, starting with:\n"
    "from manim import *\n"
)


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
