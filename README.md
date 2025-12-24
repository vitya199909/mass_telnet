# Mass Telnet Command Executor

CLI script for mass command execution on switches via Telnet with support for:

- Connecting to multiple ports (`IP` or `IP:PORT`)
- Parallel command execution with configurable number of threads
- Connection and command execution timeouts
- Retry attempts on failed connections
- Logging to separate `logs/` folder (`log.txt`, `success.txt`, `fail.txt`)
- Summary at the end with execution time (ms)
- Progress during execution
- **NEW: TFTP configuration backup support**

---

## 📂 File Structure

```
run.py                  # Main script
download_config.py      # TFTP backup script
config.json             # Configuration file
switches.txt            # List of switches (IP or IP:PORT)
commands.txt            # Commands to execute
credentials.json        # Login/password
logs/                   # Logs folder
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

- Script automatically creates `logs/` folder and `log.txt`, `success.txt`, `fail.txt` files if they don't exist
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
- Files are saved on TFTP server with format: `10.2.20.5_234.cfg`

**Example output:**
```
[1/4] 10.2.20.6:234 (try 1)
Executing: upload cfg_toTFTP 10.1.11.97 dest_file 10.2.20.6_234.cfg
Upload successful: 10.2.20.6_234.cfg
✓ SUCCESS 10.2.20.6:234
```

---

## 📊 Logging

- `logs/log.txt` — detailed logs with date, IP, port, result and command output
- `logs/success.txt` — list of successful connections with run date
- `logs/fail.txt` — list of failed connections with run date

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
- **Backup files named by IP and port for easy identification**

---

## 📌 Recommendations

- Don't commit real credentials to GitHub — use `credentials.example.json`
- Multiple runs can be added to history, logging preserves previous records
- For large networks, increase `parallel_connections`, but don't overload switches

---

## ⚡ Provider Use Case Example

- Provider has 1000 switches → one script run replaces hours of manual work
- After completion, easily review:
- Failed connections (`fail.txt`)
- Successful connections (`success.txt`)
