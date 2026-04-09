# 🔧 QR Code Cross-Device Fix - Summary

## Problem Solved ✅

**Before:** QR codes only worked on the device that generated them (localhost URLs)
```
QR Code: http://localhost:5000/verify/CERT123
Device A: ✓ Works
Device B: ✗ Fails (can't access localhost)
Device C: ✗ Fails (can't access localhost)
```

**After:** QR codes now work on ANY device with access to your server
```
QR Code: http://192.168.1.50:5000/verify/CERT123  (or your domain)
Device A: ✓ Works
Device B: ✓ Works  
Device C: ✓ Works
```

## Changes Made 📝

### 1. **config.py**
- Added `SERVER_ADDRESS` configuration variable
- Reads from environment variable `SERVER_ADDRESS`
- Provides fallback to localhost if not configured
- Format: `http://domain.com` or `http://192.168.1.100:5000`

### 2. **app.py**
- Added `get_public_url()` function to get the correct server address
- Updated certificate issuance to use `get_public_url()` instead of `get_base_url()`
- QR codes now encode the public URL instead of localhost

### 3. **New Helper Files**
- `.env.example` - Example environment configuration
- `QR_CODE_CROSS_DEVICE_FIX.md` - Detailed explanation and troubleshooting
- `QUICK_QR_SETUP.md` - Quick setup instructions
- `setup_qr_config.py` - Utility script to find your local IP

## How to Use 🚀

### Option 1: Using Environment Variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:SERVER_ADDRESS = "http://192.168.1.50:5000"
python app.py
```

**Windows (Command Prompt):**
```cmd
set SERVER_ADDRESS=http://192.168.1.50:5000
python app.py
```

**Linux/Mac:**
```bash
export SERVER_ADDRESS="http://192.168.1.50:5000"
python app.py
```

Replace `192.168.1.50` with your actual local IP address.

### Option 2: Using .env File

Create `.env` file in the project root:
```
SERVER_ADDRESS=http://192.168.1.50:5000
```

### Option 3: Find Your IP Easily

Run the helper script:
```bash
python setup_qr_config.py
```

This will show your local IP and provide ready-to-use commands.

## Testing 🧪

1. Set `SERVER_ADDRESS` (see above)
2. Restart the Flask app
3. Issue a new certificate (old ones still have localhost URLs)
4. Scan the QR code with **any device on your network**
5. ✓ Certificate verification page should load!

## Examples 📋

### For Local Network Testing:
```
SERVER_ADDRESS=http://192.168.1.50:5000
```
Works on any device on your local network

### For Production with Domain:
```
SERVER_ADDRESS=http://certify.myuniversity.edu
# or
SERVER_ADDRESS=https://certify.myuniversity.edu
```
Works anywhere on the internet

### For Custom Port:
```
SERVER_ADDRESS=http://10.0.0.5:8080
```
Works on any device that can access that IP and port

## Important Notes ⚠️

- **Only new certificates** will have the correct QR codes. Reissue old certificates if needed.
- **Network accessibility**: The address you set must be reachable from the devices scanning the QR codes
- **Firewall**: Ensure your firewall allows connections on the specified port
- **Port forwarding**: If behind a router and using internet access, set up port forwarding

## Troubleshooting 🔍

| Problem | Solution |
|---------|----------|
| QR codes still show localhost | Restart the app after setting SERVER_ADDRESS |
| Can't scan from other devices | Verify the IP/domain is correct and accessible |
| Connection refused error | Check firewall settings and port accessibility |
| Still not working | Run `setup_qr_config.py` to verify your network setup |

## Technical Details 🔬

The fix works by:
1. Reading `SERVER_ADDRESS` from environment or config
2. Using this address when generating QR codes (instead of localhost)
3. QR codes now contain absolute public URLs that work anywhere
4. The `/verify/<certificate_id>` route remains the same and works universally

All original functionality is preserved - just with proper cross-device support! 🎉
