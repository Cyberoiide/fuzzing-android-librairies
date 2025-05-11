import os
import subprocess
import shutil
from pathlib import Path
import time
import random

# Chemin vers le binaire Sloth
SLOTH_BIN = "./sloth"
# Chemin vers le binaire cible pour le fuzzing
# TARGET_BIN = "/rootfs/boofuzz"
TARGET_BIN = "/rootfs/jpegfuzz"
# Chemin vers la bibliothèque cible pour le fuzzing
# TARGET_LIB = "/rootfs/system/lib64/libBooFuzz.so"
TARGET_LIB = "/rootfs/system/lib64/libJpegFuzz.so"
# Répertoire pour les entrées de test
INPUT_DIR = "./test"
# Répertoire pour les crashes détectés
CRASH_DIR = "./crashes"
# Nombre de cas de test à générer
NB_CASES = 10
# Taille maximale des entrées générées
MAX_INPUT_SIZE = 64

def ensure_sloth_compiled():
    """Vérifie si le binaire Sloth est compilé, sinon le compile."""
    if not Path(SLOTH_BIN).is_file():
        print("[🔨] Sloth not found — running make...")
        subprocess.run(["make"], check=True)
    else:
        print("[✓] Sloth binary already compiled.")

def generate_inputs():
    """Génère des entrées aléatoires pour le fuzzing."""
    Path(INPUT_DIR).mkdir(exist_ok=True)
    for i in range(NB_CASES):
        with open(f"{INPUT_DIR}/input{i}", "wb") as f:
            f.write(os.urandom(random.randint(6, MAX_INPUT_SIZE)))  # ≥6 bytes

def launch_fuzzer():
    """Lance le fuzzer Sloth avec les entrées générées."""
    print("=== 🚀 Launching Sloth Fuzzer ===")
    os.environ["SLOTH_TARGET_LIBRARY"] = TARGET_LIB
    subprocess.run([SLOTH_BIN, TARGET_BIN, INPUT_DIR], check=True)

def move_crashes():
    Path(CRASH_DIR).mkdir(exist_ok=True)
    for fname in os.listdir("."):
        if fname.startswith("crash-"):
            crash_path = os.path.join(CRASH_DIR, fname)
            print(f"[+] Crash detected: {fname}")
            shutil.move(fname, crash_path)

            # 🧨 Affichage hexadécimal
            print(f"\n🧨 Crash hex dump ({fname}):\n")
            subprocess.run(["xxd", crash_path])

            # 📦 Affichage en tableau de bytes formatés
            print(f"\n📦 Crash bytes (C-style):\n")
            with open(crash_path, "rb") as f:
                data = f.read()
                byte_array = [f"0x{b:02X}" for b in data]
                for i in range(0, len(byte_array), 16):
                    print(", ".join(byte_array[i:i+16]))

def main():
    """Fonction principale pour exécuter le fuzzer."""
    ensure_sloth_compiled()
    generate_inputs()
    start = time.time()
    try:
        launch_fuzzer()
    except subprocess.CalledProcessError:
        print("[-] Sloth exited with an error (likely a crash was found).")
    move_crashes()
    duration = time.time() - start
    print(f"\n==> Fuzzing completed in {duration:.2f} seconds.")
    print(f"🗂 Crash files saved in: {CRASH_DIR}/")

if __name__ == "__main__":
    main()