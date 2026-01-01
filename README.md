# Mass Telnet Command Executor

CLI script for mass command execution on switches via Telnet with support for:

- Connecting to multiple ports (`IP` or `IP:PORT`)
- Parallel command execution with configurable number of threads
- Connection and command execution timeouts
- Retry attempts on failed connections
- Logging to separate `logs/` folder with timestamp-based filenames
- Summary at the end with execution time (ms)
- Progress during execution
- **NEW: TFTP configuration backup support with timestamped config files**

---

## 📂 File Structure

```
run.py                  # Main script
download_config.py      # TFTP backup script
config.json             # Configuration file
switches.txt            # List of switches (IP or IP:PORT)
commands.txt            # Commands to execute
credentials.json        # Login/password
logs/                   # Logs folder with timestamped files
```

---

## ⚙️ Configuration File `config.json`

```json
{
  "default_port": 23,
  "parallel_connections": 5,
  "connection_timeout": 10,
  "command_timeout": 5,
  "max_retries": 2,
  "tftp_server": "10.1.11.97"
}
```

- `default_port` — default Telnet port
- `parallel_connections` — number of simultaneous connections
- `connection_timeout` — switch connection timeout (seconds)
- `command_timeout` — command execution timeout (seconds)
- `max_retries` — number of retry attempts on failed connections
- `tftp_server` — TFTP server IP address for configuration backups

---

## 📄 File Formats

**switches.txt**

```
192.168.1.10
192.168.1.11:2323
192.168.1.12:24
```

**commands.txt**

```
help
save
```

**credentials.json**

```json
{
  "username": "admin",
  "password": "your_pass"
}
```

---

## 🖥️ Usage

**Execute commands on switches:**
```bash
python run.py
```

**Backup configurations via TFTP:**
```bash
python download_config.py
```

- Script automatically creates `logs/` folder and timestamped log files (e.g., `log_2026-01-01_17-03-28.txt`, `success.txt`, `fail.txt`)
- Shows progress in terminal during execution
- After completion shows summary:
- Total number of switches
- Number of successful and failed connections
- Execution time (ms)

---

## 💾 TFTP Backup Feature

The `download_config.py` script automatically backs up switch configurations to a TFTP server:

- Connects to each switch from `switches.txt`
- Executes `upload cfg_toTFTP <tftp_server> dest_file <IP>_<PORT>.cfg`
- Waits for "Success" confirmation from the switch
- Falls back to alternative command format if needed
- Files are saved on TFTP server with timestamped format: `10.2.20.5_234_2026-01-01_17-03-28.cfg`

**Example output:**
```
[1/4] 10.2.20.6:234 (try 1)
Executing: upload cfg_toTFTP 10.1.11.97 dest_file 10.2.20.6_234_2026-01-01_17-03-28.cfg
Upload successful: 10.2.20.6_234_2026-01-01_17-03-28.cfg
✓ SUCCESS 10.2.20.6:234
```

---

## 📊 Logging

- `logs/log_YYYY-MM-DD_HH-MM-SS.txt` — detailed logs with timestamp in filename, containing IP, port, result and command output
- `logs/success.txt` — list of successful connections with run date
- `logs/fail.txt` — list of failed connections with run date
- Log files are created with timestamp for each script run, preserving history of all executions

---

## 🔹 Features

- Support for IP or IP:PORT
- Parallel connections with configurable number of threads
- Connection and command execution timeouts
- Retry attempts for failed connections
- Execution progress in terminal
- Summary with execution time in milliseconds
- Modular file structure for easy editing: `switches.txt`, `commands.txt`, `credentials.json`
- **TFTP configuration backup with automatic retry on command format variations**
- **Backup files named with IP, port and timestamp for easy identification and version tracking**
- **Timestamped log files preserve execution history**

---

## 📌 Recommendations

- Each script run creates a new timestamped log file, preserving complete execution history
- Config backups include timestamps, allowing version tracking and recovery
- For large networks, increase `parallel_connections`, but don't overload switches
- Old log files can be safely archived or deleted without affecting new runs

---

## ⚡ Provider Use Case Example

- Provider has 1000 switches → one script run replaces hours of manual work
- After completion, easily review:
- Failed connections (`fail.txt`)
- Successful connections (`success.txt`)
