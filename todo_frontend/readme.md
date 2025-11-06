# TodolistClient Frontend

## Install
* pip install streamlit requests

## Start App
* streamlit run app.py




## Streamlit

Frontend-Framework, das in TypeScript und React geschrieben ist.
Die wichtigsten Bausteine sind:

React: Das ist das Fundament der Benutzeroberfläche. Alle UI-Elemente (Widgets, Buttons, Textfelder, Diagramme usw.) sind React-Komponenten.

Redux: Wird im Hintergrund zur State-Verwaltung zwischen Client (Browser) und Backend (Python-Server) genutzt.

protobuf / WebSocket-Kommunikation: Das Frontend und das Python-Backend sprechen über ein binäres Protokoll (Protocol Buffers), um Daten effizient auszutauschen.

Emotion (CSS-in-JS) und TypeScript: Für Styling und Typsicherheit im Frontend.

vega-lite / plotly / deck.gl: Für interaktive Visualisierungen (werden von Streamlit integriert, nicht selbst entwickelt).