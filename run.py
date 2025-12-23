import telnetlib
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_PORT = 23
MAX_PARALLEL_CONNECTIONS = 1

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "log.txt")
SUCCESS_FILE = os.path.join(LOG_DIR, "success.txt")
FAIL_FILE = os.path.join(LOG_DIR, "fail.txt")

# --- Створюємо папку logs якщо нема ---
os.makedirs(LOG_DIR, exist_ok=True)

# --- Креденшіали ---
with open('credentials.json') as f:
    creds = json.load(f)

USERNAME = creds['username']
PASSWORD = creds['password']

# --- Свічі ---
with open('switches.txt') as f:
    switches = [line.strip() for line in f if line.strip()]

# --- Команди ---
with open('commands.txt') as f:
    commands = [line.strip() for line in f if line.strip()]

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

# --- Відкриваємо файли ---
log_file = open(LOG_FILE, 'a')
success_file = open(SUCCESS_FILE, 'a')
fail_file = open(FAIL_FILE, 'a')

success_file.write(f"\n=== SUCCESS LIST ({timestamp}) ===\n")
fail_file.write(f"\n=== FAIL LIST ({timestamp}) ===\n")

def handle_switch(entry):
    try:
        if ':' in entry:
            host, port = entry.split(':')
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
        output = tn.read_all().decode(errors='ignore')

        return ("success", f"{host}:{port}", output)

    except Exception as e:
        return ("fail", entry, str(e))


success_count = 0
fail_count = 0

print(f"[INFO] Starting with {MAX_PARALLEL_CONNECTIONS} parallel connections\n")

with ThreadPoolExecutor(max_workers=MAX_PARALLEL_CONNECTIONS) as executor:
    futures = [executor.submit(handle_switch, sw) for sw in switches]

    for future in as_completed(futures):
        status, target, result = future.result()

        if status == "success":
            print(f"[SUCCESS] {target}")
            log_file.write(f"{timestamp} {target} SUCCESS\n{result}\n\n")
            success_file.write(f"{target}\n")
            success_count += 1
        else:
            print(f"[FAIL] {target}")
            log_file.write(f"{timestamp} {target} FAIL {result}\n\n")
            fail_file.write(f"{target}\n")
            fail_count += 1

log_file.close()
success_file.close()
fail_file.close()

print("\n=== Summary ===")
print(f"Total devices: {len(switches)}")
print(f"Successful:   {success_count}")
print(f"Failed:       {fail_count}")
print("================\nAll done.")