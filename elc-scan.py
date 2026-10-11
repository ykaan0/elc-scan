import argparse
import asyncio
import socket
import subprocess
import sys
import time

def parse_ports(port_arg):
    ports = set()
    for item in port_arg.split(","):
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            start, end = item.split("-", 1)
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(item))
    return sorted([p for p in ports if 1 <= p <= 65535])

async def test_port(semaphore, target_ip, port, timeout, open_ports):
    async with semaphore:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            open_ports.append(port)
            print(f"[+] Open {port}")
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            pass

async def scan(target_ip, ports, concurrency, timeout):
    semaphore = asyncio.Semaphore(concurrency)
    open_ports = []
    tasks = [
        test_port(semaphore, target_ip, port, timeout, open_ports)
        for port in ports
    ]
    await asyncio.gather(*tasks)
    return sorted(open_ports)

def main():
    parser = argparse.ArgumentParser(
        prog="elc-scan",
        description="elc-scan - Fast asynchronous port scanner inspired by RustScan",
        add_help=True
    )
    parser.add_argument("-a", "--addresses", dest="target", required=True, help="Target IP address or hostname")
    parser.add_argument("-r", "--range", dest="ports", default="1-65535", help="Port range (default: 1-65535)")
    parser.add_argument("-b", "--batch-size", dest="batch_size", type=int, default=2000, help="Batch size / concurrency (default: 2000)")
    parser.add_argument("-t", "--timeout", dest="timeout", type=int, default=1500, help="Timeout in milliseconds (default: 1500)")
    parser.add_argument("--nmap", dest="run_nmap", action="store_true", help="Run nmap automatically on open ports")
    parser.add_argument("--nmap-args", dest="nmap_args", default="-sV -sC", help="Custom arguments for nmap (default: -sV -sC)")
    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror as err:
        print(f"[-] Resolution error: {err}", file=sys.stderr)
        sys.exit(1)

    try:
        ports = parse_ports(args.ports)
    except ValueError:
        print("[-] Invalid port range specified.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Target: {args.target} ({target_ip})")
    print(f"[*] Scanning {len(ports)} ports | Batch: {args.batch_size} | Timeout: {args.timeout}ms")

    start_time = time.time()
    try:
        open_ports = asyncio.run(
            scan(target_ip, ports, args.batch_size, args.timeout / 1000.0)
        )
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
        sys.exit(0)

    elapsed = time.time() - start_time
    print(f"\n[*] Scan completed in {elapsed:.2f}s")
    print(f"[+] Open ports found: {open_ports}")

    if open_ports:
        port_list_str = ",".join(str(p) for p in open_ports)
        nmap_cmd = f"nmap {args.nmap_args} -p {port_list_str} {target_ip}"
        print(f"\n[*] Nmap command:\n    {nmap_cmd}")
        if args.run_nmap:
            print("\n[*] Executing Nmap...")
            full_cmd = ["nmap"] + args.nmap_args.split() + ["-p", port_list_str, target_ip]
            try:
                subprocess.run(full_cmd)
            except FileNotFoundError:
                print("[-] Nmap executable not found in PATH.", file=sys.stderr)

if __name__ == "__main__":
    main()