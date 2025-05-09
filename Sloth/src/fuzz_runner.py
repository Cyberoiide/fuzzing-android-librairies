import os
import subprocess
import shutil
from pathlib import Path
import time
import random

SLOTH_BIN = "./sloth"
TARGET_BIN = "/rootfs/boofuzz"
TARGET_LIB = "/rootfs/system/lib64/libBooFuzz.so"
INPUT_DIR = "./test"
CRASH_DIR = "./crashes"
NB_CASES = 10
MAX_INPUT_SIZE = 64

def ensure_sloth_compiled():
    if not Path(SLOTH_BIN).is_file():
        print("[*] Sloth not found — running make...")
        subprocess.run(["make"], check=True)
    else:
        print("[✓] Sloth binary already compiled.")

def generate_inputs():
    Path(INPUT_DIR).mkdir(exist_ok=True)
    for i in range(NB_CASES):
        with open(f"{INPUT_DIR}/input{i}", "wb") as f:
            f.write(os.urandom(random.randint(6, MAX_INPUT_SIZE)))  # ≥6 bytes

def launch_fuzzer():
    print("=== Launching Sloth Fuzzer ===")
    os.environ["SLOTH_TARGET_LIBRARY"] = TARGET_LIB
    subprocess.run([SLOTH_BIN, TARGET_BIN, INPUT_DIR], check=True)

def move_crashes():
    Path(CRASH_DIR).mkdir(exist_ok=True)
    for fname in os.listdir("."):
        if fname.startswith("crash-"):
            print(f"[+] Crash detected: {fname}")
            shutil.move(fname, f"{CRASH_DIR}/{fname}")

def main():
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