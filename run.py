import telnetlib
import json
import time

# --- read credentials ---
with open('credentials.json') as f:
    creds = json.load(f)
USERNAME = creds['username']
PASSWORD = creds['password']

# --- read switches ---
with open('switches.txt') as f:
    switches = [line.strip() for line in f if line.strip()]

# --- read commands ---
with open('commands.txt') as f:
    commands = [line.strip() for line in f if line.strip()]

# --- open log ---
log_file = open('log.txt', 'a')

# --- main loop ---
for sw in switches:
    try:
        print(f"[INFO] Connecting to {sw}...")
        tn = telnetlib.Telnet(sw, timeout=10)
        tn.read_until(b"login: ")
        tn.write(USERNAME.encode('ascii') + b"\n")
        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode('ascii') + b"\n")
        
        for cmd in commands:
            tn.write(cmd.encode('ascii') + b"\n")
            time.sleep(1)  # short pause between commands
        
        tn.write(b"exit\n")
        output = tn.read_all().decode('ascii')
        
        print(f"[SUCCESS] {sw}")
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {sw}: SUCCESS\n{output}\n\n")
        
    except Exception as e:
        print(f"[FAIL] {sw}: {e}")
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {sw}: FAIL {e}\n\n")

log_file.close()
print("All done.")