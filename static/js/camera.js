// Camera capture functionality
let stream = null;

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startCamera');
    const captureBtn = document.getElementById('capturePhoto');
    const stopBtn = document.getElementById('stopCamera');
    const video = document.getElementById('cameraFeed');
    const canvas = document.getElementById('photoCanvas');
    const capturedPhoto = document.getElementById('capturedPhoto');
    const submitBtn = document.getElementById('submitBtn');

    // Check if browser supports getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showStatus('❌ Your browser does not support camera access. Please use Chrome, Firefox, Safari, or Edge.', 'error');
        if (startBtn) startBtn.disabled = true;
        console.error('getUserMedia not supported');
        return;
    }

    if (startBtn) {
        startBtn.addEventListener('click', async function() {
            try {
                console.log('Requesting camera access...');
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user' },
                    audio: false
                });
                console.log('Camera access granted');

                video.srcObject = stream;
                video.play();

                startBtn.disabled = true;
                captureBtn.disabled = false;
                stopBtn.disabled = false;
                showStatus('✓ Camera started successfully', 'success');
            } catch (e) {
                console.error('Camera error:', e);
                if (e.name === 'NotAllowedError') {
                    showStatus('❌ Camera permission denied. Please check your browser settings.', 'error');
                } else if (e.name === 'NotFoundError') {
                    showStatus('❌ No camera found. Please connect a camera device.', 'error');
                } else if (e.name === 'SecurityError') {
                    showStatus('❌ Camera access blocked for security reasons. Use http://localhost:5000 instead of IP address.', 'error');
                } else {
                    showStatus('❌ Error accessing camera: ' + e.message, 'error');
                }
            }
        });
    }

    if (captureBtn) {
        captureBtn.addEventListener('click', function() {
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);

            if (capturedPhoto) {
                const imageData = canvas.toDataURL('image/jpeg');
                capturedPhoto.src = imageData;
                capturedPhoto.style.display = 'block';
            }

            if (submitBtn) {
                submitBtn.disabled = false;
            }

            showStatus('✓ Photo captured successfully!', 'success');
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }

            video.srcObject = null;

            startBtn.disabled = false;
            captureBtn.disabled = true;
            stopBtn.disabled = true;
            showStatus('Camera stopped', 'info');
        });
    }
});

function showStatus(message, type) {
    const statusEl = document.getElementById('statusMessage');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.className = `status-message ${type}`;
    }
    console.log(`[${type.toUpperCase()}] ${message}`);
}

