from pathlib import Path
import subprocess
import sys

INGESTORS = Path("ingestors")

for script in INGESTORS.glob("*.py"):
    print(f"\n===== Running {script.name} =====")

    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"FAILED: {script.name}")