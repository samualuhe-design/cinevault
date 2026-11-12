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
        "carpetas": ["General", "Favoritas", "Sci-Fi", "Terror", "Acción", "Comedia"],
        "peliculas": [],
    }


def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


st.set_page_config(
    page_title="CineVault Pro", page_icon="🎬", layout="centered"
)

# --- ESTILO VISUAL OSCURO ESTILO STREAMING ---
st.markdown(
    """
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3 { color: #E50914 !important; }
    .stButton>button {
        background-color: #E50914;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .stButton>button:hover { background-color: #B20710; color: white; }
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid #2C2C2C;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

datos = cargar_datos()

# --- ENCABEZADO Y ESTADÍSTICAS ---
st.title("🎬 CINEVAULT")

total_pelis = len(datos["peliculas"])
pendientes_count = sum(1 for p in datos["peliculas"] if p["estado"] == "Pendiente")
vistas_count = sum(1 for p in datos["peliculas"] if p["estado"] == "Vista")

m1, m2, m3 = st.columns(3)
m1.metric("🎞️ Total", total_pelis)
m2.metric("⏳ Pendientes", pendientes_count)
m3.metric("✅ Vistas", vistas_count)

# --- BARRA LATERAL: CARPETAS Y RESPALDO ---
st.sidebar.header("📁 Carpetas")
carpeta_seleccionada = st.sidebar.selectbox(
    "Elegir carpeta:", ["Todas"] + datos["carpetas"]
)

nueva_carpeta = st.sidebar.text_input("Crear nueva carpeta:", placeholder="Ej: Marvel, Anime...")
if st.sidebar.button("➕ Crear Carpeta"):
    nombre_limpio = nueva_carpeta.strip()
    if nombre_limpio and nombre_limpio not in datos["carpetas"] and nombre_limpio != "Todas":
        datos["carpetas"].append(nombre_limpio)
        guardar_datos(datos)
        st.sidebar.success(f"Carpeta '{nombre_limpio}' creada.")
        st.rerun()
    elif nombre_limpio:
        st.sidebar.warning("Esa carpeta ya existe o no es válida.")

if carpeta_seleccionada not in ["Todas", "General"]:
    if st.sidebar.button(f"🗑️ Eliminar '{carpeta_seleccionada}'"):
        for p in datos["peliculas"]:
            if p["carpeta"] == carpeta_seleccionada:
                p["carpeta"] = "General"
        datos["carpetas"].remove(carpeta_seleccionada)
        guardar_datos(datos)
        st.rerun()

st.sidebar.divider()
st.sidebar.header("💾 Copia de Seguridad")
st.sidebar.download_button(
    label="⬇️ Descargar mis películas (.json)",
    data=json.dumps(datos, indent=4, ensure_ascii=False),
    file_name="mis_peliculas_backup.json",
    mime="application/json",
)

archivo_subido = st.sidebar.file_uploader("⬆️ Cargar respaldo (.json)", type=["json"])
if archivo_subido is not None:
    try:
        datos_nuevos = json.load(archivo_subido)
        if "peliculas" in datos_nuevos and "carpetas" in datos_nuevos:
            guardar_datos(datos_nuevos)
            st.sidebar.success("¡Lista cargada con éxito!")
            st.rerun()
    except Exception:
        st.sidebar.error("El archivo no tiene el formato correcto.")

# --- FORMULARIO RÁPIDO PARA AGREGAR PELÍCULA ---
st.subheader("➕ Agregar Rápido")
with st.form("form_rapido", clear_on_submit=True):
    col_t, col_c = st.columns([2, 1])
    with col_t:
        nuevo_titulo = st.text_input("Título *", placeholder="Escribí el nombre de la peli...")
    with col_c:
        default_idx = (
            datos["carpetas"].index(carpeta_seleccionada)
            if carpeta_seleccionada in datos["carpetas"]
            else 0
        )
        pel_carpeta = st.selectbox("Carpeta", datos["carpetas"], index=default_idx)

    col_e, col_r, col_n = st.columns([1, 1, 2])
    with col_e:
        pel_estado = st.selectbox("Estado", ["Pendiente", "Viendo", "Vista"])
    with col_r:
        pel_rating = st.selectbox(
            "Estrellas",
            [
                "Sin calificar",
                "⭐ (1/5)",
                "⭐⭐ (2/5)",
                "⭐⭐⭐ (3/5)",
                "⭐⭐⭐⭐ (4/5)",
                "⭐⭐⭐⭐⭐ (5/5)",
            ],
        )
    with col_n:
        pel_nota = st.text_input("Nota / Plataforma", placeholder="Ej: Netflix, recomendada...")

    if st.form_submit_button("💾 Guardar Película"):
        if nuevo_titulo.strip():
            nueva_peli = {
                "id": random.randint(10000, 99999),
                "titulo": nuevo_titulo.strip(),
                "carpeta": pel_carpeta,
                "rating": pel_rating,
                "estado": pel_estado,
                "nota": pel_nota.strip(),
            }
            datos["peliculas"].insert(0, nueva_peli)  # La pone primera en la lista
            guardar_datos(datos)
            st.toast(f"✅ '{nuevo_titulo.strip()}' agregada!", icon="🎬")
            st.rerun()
        else:
            st.warning("Falta escribir el título de la película.")

st.divider()

# --- BUSCADOR, FILTRO DE ESTADO Y RULETA ---
col_busq, col_est_filtro = st.columns([2, 1])
with col_busq:
    busqueda = st.text_input("🔍 Buscar por nombre o nota:", placeholder="Buscar...")
with col_est_filtro:
    filtro_estado = st.selectbox("Filtrar estado:", ["Todos", "Pendiente", "Viendo", "Vista"])

if st.button("🎲 ¿Qué veo hoy? (Elegir al azar entre pendientes)"):
    pendientes = [
        p
        for p in datos["peliculas"]
        if p["estado"] == "Pendiente"
        and (carpeta_seleccionada == "Todas" or p["carpeta"] == carpeta_seleccionada)
    ]
    if pendientes:
        elegida = random.choice(pendientes)
        st.balloons()
        st.success(
            f"🍿 **Hoy toca:** {elegida['titulo']}  \n"
            f"📂 Carpeta: **{elegida['carpeta']}** | 📝 Nota: *{elegida['nota'] or 'Sin notas'}*"
        )
    else:
        st.info("No tenés películas en estado 'Pendiente' con los filtros actuales.")

# --- LISTADO DE PELÍCULAS ---
peliculas_filtradas = []
for p in datos["peliculas"]:
    if carpeta_seleccionada != "Todas" and p["carpeta"] != carpeta_seleccionada:
        continue
    if filtro_estado != "Todos" and p["estado"] != filtro_estado:
        continue
    if (
        busqueda
        and busqueda.lower() not in p["titulo"].lower()
        and busqueda.lower() not in p["nota"].lower()
    ):
        continue
    peliculas_filtradas.append(p)

st.subheader(
    f"🎞️ Lista ({len(peliculas_filtradas)}) — {carpeta_seleccionada}"
)

if not peliculas_filtradas:
    st.info("No hay películas que coincidan con esta búsqueda o filtro.")
else:
    opciones_rating = [
        "Sin calificar",
        "⭐ (1/5)",
        "⭐⭐ (2/5)",
        "⭐⭐⭐ (3/5)",
        "⭐⭐⭐⭐ (4/5)",
        "⭐⭐⭐⭐⭐ (5/5)",
    ]
    opciones_estado = ["Pendiente", "Viendo", "Vista"]

    for p in peliculas_filtradas:
        with st.container(border=True):
            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(f"### {p['titulo']}")
                st.caption(f"📂 {p['carpeta']}  •  {p['rating']}  •  Estado: **{p['estado']}**")
                if p["nota"]:
                    st.write(f"📝 *{p['nota']}*")
            with col_del:
                if st.button("🗑️", key=f"del_{p['id']}", help="Eliminar película"):
                    datos["peliculas"].remove(p)
                    guardar_datos(datos)
                    st.rerun()

            # Panel desplegable para editar rápido esa película
            with st.expander("✏️ Editar estado, estrellas o nota"):
                c1, c2 = st.columns(2)
                with c1:
                    nuevo_est = st.selectbox(
                        "Estado",
                        opciones_estado,
                        index=opciones_estado.index(p["estado"]),
                        key=f"est_sel_{p['id']}",
                    )
                with c2:
                    idx_r = opciones_rating.index(p["rating"]) if p["rating"] in opciones_rating else 0
                    nuevo_rat = st.selectbox(
                        "Calificación",
                        opciones_rating,
                        index=idx_r,
                        key=f"rat_sel_{p['id']}",
                    )

                nueva_nota_edit = st.text_input(
                    "Nota", value=p["nota"], key=f"nota_in_{p['id']}"
                )

                if st.button("Guardar cambios", key=f"save_{p['id']}"):
                    p["estado"] = nuevo_est
                    p["rating"] = nuevo_rat
                    p["nota"] = nueva_nota_edit.strip()
                    guardar_datos(datos)
                    st.rerun()
