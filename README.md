# Stremio Discord Rich Presence

Shows what you're watching in Stremio as your Discord status. Runs as a systemd user service.


<img width="587" height="510" alt="image" src="https://github.com/user-attachments/assets/60bcff63-2199-43cb-8cee-28b0697f6918" />

## Requirements
- Arch Linux (or any systemd distro)
- Stremio and Discord running
- Python 3
- A Discord application ID (https://discord.com/developers/applications)

## Install

```bash
git clone https://github.com/noahazrz/stremio-rpc.git
cd stremio-rpc

# Python environment
python -m venv ~/.venvs/stremio-rpc
~/.venvs/stremio-rpc/bin/pip install -r requirements.txt

# Script
mkdir -p ~/.local/bin
cp stremio-rpc.py ~/.local/bin/
sed -i 's/YOUR_DISCORD_APPLICATION_ID/<your real application id>/' ~/.local/bin/stremio-rpc.py

# Service
mkdir -p ~/.config/systemd/user
cp stremio-rpc.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now stremio-rpc.service
```

## Optional: desktop entry
```bash
cp com.stremio.stremio.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications
```

## Troubleshooting
```bash
systemctl --user status stremio-rpc.service
journalctl --user -u stremio-rpc.service -f
```
If Discord runs as a Flatpak or Vesktop, the IPC socket may need extra permissions.

## Uninstall
```bash
systemctl --user disable --now stremio-rpc.service
rm ~/.config/systemd/user/stremio-rpc.service ~/.local/bin/stremio-rpc.py
rm -r ~/.venvs/stremio-rpc
```
