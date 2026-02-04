import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO MÓVIL ---
st.set_page_config(page_title="Leganés C - Gestión", layout="centered", page_icon="🛡️")

st.markdown("""
    <style>
    /* Optimización para pantallas táctiles */
    .stSlider { padding-bottom: 20px; }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; 
        background-color: #004595; color: white; border: none; font-size: 18px !important;
    }
    /* Pestañas (Tabs) Gigantes */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #f1f5f9; border-radius: 10px;
        flex-grow: 1; text-align: center; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #004595 !important; color: white !important; }
    
    /* Ajuste de fuentes para móvil */
    h1 { font-size: 24px !important; text-align: center; color: #004595; }
    h2 { font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONSTANTES Y PERSISTENCIA ---
DB_FILE = "seguimiento_futbol.json"
JUGADORES = ["David Gonzalez Rozas", "Jaime Catalina Contreras", "Marco Lopez Dato", "Igor Sava"]
LOGO_PATH = "escudo_leganes.png"

def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def guardar_datos(datos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def obtener_fecha_hoy():
    ahora = datetime.now()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"

# --- 3. GENERADOR DE PDF (CORREGIDO SIN ENCODE) ---
def generar_pdf_oficial(fecha_sel, db):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 69, 149)
    pdf.cell(0, 10, f"INFORME LEGANÉS C - {fecha_sel}", ln=True, align="C")
    pdf.ln(10)
    
    # Tabla simple para el informe
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 10, "Jugador", 1, 0, "C", True)
    pdf.cell(70, 10, "Pre-Entreno", 1, 0, "C", True)
    pdf.cell(70, 10, "Post-Entreno", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 9)
    for jug in JUGADORES:
        regs = [r for r in db.get(jug, []) if r["fecha"] == fecha_sel]
        pre = next((r for r in regs if r["momento"] == "PRE"), None)
        post = next((r for r in regs if r["momento"] == "POST"), None)
        
        pdf.cell(50, 10, jug[:20], 1)
        txt_pre = f"D:{pre['datos']['descanso']} E:{pre['datos']['estres']} F:{pre['datos']['fatiga']}" if pre else "---"
        pdf.cell(70, 10, txt_pre, 1)
        txt_post = f"I:{post['datos']['intensidad']} F:{post['datos']['fatiga_actual']}" if post else "---"
        pdf.cell(70, 10, txt_post, 1, 1)

    return pdf.output() # fpdf2 entrega bytes directamente

# --- 4. LÓGICA DE RESETEO ---
# Si el jugador cambia, incrementamos una versión en el state para resetear widgets
if 'nombre_anterior' not in st.session_state:
    st.session_state.nombre_anterior = JUGADORES[0]
if 'form_version' not in st.session_state:
    st.session_state.form_version = 0

def detectar_cambio_jugador():
    if st.session_state.sel_jugador != st.session_state.nombre_anterior:
        st.session_state.nombre_anterior = st.session_state.sel_jugador
        st.session_state.form_version += 1

# --- 5. INTERFAZ ---
if 'seccion' not in st.session_state:
    st.session_state.seccion = 'Jugadores'

with st.sidebar:
    st.title("🛡️ Menú")
    if st.button("📝 ENCUESTA"): st.session_state.seccion = 'Jugadores'
    if st.button("🛡️ STAFF"): st.session_state.seccion = 'Staff'

if st.session_state.seccion == 'Jugadores':
    st.header("📋 Registro de Sesión")
    
    # Selector de jugador con callback de reseteo
    nombre_j = st.selectbox("Selecciona tu nombre:", JUGADORES, key="sel_jugador", on_change=detectar_cambio_jugador)
    
    tab_pre, tab_post = st.tabs(["🔹 PRE", "🔸 POST"])
    
    # El uso de 'key' dinámico basado en form_version fuerza a Streamlit a olvidar valores viejos
    ver = st.session_state.form_version

    with tab_pre:
        with st.form(key=f"form_pre_{ver}"):
            st.write("### Datos de Bienvenida")
            d = st.select_slider("Calidad Descanso", options=range(11), value=0, key=f"d_{ver}")
            e = st.select_slider("Nivel Estrés", options=range(11), value=0, key=f"e_{ver}")
            f = st.select_slider("Fatiga Muscular", options=range(11), value=0, key=f"f_{ver}")
            if st.form_submit_button("GUARDAR PRE"):
                db = cargar_datos()
                if nombre_j not in db: db[nombre_j] = []
                db[nombre_j].append({"fecha": obtener_fecha_hoy(), "momento": "PRE", "datos": {"descanso": d, "estres": e, "fatiga": f}})
                guardar_datos(db)
                st.success("¡Datos Pre guardados!")

    with tab_post:
        with st.form(key=f"form_post_{ver}"):
            st.write("### Carga de Sesión")
            i = st.select_slider("Intensidad (RPE)", options=range(11), value=0, key=f"i_{ver}")
            fa = st.select_slider("Fatiga Post", options=range(11), value=0, key=f"fa_{ver}")
            if st.form_submit_button("GUARDAR POST"):
                db = cargar_datos()
                if nombre_j not in db: db[nombre_j] = []
                db[nombre_j].append({"fecha": obtener_fecha_hoy(), "momento": "POST", "datos": {"intensidad": i, "fatiga_actual": fa}})
                guardar_datos(db)
                st.success("¡Datos Post guardados!")

elif st.session_state.seccion == 'Staff':
    st.header("🛡️ Cuerpo Técnico")
    if st.text_input("Contraseña", type="password") == "123456":
        db = cargar_datos()
        fechas = sorted(list(set(r["fecha"] for h in db.values() for r in h)), reverse=True)
        if fechas:
            f_sel = st.selectbox("Fecha:", fechas)
            if st.download_button("📄 DESCARGAR PDF", data=generar_pdf_oficial(f_sel, db), file_name=f"Informe_{f_sel}.pdf"):
                st.balloons()
