
import os
import subprocess
import secrets
import shutil
import time
import re
import json
import webbrowser
import socket
import threading
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

INSTALL_DIR = Path(__file__).resolve().parent
DEFAULT_PORT = 8080
SETTINGS_FILE = INSTALL_DIR / ".overleaf_installer_settings.json"
BASE_SHARELATEX_IMAGE = "sharelatex/sharelatex:latest"

LANG = "en"
installing_now = False
container_status_labels = {}
advanced_forced_full_texlive_prev = None

TEXTS = {
    "de": {
        "title": "Overleaf Installer - Community Edition",
        "mode_label": "Installationsoption:",
        "mode_default": "[STANDARD] localhost:8080",
        "mode_custom": "[BENUTZERDEFINIERT] localhost mit eigenem Port",
        "install_profile_label": "Installationsprofil:",
        "install_profile_basic": "Basis (offizielles Image)",
        "install_profile_advanced": "Erweitert (eigenes Dockerfile-Image)",
        "custom_image_tag_label": "Eigenes Image-Tag:",
        "custom_image_tag_hint": "Nur für Erweitert. Beispiel: overleaf-sharelatex:custom",
        "port_label": "Benutzerdefinierter Port:",
        "port_placeholder": "Beispiel: 666",
        "site_language_label": "Standard-Webseiten-Sprache:",
        "site_language_hint": "Gilt als Standardsprache für neue Sitzungen.",
        "full_texlive_check": "Vollständiges TeX Live im Container installieren (scheme-full)",
        "full_texlive_hint": "Dauert lange und lädt viele Pakete herunter.",
        "full_texlive_advanced_forced": "TeX Live wird in das eigene Docker-Image integriert.",
        "safety_label": "Sicherheitsoptionen:",
        "recreate_env_check": "overleaf.env neu erstellen (neue Secrets)",
        "reset_data_check": "Container und lokale Daten vor Installation zurücksetzen",
        "preflight_title": "Vorabprüfung",
        "refresh_checks": "Checks aktualisieren",
        "status_git": "Git",
        "status_compose": "Compose",
        "status_docker": "Docker",
        "status_port": "Port",
        "status_unknown": "Unbekannt",
        "status_ok": "OK",
        "status_fail": "Fehler",
        "actions_title": "Aktionen",
        "btn_install": "Installieren",
        "btn_repair": "Konfiguration reparieren",
        "btn_update": "Images aktualisieren",
        "progress_idle": "Bereit",
        "control_panel": "Container-Steuerung",
        "btn_start": "Start",
        "btn_stop": "Stop",
        "btn_restart": "Neustart",
        "container_status": "Container-Status:",
        "diag_title": "Log",
        "btn_copy_diag": "Log kopieren",
        "btn_export_log": "Log exportieren",
        "user_mgmt_title": "Benutzerverwaltung",
        "btn_delete_user": "Benutzer verwalten",
        "users_window_title": "Benutzer verwalten",
        "users_refresh": "Aktualisieren",
        "users_delete_selected": "Ausgewählten Benutzer löschen",
        "users_close": "Schließen",
        "users_loading": "Benutzer werden geladen...",
        "users_load_failed": "[ERROR] Benutzerliste konnte nicht geladen werden.",
        "users_empty": "[INFO] Keine Benutzer gefunden.",
        "users_no_selection": "Bitte zuerst einen Benutzer auswählen.",
        "err_delete_email": "Bitte eine gültige E-Mail zum Löschen eingeben.",
        "confirm_delete_user": "Benutzer {} wirklich löschen? Alle eigenen Projekte werden ebenfalls gelöscht.",
        "delete_user_not_found": "[INFO] Benutzer nicht gefunden: {}",
        "delete_user_done": "[OK] Benutzer gelöscht: {} | Gelöschte Projekte: {}",
        "log_label": "Log:",
        "err_git": "Git ist nicht installiert.",
        "err_docker_compose": "docker compose / docker-compose wurde nicht gefunden.",
        "err_docker_run": "Docker antwortet nicht.",
        "err_port": "Ungültiger Port. Erlaubt: 1-65535.",
        "warn_port": "Port {} scheint belegt zu sein. Trotzdem fortfahren?",
        "warn_reset_data": "Dadurch werden lokale Container und ./data gelöscht. Fortfahren?",
        "log_init": "Konfiguration wird gestartet...",
        "log_dl": "Container werden gestartet...",
        "log_success": "[OK] Installation abgeschlossen",
        "log_access": "Zugriff:",
        "log_auto": "[INFO] Server wird mit Docker-Richtlinien automatisch neu gestartet.",
        "msg_final_title": "Fertig",
        "msg_final_body": "Overleaf wurde installiert/aktualisiert.\nWenn die Webseite einen Fehler zeigt, warten Sie ein paar Sekunden und laden Sie die Seite neu.",
        "server_stop": "[OK] Server gestoppt.",
        "server_start": "[OK] Server gestartet.",
        "server_restart": "[OK] Server neu gestartet.",
        "not_installed": "[ERROR] Arbeitsordner wurde nicht gefunden.",
        "select_lang": "Select Language / Sprache auswählen",
        "switch_to_de": "Zu DE wechseln",
        "switch_to_en": "Zu EN wechseln",
        "validation_port": "Bitte einen Port zwischen 1 und 65535 eingeben.",
        "repair_done": "[OK] Konfiguration wurde repariert (Dateien neu geschrieben).",
        "update_done": "[OK] Images wurden aktualisiert und gestartet.",
        "diag_copied": "[OK] Log in die Zwischenablage kopiert.",
        "log_exported": "[OK] Log exportiert: {}",
        "open_app_missing": "[INFO] Keine App-URL verfügbar.",
        "copy_url_missing": "[INFO] Keine URL zum Kopieren verfügbar.",
        "phase_preflight": "Phase: Vorabprüfung",
        "phase_files": "Phase: Dateien schreiben",
        "phase_containers": "Phase: Container starten",
        "phase_mongo": "Phase: Mongo-Replikat initialisieren",
        "phase_build_image": "Phase: Eigenes Image bauen",
        "phase_texlive": "Phase: Vollständiges TeX Live installieren",
        "phase_done": "Phase: Fertig"
    },
    "en": {
        "title": "Overleaf Installer - Community Edition",
        "mode_label": "Installation Option:",
        "mode_default": "[DEFAULT] localhost:8080",
        "mode_custom": "[CUSTOM] localhost with custom port",
        "install_profile_label": "Installation profile:",
        "install_profile_basic": "Basic (upstream image)",
        "install_profile_advanced": "Advanced (custom Dockerfile image)",
        "custom_image_tag_label": "Custom image tag:",
        "custom_image_tag_hint": "Advanced only. Example: overleaf-sharelatex:custom",
        "port_label": "Custom Port:",
        "port_placeholder": "Ex: 666",
        "site_language_label": "Default site language:",
        "site_language_hint": "Used as default language for new sessions.",
        "full_texlive_check": "Install full TeX Live in container (scheme-full)",
        "full_texlive_hint": "Takes a long time and downloads many packages.",
        "full_texlive_advanced_forced": "TeX Live will be integrated into the custom Docker image.",
        "safety_label": "Safety options:",
        "recreate_env_check": "Recreate overleaf.env (new secrets)",
        "reset_data_check": "Reset containers and local data before install",
        "preflight_title": "Preflight",
        "refresh_checks": "Refresh checks",
        "status_git": "Git",
        "status_compose": "Compose",
        "status_docker": "Docker",
        "status_port": "Port",
        "status_unknown": "Unknown",
        "status_ok": "OK",
        "status_fail": "Fail",
        "actions_title": "Actions",
        "btn_install": "Install",
        "btn_repair": "Repair config",
        "btn_update": "Update images",
        "progress_idle": "Ready",
        "control_panel": "Container Control",
        "btn_start": "Start",
        "btn_stop": "Stop",
        "btn_restart": "Restart",
        "container_status": "Container status:",
        "diag_title": "Logs",
        "btn_copy_diag": "Copy Logs",
        "btn_export_log": "Export log",
        "user_mgmt_title": "User Management",
        "btn_delete_user": "Manage users",
        "users_window_title": "Manage users",
        "users_refresh": "Refresh",
        "users_delete_selected": "Delete selected user",
        "users_close": "Close",
        "users_loading": "Loading users...",
        "users_load_failed": "[ERROR] Failed to load users list.",
        "users_empty": "[INFO] No users found.",
        "users_no_selection": "Please select a user first.",
        "err_delete_email": "Enter a valid email to delete.",
        "confirm_delete_user": "Delete user {}? All owned projects will also be deleted.",
        "delete_user_not_found": "[INFO] User not found: {}",
        "delete_user_done": "[OK] User deleted: {} | Deleted projects: {}",
        "log_label": "Operation Log:",
        "err_git": "Git is not installed.",
        "err_docker_compose": "docker compose / docker-compose not found.",
        "err_docker_run": "Docker is not responding.",
        "err_port": "Invalid port. Allowed range: 1-65535.",
        "warn_port": "Port {} seems busy. Continue anyway?",
        "warn_reset_data": "This will remove local containers and ./data. Continue?",
        "log_init": "Starting configuration...",
        "log_dl": "Starting containers...",
        "log_success": "[OK] Installation completed",
        "log_access": "Access:",
        "log_auto": "[INFO] Server auto-restarts per Docker policy.",
        "msg_final_title": "Finished",
        "msg_final_body": "Overleaf installation/update completed.\nIf the website shows an error, wait a few seconds and reload the page.",
        "server_stop": "[OK] Server stopped.",
        "server_start": "[OK] Server started.",
        "server_restart": "[OK] Server restarted.",
        "not_installed": "[ERROR] Working folder not found.",
        "select_lang": "Select Language / Sprache auswählen",
        "switch_to_de": "Switch to DE",
        "switch_to_en": "Switch to EN",
        "validation_port": "Enter a port between 1 and 65535.",
        "repair_done": "[OK] Configuration repaired (files rewritten).",
        "update_done": "[OK] Images updated and services restarted.",
        "diag_copied": "[OK] Logs copied to clipboard.",
        "log_exported": "[OK] Log exported: {}",
        "open_app_missing": "[INFO] No app URL available.",
        "copy_url_missing": "[INFO] No URL available to copy.",
        "phase_preflight": "Phase: Preflight",
        "phase_files": "Phase: Write files",
        "phase_containers": "Phase: Start containers",
        "phase_mongo": "Phase: Init Mongo replica",
        "phase_build_image": "Phase: Build custom image",
        "phase_texlive": "Phase: Install full TeX Live",
        "phase_done": "Phase: Done"
    }
}


