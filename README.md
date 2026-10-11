# elc-scan

An ultra-fast, asynchronous TCP port scanner inspired by **RustScan**. Powered by Python's `asyncio`, **elc-scan** is designed to scan all 65,535 ports within seconds using high-concurrency event loops, seamlessly preparing detected open ports for deep inspection with Nmap.

---

## Features

- **Asynchronous Engine:** Utilizes Python's `asyncio` and semaphores to scan thousands of ports concurrently.
- **Default Full-Port Scanning:** Scans the full `1-65535` port range automatically when no port range is specified.
- **Flexible Port Specification:** Supports single ports (`80`), port ranges (`20-1000`), and comma-separated lists (`80,443,8080`).
- **Nmap Integration:** Automatically prepares ready-to-run Nmap commands for open ports, with an optional flag to execute Nmap immediately.
- **Fine-Tuned Performance:** Configurable batch size (concurrency) and socket timeouts in milliseconds.

---

## Requirements

- Python 3.8+
- *(Optional)* [Nmap](https://nmap.org/) for automated deep service detection and vulnerability scanning.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/ykaan0/scanner.git elc-scan
cd elc-scan
```

No external Python dependencies are required—**elc-scan** runs entirely on the Python Standard Library.

---

## Usage

### 1. Full Scan (All 65,535 Ports)
```bash
python elc-scan.py -a 192.168.1.1
```

### 2. Custom Port Range or Specific Ports
```bash
python elc-scan.py -a 192.168.1.1 -r 20-1000
```

```bash
python elc-scan.py -a 192.168.1.1 -r 22,80,443,8080,8443
```

### 3. Speed & Timeout Tuning
On low-latency networks, increase concurrency and lower the timeout:
```bash
python elc-scan.py -a 10.10.10.10 -b 3000 -t 800
```

### 4. Automatic Nmap Execution
Immediately launch Nmap against all discovered open ports:
```bash
python elc-scan.py -a 192.168.1.1 -r 1-10000 --nmap
```

Pass custom Nmap flags:
```bash
python elc-scan.py -a 192.168.1.1 --nmap --nmap-args "-sV -sC -A -T4"
```

---

## CLI Options

| Option | Flag | Default | Description |
|---|---|---|---|
| `--addresses` | `-a` | *Required* | Target IP address or hostname |
| `--range` | `-r` | `1-65535` | Port range or comma-separated list to scan |
| `--batch-size` | `-b` | `2000` | Maximum concurrent connections (concurrency limit) |
| `--timeout` | `-t` | `1500` | Socket connection timeout in milliseconds |
| `--nmap` | - | `False` | Automatically run Nmap on discovered open ports |
| `--nmap-args` | - | `-sV -sC` | Custom arguments passed to Nmap |
| `--help` | `-h` | - | Display help and usage information |

---

## Example Output

```text
[*] Target: 127.0.0.1 (127.0.0.1)
[*] Scanning 1000 ports | Batch: 500 | Timeout: 500ms
[+] Open 135
[+] Open 445

[*] Scan completed in 1.53s
[+] Open ports found: [135, 445]

[*] Nmap command:
    nmap -sV -sC -p 135,445 127.0.0.1
```
