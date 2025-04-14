import subprocess
import os
import uuid
import glob

def run_manim(code_str):
    temp_filename = f"temp_{uuid.uuid4().hex[:8]}"
    file_path = f"temp/{temp_filename}.py"

    os.makedirs("temp", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(code_str)

    try:
        subprocess.run(
            ["manim", "-ql", file_path],
            check=True
        )
        return find_latest_video()
    except subprocess.CalledProcessError:
        return None

def find_latest_video():
    files = glob.glob("media/videos/**/*.mp4", recursive=True)
    return max(files, key=os.path.getctime) if files else None
