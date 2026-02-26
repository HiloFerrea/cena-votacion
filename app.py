# ============================================
# 🍽️ Votación Oficial™ - Cena entre Amigos (MULTIUSUARIO REAL)
# Autor: Hilo
# Región: La Plata, PBA
# ============================================

import random
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

# ----------------------------
# CONFIG
# ----------------------------
APP_TITLE = "🍽️ Votación Oficial™ - Cena"
APP_REGION = "La Plata, Provincia de Buenos Aires"
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

AMIGOS = ["Rami", "Lucho", "Rafa", "Rulo", "Hilo"]

# OJO: strings para conservar ceros a la izquierda
PINS = {
    "Rami": "157",
    "Lucho": "023",
    "Rafa": "820",
    "Rulo": "029",
    "Hilo": "623",
}

OPCIONES = [
    "BACCI",
    "Bar de birras",
    "Restaurante cheto",
    "Pizzería cheta, de esas que le gustan a Rami 🍕",
    "Club",
]

st.set_page_config(page_title=APP_TITLE, page_icon="🍝", layout="centered")


# ----------------------------
# STORE GLOBAL (compartido entre usuarios)
# ----------------------------
@st.cache_resource
def global_store():
    # Se comparte entre sesiones mientras el server esté vivo
    return {
        "lock": threading.Lock(),
        "votes": {},  # {persona: voto_final}
    }


def load_votes() -> dict:
    store = global_store()
    with store["lock"]:
        return dict(store["votes"])  # copia


def save_votes(votes: dict) -> None:
    store = global_store()
    with store["lock"]:
        store["votes"] = dict(votes)


# ----------------------------
# HELPERS
# ----------------------------
def now_str() -> str:
    return datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")


def is_club_option(text: str) -> bool:
    return text.strip().lower() == "club"


def votes_df(votes: dict) -> pd.DataFrame:
    if not votes:
        return pd.DataFrame(columns=["persona", "voto"])
    df = pd.DataFrame([{"persona": k, "voto": v} for k, v in votes.items()])
    return df.sort_values("persona")


def winner_info(df: pd.DataFrame):
    if df.empty:
        return None, None, None
    counts = df["voto"].value_counts()
    max_v = int(counts.max())
    leaders = counts[counts == max_v].index.tolist()
    return counts, leaders, max_v


# ----------------------------
# CIERRE DE VOTACIÓN (HOY 23:59)
# ----------------------------
now = datetime.now(TZ)
cierre = now.replace(hour=23, minute=59, second=0, microsecond=0)
votacion_abierta = now < cierre


# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.markdown("### 🏛️ Hora oficial del hambre")
    st.markdown(f"**{APP_REGION}**")
    st.markdown(f"🕒 {now_str()}")
    st.caption("Sistema Democrático Gastronómico (SDG v1.3 — multiusuario)")
    st.divider()

    st.subheader("🧨 Administración (Solo Hilo)")
    admin_nombre = st.selectbox("Administrador", AMIGOS)
    admin_pin = st.text_input("Clave (últimos 3 del teléfono)", type="password", max_chars=3)

    if st.button("RESET TOTAL 💣", use_container_width=True):
        if admin_nombre != "Hilo":
            st.error("🚫 Solo Hilo puede reiniciar la votación.")
        elif admin_pin != PINS["Hilo"]:
            st.error("🚫 Clave incorrecta.")
        else:
            save_votes({})
            st.success("🧹 Votación reiniciada por autoridad competente.")
            st.rerun()

    st.divider()
    st.subheader("🔄 Actualizar")
    st.caption("Si estás mirando fijo, esto refresca manualmente.")
    if st.button("Actualizar resultados", use_container_width=True):
        st.rerun()


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
    unsafe_allow_html=True,
)

st.title(APP_TITLE)

# Mensaje + contador de cierre
if not votacion_abierta:
    st.error("⛔ Votación cerrada. Se aceptan solo resultados.")
else:
    restante = cierre - datetime.now(TZ)
    total_seconds = int(restante.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    segundos = total_seconds % 60
    st.info(
        "🗳️ **Tiempo para votar hasta hoy 23:59**\n\n"
        f"⏳ Restan: **{horas:02d}:{minutos:02d}:{segundos:02d}**"
    )

st.divider()

# 🔄 Auto refresh cada 3 segundos (para ver avance en vivo)
st.autorefresh(interval=3000, key="auto_refresh")


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
        pin = st.text_input("Ingresá tu clave (últimos 3 de tu teléfono)", type="password", max_chars=3)

        votes_live = load_votes()

        if nombre in votes_live:
            st.info(f"✅ Ya votaste: **{votes_live[nombre]}**")
            st.caption("Si querés cambiar el voto, pedile a Hilo el reset 😄")
        else:
            opcion = st.radio("Elegí el destino gastronómico:", OPCIONES)

            club_texto = None
            if is_club_option(opcion):
                club_texto = st.text_input(
                    "¿Qué club específicamente?",
                    placeholder="Ej: Club Tacuarí, Atenas, etc."
                )

            if not votacion_abierta:
                st.warning("La votación está cerrada: no se registran nuevos votos.")
            elif st.button("VOTAR 🚨", use_container_width=True):
                if pin != PINS[nombre]:
                    st.error("🚫 Clave incorrecta. Intento de fraude gastronómico detectado.")
                else:
                    votes_now = load_votes()
                    if nombre in votes_now:
                        st.warning("Ese nombre ya votó (según el padrón).")
                    elif is_club_option(opcion) and (not club_texto or not club_texto.strip()):
                        st.warning("Especificá qué club (Tacuarí, Atenas, etc.).")
                    else:
                        voto_final = opcion
                        if is_club_option(opcion):
                            voto_final = f"{opcion} — {club_texto.strip()}"

                        votes_now[nombre] = voto_final
                        save_votes(votes_now)
                        st.success(f"Voto registrado: **{nombre} → {voto_final}**")
                        st.rerun()

    with col2:
        st.subheader("📌 Avance")
        votes_live = load_votes()
        for a in AMIGOS:
            st.write(f"- {'✅' if a in votes_live else '⌛'} {a}")
        st.write("")
        st.metric("Votaron", f"{len(votes_live)}/{len(AMIGOS)}")


# ----------------------------
# TAB 2 - RESULTADOS
# ----------------------------
with tab2:
    st.subheader("Resultados en vivo")

    votes_live = load_votes()
    df = votes_df(votes_live)

    if df.empty:
        st.write("Todavía no hay votos. Esto es una asamblea vacía.")
    else:
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
            st.info("Tip: con el auto-refresh debería actualizarse solo cada 3 segundos.")