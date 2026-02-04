import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Leganés C - Gestión de Carga", layout="centered", page_icon="🛡️")

# CSS Profesional: Estética Blanquiazul y Botones Táctiles
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #004595; font-family: 'Arial', sans-serif; font-weight: bold; }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 4em; font-weight: bold; 
        background-color: #004595; color: white; border: 2px solid #004595;
        font-size: 18px !important;
        margin-top: 10px;
    }
    .stButton>button:hover { background-color: white; color: #004595; }
    .stSelectbox label, .stSlider label, .stRadio label { color: #004595; font-weight: bold; font-size: 16px; }
    .portada-container { text-align: center; padding: 10px; margin-bottom: 20px; }
    .footer-text { text-align: center; color: #94a3b8; font-size: 12px; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONSTANTES Y PERSISTENCIA ---
DB_FILE = "seguimiento_futbol.json"
JUGADORES = ["David Gonzalez Rozas", "Jaime Catalina Contreras", "Marco Lopez Dato", "Igor Sava"]
LOGO_PATH = "escudo_leganes.png"

def verificar_logo():
    """Verifica si existe el logo localmente"""
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
    dias = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", 
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
             7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    ahora = datetime.now()
    return f"{dias[ahora.strftime('%A')]} {ahora.day} de {meses[ahora.month]}"

# --- 3. GENERADOR DE PDF (FORMATO PROFESIONAL) ---
def generar_pdf_oficial(fecha_sel, db):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. ENCABEZADO CON ESCUDO
    if verificar_logo():
        pdf.image(LOGO_PATH, 10, 10, 28)
        pdf.set_xy(42, 16)
    else:
        pdf.set_xy(15, 16)
        
    pdf.set_text_color(0, 69, 149) # Azul Leganés
    pdf.set_font("Arial", "B", 24)
    pdf.cell(150, 10, "C.D. LEGANES C", ln=True, align="L")
    
    pdf.set_font("Arial", "B", 13)
    pdf.set_x(pdf.get_x() if not verificar_logo() else 42)
    pdf.cell(150, 8, "INFORME OFICIAL DE CONTROL DE CARGA", ln=True, align="L")
    
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Arial", "I", 10)
    pdf.set_x(pdf.get_x() if not verificar_logo() else 42)
    pdf.cell(150, 8, f"Sesion correspondiente al {fecha_sel}", ln=True, align="L")
    
    # Línea decorativa blanquiazul
    pdf.set_draw_color(0, 69, 149)
    pdf.set_line_width(0.5)
    pdf.line(10, 45, 200, 45)
    pdf.ln(20)

    # 2. TABLA DE DATOS
    pdf.set_fill_color(0, 69, 149)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)
    
    # Cabeceras
    pdf.cell(45, 12, "JUGADOR", 1, 0, "C", True)
    pdf.cell(75, 12, "DATOS PRE-ENTRENO", 1, 0, "C", True)
    pdf.cell(70, 12, "DATOS POST-ENTRENO", 1, 1, "C", True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    
    def color_segun_valor(v):
        if v < 5: return (0, 0, 0)
        if 5 <= v <= 8: return (0, 0, 255)
        return (255, 0, 0)

    nombres_graf = []
    fatigas_graf = []

    for jug in JUGADORES:
        eventos = [r for r in db.get(jug, []) if r["fecha"] == fecha_sel]
        pre = next((r for r in eventos if r["momento"] == "PRE"), None)
        post = next((r for r in eventos if r["momento"] == "POST"), None)
        
        f_val = max((pre['datos']['fatiga'] if pre else 0), (post['datos']['fatiga_actual'] if post else 0))
        nombres_graf.append(jug.split()[0])
        fatigas_graf.append(f_val)

        x_start = pdf.get_x()
        y_start = pdf.get_y()
        alto_fila = 14

        # Skeleton (Bordes limpios)
        pdf.cell(45, alto_fila, "", 1)
        pdf.cell(75, alto_fila, "", 1)
        pdf.cell(70, alto_fila, "", 1)
        
        pdf.set_xy(x_start, y_start)
        pdf.cell(45, alto_fila, f" {jug}", 0)
        
        # PRE
        pdf.set_xy(x_start + 45, y_start)
        if pre:
            d = pre['datos']
            val_d = d.get('descanso', d.get('sueno', 0))
            pdf.write(alto_fila, " Descanso: ")
            pdf.write(alto_fila, str(val_d))
            pdf.write(alto_fila, " Estres: ")
            pdf.set_text_color(*color_segun_valor(d['estres'])); pdf.write(alto_fila, str(d['estres']))
            pdf.set_text_color(0,0,0); pdf.write(alto_fila, " Fatiga: ")
            pdf.set_text_color(*color_segun_valor(d['fatiga'])); pdf.write(alto_fila, str(d['fatiga']))
            pdf.set_text_color(0,0,0)
        else:
            pdf.set_text_color(150, 150, 150)
            pdf.cell(75, alto_fila, " Sin respuesta", 0)

        # POST
        pdf.set_xy(x_start + 120, y_start)
        if post:
            d = post['datos']
            pdf.set_text_color(0,0,0); pdf.write(alto_fila, " Intensidad: ")
            pdf.set_text_color(*color_segun_valor(d['intensidad'])); pdf.write(alto_fila, str(d['intensidad']))
            pdf.set_text_color(0,0,0); pdf.write(alto_fila, " Fatiga: ")
            pdf.set_text_color(*color_segun_valor(d['fatiga_actual'])); pdf.write(alto_fila, str(d['fatiga_actual']))
        else:
            pdf.set_text_color(150, 150, 150)
            pdf.cell(70, alto_fila, " Sin respuesta", 0)
            
        pdf.set_text_color(0,0,0)
        pdf.set_xy(x_start, y_start + alto_fila)

    # 3. GRÁFICO DE MAPA DE CALOR
    plt.figure(figsize=(7, 4))
    colors = ['#ef4444' if f >= 9 else '#3b82f6' if f >= 5 else '#1f2937' for f in fatigas_graf]
    plt.bar(nombres_graf, fatigas_graf, color=colors)
    plt.title("MAPA DE FATIGA ACUMULADA POR JUGADOR", color='#004595', fontweight='bold', pad=15)
    plt.ylim(0, 10)
    plt.ylabel("Nivel de Fatiga (0-10)")
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    tmp_img = "tmp_chart.png"
    plt.savefig(tmp_img, bbox_inches='tight', dpi=150)
    plt.close()
    
    pdf.ln(12)
    pdf.image(tmp_img, x=35, w=140)
    
    if os.path.exists(tmp_img): os.remove(tmp_img)

    return pdf.output(dest="S").encode("latin-1")

# --- 4. CONTROL DE NAVEGACIÓN ---
if 'seccion' not in st.session_state:
    st.session_state.seccion = 'Inicio'

with st.sidebar:
    if verificar_logo():
        st.image(LOGO_PATH, width=150)
    else:
        st.warning("⚠️ Falta escudo")
    st.title("MENÚ PRINCIPAL")
    st.write("---")
    if st.button("🏠 PORTADA"): st.session_state.seccion = 'Inicio'
    if st.button("📝 CUESTIONARIOS"): st.session_state.seccion = 'Jugadores'
    if st.button("🛡️ ACCESO STAFF"): st.session_state.seccion = 'Staff'

# --- 5. PÁGINAS ---

if st.session_state.seccion == 'Inicio':
    # DISEÑO DE PORTADA CON ESCUDO CENTRAL
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if verificar_logo():
            st.image(LOGO_PATH, use_container_width=True)
        else:
            st.error("❌ Coloca 'escudo_leganes.png' en la carpeta del proyecto")
    
    st.markdown("""
        <div class="portada-container">
            <h1>C.D. LEGANÉS C</h1>
            <h3 style='border:none; color: #475569;'>SISTEMA DE GESTIÓN DE RENDIMIENTO</h3>
            <p>Monitoreo oficial de carga interna y bienestar del jugador</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("ENTRAR JUGADORES"): st.session_state.seccion = 'Jugadores'
    with c2:
        if st.button("ENTRAR STAFF"): st.session_state.seccion = 'Staff'
    
    st.markdown('<div class="footer-text">© 2025 C.D. Leganés C - Departamento de Preparación Física</div>', unsafe_allow_html=True)

elif st.session_state.seccion == 'Jugadores':
    st.header("📋 Registro de Sesión Diaria")
    nombre_j = st.selectbox("Identifícate en la plantilla:", JUGADORES)
    momento_j = st.radio("Momento de la toma de datos:", ["PRE", "POST"], horizontal=True)
    
    with st.form("form_jugador"):
        if momento_j == "PRE":
            d = st.select_slider("Calidad del Descanso", options=range(11), value=7)
            e = st.select_slider("Nivel de Estrés Percibido", options=range(11), value=2)
            f = st.select_slider("Fatiga Muscular Previa", options=range(11), value=0)
            envio = {"descanso": d, "estres": e, "fatiga": f}
        else:
            i = st.select_slider("Intensidad de la Sesión (RPE)", options=range(11), value=5)
            fa = st.select_slider("Fatiga Post-Entrenamiento", options=range(11), value=0)
            envio = {"intensidad": i, "fatiga_actual": fa}
            
        if st.form_submit_button("GUARDAR REGISTRO"):
            db = cargar_datos(); fecha = obtener_fecha_hoy()
            if nombre_j not in db: db[nombre_j] = []
            if any(r["fecha"] == fecha and r["momento"] == momento_j for r in db[nombre_j]):
                st.error("Atención: Ya has registrado estos datos hoy.")
            else:
                db[nombre_j].append({"fecha": fecha, "momento": momento_j, "datos": envio})
                guardar_datos(db); st.success(f"¡Hecho! Datos guardados para {nombre_j.split()[0]}.")

elif st.session_state.seccion == 'Staff':
    st.header("🛡️ Acceso Cuerpo Técnico")
    if st.text_input("Contraseña de Seguridad", type="password") == "123456":
        st.subheader("📊 Panel de Análisis")
        db_s = cargar_datos()
        fechas_s = sorted(list(set(r["fecha"] for h in db_s.values() for r in h)), reverse=True)
        
        if fechas_s:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                f_ver = st.selectbox("Seleccionar Sesión:", fechas_s)
            
            # Generar datos del PDF
            try:
                data_pdf = generar_pdf_oficial(f_ver, db_s)
                with col_btn:
                    st.write("") # Espaciador
                    st.write("") # Espaciador
                    st.download_button("📄 PDF", data=data_pdf, 
                                       file_name=f"Informe_LeganesC_{f_ver.replace(' ','_')}.pdf")
            except Exception as ex:
                st.error(f"Error al generar el documento: {ex}")
            
            st.divider()
            # Vista rápida de tarjetas
            for j in JUGADORES:
                regs = [r for r in db_s.get(j, []) if r["fecha"] == f_ver]
                if regs:
                    with st.expander(f"👤 {j.upper()}"):
                        c1, c2 = st.columns(2)
                        p_pre = next((r for r in regs if r["momento"] == "PRE"), None)
                        p_post = next((r for r in regs if r["momento"] == "POST"), None)
                        if p_pre: 
                            v_desc = p_pre['datos'].get('descanso', p_pre['datos'].get('sueno', 0))
                            c1.info(f"**DATOS PRE**\n\nDescanso: {v_desc}\n\nEstrés: {p_pre['datos']['estres']}\n\nFatiga: {p_pre['datos']['fatiga']}")
                        if p_post:
                            c2.success(f"**DATOS POST**\n\nIntensidad: {p_post['datos']['intensidad']}\n\nFatiga: {p_post['datos']['fatiga_actual']}")
        else:
            st.info("Todavía no se han registrado sesiones en la base de datos.")