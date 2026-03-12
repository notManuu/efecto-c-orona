import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random

# --- CONFIGURACIÓN GLOBAL ---
st.set_page_config(page_title="Simulador de Altas Tensiones", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/IPN_logo.svg/1200px-IPN_logo.svg.png", width=100) # Un toque institucional
st.sidebar.title("Navegación")
modulo_seleccionado = st.sidebar.radio(
    "Seleccione el módulo de simulación:",
    ["1. Fundamentos (Microescala)", "2. Torre Híbrida (Macroescala)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Condiciones Ambientales")
# Presión fijada por defecto para la altitud de la CDMX
presion = st.sidebar.slider("Presión Atmosférica (bar)", 0.5, 1.2, 0.78, help="A menor presión, menor rigidez dieléctrica.")
factor_presion = presion / 1.013

# ==========================================
# MÓDULO 1: FUNDAMENTOS FÍSICOS
# ==========================================
if modulo_seleccionado == "1. Fundamentos (Microescala)":
    st.title("🔬 Módulo 1: Fundamentos del Efecto Corona")
    
    with st.expander("📖 ¿Para qué sirve esta sección? (Instrucciones)", expanded=True):
        st.write("""
        **Objetivo:** Comprender cómo se comporta el aire ante un campo eléctrico no uniforme antes de llegar a la ruptura total.
        * **Paso 1:** Ajuste la distancia entre los electrodos.
        * **Paso 2:** Seleccione la polaridad (Positiva genera Streamers, Negativa genera pulsos de Trichel).
        * **Paso 3:** Suba la tensión lentamente. Observe cómo se ilumina la punta y cómo aparece el pulso en el osciloscopio de nanosegundos.
        """)

    col_ctrl, col_cam, col_osc = st.columns([1, 1.5, 1.5])
    
    with col_ctrl:
        st.subheader("Controles")
        distancia = st.slider("Separación (cm)", 1.0, 15.0, 5.0, 0.5)
        polaridad = st.radio("Polaridad", ["Positiva (+)", "Negativa (-)"])
        
        d_metros = distancia / 100.0
        u_50 = (500.0 if polaridad == "Positiva (+)" else 455.0) * d_metros * factor_presion
        t_corona = u_50 * (0.70 if polaridad == "Positiva (+)" else 0.65)
        
        t_max = int(550 * (15.0 / 100.0)) + 20
        tension = st.slider("Tensión Aplicada (kV)", 0, t_max, 0, 1)

    with col_cam:
        st.subheader("Cámara (Vista Física)")
        fig_cam = go.Figure()
        fig_cam.add_trace(go.Scatter(x=[-2, 0, 2], y=[15, distancia, 15], fill="toself", fillcolor="#b5a642", line=dict(color="#8a7d30"), hoverinfo="none", name="Punta"))
        fig_cam.add_trace(go.Scatter(x=[-15, 15], y=[0, 0], mode="lines", line=dict(color="#a0aec0", width=8), hoverinfo="none", name="Tierra"))
        
        if tension >= u_50:
            st.error("💥 RUPTURA DIELÉCTRICA")
            pts_y = np.linspace(distancia, 0, 10)
            pts_x = [0] + [random.uniform(-1.5, 1.5) for _ in range(8)] + [0]
            fig_cam.add_trace(go.Scatter(x=pts_x, y=pts_y, mode="lines", line=dict(color="#ffffff", width=4)))
            fig_cam.add_trace(go.Scatter(x=pts_x, y=pts_y, mode="lines", line=dict(color="#00ffff", width=12), opacity=0.4))
        elif tension >= t_corona:
            st.warning("⚡ EFECTO CORONA")
            color_halo = "purple" if polaridad == "Positiva (+)" else "blue"
            fig_cam.add_trace(go.Scatter(x=[0], y=[distancia - 0.5], mode="markers", marker=dict(size=60, color=color_halo, opacity=0.4)))
        else:
            st.success("✅ AISLAMIENTO ESTABLE")

        fig_cam.update_layout(xaxis=dict(range=[-15, 15], visible=False), yaxis=dict(range=[-2, 17], visible=False), template="plotly_dark", height=350, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_cam, use_container_width=True)

    with col_osc:
        st.subheader("Osciloscopio (Nanosegundos)")
        t_ns = np.linspace(0, 300, 400)
        i_ma = np.zeros_like(t_ns)
        
        if tension >= u_50:
            i_ma = 500 * (1 - np.exp(-t_ns/10)) 
        elif tension >= t_corona:
            if polaridad == "Positiva (+)":
                i_ma = 110.0 * (np.exp(-t_ns/90.0) - np.exp(-t_ns/30.0))
            else:
                i_ma = -40.0 * (np.exp(-t_ns/25.0) - np.exp(-t_ns/10.0))

        fig_osc = go.Figure()
        fig_osc.add_hline(y=0, line_color="gray", line_width=1)
        color_trazo = "#ef4444" if tension >= u_50 else ("#10b981" if tension == 0 else "#3b82f6")
        fig_osc.add_trace(go.Scatter(x=t_ns, y=i_ma, mode="lines", line=dict(color=color_trazo, width=3), fill='tozeroy', fillcolor=f"rgba({59 if color_trazo=='#3b82f6' else 239}, {130 if color_trazo=='#3b82f6' else 68}, {246 if color_trazo=='#3b82f6' else 68}, 0.2)"))
        
        rango_y = [-30, 60] if tension < u_50 else [-30, 100]
        fig_osc.update_layout(xaxis_title="Tiempo t (ns)", yaxis_title="Corriente I (mA)", yaxis=dict(range=rango_y), template="plotly_dark", height=350, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_osc, use_container_width=True)

# ==========================================
# MÓDULO 2: TORRE HÍBRIDA
# ==========================================
elif modulo_seleccionado == "2. Torre Híbrida (Macroescala)":
    st.title("🌐 Módulo 2: Interacción en Torres Híbridas")
    
    with st.expander("📖 ¿Para qué sirve esta sección? (Instrucciones)", expanded=True):
        st.write("""
        **Objetivo:** Visualizar cómo la carga espacial de una línea de CD afecta el aislamiento de una línea de CA vecina.
        * **Paso 1:** Mantenga la "Carga Espacial CD" en 0 kV para ver el funcionamiento normal.
        * **Paso 2:** Deslice lentamente la perilla de "Carga Espacial CD". Observe cómo los iones (puntos rojos/azules) migran en la torre.
        * **Paso 3:** En la gráfica derecha, note cómo la onda verde es empujada hacia la línea crítica roja. Al cruzarla, se desata el ruido electromagnético.
        """)

    col_ctrl2, col_torre, col_graf2 = st.columns([1, 1.5, 1.5])
    
    limite_corona_torre = 350 * factor_presion

    with col_ctrl2:
        st.subheader("Controles del Sistema")
        v_ac_pico = st.slider("Amplitud CA (kV Pico)", 0, 500, 200, 10)
        v_dc_offset = st.slider("Carga Espacial CD (kV)", -400, 400, 0, 10)
        
        estres_max_torre = abs(v_dc_offset) + v_ac_pico
        en_corona_torre = estres_max_torre >= limite_corona_torre
        
        st.markdown("---")
        if en_corona_torre:
            st.error(f"⚠️ RUIDO DETECTADO\nEstrés: {estres_max_torre} kV")
        else:
            st.success(f"✅ SISTEMA LIMPIO\nEstrés: {estres_max_torre} kV")

    with col_torre:
        st.subheader("Estructura Física")
        fig_torre = go.Figure()
        
        fig_torre.add_trace(go.Scatter(x=[-20, 20], y=[0, 0], mode="lines", line=dict(color="#4ade80", width=4), hoverinfo="none", showlegend=False))
        fig_torre.add_trace(go.Scatter(x=[0, 0], y=[0, 35], mode="lines", line=dict(color="#94a3b8", width=6), hoverinfo="none", showlegend=False))
        fig_torre.add_trace(go.Scatter(x=[-12, 12], y=[30, 30], mode="lines", line=dict(color="#94a3b8", width=6), hoverinfo="none", showlegend=False))
        
        fig_torre.add_trace(go.Scatter(x=[-10, -10], y=[30, 20], mode="lines+markers", marker=dict(symbol="line-ew", size=10), line=dict(color="#cbd5e1", width=3), name="Aislador CA"))
        fig_torre.add_trace(go.Scatter(x=[10, 10], y=[30, 20], mode="lines+markers", marker=dict(symbol="line-ew", size=10), line=dict(color="#cbd5e1", width=3), name="Aislador CD"))
        
        fig_torre.add_trace(go.Scatter(x=[-10], y=[19], mode="markers", marker=dict(size=15, color="#3b82f6"), name="Línea CA"))
        fig_torre.add_trace(go.Scatter(x=[10], y=[19], mode="markers", marker=dict(size=15, color="#ef4444"), name="Línea CD"))

        if abs(v_dc_offset) > 10:
            num_iones = int(abs(v_dc_offset) / 10)
            x_iones = [random.uniform(-8, 10) for _ in range(num_iones)]
            y_iones = [random.uniform(17, 21) for _ in range(num_iones)]
            color_ion = "#ef4444" if v_dc_offset > 0 else "#3b82f6"
            fig_torre.add_trace(go.Scatter(x=x_iones, y=y_iones, mode="markers", marker=dict(size=4, color=color_ion, opacity=0.5), name="Migración Iónica"))

        if en_corona_torre:
            fig_torre.add_trace(go.Scatter(x=[-10], y=[19], mode="markers", marker=dict(size=70, color="purple", opacity=0.4), name="Corona (Halo)", hoverinfo="none"))

        fig_torre.update_layout(xaxis=dict(range=[-20, 20], visible=False), yaxis=dict(range=[-2, 40], visible=False), template="plotly_dark", height=350, margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig_torre, use_container_width=True)

    with col_graf2:
        st.subheader("Dinámica del Gradiente (60 Hz)")
        t_ms = np.linspace(0, 33, 1000)
        onda_ca_pura = v_ac_pico * np.sin(2 * np.pi * 60 * (t_ms / 1000.0))
        onda_hibrida = onda_ca_pura + v_dc_offset
        
        fig_graf = go.Figure()
        
        fig_graf.add_hline(y=limite_corona_torre, line_dash="dash", line_color="red", annotation_text="Umbral Incepción")
        fig_graf.add_hline(y=-limite_corona_torre, line_dash="dash", line_color="red")
        
        fig_graf.add_trace(go.Scatter(x=t_ms, y=onda_ca_pura, mode="lines", name="Campo CA Original", line=dict(color="gray", dash="dot")))
        fig_graf.add_trace(go.Scatter(x=t_ms, y=onda_hibrida, mode="lines", name="Campo Híbrido", line=dict(color="#10b981", width=3)))
        
        if en_corona_torre:
            ruido = np.zeros_like(t_ms)
            for i in range(len(t_ms)):
                if onda_hibrida[i] >= limite_corona_torre:
                    if i % 6 == 0: ruido[i] = random.uniform(20, 90)
                elif onda_hibrida[i] <= -limite_corona_torre:
                    if i % 3 == 0: ruido[i] = random.uniform(-40, -10)
            
            fig_graf.add_trace(go.Scatter(x=t_ms, y=onda_hibrida + ruido, mode="lines", name="Ruido (Interferencia)", line=dict(color="#f97316", width=1.5)))
            fig_graf.add_trace(go.Scatter(x=t_ms, y=np.where(abs(onda_hibrida) > limite_corona_torre, onda_hibrida, None), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)', name="Zona Activa", mode='none'))

        fig_graf.update_layout(xaxis_title="Tiempo (ms)", yaxis_title="Tensión Efectiva (kV)", template="plotly_dark", height=350, margin=dict(l=0, r=0, t=0, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig_graf, use_container_width=True)
