# web_dashboard.py

from flask import Flask, render_template, Response, jsonify
import cv2
import json
import os
from datetime import datetime, timedelta
from threading import Lock
import base64

app = Flask(__name__)

# Shared state (thread-safe)
state_lock = Lock()
dashboard_state = {
    'current_count': 0,
    'status': 'offline',
    'last_update': None,
    'events': [],  # Recent events
    'stats': {
        'total_today': 0,
        'peak_count': 0,
        'total_events': 0
    }
}

# Store latest frame for streaming
latest_frame = None
frame_lock = Lock()


def update_dashboard_state(count, event_type=None):
    """Update dashboard state from main monitoring loop"""
    with state_lock:
        dashboard_state['current_count'] = count
        dashboard_state['status'] = 'monitoring'
        dashboard_state['last_update'] = datetime.now().isoformat()
        
        if event_type:
            event = {
                'type': event_type,
                'count': count,
                'timestamp': datetime.now().isoformat()
            }
            dashboard_state['events'].insert(0, event)
            dashboard_state['events'] = dashboard_state['events'][:50]  # Keep last 50
            
            dashboard_state['stats']['total_events'] += 1
            if count > dashboard_state['stats']['peak_count']:
                dashboard_state['stats']['peak_count'] = count


def update_frame(frame):
    """Update the latest frame for video streaming"""
    global latest_frame
    with frame_lock:
        latest_frame = frame.copy()


def generate_frames():
    """Generator for video streaming"""
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/status')
def api_status():
    """API endpoint for current status"""
    with state_lock:
        return jsonify(dashboard_state)


@app.route('/api/snapshots')
def api_snapshots():
    """API endpoint for recent snapshots"""
    from config import SNAPSHOT_DIR
    
    if not os.path.exists(SNAPSHOT_DIR):
        return jsonify([])
    
    snapshots = []
    for filename in sorted(os.listdir(SNAPSHOT_DIR), reverse=True)[:10]:
        if filename.endswith('.jpg'):
            filepath = os.path.join(SNAPSHOT_DIR, filename)
            snapshots.append({
                'filename': filename,
                'timestamp': os.path.getmtime(filepath),
                'url': f'/snapshots/{filename}'
            })
    
    return jsonify(snapshots)


def run_dashboard(host='0.0.0.0', port=5000):
    """Start the Flask dashboard server"""
    app.run(host=host, port=port, debug=False, threaded=True)
