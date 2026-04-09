# Testing the Cross-Device QR Code Fix

## Pre-Test Checklist

- [ ] Python 3.7+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Project folder accessible
- [ ] Admin account credentials available
- [ ] Another device (phone/tablet) available for testing

---

## Test Environment Setup

### Setup 1: Single Device Testing (Basic)

**Time:** 5 minutes  
**What you need:** Just your computer

**Steps:**

1. **Start the application**
   ```bash
   cd f:\CertiChain-Verify
   python app.py
   ```
   Expected output: `* Running on http://0.0.0.0:5000`

2. **Open browser to localhost**
   ```
   http://localhost:5000
   ```
   Should see the homepage.

3. **Login with admin credentials**
   - Username: `admin`
   - Password: `admin`

4. **Visit QR Setup page**
   - Click profile dropdown (top right)
   - Select "QR Code Setup"
   - Note the automatically detected IP (e.g., 192.168.1.100)

5. **Click "Save Configuration"**
   - Confirm success message
   - Check that `qr_config.json` was created in project root

6. **Issue a test certificate**
   - Go to Admin Dashboard
   - Click "Issue Certificate"
   - Fill in the form:
     - Student Name: John Doe
     - Student ID: 12345
     - Course Name: Python 101
     - Degree Type: Certificate
     - Department: IT
     - Graduation Date: 2024-12-17
   - Click "Issue Certificate"

7. **Verify QR code contains correct URL**
   - On the certificate view page, look at the QR code
   - Right-click on QR code → "View image"
   - OR use a QR code decoder online
   - Expected URL: `http://192.168.1.100:5000/verify/[CERT_ID]`
   - ✓ Should NOT contain localhost!

---

### Setup 2: Local Network Testing (Recommended)

**Time:** 10 minutes  
**What you need:** Computer + Phone/Tablet on same WiFi

**Prerequisites:**
1. Get your computer's IP address:
   - Windows: Open cmd → `ipconfig` → note IPv4 address
   - Mac: Open terminal → `ifconfig` → note inet address
   - Linux: Open terminal → `ip addr` → note inet address

2. Find your computer's hostname:
   - Windows: `hostname` command
   - Mac/Linux: `hostname` command

**Steps:**

1. **Update QR configuration**
   - Navigate to `/setup` page
   - Enter your IP: `http://192.168.1.100:5000` (use your actual IP)
   - Click "Save Configuration"
   - ✓ Config saved

2. **Issue a test certificate** (same as above)
   - This will generate QR code with your IP address

3. **From your phone/tablet**
   - Connect to the SAME WiFi network as your computer
   - Open phone's camera or QR scanner app
   - Scan the QR code from your computer screen
   - ✓ Should redirect to verification page with certificate details

4. **Verify certificate details are correct**
   - Should show: Student name, course, degree type, etc.
   - Status: "Valid" or "Verified"
   - ✓ Test successful!

---

### Setup 3: Advanced Testing (Production Simulation)

**Time:** 15 minutes  
**What you need:** Domain name or public IP

**Prerequisites:**
1. Configure your server for external access:
   - Option A: Use your public domain
   - Option B: Use your public IP (if not behind router)
   - Option C: Configure port forwarding on router

**Steps:**

1. **Update QR configuration**
   - Navigate to `/setup` page
   - Enter domain: `https://yourdomain.com` OR public IP
   - Click "Save Configuration"

2. **Test from external network**
   - Use a different WiFi network (mobile hotspot, different office, etc.)
   - Scan QR code
   - ✓ Should work from any network

---

## Automated Test Cases

### Test 1: Configuration Persistence
```
1. Set SERVER_ADDRESS to "http://192.168.1.100:5000"
2. Restart the app
3. Check: Config should still be set
✓ PASS if configuration persists
✗ FAIL if configuration resets to None
```

### Test 2: Automatic IP Detection
```
1. Delete qr_config.json file
2. Restart the app
3. Visit /setup page
4. Check: Local IP should be auto-populated
✓ PASS if IP is shown (not 127.0.0.1)
✗ FAIL if IP is localhost
```