def t(key):
    return TEXTS.get(LANG, TEXTS["en"]).get(key, key)


def ui_call(fn, *args, **kwargs):
    try:
        if "root" in globals() and root.winfo_exists():
            root.after(0, lambda: fn(*args, **kwargs))
        else:
            fn(*args, **kwargs)
    except Exception:
        pass


def _append_log_line(msg):
    if "output_box" not in globals():
        return
    output_box.config(state="normal")
    output_box.insert(END, msg + "\n")
    output_box.see(END)
    output_box.config(state="disabled")


def log(msg):
    ui_call(_append_log_line, msg)


def get_log_text():
    if "output_box" not in globals():
        return ""
    return output_box.get("1.0", END).strip()


def set_phase(step, total, text):
    def _set():
        progress_var.set(step)
        progress_bar.configure(maximum=total)
        progress_label_var.set(text)

    ui_call(_set)


def reset_progress():
    set_phase(0, 6, t("progress_idle"))


def set_installing_state(is_busy):
    global installing_now
    installing_now = is_busy

    def _set():
        state = DISABLED if is_busy else NORMAL
        btn_install.configure(state=state)
        btn_repair.configure(state=state)
        btn_update.configure(state=state)
        btn_delete_user.configure(state=state)
        btn_start.configure(state=state)
        btn_stop.configure(state=state)
        btn_restart.configure(state=state)
        btn_refresh_checks.configure(state=state)
        refresh_install_enabled()

    ui_call(_set)


def check_command(cmd):
    return shutil.which(cmd) is not None


def check_docker_running():
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def sanitize_port(raw):
    if not raw or not raw.isdigit():
        return None
    port = int(raw)
    if 1 <= port <= 65535:
        return port
    return None


