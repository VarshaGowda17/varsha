# 🚀 Get Started Now - 5 Minutes to Working QR Codes

## What Was Fixed

Your QR codes now work on **any device** - phones, tablets, computers, everywhere!

## What You Need to Do

### Step 1: Find Your IP (1 minute)

Open a terminal/command prompt and run:
```bash
python setup_qr_config.py
```

You'll see output like:
```
✓ Primary Local IP: 192.168.1.50
  Use: SERVER_ADDRESS=http://192.168.1.50:5000
```

**Remember your IP!** (e.g., 192.168.1.50)

### Step 2: Set the Configuration (1 minute)

**Choose ONE method:**

#### Method A: Environment Variable (Easiest)

**Windows (PowerShell):**
```powershell
$env:SERVER_ADDRESS = "http://192.168.1.50:5000"
```
*(Replace 192.168.1.50 with YOUR IP from Step 1)*

**Windows (Command Prompt):**
```cmd
set SERVER_ADDRESS=http://192.168.1.50:5000
```

**Mac/Linux:**
```bash
export SERVER_ADDRESS="http://192.168.1.50:5000"
```

#### Method B: Using .env File

1. Create a new file named `.env` in the project folder
2. Add this line:
   ```
   SERVER_ADDRESS=http://192.168.1.50:5000
   ```
3. Save and close

### Step 3: Restart Your App (1 minute)

```bash
python app.py
```

### Step 4: Test It! (2 minutes)

1. Open http://localhost:5000 in your browser
2. Go to Admin Dashboard (login with admin/admin)
3. Click "Issue Certificate"
4. Fill in the form and click "Issue Certificate"
5. **Grab your phone!** 📱
6. Open the camera app and scan the QR code
7. ✅ The certificate page should load on your phone!

---

## Done! 🎉

Your QR codes now work everywhere! Here's what changed:

| | Before | After |
|---|--------|-------|
| QR Code Contains | `http://localhost:5000/...` | `http://192.168.1.50:5000/...` |
| Scan from same computer | ✓ Works | ✓ Works |
| Scan from other devices | ✗ Fails | ✓ Works |
| Scan from phone | ✗ Fails | ✓ Works |
| Scan from tablet | ✗ Fails | ✓ Works |

---

## For Different Scenarios

### Testing on Local Network (Home/Office)
```
SERVER_ADDRESS=http://192.168.1.50:5000
```
Works on any device on your network!

### Using a Real Domain (Production)
```
SERVER_ADDRESS=http://yourdomainname.com
```

### Different Port
```
SERVER_ADDRESS=http://192.168.1.50:8080
```

---

## Troubleshooting

**Q: I set it but QR codes still show localhost**
- Restart the app after setting SERVER_ADDRESS
- Make sure you're issuing a NEW certificate (old ones keep old QR codes)

**Q: I can't scan from my phone**
- Verify the IP address is correct (run `ipconfig` again)
- Make sure your phone is on the same WiFi network
- Try accessing http://YOUR_IP:5000 from your phone's browser directly

**Q: Which IP should I use?**
- Run `python setup_qr_config.py` - it will show you
- Use the one listed as "Primary Local IP"

---

## Need Help?

Read the detailed guides:
- **Quick Reference:** README_QR_FIX.md
- **Full Documentation:** QR_CODE_CROSS_DEVICE_FIX.md
- **Troubleshooting:** QR_FIX_SUMMARY.md

---

**That's all you need!** Enjoy your working QR codes! 🎊
