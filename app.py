# ============================================
# 🍽️ Votación Oficial™ - Cena entre Amigos
# Autor: Hilo
# Región: La Plata, PBA
# ============================================

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import random

# ----------------------------
# CONFIG
# ----------------------------
APP_TITLE = "🍽️ Votación Oficial™ - Cena"
APP_REGION = "La Plata, Provincia de Buenos Aires"
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

AMIGOS = ["Rulo", "Lucho", "Rami", "Hilo"]

OPCIONES_DEFAULT = [
    "BACCI 🍝",
    "Bar de siempre 🍺",
    "Restaurante cheto 🍷",
    "Pizzería salvadora 🍕",
    "Club (modo caos) 🕺"
]

RESET_PASSWORD = "asado"

st.set_page_config(page_title=APP_TITLE, page_icon="🍝", layout="centered")

# ----------------------------
# FUNCIONES
# ----------------------------
def now_str():
    return datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")

def init_state():
    if "votes" not in st.session_state:
        st.session_state.votes = {}
    if "opciones" not in st.session_state:
        st.session_state.opciones = OPCIONES_DEFAULT.copy()

def winner_info(df):
    if df.empty:
        return None, None, None
    counts = df["voto"].value_counts()
    max_v = counts.max()
    leaders = counts[counts == max_v].index.tolist()
    return counts, leaders, max_v

# ----------------------------
# INIT
# ----------------------------
init_state()

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    f"""
    <div style='padding:10px; border-radius:8px; background-color:#f2f2f2; text-align:center'>
        🕒 <b>Hora oficial del hambre</b><br>
        {APP_REGION}<br>
        {now_str()}
    </div>
    """,
    unsafe_allow_html=True
)

st.title(APP_TITLE)
st.caption("Democracia gastronómica de baja intensidad.")

st.divider()

# ----------------------------
# VOTACIÓN
# ----------------------------
tab1, tab2 = st.tabs(["🗳️ Votar", "📊 Resultados"])

with tab1:
    st.subheader("Emití tu voto")

    nombre = st.selectbox("¿Quién sos?", AMIGOS)

    if nombre in st.session_state.votes:
        st.info(f"Ya votaste: {st.session_state.votes[nombre]}")
    else:
        opcion = st.radio("Elegí el destino gastronómico:", st.session_state.opciones)
        if st.button("VOTAR 🚨", use_container_width=True):
            st.session_state.votes[nombre] = opcion
            st.success(f"Voto registrado: {nombre} → {opcion}")
            st.rerun()

with tab2:
    st.subheader("Resultados en vivo")

    if not st.session_state.votes:
        st.write("Todavía no hay votos.")
    else:
        df = pd.DataFrame(
            [{"persona": k, "voto": v} for k, v in st.session_state.votes.items()]
        )

        st.bar_chart(df["voto"].value_counts())

        counts, leaders, max_v = winner_info(df)

        st.divider()

        frases = [
            "La voluntad popular ha hablado.",
            "Esto es estadística aplicada al hambre.",
            "No lloren, organicen revancha.",
            "El pueblo decide (más o menos)."
        ]

        st.write(random.choice(frases))

        if len(leaders) == 1:
            st.success(f"🏆 Va ganando: {leaders[0]} con {max_v} voto(s)")
        else:
            st.warning(f"🤝 Empate entre: {', '.join(leaders)}")

# ----------------------------
# RESET
# ----------------------------
with st.expander("⚙️ Administración"):
    clave = st.text_input("Clave de reset", type="password")
    if st.button("RESET TOTAL 💣"):
        if clave == RESET_PASSWORD:
            st.session_state.votes = {}
            st.success("Votación reiniciada.")
            st.rerun()
        else:
            st.error("Clave incorrecta.")
