import telnetlib
import json
import time
import os

DEFAULT_PORT = 23
LOG_DIR = "log"

# --- Створюємо папку log/, якщо її нема ---
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_PATH = os.path.join(LOG_DIR, "log.txt")
SUCCESS_PATH = os.path.join(LOG_DIR, "success.txt")
FAIL_PATH = os.path.join(LOG_DIR, "fail.txt")

# --- Креденшіали ---
with open('credentials.json') as f:
    creds = json.load(f)

USERNAME = creds['username']
PASSWORD = creds['password']

# --- Свічі ---
with open('switches.txt') as f:
    raw_switches = [line.strip() for line in f if line.strip()]

# --- Команди ---
with open('commands.txt') as f:
    commands = [line.strip() for line in f if line.strip()]

# --- Відкриваємо файли (створяться автоматично, якщо нема) ---
log_file = open(LOG_PATH, 'a')
success_file = open(SUCCESS_PATH, 'a')
fail_file = open(FAIL_PATH, 'a')

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
success_file.write(f"\n=== SUCCESS LIST ({timestamp}) ===\n")
fail_file.write(f"\n=== FAIL LIST ({timestamp}) ===\n")

success_count = 0
fail_count = 0

for entry in raw_switches:
    try:
        if ':' in entry:
            host, port = entry.split(':')
            port = int(port)
        else:
            host = entry
            port = DEFAULT_PORT

        print(f"[INFO] Connecting to {host}:{port}")

        tn = telnetlib.Telnet(host, port, timeout=10)

        tn.read_until(b"login: ")
        tn.write(USERNAME.encode() + b"\n")

        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode() + b"\n")

        for cmd in commands:
            tn.write(cmd.encode() + b"\n")
            time.sleep(1)

        tn.write(b"exit\n")
        output = tn.read_all().decode(errors='ignore')

        print(f"[SUCCESS] {host}:{port}")
        log_file.write(f"{timestamp} {host}:{port} SUCCESS\n{output}\n\n")
        success_file.write(f"{host}:{port}\n")
        success_count += 1

    except Exception as e:
        print(f"[FAIL] {entry}: {e}")
        log_file.write(f"{timestamp} {entry} FAIL {e}\n\n")
        fail_file.write(f"{entry}\n")
        fail_count += 1

log_file.close()
success_file.close()
fail_file.close()

print("\n=== Summary ===")
print(f"Total devices: {len(raw_switches)}")
print(f"Successful:   {success_count}")
print(f"Failed:       {fail_count}")
print("================\nAll done.")