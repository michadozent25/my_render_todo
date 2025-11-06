import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")

# ---------- kleine Helfer ----------
def api_post(path: str, **kwargs):
    url = f"{API_BASE}/{path.lstrip('/')}"
    return requests.post(url, timeout=15, **kwargs)

def api_get(path: str, **kwargs):
    url = f"{API_BASE}/{path.lstrip('/')}"
    return requests.get(url, timeout=15, **kwargs)

def do_login(username: str, password: str):
    resp = api_post("/users/authenticate", json={"name": username, "password": password})
    if resp.status_code == 200:
        st.session_state["user"] = resp.json()
        st.session_state["logged_in"] = True
        return True, None
    elif resp.status_code in (401, 404):
        return False, "Name oder Passwort falsch."
    else:
        return False, f"Login-Fehler ({resp.status_code}): {resp.text}"

def do_register(username: str, password: str):
    # Backend erwartet: POST /users  mit {"name": "...", "password": "..."}
    resp = api_post("/users/", json={"name": username, "password": password})
    if resp.status_code == 200:
        # direkt einloggen
        return do_login(username, password)
    elif resp.status_code == 409:
        return False, "Benutzername bereits vergeben."
    else:
        return False, f"Registrierung fehlgeschlagen ({resp.status_code}): {resp.text}"

# ---------- UI ----------
st.set_page_config(page_title="Todos", layout="centered")

def login_view():
    st.title("Anmelden")
    with st.form("login_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", autocomplete="username")
        with col2:
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
    with st.form("register_form", clear_on_submit=False):
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

    # HINWEIS: Dein Backend hatte nur OPEN/DONE erlaubt.
    # Wenn du "IN_PROGRESS" verwenden willst, erlaube das im Backend (ALLOWED_STATES).
    state = st.selectbox("Status", ["OPEN", "DONE"])  # füge "IN_PROGRESS" nur, wenn Backend es akzeptiert
    deadline = st.date_input("Deadline")

    if st.button("Todo erstellen", use_container_width=True):
        payload = {
            "task": task,
            "description": description,
            "deadline": deadline.isoformat(),
            "state": state,
        }
        r = api_post("/todos/", json=payload, params={"user_id": user_id})
        if r.status_code == 200:
            st.success("Todo gespeichert.")
            st.json(r.json())
        else:
            st.error(f"Fehler beim Speichern ({r.status_code}): {r.text}")

    st.subheader("Todos")
    r = api_get(f"/users/{user_id}/todos")
    if r.status_code == 200:
        todos = r.json()
        if todos:
            # Streamlit kann dict/list direkt als Tabelle darstellen
            st.table(todos)
        else:
            st.info("Keine Todos.")
    else:
        st.error(f"Fehler beim Laden ({r.status_code}): {r.text}")

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    mode = header_bar()
    if st.session_state["logged_in"]:
        authed_view()
    else:
        if mode == "Login":
            login_view()
        else:
            register_view()

if __name__ == "__main__":
    main()
