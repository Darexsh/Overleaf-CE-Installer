* * *

<div align="center">

# 🧩 Overleaf CE Installer (GUI + CLI)

**A cross-platform GUI installer and control panel for Overleaf Community Edition**  
🐳 Docker + 🍃 Mongo + 🔴 Redis + 🧪 optional full TeX Live

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue) ![Platform](https://img.shields.io/badge/Platform-Cross--Platform-informational) ![Python](https://img.shields.io/badge/Python-3.x-orange)

</div>

* * *

## ✨ Authors

| Name | GitHub | Role | Contributions |
| --- | --- | --- | --- |
| **[Darexsh by Daniel Sichler](https://github.com/Darexsh)** | [Link](https://github.com/Darexsh?tab=repositories) | Maintainer / GUI Development | Cross-platform installer flow, GUI controls, diagnostics, user management |
| **[ffborgo](https://github.com/ffborgo)** | [Link](https://github.com/ffborgo/overleaf-installer) | Original inspiration | Original Overleaf installer concept and workflow inspiration |

* * *

## 🚀 About the Project

This project provides both a desktop GUI and a CLI for installing and managing **Overleaf Community Edition** locally with Docker.

It is designed to keep setup simple and reproducible from a single folder, while still offering practical operations like repair, image updates, user management, diagnostics, and optional full TeX Live installation.

> Attribution note: this project is inspired by [ffborgo/overleaf-installer](https://github.com/ffborgo/overleaf-installer).  
> At the time of writing, no explicit upstream `LICENSE` file was found there. This repository licenses only the code contained in this repository.

* * *

## 🎯 Features

- 📁 **One-folder deployment**: all files are created/managed in the script directory.
- 🌐 **Local setup modes**: default `localhost:8080` or custom local port.
- 🗣️ **Default site language selector**: writes `OVERLEAF_SITE_LANGUAGE` into `overleaf.env`.
- ✅ **Preflight checks**: Git, Compose, Docker, and port status.
- 🛠️ **Install / Repair / Update** actions.
- 📚 **Optional full TeX Live**: install `scheme-full` via `tlmgr` in `sharelatex`.
- 🧱 **Container controls**: start, stop, recreate-restart, logs, refresh status.
- 👥 **User management window**: list users, select, and delete with confirmation.
- 🩺 **Diagnostics tools**: copy diagnostics and export installer log.
- 🖼️ **Fixed-size GUI with scrollable controls** and fixed-size log panel.
- 🖥️ **CLI companion**: full install/repair/control/user commands via terminal (`install_overleaf_cli.py`).

* * *

## 📥 Installation

1. Ensure requirements are available:
   - Docker Desktop running
   - `docker compose` (or `docker-compose`)
   - `git`
   - Python 3

2. Run the installer:

```powershell
python install_overleaf.py
```

```bash
python3 install_overleaf.py
```

Or run the CLI version:

```bash
python install_overleaf_cli.py --help
```

3. In the GUI:
   - select installer language (`English` or `Deutsch`)
   - choose install option (default/custom port)
   - choose default site language
   - optionally enable full TeX Live
   - click **Install**

On first setup (or after data reset), the GUI opens:

- `http://localhost:<port>/launchpad`

* * *

## 📝 Usage

1. **Install / Repair**
   - Use `Install` for normal setup.
   - Use `Repair config` to reapply env/config and recreate `sharelatex`.

2. **Apply language changes**
   - select site language in install options
   - run `Repair config`
   - hard-refresh browser (`Ctrl+F5`)

3. **Install full TeX Live**
   - check `Install full TeX Live in container (scheme-full)`
   - run `Install` or `Repair config`
   - process streams live output in log

4. **Manage users**
   - open `User Management -> Manage users`
   - refresh list
   - select user
   - delete selected user (with confirmation)

5. **Container operations**
   - use start/stop/restart/log/status buttons in Container Control

6. **CLI workflow**
   - install: `python install_overleaf_cli.py install --port 666 --site-language de`
   - repair: `python install_overleaf_cli.py repair --full-texlive`
   - users: `python install_overleaf_cli.py users list`
   - delete user: `python install_overleaf_cli.py users delete --email user@example.com`

* * *

## 📂 File Layout

All project runtime files are in this folder:

- `install_overleaf.py`
- `install_overleaf_cli.py`
- `overleaf.env`
- `docker-compose.yml`
- `data/`
- `.overleaf_installer_settings.json`
- exported logs (`installer_log_*.txt`)

* * *

## ⚙️ Technical Details

- GUI: Python Tkinter
- CLI: Python argparse
- Runtime: Docker Compose
- Services:
  - `sharelatex/sharelatex:latest`
  - `mongo:8.0`
  - `redis:7`
- Mongo replica set init is handled by installer
- Full TeX Live option uses:
  - `tlmgr update --self`
  - `tlmgr install scheme-full`
  - `tlmgr path add`
- Cross-release TeX repo mismatch is handled by auto-switch to historic TeX Live repo when needed

* * *

## 🧯 Troubleshooting

- **UI language still English**:
  run `Repair config` after changing site language, then hard-refresh browser.

- **Port busy**:
  choose another custom port.

- **Docker permission errors**:
  make sure Docker Desktop is running and your shell can access Docker.

- **Full TeX install takes long**:
  this is expected; monitor live log output.

* * *

## 📜 License

The code in this repository is licensed under the **MIT License**.

**Copyright (c) 2025 Daniel Sichler**

Please include the following notice with any use or distribution:

> Developed by Daniel Sichler aka Darexsh. Licensed under the MIT License. See `LICENSE` for details.

The full license is available in the [LICENSE](LICENSE) file.

* * *

<div align="center"><sub>Created with ❤️ by Daniel Sichler</sub></div>