### Test 3: QR Code URL Format
```
1. Issue a new certificate after configuration
2. Check the QR code URL in database/file
3. Verify format: http://[IP]:5000/verify/[CERT_ID]
✓ PASS if format is correct and uses configured IP
✗ FAIL if format is localhost or incorrect
```

### Test 4: Cross-Device Access
```
1. Issue certificate on Device A
2. Scan QR code from Device B (same network)
3. Try to access verification page
4. Verify certificate details display
✓ PASS if certificate details show correctly
✗ FAIL if verification page doesn't load
```

### Test 5: API Endpoint
```
GET /api/qr-config
Expected response:
{
  "current_server": "http://192.168.1.100:5000",
  "local_ip": "192.168.1.100",
  "configured": true
}
✓ PASS if response contains correct IP
✗ FAIL if response is missing or incorrect
```

---

## Troubleshooting During Testing

### Problem: Config not saving
```
Solution 1: Check file permissions in project directory
Solution 2: Verify admin login - setup requires admin access
Solution 3: Check disk space - ensure enough free space
Solution 4: Check qr_config.json file - should be readable
```

### Problem: Wrong IP detected
```
Solution 1: Manually set IP via /setup page
Solution 2: Use environment variable:
           export SERVER_ADDRESS="http://YOUR_IP:5000"
Solution 3: Edit qr_config.json manually with correct IP
```

### Problem: QR code not scanning on phone
```
Solution 1: Verify phone is on same WiFi network
Solution 2: Check firewall - port 5000 might be blocked
Solution 3: Try entering URL manually to test connection
Solution 4: Restart Flask app and regenerate QR code
```

### Problem: Verification page not loading
```
Solution 1: Check app is still running on your computer
Solution 2: Verify IP address is correct
Solution 3: Try accessing via browser first: http://192.168.1.100:5000
Solution 4: Check router firewall/port forwarding
```

---

## Test Results Template

```
Date: ____________
Tester: ___________
Environment: ________ (Single Device / Local Network / Production)

TEST RESULTS:

[ ] Configuration saved to qr_config.json
[ ] IP auto-detected correctly
[ ] QR code contains correct server address
[ ] QR code scans on same device
[ ] QR code scans on different device (same network)
[ ] Certificate details display correctly
[ ] Verification status shows correct
[ ] Configuration persists after app restart
[ ] API endpoint returns correct info

ISSUES FOUND:
- Issue 1: ___________________
- Issue 2: ___________________
- Issue 3: ___________________

NOTES:
_________________________________
_________________________________
_________________________________

Overall Result: [PASS / FAIL / PARTIAL]
```

---

## Success Criteria

### ✓ Testing is Successful When:

1. QR codes contain network IP instead of localhost
2. QR codes scan successfully on the same device
3. QR codes scan successfully on other devices (same network)
4. Configuration saves and persists after app restart
5. No errors in application logs
6. Certificate verification works correctly
7. Admin can easily configure the server address

### ✗ Testing Failed When:

1. QR codes still contain localhost URLs
2. QR codes cannot be scanned from other devices
3. Configuration doesn't persist after restart
4. Application errors appear in logs
5. Setup page is not accessible
6. Verification page shows errors

---

## Quick Test Command

Run this to verify everything is working:

```bash
# Test 1: Check config file exists
test -f qr_config.json && echo "✓ Config file exists" || echo "✗ Config file missing"

# Test 2: Check config content
cat qr_config.json

# Test 3: Try to access the setup page from browser
# Open: http://localhost:5000/setup (if logged in as admin)

# Test 4: Check API endpoint
# Open: http://localhost:5000/api/qr-config
```

---

## Next: User Acceptance Testing

After technical testing passes:

1. Have actual users scan QR codes
2. Collect feedback on ease of setup
3. Test with different phone models/OS
4. Test with different network types
5. Verify all certificate information displays correctly

---

## Documentation for Reference

- Full Guide: `QR_CODE_SETUP_COMPLETE.md`
- Architecture: `ARCHITECTURE_DIAGRAM.md`
- Quick Reference: `QR_QUICK_REFERENCE.md`
- Changes Summary: `CROSSDEVICE_QR_FIX_SUMMARY.md`
