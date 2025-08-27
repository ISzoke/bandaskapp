# BandaskApp Systemd Services

This file contains the systemd service configurations for BandaskApp. Copy these files to `/etc/systemd/system/` to enable automatic startup and management.

## 1. Monitor Service (bandaskapp-monitor.service)

The monitor service must start first as it provides real-time data updates to the database.

```ini
[Unit]
Description=BandaskApp Monitor Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/your/bandaskapp
Environment=PATH=/path/to/your/bandaskapp/venv/bin
ExecStart=/path/to/your/bandaskapp/venv/bin/python manage.py monitor --interval 5
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## 2. Web Server Service (bandaskapp.service)

The web server service depends on the monitor service and will only start after the monitor is running.

```ini
[Unit]
Description=BandaskApp Heating Control System
After=network.target bandaskapp-monitor.service
Requires=bandaskapp-monitor.service
Wants=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/your/bandaskapp
Environment=PATH=/path/to/your/bandaskapp/venv/bin
ExecStart=/path/to/your/bandaskapp/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Installation Instructions

1. **Replace placeholders:**
   - `YOUR_USERNAME` with your actual username
   - `/path/to/your/bandaskapp` with the actual path to your BandaskApp installation
   - If using conda instead of venv, adjust the PATH and ExecStart accordingly

2. **Copy service files:**
   ```bash
   sudo cp bandaskapp-monitor.service /etc/systemd/system/
   sudo cp bandaskapp.service /etc/systemd/system/
   ```

3. **Reload systemd and enable services:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable bandaskapp-monitor
   sudo systemctl enable bandaskapp
   ```

4. **Start services:**
   ```bash
   sudo systemctl start bandaskapp-monitor
   sudo systemctl start bandaskapp
   ```

5. **Check status:**
   ```bash
   sudo systemctl status bandaskapp-monitor
   sudo systemctl status bandaskapp
   ```

## Service Management Commands

- **Check service status:** `sudo systemctl status bandaskapp-monitor bandaskapp`
- **View service logs:** `sudo journalctl -u bandaskapp-monitor -f`
- **Restart services:** `sudo systemctl restart bandaskapp-monitor bandaskapp`
- **Stop services:** `sudo systemctl stop bandaskapp bandaskapp-monitor`

## Important Notes

- The monitor service **must** start before the web server service
- Both services will restart automatically if they crash
- Logs are available through `journalctl` for easy debugging
- Services will start automatically on system boot if enabled