def selected_port():
    if mode_var.get() == 1:
        return DEFAULT_PORT
    return sanitize_port(port_entry.get().strip())


def selected_domain():
    port = selected_port()
    if port is None:
        return None
    return f"localhost:{port}"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_compose_cmd():
    try:
        res = subprocess.run(
            ["docker", "compose", "version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            text=True,
        )
        if res.returncode == 0:
            return ["docker", "compose"]
    except Exception:
        pass
    if check_command("docker-compose"):
        return ["docker-compose"]
    return None


def run_cmd(cmd, check=False, capture=False):
    kwargs = {"check": check, "text": True}
    if capture:
        kwargs["capture_output"] = True
    return subprocess.run(cmd, **kwargs)


def upsert_env_var(env_path, key, value):
    line_value = f"{key}={value}"
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(line_value + "\n")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    replaced = False
    out_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            out_lines.append(line_value)
            replaced = True
        else:
            out_lines.append(line)

    if not replaced:
        out_lines.append(line_value)

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).rstrip() + "\n")


def create_env(domain, port, recreate=False, site_language="en"):
    env_path = INSTALL_DIR / "overleaf.env"
    if env_path.exists() and not recreate:
        log(".env exists. Keeping config.")
        upsert_env_var(env_path, "OVERLEAF_SITE_LANGUAGE", site_language)
        log("overleaf.env language updated.")
        return

    session = secrets.token_hex(32)
    jwt = secrets.token_hex(32)
    data = f"""# Generated by Overleaf Installer
OVERLEAF_APP_NAME=Overleaf Community
OVERLEAF_SITE_URL=http://{domain}
OVERLEAF_SESSION_SECRET={session}
OVERLEAF_JWT_SECRET={jwt}
OVERLEAF_MONGO_URL=mongodb://mongo/sharelatex
OVERLEAF_REDIS_HOST=redis
REDIS_HOST=redis
REDIS_PORT=6379
OVERLEAF_PORT={port}
OVERLEAF_SITE_LANGUAGE={site_language}
"""
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(data)
        if hasattr(os, "fchmod"):
            os.fchmod(f.fileno(), 0o600)
    log("overleaf.env written.")


def write_compose(port, sharelatex_image=BASE_SHARELATEX_IMAGE):
    compose_content = f"""services:
  sharelatex:
    image: {sharelatex_image}
    container_name: sharelatex
    restart: unless-stopped
    depends_on:
      - mongo
      - redis
    ports:
      - "{port}:80"
    links:
      - mongo
      - redis
    volumes:
      - ./data/sharelatex:/var/lib/overleaf
      - ./data/logs:/var/log/overleaf
    environment:
      OVERLEAF_MONGO_URL: mongodb://mongo/sharelatex
      OVERLEAF_REDIS_HOST: redis
      REDIS_HOST: redis
    env_file:
      - overleaf.env

  overleaf-mongo:
    image: mongo:8.0
    container_name: overleaf-mongo
    restart: unless-stopped
    command: "--replSet overleaf"
    volumes:
      - ./data/mongo:/data/db

  overleaf-redis:
    image: redis:7
    container_name: overleaf-redis
    restart: unless-stopped
    volumes:
      - ./data/redis:/data
"""
    with open(INSTALL_DIR / "docker-compose.yml", "w", encoding="utf-8") as f:
        f.write(compose_content)
    log("docker-compose.yml written.")


