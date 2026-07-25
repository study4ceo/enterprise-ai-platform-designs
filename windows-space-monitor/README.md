# Windows Space Monitor

Real-time dashboard to monitor disk space consumption on Windows C: drive.

## Features

- **C: Drive Usage**: Visual progress bar showing total, used, and free space
- **Top Folders by Size**: Lists folders with their size and consumption rate per minute
- **Color-coded Alerts**:
  - 🔴 **RED**: Consuming > 1 MB/min (fast growth)
  - 🟡 **YELLOW**: Consuming > 100 KB/min (moderate growth)
  - 🟢 **GREEN**: Slow or no growth
- **Process I/O Monitoring**: Shows processes with high disk read/write activity
- **Auto-refresh**: Updates every 60 seconds (1 minute)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. Start the application
2. Open your browser to: `http://localhost:5000`
3. Dashboard will auto-refresh every 60 seconds (1 minute)

## Requirements

- Python 3.7+
- Windows OS
- Administrator privileges (for full disk access)

## How It Works

- **Folder Scanning**: Recursively scans C: drive folders to calculate sizes
- **Rate Tracking**: Takes snapshots of folder sizes over time to calculate consumption rate per minute
- **Process Monitoring**: Uses psutil to track disk I/O for all running processes
- **Real-time Updates**: JavaScript fetches fresh data every 60 seconds (1 minute)

## Notes

- First scan may take longer as it builds initial size snapshots
- Consumption rates become more accurate after 1-2 minutes of monitoring
- Some folders may require administrator access to scan

## Tech Stack

- **Backend**: Python + Flask
- **Monitoring**: psutil
- **Frontend**: HTML + CSS + Vanilla JavaScript
