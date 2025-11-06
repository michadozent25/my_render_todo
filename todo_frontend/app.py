import streamlit as st
import os
import requests


API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def login():
    st.title("Login")
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password",type="password")
        submit = st.form_submit_button("Login")
        if submit:
            #  POST http://127.0.0.1:8000/users/authenticate
            response = requests.post(API_BASE+"/users/authenticate", json={
                "name":username,
                "password":password
            })
            if response.status_code==200:
                user_data= response.json()
                st.session_state["user"]=user_data
                st.success(f"Wilkommen, {user_data['name']}")
                st.session_state['logged_in']=True
                st.rerun()
            else:
                st.error("Name oder Passwort falsch!")

def welcome():
    user = st.session_state.get('user')
    st.title(f"Wilkommen, {user['name']}")

    user_id= user["id"]
    st.write('Du bist jetzt eingeloggt.')
    st.title("Neues Todo")

    task = st.text_input("Task")
    description = st.text_input("Description")
    deadline = st.date_input("Deadline")
    state = st.selectbox("State",["OPEN","IN_PROGRESS","DONE"])

    json_param={
        "task":task,
        "description":description,
        "deadline":deadline.isoformat(),
        "state":state
    }
    # http://127.0.0.1:8000/todos/?user_id=1

    if st.button("Todo erstellen"):
        response = requests.post(f"{API_BASE}/todos/",json=json_param,params={"user_id":user_id})
        if response.status_code==200:
            st.success("Todo gespeichert!")
            st.json(response.json())
        else:
            st.error(f"Fehler: {response.status_code}")

    ## alle Todos
    st.write("Todos")
    #http://127.0.0.1:8000/users/2/todos
    response = requests.get(f"{API_BASE}/users/{user_id}/todos")
    #response.raise_for_status()
    if response.status_code==200:
        todos = response.json()
        if todos:
            st.table(todos)   # alternative import pandas as pd ->pd.DataFrame(todo) 
        else:
            st.info("Keine Todos!")
    else:
            st.error(f"Fehler: {response.status_code}")


def logout():
    st.session_state['logged_in']=False
    st.session_state.pop("user",None)
    st.success("Erfolgreich abgemeldet!")
    st.rerun()

if st.session_state.get('logged_in'):
    if st.button("Logout"):
        logout()

def main():
    if "logged_in" not in st.session_state:
        st.session_state['logged_in']=False
    if st.session_state['logged_in']:
        welcome()
    else:
        login()
if __name__=="__main__":
    main()