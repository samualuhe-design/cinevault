import json
import os
import random
import streamlit as st

ARCHIVO_DATOS = "mis_peliculas.json"


def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "carpetas": ["General", "Favoritas", "Sci-Fi", "Terror"],
        "peliculas": [],
    }


def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


st.set_page_config(
    page_title="CineVault", page_icon="🎬", layout="centered"
)

# Estilo visual estilo streaming oscuro
st.markdown(
    """
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3 { color: #E50914 !important; }
    .stButton>button { background-color: #E50914; color: white; border-radius: 5px; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #B20710; color: white; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎬 CINEVAULT")
st.write("Tu gestor de películas personal")

datos = cargar_datos()

# --- BARRA LATERAL (Gestión de Carpetas) ---
st.sidebar.header("📁 Mis Carpetas")
carpeta_seleccionada = st.sidebar.selectbox(
    "Filtrar por carpeta:", ["Todas"] + datos["carpetas"]
)

nueva_Carpeta = st.sidebar.text_input("Nueva carpeta:")
if st.sidebar.button("Añadir Carpeta"):
    nueva_Carpeta = nueva_Carpeta.strip()
    if (
        nueva_Carpeta
        and nueva_Carpeta not in datos["carpetas"]
        and nueva_Carpeta != "Todas"
    ):
        datos["carpetas"].append(nueva_Carpeta)
        guardar_datos(datos)
        st.sidebar.success(f"Carpeta '{nueva_Carpeta}' creada.")
        st.rerun()
    elif nueva_Carpeta:
        st.sidebar.warning("Esa carpeta ya existe o no es válida.")

# --- SECCIÓN PRINCIPAL: AÑADIR PELÍCULA ---
with st.expander("➕ Añadir Nueva Película", expanded=False):
    with st.form("form_pelicula"):
        nuevo_titulo = st.text_input("Título de la película:")
        col1, col2 = st.columns(2)
        with col1:
            pel_carpeta = st.selectbox("Carpeta", datos["carpetas"])
            pel_rating = st.selectbox(
                "Calificación",
                [
                    "Sin calificar",
                    "⭐ (1/5)",
                    "⭐⭐ (2/5)",
                    "⭐⭐⭐ (3/5)",
                    "⭐⭐⭐⭐ (4/5)",
                    "⭐⭐⭐⭐⭐ (5/5)",
                ],
            )
        with col2:
            pel_estado = st.selectbox(
                "Estado", ["Pendiente", "Viendo", "Vista"]
            )
        pel_nota = st.text_input("Nota / Plataforma / Comentario (opcional):")

        submitted = st.form_submit_button("Guardar Película")
        if submitted:
            if nuevo_titulo.strip():
                nueva_peli = {
                    "id": random.randint(10000, 99999),
                    "titulo": nuevo_titulo.strip(),
                    "carpeta": pel_carpeta,
                    "rating": pel_rating,
                    "estado": pel_estado,
                    "nota": pel_nota.strip(),
                }
                datos["peliculas"].append(nueva_peli)
                guardar_datos(datos)
                st.success(f"¡'{nuevo_titulo}' guardada con éxito!")
                st.rerun()
            else:
                st.warning("Por favor, escribí el título de la película.")

# --- BUSCADOR Y RULETA ALEATORIA ---
st.divider()
col_busq, col_azar = st.columns([2, 1])
with col_busq:
    busqueda = st.text_input("🔍 Buscar película o nota:", "")
with col_azar:
    st.write("")  # Espaciador
    if st.button("🎲 ¿Qué veo hoy?"):
        pendientes = [
            p
            for p in datos["peliculas"]
            if p["estado"] == "Pendiente"
            and (
                carpeta_seleccionada == "Todas"
                or p["carpeta"] == carpeta_seleccionada
            )
        ]
        if pendientes:
            elegida = random.choice(pendientes)
            st.balloons()
            st.success(
                f"**Te toca ver:** {elegida['titulo']} (📂 {elegida['carpeta']})"
            )
        else:
            st.warning("No hay películas pendientes en esta selección.")

# --- FILTRAR Y MOSTRAR PELÍCULAS ---
peliculas_filtradas = []
for p in datos["peliculas"]:
    if (
        carpeta_seleccionada != "Todas"
        and p["carpeta"] != carpeta_seleccionada
    ):
        continue
    if (
        busqueda
        and busqueda.lower() not in p["titulo"].lower()
        and busqueda.lower() not in p["nota"].lower()
    ):
        continue
    peliculas_filtradas.append(p)

st.subheader(
    f"Películas ({carpeta_seleccionada if carpeta_seleccionada != 'Todas' else 'Todas'})"
)

if not peliculas_filtradas:
    st.info("No hay películas para mostrar aquí.")
else:
    for p in peliculas_filtradas:
        with st.container():
            st.markdown(
                f"### 🎬 {p['titulo']}  \n"
                f"📂 **Carpeta:** {p['carpeta']} | 📊 **Estado:** {p['estado']} | ⭐ **Rating:** {p['rating']}"
            )
            if p["nota"]:
                st.write(f"📝 *Notas:* {p['nota']}")

            # Botones de acción rápidos por película
            col_acc1, col_acc2, col_acc3 = st.columns(3)
            with col_acc1:
                if st.button(
                    "Cambiar Estado", key=f"est_{p['id']}"
                ):
                    estados = ["Pendiente", "Viendo", "Vista"]
                    idx = estados.index(p["estado"])
                    p["estado"] = estados[(idx + 1) % len(estados)]
                    guardar_datos(datos)
                    st.rerun()
            with col_acc2:
                if st.button("🗑️ Borrar", key=f"del_{p['id']}"):
                    datos["peliculas"].remove(p)
                    guardar_datos(datos)
                    st.rerun()
            st.divider()