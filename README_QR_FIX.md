# 🎯 Quick Start: Make Your QR Codes Work Everywhere

## The Problem in One Picture

```
❌ BEFORE (Broken):
   Issue Certificate → QR Code generated with: http://localhost:5000/verify/CERT123
                  ↓
        When you scan:
        Device A (same computer): ✓ Works
        Device B (phone): ✗ Failed - can't access localhost
        Device C (tablet): ✗ Failed - can't access localhost

✅ AFTER (Fixed):
   Set SERVER_ADDRESS → QR Code generated with: http://192.168.1.50:5000/verify/CERT123
                  ↓
        When you scan:
        Device A: ✓ Works
        Device B: ✓ Works
        Device C: ✓ Works
```

## 3-Step Quick Fix

### Step 1️⃣: Find Your Computer's IP

Run in terminal:
```bash
python setup_qr_config.py
```
It will show you something like:
```
✓ Primary Local IP: 192.168.1.50
  Use: SERVER_ADDRESS=http://192.168.1.50:5000
```

### Step 2️⃣: Set SERVER_ADDRESS

**Pick ONE option:**

**Option A - Windows PowerShell:**
```powershell
$env:SERVER_ADDRESS = "http://192.168.1.50:5000"
```

**Option B - Windows Command Prompt:**
```cmd
set SERVER_ADDRESS=http://192.168.1.50:5000
```

**Option C - Create .env file:**
```
# Create a file named ".env" in the project folder with:
SERVER_ADDRESS=http://192.168.1.50:5000
```

### Step 3️⃣: Restart Your App

```bash
python app.py
```

## ✅ Done! Test It Out

1. Go to Admin Dashboard
2. Issue a new certificate
3. Take out your phone
4. **Scan the QR code** 📱
5. 🎉 Certificate verification page loads!

---

## Common IP Addresses

| Device | Typical IP Range | Example |
|--------|-----------------|---------|
| Office Network | 192.168.x.x | 192.168.1.50 |
| Home Network | 192.168.x.x | 192.168.1.100 |
| School Network | 10.0.x.x | 10.0.0.50 |
| Domain Name | - | certify.myuniversity.edu |

---

## Still Have Issues? 

Check the detailed guide:
- **Full instructions:** [QR_CODE_CROSS_DEVICE_FIX.md](QR_CODE_CROSS_DEVICE_FIX.md)
- **Troubleshooting:** [QR_FIX_SUMMARY.md](QR_FIX_SUMMARY.md)

---

## What Changed in Code?

**Before:**
```python
verification_url = f"{get_base_url()}/verify/{certificate.certificate_id}"
# Result: http://localhost:5000/verify/CERT123
```

**After:**
```python
verification_url = f"{get_public_url()}/verify/{certificate.certificate_id}"
# Result: http://192.168.1.50:5000/verify/CERT123 (or your server address)
```

That's it! 🚀