def generate_custom_dockerfile(dockerfile_path, include_full_texlive):
    lines = [
        f"FROM {BASE_SHARELATEX_IMAGE}",
        "",
    ]
    if include_full_texlive:
        lines += [
            "RUN set -eux; \\",
            "    YEAR=$(tlmgr --version | sed -n 's/.*version \\([0-9]\\{4\\}\\).*/\\1/p'); \\",
            "    tlmgr update --self || (tlmgr option repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/${YEAR}/tlnet-final && tlmgr update --self); \\",
            "    tlmgr install scheme-full; \\",
            "    tlmgr path add; \\",
            "    mktexlsr",
            "",
        ]
    with open(dockerfile_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    log(f"Dockerfile generated: {dockerfile_path.name}")


def build_custom_sharelatex_image(image_tag, dockerfile_path):
    log(f"[INFO] Building custom image: {image_tag}")
    run_cmd(
        ["docker", "build", "-f", str(dockerfile_path), "-t", image_tag, str(INSTALL_DIR)],
        check=True,
    )
    log(f"[OK] Custom image built: {image_tag}")


def init_mongo_replica():
    log("Init Mongo (wait 10s)...")
    time.sleep(10)
    result = run_cmd(["docker", "exec", "mongo", "mongosh", "--eval", "rs.initiate()"], capture=True)
    out = ((result.stdout or "") + (result.stderr or "")).strip()
    if "ok" in out or "already initialized" in out:
        log("[OK] Mongo replica set ready.")
    else:
        log(f"[!] Mongo init warning: {out}")


def run_tlmgr(args, check=True, stream=False):
    cmd = ["docker", "exec", "sharelatex", "tlmgr"] + args
    if stream:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        lines = []
        if proc.stdout:
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    lines.append(line)
                    log(line)
        proc.wait()
        output = "\n".join(lines)
        if check and proc.returncode != 0:
            raise RuntimeError(f"tlmgr {' '.join(args)} failed")
        return proc.returncode, output

    res = run_cmd(cmd, capture=True)
    output = ((res.stdout or "") + (res.stderr or "")).strip()
    if output:
        log(output)
    if check and res.returncode != 0:
        raise RuntimeError(f"tlmgr {' '.join(args)} failed")
    return res.returncode, output


def install_full_texlive():
    log("[INFO] Installing full TeX Live in sharelatex container...")
    log("[INFO] Step 1/3: tlmgr update --self")

    _, ver_out = run_tlmgr(["--version"], check=False)
    year_match = re.search(r"version\s+(\d{4})", ver_out)
    local_year = year_match.group(1) if year_match else None

    upd_code, upd_out = run_tlmgr(["update", "--self"], check=False, stream=True)
    if upd_code != 0:
        cross_release = (
            "older than remote repository" in upd_out
            and "Cross release updates are only supported" in upd_out
        )
        if cross_release and local_year:
            historic_repo = (
                f"https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/{local_year}/tlnet-final"
            )
            log(f"[WARN] Cross-release tlmgr repo detected. Switching to historic repo: {historic_repo}")
            run_tlmgr(["option", "repository", historic_repo], check=True)
            run_tlmgr(["update", "--self"], check=True, stream=True)
        else:
            raise RuntimeError("tlmgr update --self failed")

    log("[INFO] Step 2/3: tlmgr install scheme-full (this can take a long time)")
    run_tlmgr(["install", "scheme-full"], check=True, stream=True)
    log("[INFO] Step 3/3: tlmgr path add")
    run_tlmgr(["path", "add"], check=True, stream=True)
    log("[OK] Full TeX Live installation finished.")


def get_container_status(name):
    res = run_cmd(["docker", "inspect", "-f", "{{.State.Status}}", name], capture=True)
    if res.returncode != 0:
        return "missing"
    return (res.stdout or "").strip() or "unknown"


def update_container_status_label():
    status = {
        "sharelatex": get_container_status("sharelatex"),
        "mongo": get_container_status("mongo"),
        "redis": get_container_status("redis"),
    }
    status_style = {
        "running": ("running", "#1f7a1f"),
        "exited": ("stopped", "#b42318"),
        "created": ("created", "#9a6700"),
        "restarting": ("restarting", "#9a6700"),
        "paused": ("paused", "#175cd3"),
        "missing": ("not found", "#667085"),
        "unknown": ("unknown", "#667085"),
    }

    def _set_badges():
        for name, raw_status in status.items():
            badge = container_status_labels.get(name)
            if not badge:
                continue
            label, fg = status_style.get(raw_status, (raw_status.lower(), "#667085"))
            badge.configure(text=f"{name}: {label}", foreground=fg)

    ui_call(_set_badges)


def compose_action_thread(action):
    compose = get_compose_cmd()
    if not compose:
        messagebox.showerror("Error", t("err_docker_compose"))
        return
    os.chdir(INSTALL_DIR)
    try:
        if action == "start":
            run_cmd(compose + ["start"], check=True)
            log(t("server_start"))
        elif action == "stop":
            run_cmd(compose + ["stop"], check=True)
            log(t("server_stop"))
        elif action == "restart":
            # Normal restart without recreate to preserve container-installed tools.
            run_cmd(compose + ["restart"], check=True)
            log(t("server_restart"))
        update_container_status_label()
    except Exception as e:
        log(f"[ERROR] {e}")


def start_server_thread():
    threading.Thread(target=compose_action_thread, args=("start",), daemon=True).start()


def stop_server_thread():
    threading.Thread(target=compose_action_thread, args=("stop",), daemon=True).start()


def restart_server_thread():
    threading.Thread(target=compose_action_thread, args=("restart",), daemon=True).start()

def do_refresh_preflight():
    port = selected_port()
    mode_is_custom = mode_var.get() == 2
    port_valid = port is not None
    port_ok = port_valid and (not is_port_in_use(port))
    checks = {
        "git": check_command("git"),
        "compose": get_compose_cmd() is not None,
        "docker": check_docker_running(),
        "port": port_ok,
    }

    def apply_results():
        def paint(lbl, ok):
            lbl.configure(text=t("status_ok") if ok else t("status_fail"), foreground=("green" if ok else "red"))

        paint(preflight_git_val, checks["git"])
        paint(preflight_compose_val, checks["compose"])
        paint(preflight_docker_val, checks["docker"])

        # In custom mode, empty/invalid port is an explicit failure.
        if mode_is_custom and not port_valid:
            preflight_port_val.configure(text=t("status_fail"), foreground="red")
        elif not mode_is_custom and not port_valid:
            preflight_port_val.configure(text=t("status_unknown"), foreground="orange")
        else:
            paint(preflight_port_val, checks["port"])

    ui_call(apply_results)


def refresh_preflight_thread():
    threading.Thread(target=do_refresh_preflight, daemon=True).start()


def save_settings():
    data = {
        "lang": LANG,
        "mode": mode_var.get(),
        "install_profile": install_profile_var.get(),
        "custom_image_tag": custom_image_tag_var.get().strip(),
        "custom_port": port_entry.get().strip(),
        "site_language": site_lang_var.get(),
        "install_full_texlive": full_texlive_var.get(),
        "recreate_env": recreate_env_var.get(),
        "reset_data": reset_data_var.get(),
    }
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def save_language_setting(language):
    data = load_settings()
    data["lang"] = language
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load_settings():
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def validate_inputs(show_errors=True):
    port_error = ""

    if mode_var.get() == 2 and sanitize_port(port_entry.get().strip()) is None:
        port_error = t("validation_port")

    if show_errors:
        port_error_var.set(port_error)

    return port_error == ""


def refresh_install_enabled():
    valid = validate_inputs(show_errors=True)
    if installing_now:
        btn_install.configure(state=DISABLED)
        return
    btn_install.configure(state=(NORMAL if valid else DISABLED))


def update_visibility():
    global advanced_forced_full_texlive_prev

    if mode_var.get() == 2:
        if not custom_port_frame.winfo_ismapped():
            custom_port_frame.pack(fill="x")
    else:
        if custom_port_frame.winfo_ismapped():
            custom_port_frame.pack_forget()

    if install_profile_var.get() == "advanced":
        if not advanced_profile_frame.winfo_ismapped():
            advanced_profile_frame.pack(fill="x")
        if advanced_forced_full_texlive_prev is None:
            advanced_forced_full_texlive_prev = full_texlive_var.get()
        full_texlive_var.set(1)
        full_texlive_checkbtn.configure(state=DISABLED)
        full_texlive_text_var.set(t("full_texlive_advanced_forced"))
        full_texlive_hint_var.set(t("full_texlive_advanced_forced"))
    else:
        if advanced_profile_frame.winfo_ismapped():
            advanced_profile_frame.pack_forget()
        if advanced_forced_full_texlive_prev is not None:
            full_texlive_var.set(1 if advanced_forced_full_texlive_prev else 0)
            advanced_forced_full_texlive_prev = None
        full_texlive_checkbtn.configure(state=NORMAL)
        full_texlive_text_var.set(t("full_texlive_check"))
        full_texlive_hint_var.set(t("full_texlive_hint"))

    refresh_install_enabled()
    refresh_preflight_thread()
    save_settings()


def collect_diagnostics_text():
    compose = get_compose_cmd()
    lines = [
        f"timestamp={datetime.now().isoformat()}",
        f"install_dir={INSTALL_DIR}",
        f"selected_domain={selected_domain()}",
        f"selected_mode={mode_var.get()}",
    ]

    for cmd in (["git", "--version"], ["docker", "--version"]):
        res = run_cmd(cmd, capture=True)
        lines.append(f"$ {' '.join(cmd)}")
        lines.append(((res.stdout or "") + (res.stderr or "")).strip())

    if compose:
        res = run_cmd(compose + ["version"], capture=True)
        lines.append(f"$ {' '.join(compose)} version")
        lines.append(((res.stdout or "") + (res.stderr or "")).strip())
        res = run_cmd(compose + ["ps"], capture=True)
        lines.append(f"$ {' '.join(compose)} ps")
        lines.append(((res.stdout or "") + (res.stderr or "")).strip())

    lines.append("\n--- installer log ---")
    lines.append(get_log_text())
    return "\n".join(lines).strip()


def copy_diagnostics():
    text = collect_diagnostics_text()
    root.clipboard_clear()
    root.clipboard_append(text)
    log(t("diag_copied"))


def export_log():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = INSTALL_DIR / f"installer_log_{stamp}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(get_log_text())
    log(t("log_exported").format(out_path))


def fetch_users_from_mongo():
    js = (
        "const dbx=db.getSiblingDB('sharelatex');"
        "dbx.users.find({}, {email:1,_id:0}).sort({email:1}).forEach(u=>{ if(u.email){ print(u.email) } });"
    )
    res = run_cmd(["docker", "exec", "mongo", "mongosh", "--quiet", "--eval", js], capture=True)
    if res.returncode != 0:
        return None, ((res.stdout or "") + (res.stderr or "")).strip()
    lines = [line.strip() for line in (res.stdout or "").splitlines() if line.strip()]
    return lines, ""


def refresh_users_list():
    if "users_listbox" not in globals():
        return

    users_status_var.set(t("users_loading"))

    def worker():
        users, err = fetch_users_from_mongo()

        def apply():
            if "users_listbox" not in globals() or not users_listbox.winfo_exists():
                return
            users_listbox.delete(0, END)
            if users is None:
                users_status_var.set(t("users_load_failed"))
                log(t("users_load_failed"))
                if err:
                    log(err)
                return
            for email in users:
                users_listbox.insert(END, email)
            users_status_var.set("" if users else t("users_empty"))

        ui_call(apply)

    threading.Thread(target=worker, daemon=True).start()


def open_users_window():
    global users_window, users_listbox, users_status_var
    if "users_window" in globals() and users_window.winfo_exists():
        users_window.lift()
        users_window.focus_force()
        refresh_users_list()
        return

    users_window = Toplevel(root)
    users_window.title(t("users_window_title"))
    users_window.geometry("520x420")
    users_window.resizable(False, False)
    users_window.transient(root)

    wrap = ttk.Frame(users_window, padding=12)
    wrap.pack(fill="both", expand=True)

    list_frame = ttk.Frame(wrap)
    list_frame.pack(fill="both", expand=True)

    users_listbox = Listbox(list_frame, selectmode=SINGLE)
    users_listbox.pack(side="left", fill="both", expand=True)
    list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=users_listbox.yview)
    list_scroll.pack(side="right", fill="y")
    users_listbox.configure(yscrollcommand=list_scroll.set)

    users_status_var = StringVar(value="")
    ttk.Label(wrap, textvariable=users_status_var).pack(anchor="w", pady=(8, 8))

    btn_row = ttk.Frame(wrap)
    btn_row.pack(fill="x")
    ttk.Button(btn_row, text=t("users_refresh"), command=refresh_users_list).pack(side="left")
    ttk.Button(btn_row, text=t("users_delete_selected"), command=start_delete_selected_user_thread).pack(side="left", padx=(8, 0))
    ttk.Button(btn_row, text=t("users_close"), command=users_window.destroy).pack(side="right")

    refresh_users_list()


