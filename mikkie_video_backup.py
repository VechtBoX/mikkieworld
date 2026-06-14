# mikkie_video.py
from datetime import datetime
import os
import subprocess

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_video(prompt: str, style: str = "mikkie_world"):
    """
    Video generatie agent voor MIKKIE WORLD.
    Later koppelen we hier Seedance 2.0 of MoneyPrinterTurbo aan.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"video_{timestamp}.mp4")

    print(f"[{datetime.now()}] 🎬 Video genereren voor MIKKIE WORLD")
    print(f"Prompt: {prompt}")
    print(f"Stijl: {style}")

    # === HIER KOMT DE ECHTE INTEGRATIE (later invulle

    print("→ Video generatie gestart (placeholder modus)...")
    # Simuleer even werk
   # mikkie_video.py
import os
import subprocess
from datetime import datetime

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MONEY_PRINTER_PATH = "/Users/hendrikbroeze/MoneyPrinterTurbo"

def generate_video(prompt: str, style: str = "mikkie_world"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"video_{timestamp}.mp4")

    print(f"[{datetime.now()}] 🎬 MIKKIE WORLD Video Generatie")
    print(f"Prompt: {prompt}")
    print(f"Stijl: {style}")
    print("→ MoneyPrinterTurbo aanroepen...\n")

    try:
        # Probeer MoneyPrinterTurbo aan te roepen
        result = subprocess.run(
            ["python3", "main.py", "--prompt", prompt],
            cwd=MONEY_PRINTER_PATH,
            capture_output=True,
            text=True,
            timeout=300
        )

        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)
        print("==============\n")

        # Maak een logbestand + placeholder
        with open(output_path, "w") as f:
            f.write(f"MIKKIE WORLD Video\n")
            f.write(f"Prompt: {prompt}\n\n")
            f.write(f"MoneyPrinterTurbo STDOUT:\n{result.stdout}\n\n")
            f.write(f"MoneyPrinterTurbo STDERR:\n{result.stderr}")

        print(f"✅ Log opgeslagen als: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Fout: {e}")
        with open(output_path, "w") as f:
            f.write(f"ERROR: {e}")
        return output_path


if __name__ == "__main__":
    generate_video("Een schattige aap en olifant bouwen een boomhut in het bos")
