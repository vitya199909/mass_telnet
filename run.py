import telnetlib
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- COLORS ----------
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

START_TIME = time.perf_counter()

# ---------- CONFIG ----------
with open("config.json") as f:
    config = json.load(f)

DEFAULT_PORT = config["default_port"]
CONNECTION_TIMEOUT = config["connection_timeout"]
COMMAND_DELAY = config["command_delay"]
RETRIES = config["retries"]
PARALLEL = config["parallel_workers"]

# ---------- FILES ----------
with open("credentials.json") as f:
    creds = json.load(f)

USERNAME = creds["username"]
PASSWORD = creds["password"]

with open("switches.txt") as f:
    switches = [l.strip() for l in f if l.strip()]

with open("commands.txt") as f:
    commands = [l.strip() for l in f if l.strip()]

# ---------- LOGS ----------
os.makedirs("logs", exist_ok=True)

log_path = "logs/log.txt"
success_path = "logs/success.txt"
fail_path = "logs/fail.txt"

log_file = open(log_path, "a")
success_file = open(success_path, "a")
fail_file = open(fail_path, "a")

timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
success_file.write(f"\n=== SUCCESS {timestamp} ===\n")
fail_file.write(f"\n=== FAIL {timestamp} ===\n")

# ---------- COUNTERS ----------
success_count = 0
fail_count = 0

# ---------- FUNCTION ----------
def handle_switch(entry, index, total):
    global success_count, fail_count

    if ":" in entry:
        host, port = entry.split(":")
        port = int(port)
    else:
        host = entry
        port = DEFAULT_PORT

    for attempt in range(1, RETRIES + 2):
        try:
            print(f"{Colors.CYAN}[{index}/{total}]{Colors.RESET} {Colors.BLUE}{host}:{port}{Colors.RESET} {Colors.YELLOW}(try {attempt}){Colors.RESET}")

            tn = telnetlib.Telnet(host, port, timeout=CONNECTION_TIMEOUT)
            tn.read_until(b"login: ", CONNECTION_TIMEOUT)
            tn.write(USERNAME.encode() + b"\n")

            tn.read_until(b"Password: ", CONNECTION_TIMEOUT)
            tn.write(PASSWORD.encode() + b"\n")

            for cmd in commands:
                tn.write(cmd.encode() + b"\n")
                time.sleep(COMMAND_DELAY)

            # Try both logout and exit commands for compatibility
            tn.write(b"logout\n")
            time.sleep(0.5)
            tn.write(b"exit\n")
            output = tn.read_all().decode(errors="ignore")

            log_file.write(f"{timestamp} {host}:{port} SUCCESS\n{output}\n\n")
            success_file.write(f"{host}:{port}\n")
            success_count += 1
            print(f"{Colors.GREEN}✓ SUCCESS{Colors.RESET} {host}:{port}")
            return

        except Exception as e:
            if attempt > RETRIES:
                log_file.write(f"{timestamp} {host}:{port} FAIL {e}\n\n")
                fail_file.write(f"{host}:{port}\n")
                fail_count += 1
                print(f"{Colors.RED}✗ FAILED{Colors.RESET} {host}:{port} - {e}")

# ---------- EXECUTION ----------
with ThreadPoolExecutor(max_workers=PARALLEL) as executor:
    futures = []
    total = len(switches)

    for idx, sw in enumerate(switches, 1):
        futures.append(executor.submit(handle_switch, sw, idx, total))

    for _ in as_completed(futures):
        pass

# ---------- FINISH ----------
log_file.close()
success_file.close()
fail_file.close()

END_TIME = time.perf_counter()
duration = END_TIME - START_TIME

print(f"\n{Colors.BOLD}=== SUMMARY ==={Colors.RESET}")
print(f"Total:      {Colors.CYAN}{len(switches)}{Colors.RESET}")
print(f"Success:    {Colors.GREEN}{success_count}{Colors.RESET}")
print(f"Failed:     {Colors.RED}{fail_count}{Colors.RESET}")
print(f"Time spent: {Colors.YELLOW}{duration:.3f}{Colors.RESET} seconds")



