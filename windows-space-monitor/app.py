"""Windows Space Monitor - Real-time disk space consumption tracker."""

import os
import time
import psutil
from pathlib import Path
from flask import Flask, render_template, jsonify
from collections import defaultdict
import threading

app = Flask(__name__)

# Store size snapshots for change calculation
size_history = defaultdict(lambda: [])  # {path: [(timestamp, size), ...]}

def cleanup_old_history():
    """Remove history older than 30 minutes."""
    current_time = time.time()
    cutoff_time = current_time - (30 * 60)  # 30 minutes ago
    
    for path in list(size_history.keys()):
        size_history[path] = [(ts, size) for ts, size in size_history[path] if ts > cutoff_time]
        if not size_history[path]:
            del size_history[path]


def get_folder_size(path):
    """Calculate total size of a folder."""
    total_size = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total_size += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total_size += get_folder_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total_size


def get_size_change(path, current_size, minutes_ago):
    """Get size change from X minutes ago."""
    if path not in size_history or not size_history[path]:
        return 0
    
    target_time = time.time() - (minutes_ago * 60)
    
    # Find closest snapshot to target time
    history = size_history[path]
    closest_snapshot = min(history, key=lambda x: abs(x[0] - target_time))
    
    # Only use if snapshot is within reasonable range (±30 seconds)
    if abs(closest_snapshot[0] - target_time) < 30:
        return current_size - closest_snapshot[1]
    
    return 0


def get_top_folders(drive="C:\\", limit=20):
    """Get top folders by size with change tracking."""
    cleanup_old_history()
    folders = []
    current_time = time.time()
    
    try:
        for entry in os.scandir(drive):
            if entry.is_dir(follow_symlinks=False):
                path = entry.path
                current_size = get_folder_size(path)
                
                # Store current snapshot
                size_history[path].append((current_time, current_size))
                
                # Calculate changes
                change_1min = get_size_change(path, current_size, 1)
                change_10min = get_size_change(path, current_size, 10)
                change_30min = get_size_change(path, current_size, 30)
                
                # Determine alert level based on 1min change
                if change_1min > 1024 * 1024:  # > 1 MB in 1 min
                    alert = "red"
                elif change_1min > 100 * 1024:  # > 100 KB in 1 min
                    alert = "yellow"
                else:
                    alert = "green"
                
                folders.append({
                    "path": path,
                    "size": current_size,
                    "size_mb": current_size / (1024 * 1024),
                    "change_1min": change_1min,
                    "change_10min": change_10min,
                    "change_30min": change_30min,
                    "change_1min_mb": change_1min / (1024 * 1024),
                    "change_10min_mb": change_10min / (1024 * 1024),
                    "change_30min_mb": change_30min / (1024 * 1024),
                    "alert": alert
                })
    except (PermissionError, OSError):
        pass
    
    # Sort by size descending
    folders.sort(key=lambda x: x["size"], reverse=True)
    return folders[:limit]


def get_process_io():
    """Get processes with high disk I/O."""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            io = proc.info['io_counters']
            if io:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "read_bytes": io.read_bytes,
                    "write_bytes": io.write_bytes,
                    "read_mb": io.read_bytes / (1024 * 1024),
                    "write_mb": io.write_bytes / (1024 * 1024)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by total I/O
    processes.sort(key=lambda x: x["read_bytes"] + x["write_bytes"], reverse=True)
    return processes[:20]


def get_disk_info():
    """Get C: drive disk usage."""
    usage = psutil.disk_usage("C:\\")
    return {
        "total_gb": usage.total / (1024**3),
        "used_gb": usage.used / (1024**3),
        "free_gb": usage.free / (1024**3),
        "percent": usage.percent
    }


@app.route("/")
def index():
    """Render dashboard."""
    return render_template("dashboard.html")


@app.route("/api/disk")
def get_disk():
    """API endpoint for disk info (fast)."""
    return jsonify(get_disk_info())


@app.route("/api/folders")
def get_folders():
    """API endpoint for folder data (slow, lazy load)."""
    return jsonify(get_top_folders())


@app.route("/api/open-folder", methods=["POST"])
def open_folder():
    """Open folder in Windows Explorer."""
    from flask import request
    import subprocess
    
    data = request.get_json()
    folder_path = data.get("path")
    
    if folder_path and os.path.exists(folder_path):
        try:
            subprocess.Popen(f'explorer "{folder_path}"')
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False, "error": "Invalid path"})


@app.route("/api/shutdown", methods=["POST"])
def shutdown():
    """Shutdown the Flask server."""
    try:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            # Alternative method for newer Flask versions
            import os
            import signal
            os.kill(os.getpid(), signal.SIGINT)
        else:
            func()
        return jsonify({"success": True, "message": "Server shutting down..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/processes")
def get_processes():
    """API endpoint for process data (lazy load)."""
    return jsonify(get_process_io())


@app.route("/api/data")
def get_data():
    """API endpoint for all dashboard data (legacy)."""
    return jsonify({
        "disk": get_disk_info(),
        "folders": get_top_folders(),
        "processes": get_process_io()
    })


if __name__ == "__main__":
    print("Starting Windows Space Monitor...")
    print("Dashboard: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
