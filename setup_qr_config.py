#!/usr/bin/env python3
"""
Utility script to find your local IP address and help configure SERVER_ADDRESS
"""

import socket
import sys
import os

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a public DNS server (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_all_local_ips():
    """Get all local IP addresses"""
    ips = []
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
    except Exception as e:
        print(f"Error getting all IPs: {e}")
    return ips

def main():
    print("\n" + "="*60)
    print("CertiChain-Verify: Local IP Configuration Helper")
    print("="*60 + "\n")
    
    # Get primary IP
    primary_ip = get_local_ip()
    if primary_ip:
        print(f"✓ Primary Local IP: {primary_ip}")
        print(f"  Use: SERVER_ADDRESS=http://{primary_ip}:5000\n")
    
    # Get all IPs
    all_ips = get_all_local_ips()
    if all_ips:
        print("All available IP addresses:")
        for ip in all_ips:
            if ip != '127.0.0.1':  # Skip loopback
                print(f"  - {ip}")
        print()
    
    print("Configuration Options:")
    print("-" * 60)
    
    if primary_ip and primary_ip != '127.0.0.1':
        print(f"\n1. For local network (recommended for testing):")
        print(f"   SERVER_ADDRESS=http://{primary_ip}:5000")
        print(f"\n   Windows (PowerShell):")
        print(f"   $env:SERVER_ADDRESS = \"http://{primary_ip}:5000\"")
        print(f"   python app.py")
        print(f"\n   Linux/Mac:")
        print(f"   export SERVER_ADDRESS=\"http://{primary_ip}:5000\"")
        print(f"   python app.py")
    
    print(f"\n2. For production (with your domain):")
    print(f"   SERVER_ADDRESS=http://yourdomain.com")
    print(f"   or")
    print(f"   SERVER_ADDRESS=https://yourdomain.com")
    
    print(f"\n3. Using .env file:")
    print(f"   Create .env file with: SERVER_ADDRESS=http://{primary_ip or '192.168.1.X'}:5000")
    
    print("\n" + "="*60)
    print("After setting SERVER_ADDRESS, restart the app!")
    print("New certificates will have working QR codes on all devices.")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
