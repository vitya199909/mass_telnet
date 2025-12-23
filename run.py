import telnetlib
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ================= CONFIG =================
MAX_WORKERS = 1
DEFAULT_PORT = 23
LOG_DIR = "logs"
# ==========================================

start_time = time.perf_counter()

# --- Підготовка логів ---
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, "log.txt")
success_path = os.path.join(LOG_DIR, "success.txt")
fail_path = os.path.join(LOG_DIR, "fail.txt")

log_file = open(log_path, "a")
success_file = open(success_path, "a")
fail_file = open(fail_path, "a")

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

success_file.write(f"\n=== SUCCESS LIST ({timestamp}) ===\n")
fail_file.write(f"\n=== FAIL LIST ({timestamp}) ===\n")

# --- Дані ---
with open("credentials.json") as f:
    creds = json.load(f)

with open("switches.txt") as f:
    switches = [line.strip() for line in f if line.strip()]

with open("commands.txt") as f:
    commands = [line.strip() for line in f if line.strip()]

USERNAME = creds["username"]
PASSWORD = creds["password"]

success_count = 0
fail_count = 0

# --- Функція підключення ---
def handle_switch(entry):
    try:
        if ":" in entry:
            host, port = entry.split(":")
            port = int(port)
        else:
            host = entry
            port = DEFAULT_PORT

        tn = telnetlib.Telnet(host, port, timeout=10)

        tn.read_until(b"login: ")
        tn.write(USERNAME.encode() + b"\n")

        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode() + b"\n")

        for cmd in commands:
            tn.write(cmd.encode() + b"\n")
            time.sleep(0.5)

        tn.write(b"exit\n")
        output = tn.read_all().decode(errors="ignore")

        return ("success", f"{host}:{port}", output)

    except Exception as e:
        return ("fail", entry, str(e))


# --- Паралельне виконання ---
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(handle_switch, sw) for sw in switches]

    for future in as_completed(futures):
        status, target, result = future.result()

        if status == "success":
            success_count += 1
            success_file.write(f"{target}\n")
            log_file.write(f"{timestamp} {target} SUCCESS\n{result}\n\n")
            print(f"[OK]   {target}")
        else:
            fail_count += 1
            fail_file.write(f"{target}\n")
            log_file.write(f"{timestamp} {target} FAIL {result}\n\n")
            print(f"[FAIL] {target}")

# --- Закриття файлів ---
log_file.close()
success_file.close()
fail_file.close()

# --- Час виконання ---
end_time = time.perf_counter()
elapsed_ms = (end_time - start_time) * 1000

print("\n=== Summary ===")
print(f"Total devices: {len(switches)}")
print(f"Successful:   {success_count}")
print(f"Failed:       {fail_count}")
print(f"Time spent:   {elapsed_ms:.2f} ms")
print("================")