def delete_user_worker(email, on_done=None):
    try:
        set_installing_state(True)
        safe_email = email.replace("\\", "\\\\").replace("'", "\\'")
        js = (
            "const dbx=db.getSiblingDB('sharelatex');"
            f"const email='{safe_email}';"
            "const user=dbx.users.findOne({email:email},{_id:1,email:1});"
            "if(!user){print('NOT_FOUND');quit(0)};"
            "const proj=dbx.projects.deleteMany({owner_ref:user._id}).deletedCount;"
            "const usr=dbx.users.deleteOne({_id:user._id}).deletedCount;"
            "print('DELETED_USER='+usr);"
            "print('DELETED_PROJECTS='+proj);"
        )
        res = run_cmd(["docker", "exec", "mongo", "mongosh", "--quiet", "--eval", js], capture=True)
        out = ((res.stdout or "") + (res.stderr or "")).strip()
        if res.returncode != 0:
            log(f"[ERROR] Failed to delete user {email}")
            if out:
                log(out)
            return

        if "NOT_FOUND" in out:
            log(t("delete_user_not_found").format(email))
            return

        projects_deleted = 0
        m = re.search(r"DELETED_PROJECTS=(\d+)", out)
        if m:
            projects_deleted = int(m.group(1))
        log(t("delete_user_done").format(email, projects_deleted))
        update_container_status_label()
    finally:
        set_installing_state(False)
        if on_done:
            ui_call(on_done)


def start_delete_selected_user_thread():
    if "users_listbox" not in globals() or not users_listbox.winfo_exists():
        return
    selection = users_listbox.curselection()
    if not selection:
        messagebox.showwarning("Warning", t("users_no_selection"))
        return
    email = users_listbox.get(selection[0]).strip()
    if not messagebox.askyesno("Confirm", t("confirm_delete_user").format(email)):
        return

    threading.Thread(target=delete_user_worker, args=(email, refresh_users_list), daemon=True).start()

