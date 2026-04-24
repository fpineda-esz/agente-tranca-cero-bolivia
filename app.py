import streamlit as st
import os
from dotenv import load_dotenv

# --- IMPORTAMOS NUESTROS MÓDULOS ---
from auditoria import guardar_log
from motor_ia import crear_agente

# 1. Configuración de la página
st.set_page_config(page_title="Tranca Cero - Bolivia", page_icon="🇧🇴", layout="centered")

# --- CSS VISUAL ---
# --- DISEÑO INSTITUCIONAL BOLIVIA ---
st.markdown("""
<style>
    /* 1. Fondo general blanco y texto gris oscuro */
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
    }
    
    /* 2. Barra superior decorativa con la Tricolor Boliviana */
    header[data-testid="stHeader"] {
        background: linear-gradient(to right, #D52B1E 33.3%, #F9E000 33.3%, #F9E000 66.6%, #007934 66.6%);
        height: 6px !important;
    }

    /* 3. Estilo de las burbujas de chat (más limpias y formales) */
    [data-testid="stChatMessage"] {
        background-color: #F8F9FA !important;
        border-radius: 8px;
        border: 1px solid #E9ECEF;
        padding: 15px;
        margin-bottom: 10px;
        color: #333333 !important; /* Fuerza el color principal a oscuro */
    }
    
    /* Forzamos que cualquier párrafo o texto dentro del chat también sea oscuro */
    [data-testid="stChatMessage"] * {
        color: #333333 !important;
    }
    
    /* 4. Botones de acción en Verde Institucional */
    .stButton>button {
        background-color: #007934;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Efecto al pasar el mouse sobre los botones */
    .stButton>button:hover {
        background-color: #005A26;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 5. Cajas de texto (inputs) con bordes más suaves */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #CED4DA;
    }
    
    /* 6. VERDADERO BOTÓN FLOTANTE CIRCULAR */
    .btn-flotante {
        position: fixed;
        bottom: 90px;
        right: 20px;
        background-color: #D52B1E; /* Rojo Institucional */
        color: white !important;
        border-radius: 50%;
        width: 55px;
        height: 55px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 26px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        text-decoration: none;
        z-index: 9999;
        transition: transform 0.2s ease, background-color 0.2s ease;
    }
    
    .btn-flotante:hover {
        transform: scale(1.1);
        background-color: #A32016;
    }

    /* Ocultar el menú superior derecho de Streamlit (Share, GitHub, Menú) */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
    }

    /* Ocultar la marca de agua inferior de "Made with Streamlit" */
    footer {
        visibility: hidden !important;
    }
    /* Ocultar el menú de hamburguesa y las insignias flotantes de Streamlit */
    #MainMenu {visibility: hidden !important;}
    [data-testid="stViewerBadge"] {display: none !important;}
</style>

<a href="javascript:window.location.reload();" target="_self" class="btn-flotante" title="Reiniciar Chat">🔄</a>


</style>
""", unsafe_allow_html=True)
# ------------------------------------

# --- INTERFAZ ---
st.title("🇧🇴 Agente Tranca Cero")

st.markdown("Hola, soy tu agente virtual que te acompañará para encontrar el trámite o servicio que buscas. Pregúntame o cuéntame qué es lo que quieres hacer y te daré una orientación clara y concisa.")

# --- INICIALIZACIÓN DE MEMORIA Y AGENTE ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "agente" not in st.session_state:
    with st.spinner("Despertando al Agente Tranca Cero..."):
        st.session_state.agente = crear_agente()

pregunta_rapida = None
if len(st.session_state.mensajes) == 0:
    st.markdown("💡 **Puedes escribir tus preguntas abajo o elegir una opción rápida:**")
    col1, col2 = st.columns(2)
    if col1.button("🪪 ¿Cómo tramito mi Cédula de Identidad?"):
        pregunta_rapida = "¿Cómo tramito una Cédula de Identidad?"
    if col2.button("🏪 Requisitos para abrir un negocio"):
        pregunta_rapida = "Quiero abrir un negocio, ¿qué requisitos necesito?"
    st.markdown("---")

for i, mensaje in enumerate(st.session_state.mensajes):
    with st.chat_message(mensaje["rol"]):
        if mensaje["rol"] == "user":
            st.markdown(f"<span class='marca-ciudadano'></span> {mensaje['contenido']}", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='marca-agente'></span> {mensaje['contenido']}", unsafe_allow_html=True)
            valoracion = st.feedback("thumbs", key=f"feedback_{i}")
            if valoracion is not None:
                st.caption("¡Gracias por tu retroalimentación!" if valoracion == 1 else "Gracias por avisar. Tomaremos nota.")

pregunta_usuario = st.chat_input("Escribe tu duda o proyecto aquí...")
consulta_final = pregunta_usuario or pregunta_rapida

if consulta_final:
    with st.chat_message("user"):
        st.markdown(f"<span class='marca-ciudadano'></span> {consulta_final}", unsafe_allow_html=True)
    
    st.session_state.mensajes.append({"rol": "user", "contenido": consulta_final})

    with st.chat_message("assistant"):
        with st.spinner("Analizando tu caso en los reglamentos..."):
            if st.session_state.agente:
                # --- AJUSTE DE MEMORIA CORTA ---
                # 1. Agarramos solo los últimos 4 mensajes (2 tuyos y 2 del bot)
                ultimos_mensajes = st.session_state.mensajes[-4:]
                
                # 2. Los convertimos en texto simple (que es lo que tu bot espera)
                historial_corto = "\n".join([f"{m['rol']}: {m['contenido']}" for m in ultimos_mensajes])
                
                # 3. Llamamos al agente con esta memoria "limpia"
                respuesta = st.session_state.agente.invoke({
                    "question": consulta_final, 
                    "chat_history": historial_corto
                })
                # --- FIN DEL AJUSTE ---
            else:
                respuesta = "Aún no tengo documentos en mi base de datos."
            st.markdown(f"<span class='marca-agente'></span> {respuesta}", unsafe_allow_html=True)
            
    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})
    guardar_log(consulta_final, respuesta) # Mandamos llamar nuestra función de auditoria.py
    st.rerun()
