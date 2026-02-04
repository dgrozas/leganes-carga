import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Leganés C - Gestión de Carga", layout="centered", page_icon="🛡️")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { color: #004595; font-family: 'Arial', sans-serif; font-weight: bold; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; 
        background-color: #004595; color: white; border: none;
        font-size: 16px !important; margin-top: 10px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0; border-radius: 10px 10px 0px 0px;
        padding: 10px 20px; font-weight: bold; color: #475569;
        flex-grow: 1; text-align: center;
    }
    .stTabs [aria-selected="true"] { background-color: #004595 !important; color: white !important; }
    .portada-container { text-align: center; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONSTANTES Y PERSISTENCIA ---
DB_FILE = "seguimiento_futbol.json"
JUGADORES = ["David Gonzalez Rozas", "Jaime Catalina Contreras", "Marco Lopez Dato", "Igor Sava"]
LOGO_PATH = "escudo_leganes.png"

def verificar_logo():
    return os.path.exists(LOGO_PATH)

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
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return f"{dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]}"

# --- 3. GENERADOR DE PDF ---
def generar_pdf_oficial(fecha_sel, db):
    pdf = FPDF()
    pdf.add_page()
    
    if verificar_logo():
        pdf.image(LOGO_PATH, 10, 10, 25)
        pdf.set_xy(40, 15)
    else:
        pdf.set_xy(10, 15)
        
    pdf.set_text_color(0, 69, 149)
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(150, 10, "C.D. LEGANES C", ln=True)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(150, 7, f"INFORME CARGA INTERNA - {fecha_sel}", ln=True)
    pdf.line(10, 40, 200, 40)
    pdf.ln(15)

    pdf.set_fill_color(0, 69, 149); pdf.set_text_color(255, 255, 255); pdf.set_font("helvetica", "B", 9)
    pdf.cell(45, 10, " JUGADOR", 1, 0, "L", True)
    pdf.cell(75, 10, " DATOS PRE-ENTRENO", 1, 0, "C", True)
    pdf.cell(70, 10, " DATOS POST-ENTRENO", 1, 1, "C", True)

    pdf.set_text_color(0, 0, 0); pdf.set_font("helvetica", "", 8)

    nombres_graf = []
    fatigas_graf = []

    for jug in JUGADORES:
        eventos = [r for r in db.get(jug, []) if r["fecha"] == fecha_sel]
        pre = next((r for r in eventos if r["momento"] == "PRE"), None)
        post = next((r for r in eventos if r["momento"] == "POST"), None)
        
        f_val = post['datos']['fatiga_actual'] if post else (pre['datos']['fatiga'] if pre else 0)
        nombres_graf.append(jug.split()[0]); fatigas_graf.append(f_val)

        pdf.cell(45, 12, jug, 1)
        
        # Palabras completas en el PDF
        txt_pre = f"Descanso: {pre['datos']['descanso']} | Estres: {pre['datos']['estres']} | Fatiga: {pre['datos']['fatiga']}" if pre else "Sin datos"
        pdf.cell(75, 12, txt_pre, 1, 0, "C")
        
        txt_post = f"Intensidad: {post['datos']['intensidad']} | Fatiga: {post['datos']['fatiga_actual']}" if post else "Sin datos"
        pdf.cell(70, 12, txt_post, 1, 1, "C")

    plt.figure(figsize=(6, 3))
    plt.bar(nombres_graf, fatigas_graf, color='#004595')
    plt.ylim(0, 10); plt.title("Nivel de Fatiga Actual"); tmp_img = "chart.png"
    plt.savefig(tmp_img, bbox_inches='tight'); plt.close()
    pdf.ln(10); pdf.image(tmp_img, x=45, w=120)
    if os.path.exists(tmp_img): os.remove(tmp_img)

    return bytes(pdf.output())

# --- 4. LÓGICA DE NAVEGACIÓN ---
if 'seccion' not in st.session_state: st.session_state.seccion = 'Inicio'
if 'form_key' not in st.session_state: st.session_state.form_key = 0

def reset_form():
    st.session_state.form_key += 1

with st.sidebar:
    if verificar_logo(): st.image(LOGO_PATH, width=120)
    st.title("GESTIÓN")
    if st.button("🏠 INICIO"): st.session_state.seccion = 'Inicio'
    if st.button("📝 ENCUESTA"): st.session_state.seccion = 'Jugadores'
    if st.button("🛡️ STAFF"): st.session_state.seccion = 'Staff'

# --- 5. PÁGINAS ---
if st.session_state.seccion == 'Inicio':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if verificar_logo(): st.image(LOGO_PATH, use_container_width=True)
    st.markdown('<div class="portada-container"><h1>C.D. LEGANÉS C</h1><h3>Gestión de Plantilla</h3></div>', unsafe_allow_html=True)
    if st.button("ACCESO JUGADORES"): st.session_state.seccion = 'Jugadores'
    if st.button("ACCESO STAFF"): st.session_state.seccion = 'Staff'

elif st.session_state.seccion == 'Jugadores':
    st.header("📋 Registro de Sesión")
    nombre_j = st.selectbox("Selecciona tu nombre:", JUGADORES, on_change=reset_form)
    tab_pre, tab_post = st.tabs(["🔹 PRE-ENTRENO", "🔸 POST-ENTRENO"])
    f_key = st.session_state.form_key

    with tab_pre:
        with st.form(key=f"pre_{f_key}"):
            d = st.select_slider("Calidad del Descanso", options=range(11), value=0, key=f"d_{f_key}")
            e = st.select_slider("Nivel de Estrés", options=range(11), value=0, key=f"e_{f_key}")
            f = st.select_slider("Fatiga Muscular Previa", options=range(11), value=0, key=f"f_{f_key}")
            if st.form_submit_button("GUARDAR PRE"):
                db = cargar_datos(); fecha = obtener_fecha_hoy()
                if nombre_j not in db: db[nombre_j] = []
                db[nombre_j].append({"fecha": fecha, "momento": "PRE", "datos": {"descanso": d, "estres": e, "fatiga": f}})
                guardar_datos(db); st.success("✅ Guardado correctamente"); st.session_state.form_key += 1

    with tab_post:
        # Lógica para mostrar éxito y botón de salir
        if f'success_{f_key}' in st.session_state:
            st.balloons()
            st.success("✅ ¡Encuesta finalizada con éxito!")
            if st.button("🚪 FINALIZAR Y SALIR"):
                st.session_state.seccion = 'Inicio'
                del st.session_state[f'success_{f_key}']
                st.rerun()
        else:
            with st.form(key=f"post_{f_key}"):
                i = st.select_slider("Intensidad (RPE)", options=range(11), value=0, key=f"i_{f_key}")
                fa = st.select_slider("Fatiga Post-Esfuerzo", options=range(11), value=0, key=f"fa_{f_key}")
                if st.form_submit_button("GUARDAR POST"):
                    db = cargar_datos(); fecha = obtener_fecha_hoy()
                    if nombre_j not in db: db[nombre_j] = []
                    db[nombre_j].append({"fecha": fecha, "momento": "POST", "datos": {"intensidad": i, "fatiga_actual": fa}})
                    guardar_datos(db)
                    st.session_state[f'success_{f_key}'] = True
                    st.rerun()

elif st.session_state.seccion == 'Staff':
    st.header("🛡️ Acceso Staff")
    if st.text_input("Contraseña", type="password") == "123456":
        db_s = cargar_datos()
        fechas = sorted(list(set(r["fecha"] for h in db_s.values() for r in h)), reverse=True)
        
        if fechas:
            f_ver = st.selectbox("Seleccionar Sesión:", fechas)
            try:
                data_pdf = generar_pdf_oficial(f_ver, db_s)
                st.download_button("📄 DESCARGAR INFORME PDF", data=data_pdf, file_name=f"Informe_{f_ver}.pdf", mime="application/pdf")
            except Exception as e: st.error(f"Error PDF: {e}")

            st.divider()
            for j in JUGADORES:
                regs = [r for r in db_s.get(j, []) if r["fecha"] == f_ver]
                if regs:
                    with st.expander(f"👤 {j.upper()}"):
                        pre = next((r for r in regs if r["momento"] == "PRE"), None)
                        post = next((r for r in regs if r["momento"] == "POST"), None)
                        c1, c2 = st.columns(2)
                        # Todos los campos visibles para el Staff
                        if pre: c1.info(f"**PRE-ENTRENO**\n\nDescanso: {pre['datos']['descanso']}\n\nEstrés: {pre['datos']['estres']}\n\nFatiga: {pre['datos']['fatiga']}")
                        if post: c2.success(f"**POST-ENTRENO**\n\nIntensidad: {post['datos']['intensidad']}\n\nFatiga: {post['datos']['fatiga_actual']}")
            
            st.sidebar.divider()
            if st.sidebar.button("🗑️ VACIAR DATOS (PELIGRO)"):
                if st.sidebar.checkbox("Confirmar borrado total"):
                    guardar_datos({}); st.rerun()
        else:
            st.info("No hay datos históricos aún.")

