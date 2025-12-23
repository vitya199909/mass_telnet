import telnetlib
import json
import time

DEFAULT_PORT = 23

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

log_file = open('log.txt', 'a')

for entry in raw_switches:
    try:
        # --- Парсимо IP і порт ---
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
        log_file.write(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} {host}:{port} SUCCESS\n{output}\n\n"
        )

    except Exception as e:
        print(f"[FAIL] {entry}: {e}")
        log_file.write(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} {entry} FAIL {e}\n\n"
        )

log_file.close()
print("All done.")