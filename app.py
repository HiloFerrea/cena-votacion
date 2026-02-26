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
    "Club (modo caos) 🕺",
]

RESET_PASSWORD = "asado"  # cambiá si querés

st.set_page_config(page_title=APP_TITLE, page_icon="🍝", layout="centered")

# ----------------------------
# FUNCIONES
# ----------------------------
def now_str():
    return datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")


def init_state():
    if "votes" not in st.session_state:
        st.session_state.votes = {}  # {persona: voto_final}
    if "opciones" not in st.session_state:
        st.session_state.opciones = OPCIONES_DEFAULT.copy()


def winner_info(df: pd.DataFrame):
    if df.empty:
        return None, None, None
    counts = df["voto"].value_counts()
    max_v = int(counts.max())
    leaders = counts[counts == max_v].index.tolist()
    return counts, leaders, max_v


def is_club_option(text: str) -> bool:
    return "club" in text.lower()


# ----------------------------
# INIT
# ----------------------------
init_state()

# ----------------------------
# SIDEBAR (estilo calculadora)
# ----------------------------
with st.sidebar:
    st.markdown("### 🏛️ Hora oficial del hambre")
    st.markdown(f"**{APP_REGION}**")
    st.markdown(f"🕒 {now_str()}")
    st.caption("Sistema Democrático Gastronómico (SDG v1.0)")
    st.divider()

    st.subheader("⚙️ Opciones")
    st.write("Podés editar opciones (una por línea).")
    txt = st.text_area(
        "Opciones",
        value="\n".join(st.session_state.opciones),
        height=160
    )
    nuevas = [x.strip() for x in txt.split("\n") if x.strip()]
    if nuevas:
        st.session_state.opciones = nuevas

    st.divider()
    st.subheader("🧨 Admin")
    clave = st.text_input("Clave de reset", type="password")
    if st.button("RESET TOTAL 💣", use_container_width=True):
        if clave == RESET_PASSWORD:
            st.session_state.votes = {}
            st.success("Votación reiniciada. Se viene el segundo round.")
            st.rerun()
        else:
            st.error("Clave incorrecta.")


# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    f"""
    <div style='padding:10px; border-radius:10px; background-color:#f2f2f2; text-align:center'>
        🕒 <b>Hora oficial del hambre</b> — {APP_REGION}<br>
        <span style='font-size: 18px;'><b>{now_str()}</b></span>
    </div>
    """,
    unsafe_allow_html=True
)

st.title(APP_TITLE)
st.caption("Democracia gastronómica de baja intensidad. Resultados vinculantes (ponele).")
st.divider()

# ----------------------------
# TABS
# ----------------------------
tab1, tab2 = st.tabs(["🗳️ Votar", "📊 Resultados"])

# ----------------------------
# TAB 1 - VOTAR
# ----------------------------
with tab1:
    st.subheader("Emití tu voto")

    col1, col2 = st.columns([2, 1], vertical_alignment="top")

    with col1:
        nombre = st.selectbox("¿Quién sos?", AMIGOS)

        if nombre in st.session_state.votes:
            st.info(f"✅ Ya votaste: **{st.session_state.votes[nombre]}**")
            st.caption("Si te arrepentís: lobby por WhatsApp como corresponde.")
        else:
            opcion = st.radio("Elegí el destino gastronómico:", st.session_state.opciones)

            club_texto = None
            if is_club_option(opcion):
                club_texto = st.text_input(
                    "¿Qué club específicamente?",
                    placeholder="Ej: Club Tacuarí, Atenas, etc."
                )

            if st.button("VOTAR 🚨", use_container_width=True):
                if is_club_option(opcion) and (not club_texto or not club_texto.strip()):
                    st.warning("Especificá qué club, no seas ambiguo 😄")
                else:
                    voto_final = opcion
                    if is_club_option(opcion):
                        voto_final = f"{opcion} — {club_texto.strip()}"

                    st.session_state.votes[nombre] = voto_final
                    st.success(f"Voto registrado: **{nombre} → {voto_final}**")
                    st.rerun()

    with col2:
        st.subheader("📌 Estado")
        for a in AMIGOS:
            st.write(f"- {'✅' if a in st.session_state.votes else '⌛'} {a}")

        faltan = [a for a in AMIGOS if a not in st.session_state.votes]
        if faltan:
            st.warning("Faltan: " + ", ".join(faltan))
        else:
            st.success("¡Votación completa!")

# ----------------------------
# TAB 2 - RESULTADOS
# ----------------------------
with tab2:
    st.subheader("Resultados en vivo")

    if not st.session_state.votes:
        st.write("Todavía no hay votos. Esto es una asamblea vacía.")
    else:
        df = pd.DataFrame([{"persona": k, "voto": v} for k, v in st.session_state.votes.items()])
        df = df.sort_values("persona")

        st.write("**Votos registrados:**")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        counts, leaders, max_v = winner_info(df)

        st.write("**Conteo:**")
        st.bar_chart(counts)

        st.divider()
        frases = [
            "La voluntad popular ha hablado (y se equivoca con seguridad).",
            "Esto es estadística aplicada al hambre.",
            "No lloren, organicen revancha.",
            "Si sale empate, se resuelve con piedra-papel-tijera o soborno en papas fritas.",
        ]
        st.write(random.choice(frases))

        if len(leaders) == 1:
            st.success(f"🏆 Va ganando: **{leaders[0]}** con **{max_v}** voto(s).")
        else:
            st.warning(f"🤝 Empate entre: **{', '.join(leaders)}** con **{max_v}** voto(s) cada uno.")
            st.info("Regla sugerida: desempate por quién llega primero o moneda al aire.")
