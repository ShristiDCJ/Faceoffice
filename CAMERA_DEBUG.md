# Camera Feature Troubleshooting

## Common Issues & Solutions:

### 1. Browser Permissions
- **Check**: Does your browser show a permission prompt when clicking "Start Camera"?
- **Fix**: 
  - Allow camera access when prompted
  - Chrome: Settings > Privacy & Security > Site Settings > Camera
  - Firefox: Check Permissions in URL bar

### 2. HTTPS Required
- **Issue**: Camera access requires HTTPS (except localhost)
- **Current**: You're accessing via IP address (172.30.34.150)
- **Solutions**:
  - Use `http://localhost:5000` instead of IP address ✅ (Best for development)
  - Or setup HTTPS with self-signed certificate
  - Or use ngrok for HTTPS tunnel

### 3. Check Browser Console for Errors
1. Open Developer Tools: Press `F12`
2. Go to Console tab
3. Click "Start Camera" button
4. Look for red error messages
5. Share the error message

### 4. Verify Camera is Connected
- Open Camera app on your computer
- If that works, camera is connected properly
- If not, camera may be unplugged or disabled

## Quick Testing (Use Localhost):

```bash
# Open browser and navigate to:
http://localhost:5000
# Instead of:
http://172.30.34.150:5000
```

## Camera Detection Code is Correct:
- ✅ camera.js loads properly
- ✅ HTML elements have correct IDs
- ✅ JavaScript uses getUserMedia API correctly

The issue is most likely HTTPS/permissions related, not code.