def run_install_flow(is_repair=False):
    try:
        set_installing_state(True)
        reset_progress()

        mode = mode_var.get()
        custom_port = port_entry.get().strip()
        site_language = site_lang_var.get().strip() or "en"
        install_profile = install_profile_var.get().strip() or "basic"
        custom_image_tag = custom_image_tag_var.get().strip() or "overleaf-sharelatex:custom"
        install_full_texlive_enabled = full_texlive_var.get() == 1
        recreate_env = recreate_env_var.get() == 1
        reset_data = reset_data_var.get() == 1 and not is_repair
        first_time_install = not (INSTALL_DIR / "overleaf.env").exists()

        if mode == 1:
            port = DEFAULT_PORT
        else:
            port = sanitize_port(custom_port)
            if port is None:
                messagebox.showerror("Error", t("err_port"))
                return

        domain = f"localhost:{port}"

        set_phase(1, 6, t("phase_preflight"))
        if not check_command("git"):
            messagebox.showerror("Error", t("err_git"))
            return

        compose = get_compose_cmd()
        if not compose:
            messagebox.showerror("Error", t("err_docker_compose"))
            return

        if not check_docker_running():
            messagebox.showerror("Error", t("err_docker_run"))
            return

        if not is_repair and is_port_in_use(port):
            if not messagebox.askyesno("Port Busy", t("warn_port").format(port)):
                return

        os.chdir(INSTALL_DIR)
        log(f"Using working directory: {INSTALL_DIR}")

        set_phase(2, 6, t("phase_files"))
        create_env(domain, port, recreate=recreate_env, site_language=site_language)
        sharelatex_image = BASE_SHARELATEX_IMAGE
        if install_profile == "advanced":
            set_phase(3, 6, t("phase_build_image"))
            dockerfile_path = INSTALL_DIR / "Dockerfile.overleaf.generated"
            generate_custom_dockerfile(dockerfile_path, include_full_texlive=install_full_texlive_enabled)
            build_custom_sharelatex_image(custom_image_tag, dockerfile_path)
            sharelatex_image = custom_image_tag
        write_compose(port, sharelatex_image=sharelatex_image)

        if is_repair:
            # Recreate sharelatex so updated overleaf.env values take effect.
            run_cmd(compose + ["up", "-d", "--force-recreate", "sharelatex"], check=True)
            if install_full_texlive_enabled and install_profile != "advanced":
                set_phase(5, 6, t("phase_texlive"))
                install_full_texlive()
            log(t("repair_done"))
            set_phase(6, 6, t("phase_done"))
            return

        if reset_data:
            if not messagebox.askyesno("Confirm", t("warn_reset_data")):
                return
            run_cmd(compose + ["down"], check=False)
            data_dir = INSTALL_DIR / "data"
            if data_dir.exists():
                shutil.rmtree(data_dir, ignore_errors=True)
                log("[INFO] Removed ./data")

        set_phase(4, 6, t("phase_containers"))
        log(t("log_dl"))
        run_cmd(compose + ["down"], check=True)
        run_cmd(compose + ["up", "-d"], check=True)

        set_phase(5, 6, t("phase_mongo"))
        init_mongo_replica()

        if install_full_texlive_enabled and install_profile != "advanced":
            set_phase(5, 6, t("phase_texlive"))
            install_full_texlive()

        app_url = f"http://{domain}"
        open_url = f"{app_url}/launchpad" if (first_time_install or reset_data) else app_url

        set_phase(6, 6, t("phase_done"))
        log(t("log_success"))
        log(f"{t('log_access')} {app_url}")
        log(t("log_auto"))
        if open_url.endswith("/launchpad"):
            log(f"[INFO] Opening first-time setup: {open_url}")

        update_container_status_label()

        messagebox.showwarning(t("msg_final_title"), t("msg_final_body"))
        webbrowser.open(open_url)

    except Exception as e:
        log(f"[ERROR] {e}")
        messagebox.showerror("Critical Error", str(e))
    finally:
        reset_progress()
        set_installing_state(False)
        refresh_preflight_thread()


def start_install_thread():
    threading.Thread(target=run_install_flow, args=(False,), daemon=True).start()


def start_repair_thread():
    threading.Thread(target=run_install_flow, args=(True,), daemon=True).start()


def update_images_thread():
    def worker():
        try:
            set_installing_state(True)
            compose = get_compose_cmd()
            if not compose:
                messagebox.showerror("Error", t("err_docker_compose"))
                return
            os.chdir(INSTALL_DIR)
            set_phase(1, 3, "Pull images")
            run_cmd(compose + ["pull"], check=True)
            set_phase(2, 3, "Restart services")
            run_cmd(compose + ["up", "-d"], check=True)
            set_phase(3, 3, t("phase_done"))
            log(t("update_done"))
            update_container_status_label()
        except Exception as e:
            log(f"[ERROR] {e}")
        finally:
            reset_progress()
            set_installing_state(False)

    threading.Thread(target=worker, daemon=True).start()


def set_lang(language):
    global LANG
    LANG = language
    save_language_setting(language)
    lang_window.destroy()
    launch_main_gui()


def toggle_main_language():
    global LANG, root
    LANG = "de" if LANG == "en" else "en"
    save_language_setting(LANG)
    save_settings()
    root.destroy()
    launch_main_gui()


def launch_lang_selector():
    global lang_window
    lang_window = Tk()
    lang_window.title("Language")
    lang_window.geometry("300x150")
    lang_window.resizable(False, False)

    ttk.Label(lang_window, text=t("select_lang"), font=("Arial", 10)).pack(pady=20)

    btn_frame = ttk.Frame(lang_window)
    btn_frame.pack(fill="x", padx=20)

    ttk.Button(btn_frame, text="English", command=lambda: set_lang("en")).pack(side="left", expand=True, padx=5)
    ttk.Button(btn_frame, text="Deutsch", command=lambda: set_lang("de")).pack(side="right", expand=True, padx=5)

    lang_window.mainloop()

