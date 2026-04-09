# Quick Reference: Cross-Device QR Code Fix

## The Problem You Had
❌ QR codes only worked on your device  
❌ Scanning from phone/tablet on same network failed  
❌ Required manual config file editing  

## The Solution
✅ QR codes now work on any device in your network  
✅ Automatic local IP detection  
✅ Easy admin panel setup in 30 seconds  
✅ Settings save automatically  

---

## Setup: 3 Simple Steps

### 1️⃣ Login
- Open app and login with admin account

### 2️⃣ Go to Setup
- Click profile dropdown → "QR Code Setup"

### 3️⃣ Save
- Click "Save Configuration" (auto-detected IP is shown)

**Done!** 🎉

---

## Test It

Issue a new certificate → Scan QR from phone on same WiFi → It works! ✓

---

## Configuration Options

| Option | Address Example | Best For |
|--------|-----------------|----------|
| Default | `http://192.168.1.100:5000` | Local network |
| Domain | `https://certs.example.com` | Internet access |
| Custom Port | `http://192.168.1.100:8000` | Different port |

---

## Find Your IP

**Windows:** Open Command Prompt → `ipconfig` → Look for IPv4  
**Mac:** Open Terminal → `ifconfig` → Look for inet  
**Linux:** Open Terminal → `ip addr` → Look for inet  

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR not scanning | Check phone is on same WiFi |
| Still doesn't work | Check firewall/router port 5000 |
| Settings not saving | Verify admin login & permissions |

---

## Documentation

📖 Full Guide: `QR_CODE_SETUP_COMPLETE.md`  
📋 Implementation Details: `CROSSDEVICE_QR_FIX_SUMMARY.md`  
📋 Technical Changes: `QR_CODE_CROSS_DEVICE_FIX.md`  

---

## Environment Variable (Optional)

```bash
export SERVER_ADDRESS="http://192.168.1.100:5000"
python app.py
```

---

## Need Help?

Check the documentation files or visit `/setup` for detailed instructions with examples!
