# Quick Setup Guide - QR Code Fix

## 1. For Testing on Local Network

If you want to test the QR codes on multiple devices on your local network:

```bash
# Find your computer's local IP address
ipconfig  # Windows
# or
ifconfig  # Linux/Mac

# Look for IPv4 Address (usually 192.168.x.x or 10.0.0.x)
```

Then set the environment variable before running:

**Windows (PowerShell):**
```powershell
$env:SERVER_ADDRESS = "http://192.168.1.XXX:5000"  # Replace XXX with your IP last octet
python app.py
```

**Windows (Command Prompt):**
```cmd
set SERVER_ADDRESS=http://192.168.1.XXX:5000
python app.py
```

**Linux/Mac:**
```bash
export SERVER_ADDRESS="http://192.168.1.XXX:5000"
python app.py
```

Then scan QR codes from any device on the same network!

## 2. For Production (Using a Domain)

Set your domain before running:
```bash
export SERVER_ADDRESS="http://yourdomain.com"
# or
export SERVER_ADDRESS="https://yourdomain.com"  # Use HTTPS if available
```

## 3. Using .env File (Recommended)

Create a `.env` file in the project root:
```
SERVER_ADDRESS=http://192.168.1.50:5000
```

The app will automatically read it when you run `python app.py`

---

**That's it!** New certificates will now have QR codes that work on any device! 🎉