def launch_main_gui():
    global root
    global mode_var, port_entry, site_lang_var, full_texlive_var, install_profile_var, custom_image_tag_var
    global recreate_env_var, reset_data_var
    global output_box, progress_var, progress_bar, progress_label_var
    global port_error_var
    global custom_port_frame, advanced_profile_frame, full_texlive_checkbtn, full_texlive_text_var, full_texlive_hint_var
    global btn_install, btn_repair, btn_update, btn_delete_user
    global btn_start, btn_stop, btn_restart
    global btn_refresh_checks
    global preflight_git_val, preflight_compose_val, preflight_docker_val, preflight_port_val
    global container_status_labels

    settings = load_settings()

    root = Tk()
    root.title(t("title"))
    root.geometry("880x820")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)

    header = ttk.Frame(frame)
    header.pack(fill="x", pady=(0, 6))
    ttk.Label(header, text=t("title"), font=("Helvetica", 14, "bold")).pack(side="left")
    lang_btn_text = t("switch_to_de") if LANG == "en" else t("switch_to_en")
    ttk.Button(header, text=lang_btn_text, command=toggle_main_language).pack(side="right")

    # Scrollable top area
    top_area = ttk.Frame(frame)
    top_area.pack(fill="both", expand=True)

    scroll_canvas = Canvas(top_area, highlightthickness=0)
    scroll_y = ttk.Scrollbar(top_area, orient="vertical", command=scroll_canvas.yview)
    scroll_canvas.configure(yscrollcommand=scroll_y.set)
    scroll_canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    scroll_content = ttk.Frame(scroll_canvas)
    scroll_window = scroll_canvas.create_window((0, 0), window=scroll_content, anchor="nw")

    def _on_content_configure(_event):
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

    def _on_canvas_configure(event):
        scroll_canvas.itemconfigure(scroll_window, width=event.width)

    scroll_content.bind("<Configure>", _on_content_configure)
    scroll_canvas.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(event):
        # Windows/macOS
        if getattr(event, "delta", 0):
            step = int(-1 * (event.delta / 120)) if event.delta else 0
            if step != 0:
                scroll_canvas.yview_scroll(step, "units")
            return
        # Linux (X11)
        if getattr(event, "num", None) == 4:
            scroll_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            scroll_canvas.yview_scroll(1, "units")

    def _bind_mousewheel(widget):
        widget.bind_all("<MouseWheel>", _on_mousewheel)
        widget.bind_all("<Button-4>", _on_mousewheel)
        widget.bind_all("<Button-5>", _on_mousewheel)

    _bind_mousewheel(scroll_canvas)

    preflight = ttk.LabelFrame(scroll_content, text=t("preflight_title"), padding=10)
    preflight.pack(fill="x", pady=4)

    preflight_grid = ttk.Frame(preflight)
    preflight_grid.pack(fill="x")
    ttk.Label(preflight_grid, text=f"{t('status_git')}:").grid(row=0, column=0, sticky="w", padx=(0, 8))
    preflight_git_val = ttk.Label(preflight_grid, text=t("status_unknown"))
    preflight_git_val.grid(row=0, column=1, sticky="w", padx=(0, 20))
    ttk.Label(preflight_grid, text=f"{t('status_compose')}:").grid(row=0, column=2, sticky="w", padx=(0, 8))
    preflight_compose_val = ttk.Label(preflight_grid, text=t("status_unknown"))
    preflight_compose_val.grid(row=0, column=3, sticky="w", padx=(0, 20))
    ttk.Label(preflight_grid, text=f"{t('status_docker')}:").grid(row=0, column=4, sticky="w", padx=(0, 8))
    preflight_docker_val = ttk.Label(preflight_grid, text=t("status_unknown"))
    preflight_docker_val.grid(row=0, column=5, sticky="w", padx=(0, 20))
    ttk.Label(preflight_grid, text=f"{t('status_port')}:").grid(row=0, column=6, sticky="w", padx=(0, 8))
    preflight_port_val = ttk.Label(preflight_grid, text=t("status_unknown"))
    preflight_port_val.grid(row=0, column=7, sticky="w")
    btn_refresh_checks = ttk.Button(preflight, text=t("refresh_checks"), command=refresh_preflight_thread)
    btn_refresh_checks.pack(anchor="w", pady=(8, 0))

    mode_frame = ttk.LabelFrame(scroll_content, text=f"1. {t('mode_label')}", padding=10)
    mode_frame.pack(fill="x", pady=4)

    mode_var = IntVar(value=int(settings.get("mode", 1)))
    ttk.Radiobutton(mode_frame, text=t("mode_default"), variable=mode_var, value=1).pack(anchor="w")
    ttk.Radiobutton(mode_frame, text=t("mode_custom"), variable=mode_var, value=2).pack(anchor="w")

    ttk.Label(mode_frame, text=t("install_profile_label")).pack(anchor="w", pady=(8, 0))
    install_profile_var = StringVar(value=settings.get("install_profile", "basic"))
    install_profile_combo = ttk.Combobox(
        mode_frame,
        textvariable=install_profile_var,
        state="readonly",
        values=["basic", "advanced"],
        width=12,
    )
    install_profile_combo.pack(anchor="w", pady=4)
    # Show friendly labels next to raw values.
    ttk.Label(
        mode_frame,
        text=f"basic = {t('install_profile_basic')} | advanced = {t('install_profile_advanced')}",
        font=("Helvetica", 9, "italic"),
    ).pack(anchor="w")

    advanced_profile_frame = ttk.Frame(mode_frame)
    ttk.Label(advanced_profile_frame, text=t("custom_image_tag_label")).pack(anchor="w", pady=(8, 0))
    custom_image_tag_var = StringVar(value=settings.get("custom_image_tag", "overleaf-sharelatex:custom"))
    custom_image_tag_entry = ttk.Entry(advanced_profile_frame, textvariable=custom_image_tag_var)
    custom_image_tag_entry.pack(fill="x", pady=4)
    ttk.Label(advanced_profile_frame, text=t("custom_image_tag_hint"), font=("Helvetica", 9, "italic")).pack(anchor="w")

    custom_port_frame = ttk.Frame(mode_frame)
    ttk.Label(custom_port_frame, text=t("port_label")).pack(anchor="w", pady=(8, 0))
    port_entry = ttk.Entry(custom_port_frame)
    port_entry.insert(0, settings.get("custom_port", str(DEFAULT_PORT)))
    port_entry.pack(fill="x", pady=4)
    ttk.Label(custom_port_frame, text=t("port_placeholder"), font=("Helvetica", 9, "italic")).pack(anchor="w")

    ttk.Label(mode_frame, text=t("site_language_label")).pack(anchor="w", pady=(8, 0))
    site_lang_var = StringVar(value=settings.get("site_language", "en"))
    site_lang_combo = ttk.Combobox(
        mode_frame,
        textvariable=site_lang_var,
        state="readonly",
        values=["en", "de", "fr", "es", "it", "pt"],
        width=8,
    )
    site_lang_combo.pack(anchor="w", pady=4)
    ttk.Label(mode_frame, text=t("site_language_hint"), font=("Helvetica", 9, "italic")).pack(anchor="w")
    full_texlive_var = IntVar(value=int(settings.get("install_full_texlive", 0)))
    full_texlive_text_var = StringVar(value=t("full_texlive_check"))
    full_texlive_checkbtn = ttk.Checkbutton(mode_frame, textvariable=full_texlive_text_var, variable=full_texlive_var)
    full_texlive_checkbtn.pack(anchor="w", pady=(8, 0))
    full_texlive_hint_var = StringVar(value=t("full_texlive_hint"))
    ttk.Label(mode_frame, textvariable=full_texlive_hint_var, font=("Helvetica", 9, "italic")).pack(anchor="w")

    port_error_var = StringVar(value="")
    ttk.Label(custom_port_frame, textvariable=port_error_var, foreground="red").pack(anchor="w")

    safety_frame = ttk.LabelFrame(scroll_content, text=f"2. {t('safety_label')}", padding=10)
    safety_frame.pack(fill="x", pady=4)
    recreate_env_var = IntVar(value=int(settings.get("recreate_env", 0)))
    reset_data_var = IntVar(value=int(settings.get("reset_data", 0)))
    ttk.Checkbutton(safety_frame, text=t("recreate_env_check"), variable=recreate_env_var).pack(anchor="w")
    ttk.Checkbutton(safety_frame, text=t("reset_data_check"), variable=reset_data_var).pack(anchor="w")

    action_frame = ttk.LabelFrame(scroll_content, text=t("actions_title"), padding=10)
    action_frame.pack(fill="x", pady=4)
    action_buttons = ttk.Frame(action_frame)
    action_buttons.pack(fill="x")
    btn_install = ttk.Button(action_buttons, text=t("btn_install"), command=start_install_thread)
    btn_install.pack(side="left", padx=(0, 8))
    btn_repair = ttk.Button(action_buttons, text=t("btn_repair"), command=start_repair_thread)
    btn_repair.pack(side="left", padx=(0, 8))
    btn_update = ttk.Button(action_buttons, text=t("btn_update"), command=update_images_thread)
    btn_update.pack(side="left")
    progress_var = IntVar(value=0)
    progress_label_var = StringVar(value=t("progress_idle"))
    ttk.Label(action_frame, textvariable=progress_label_var).pack(anchor="w", pady=(10, 2))
    progress_bar = ttk.Progressbar(action_frame, variable=progress_var, maximum=6)
    progress_bar.pack(fill="x")

    user_mgmt_frame = ttk.LabelFrame(scroll_content, text=t("user_mgmt_title"), padding=10)
    user_mgmt_frame.pack(fill="x", pady=4)
    btn_delete_user = ttk.Button(user_mgmt_frame, text=t("btn_delete_user"), command=open_users_window)
    btn_delete_user.pack(anchor="w")

    control_frame = ttk.LabelFrame(scroll_content, text=t("control_panel"), padding=10)
    control_frame.pack(fill="x", pady=4)
    btn_start = ttk.Button(control_frame, text=t("btn_start"), command=start_server_thread)
    btn_start.pack(side="left", padx=(0, 6))
    btn_stop = ttk.Button(control_frame, text=t("btn_stop"), command=stop_server_thread)
    btn_stop.pack(side="left", padx=(0, 6))
    btn_restart = ttk.Button(control_frame, text=t("btn_restart"), command=restart_server_thread)
    btn_restart.pack(side="left")
    ttk.Label(control_frame, text=f"{t('container_status')}").pack(anchor="w", pady=(8, 0))
    badges_frame = ttk.Frame(control_frame)
    badges_frame.pack(anchor="w", fill="x")
    container_status_labels = {}
    for name in ("sharelatex", "mongo", "redis"):
        badge = ttk.Label(
            badges_frame,
            text=f"{name}: unknown",
            font=("Helvetica", 9, "bold"),
        )
        badge.pack(side="left", padx=(0, 14), pady=(0, 2))
        container_status_labels[name] = badge

    diag_frame = ttk.LabelFrame(scroll_content, text=t("diag_title"), padding=10)
    diag_frame.pack(fill="x", pady=4)
    ttk.Button(diag_frame, text=t("btn_copy_diag"), command=copy_diagnostics).pack(side="left", padx=(0, 8))
    ttk.Button(diag_frame, text=t("btn_export_log"), command=export_log).pack(side="left")

    # Fixed-size log area at bottom
    log_frame = ttk.Frame(frame)
    log_frame.pack(fill="x", pady=(8, 0))
    ttk.Label(log_frame, text=t("log_label"), font=("Helvetica", 10, "bold")).pack(anchor="w")
    log_box_wrap = ttk.Frame(log_frame, height=220)
    log_box_wrap.pack(fill="x")
    log_box_wrap.pack_propagate(False)
    output_box = scrolledtext.ScrolledText(log_box_wrap, state="disabled", font=("Consolas", 9))
    output_box.pack(fill="both", expand=True)

    mode_var.trace_add("write", lambda *_: update_visibility())
    install_profile_var.trace_add("write", lambda *_: update_visibility())
    recreate_env_var.trace_add("write", lambda *_: save_settings())
    reset_data_var.trace_add("write", lambda *_: save_settings())

    port_entry.bind("<KeyRelease>", lambda *_: (refresh_install_enabled(), save_settings(), refresh_preflight_thread()))
    site_lang_var.trace_add("write", lambda *_: save_settings())
    full_texlive_var.trace_add("write", lambda *_: save_settings())
    custom_image_tag_var.trace_add("write", lambda *_: save_settings())

    update_visibility()
    refresh_install_enabled()
    refresh_preflight_thread()
    threading.Thread(target=update_container_status_label, daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    saved = load_settings().get("lang")
    if saved in ("en", "de"):
        LANG = saved
        launch_main_gui()
    else:
        launch_lang_selector()
