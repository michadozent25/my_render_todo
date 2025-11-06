import os
import time
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")

# Eine Requests-Session hält Keep-Alive-Verbindungen offen → schneller nach Warmup
SESSION = requests.Session()

# ---------- Helpers ----------
def api_url(path: str) -> str:
    return f"{API_BASE}/{path.lstrip('/')}"

def warmup(timeout: int = 20):
    """Weckt das Backend (Render Free-Tier) per /health auf."""
    try:
        SESSION.get(api_url("/health"), timeout=timeout)
    except Exception:
        # selbst wenn health fehlschlägt, versuchen wir gleich den eigentlichen Call
        pass

def request_with_retry(method: str, path: str, *, tries: int = 3, timeout: int = 30, **kwargs) -> requests.Response:
    """
    Führt einen Request mit Warmup und Retries aus.
    Wiederholt bei 502/503/504 oder Verbindungsfehlern (Free-Tier kalt).
    """
    # 1) Warmup mit UI-Feedback (nur beim ersten Versuch)
    with st.spinner("Backend wird aufgeweckt…"):
        warmup()

    url = api_url(path)
    last_exc = None
    for i in range(1, tries + 1):
        try:
            r = SESSION.request(method, url, timeout=timeout, **kwargs)
            if r.status_code in (502, 503, 504):
                raise RuntimeError(f"Upstream {r.status_code}")
            return r
        except Exception as e:
            last_exc = e
            if i == tries:
                break
            time.sleep(2 * i)  # 2s, 4s Backoff
    # Letzten Fehler hochreichen – Streamlit zeigt ihn an
    raise last_exc

def api_post(path: str, **kwargs) -> requests.Response:
    return request_with_retry("POST", path, **kwargs)

def api_get(path: str, **kwargs) -> requests.Response:
    return request_with_retry("GET", path, **kwargs)

# ---------- Auth-Logik ----------
def do_login(username: str, password: str):
    try:
        resp = api_post("/users/authenticate", json={"name": username, "password": password})
        if resp.status_code == 200:
            st.session_state["user"] = resp.json()
            st.session_state["logged_in"] = True
            return True, None
        elif resp.status_code in (401, 404):
            return False, "Name oder Passwort falsch."
        else:
            return False, f"Login-Fehler ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Login fehlgeschlagen: {e}"

def do_register(username: str, password: str):
    try:
        resp = api_post("/users/", json={"name": username, "password": password})
        if resp.status_code == 200:
            # direkt einloggen
            return do_login(username, password)
        elif resp.status_code == 409:
            return False, "Benutzername bereits vergeben."
        else:
            return False, f"Registrierung fehlgeschlagen ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Registrierung fehlgeschlagen: {e}"

# ---------- UI ----------
st.set_page_config(page_title="Todos", layout="centered")

def login_view():
    st.title("Anmelden")
    with st.form("login_form"):
        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Username", autocomplete="username")
        with c2:
            password = st.text_input("Passwort", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if not username or not password:
                st.error("Bitte Username und Passwort eingeben.")
            else:
                ok, msg = do_login(username, password)
                if ok:
                    st.success(f"Willkommen, {st.session_state['user']['name']}!")
                    st.rerun()
                else:
                    st.error(msg or "Unbekannter Fehler beim Login.")

def register_view():
    st.title("Registrieren")
    with st.form("register_form"):
        username = st.text_input("Username", help="Muss eindeutig sein.")
        pw1 = st.text_input("Passwort", type="password")
        pw2 = st.text_input("Passwort bestätigen", type="password")
        submitted = st.form_submit_button("Account anlegen")
        if submitted:
            if not username or not pw1 or not pw2:
                st.error("Alle Felder ausfüllen.")
            elif pw1 != pw2:
                st.error("Passwörter stimmen nicht überein.")
            elif len(pw1) < 6:
                st.error("Passwort zu kurz (min. 6 Zeichen).")
            else:
                ok, msg = do_register(username, pw1)
                if ok:
                    st.success(f"Account erstellt. Eingeloggt als {username}.")
                    st.rerun()
                else:
                    st.error(msg or "Registrierung fehlgeschlagen.")

def header_bar():
    st.caption(f"Backend: {API_BASE}")
    left, right = st.columns([1, 1])
    with left:
        mode = st.segmented_control("Modus", options=["Login", "Registrieren"], key="auth_mode")
    with right:
        if st.session_state.get("logged_in"):
            if st.button("Logout", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state.pop("user", None)
                st.success("Abgemeldet.")
                st.rerun()
    st.divider()
    return st.session_state.get("auth_mode", "Login")

def authed_view():
    user = st.session_state.get("user")
    st.title(f"Willkommen, {user['name']}")
    user_id = user["id"]

    st.subheader("Neues Todo")
    task = st.text_input("Task")
    description = st.text_input("Beschreibung")
    state = st.selectbox("Status", ["OPEN", "DONE"])  # Backend-States daran ausrichten
    deadline = st.date_input("Deadline")

    if st.button("Todo erstellen", use_container_width=True):
        payload = {
            "task": task,
            "description": description,
            "deadline": deadline.isoformat(),
            "state": state,
        }
        try:
            r = api_post("/todos/", json=payload, params={"user_id": user_id})
            if r.status_code == 200:
                st.success("Todo gespeichert.")
                st.json(r.json())
            else:
                st.error(f"Fehler beim Speichern ({r.status_code}): {r.text}")
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")

    st.subheader("Todos")
    try:
        r = api_get(f"/users/{user_id}/todos")
        if r.status_code == 200:
            todos = r.json()
            st.table(todos) if todos else st.info("Keine Todos.")
        else:
            st.error(f"Fehler beim Laden ({r.status_code}): {r.text}")
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    mode = header_bar()
    if st.session_state["logged_in"]:
        authed_view()
    else:
        (login_view if mode == "Login" else register_view)()

if __name__ == "__main__":
    main()
