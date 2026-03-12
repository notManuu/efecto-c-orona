import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random

# --- CONFIGURACIÓN DEL MÓDULO ---
st.set_page_config(page_title="Módulo Interactivo: Régimen Pulsado", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Módulo Interactivo: Análisis de Pulsos Corona y Ruptura")
st.markdown("Ajuste la tensión aplicada y observe el comportamiento de la corriente de fuga en el dominio de los nanosegundos. Identifique los pulsos de Trichel (-) y los Streamers (+).")

# --- PANEL DE CONTROL ---
st.sidebar.header("🎛️ Tablero de Control")

# Condiciones Estándar (IEEE Std. 4-2013)
st.sidebar.subheader("Condiciones Atmosféricas (Estándar)")
st.sidebar.write("Temperatura: $20 ^\circ C$")
st.sidebar.write("Presión: $101.3 kPa$ ($1 atm$)")

st.sidebar.markdown("---")
distancia = st.sidebar.slider("Separación entre electrodos d (cm)", 1.0, 15.0, 5.0, 0.5)
polaridad = st.sidebar.radio("Polaridad de la Fuente", ["Positiva (+)", "Negativa (-)"])

# Ajuste dinámico del slider de tensión dependiendo de la distancia
tension_maxima = int(550 * (distancia / 100)) + 20
tension_aplicada = st.sidebar.slider("Tensión Aplicada (kV)", 0, tension_maxima, 0, 1)

# --- CÁLCULOS FÍSICOS (Práctica 6) ---
# U50 = 500d para polaridad positiva, U50 = 455d para polaridad negativa (d en metros)
d_metros = distancia / 100.0

if polaridad == "Positiva (+)":
    u_50 = 500.0 * d_metros
    tension_corona = u_50 * 0.70  # Los streamers inician aprox al 70% de U50
else:
    u_50 = 455.0 * d_metros
    tension_corona = u_50 * 0.65  # Los pulsos de Trichel inician a menor tensión relativa

# --- DASHBOARD DUAL ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🔬 Cámara de Descarga (Punta-Plano)")
    
    fig_cam = go.Figure()
    
    # Dibujar electrodos
    # Punta (Arriba)
    fig_cam.add_trace(go.Scatter(x=[-2, 0, 2], y=[15, distancia, 15], fill="toself", fillcolor="#b5a642", line=dict(color="#8a7d30"), hoverinfo="none"))
    # Plano (Abajo)
    fig_cam.add_trace(go.Scatter(x=[-15, 15], y=[0, 0], mode="lines", line=dict(color="#a0aec0", width=8), hoverinfo="none"))
    
    # Lógica Visual de la Descarga
    if tension_aplicada >= u_50:
        st.error(f"💥 ¡RUPTURA! El aire perdió rigidez dieléctrica a {tension_aplicada} kV.")
        # Generar rayo
        pts_y = np.linspace(distancia, 0, 10)
        pts_x = [0] + [random.uniform(-1.5, 1.5) for _ in range(8)] + [0]
        fig_cam.add_trace(go.Scatter(x=pts_x, y=pts_y, mode="lines", line=dict(color="#ffffff", width=4)))
        fig_cam.add_trace(go.Scatter(x=pts_x, y=pts_y, mode="lines", line=dict(color="#00ffff", width=12), opacity=0.4))
    elif tension_aplicada >= tension_corona:
        tipo_pulso = "Streamers" if polaridad == "Positiva (+)" else "Pulsos de Trichel"
        st.warning(f"⚡ EFECTO CORONA ACTIVO. Generando {tipo_pulso}.")
        # Halo de corona en la punta
        color_halo = "purple" if polaridad == "Positiva (+)" else "blue"
        fig_cam.add_trace(go.Scatter(x=[0], y=[distancia - 0.5], mode="markers", marker=dict(size=40, color=color_halo, opacity=0.3)))
    else:
        st.success("✅ ESTABLE. Tensión soportada por el aislamiento.")

    fig_cam.update_layout(xaxis=dict(range=[-15, 15], visible=False), yaxis=dict(range=[-2, 17], visible=False), template="plotly_dark", height=450, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_cam, use_container_width=True)

with col2:
    st.subheader("📈 Osciloscopio: Corriente Transitoria I (mA)")
    
    # Simulación de la forma de onda en nanosegundos (doble exponencial)
    t_ns = np.linspace(0, 300, 400)
    corriente_mA = np.zeros_like(t_ns)
    
    if tension_aplicada >= u_50:
        # Falla total (corriente se dispara fuera de escala)
        corriente_mA = 500 * (1 - np.exp(-t_ns/10)) 
    elif tension_aplicada >= tension_corona:
        if polaridad == "Positiva (+)":
            # Pulso Streamer: Pico ~45mA, duración ~250ns
            # I(t) = A * (exp(-t/t1) - exp(-t/t2))
            A = 110.0
            corriente_mA = A * (np.exp(-t_ns/90.0) - np.exp(-t_ns/30.0))
        else:
            # Pulso Trichel: Pico ~-15mA, duración ~100ns
            A = -40.0
            corriente_mA = A * (np.exp(-t_ns/25.0) - np.exp(-t_ns/10.0))

    fig_osc = go.Figure()
    
    # Eje de referencia en 0
    fig_osc.add_hline(y=0, line_color="gray", line_width=1)
    
    # Trazar el pulso
    color_trazo = "#ef4444" if tension_aplicada >= u_50 else ("#10b981" if tension_aplicada == 0 else "#3b82f6")
    fig_osc.add_trace(go.Scatter(x=t_ns, y=corriente_mA, mode="lines", line=dict(color=color_trazo, width=3)))
    
    # Ajuste de escala para que se parezca a la imagen original
    rango_y = [-30, 60] if tension_aplicada < u_50 else [-30, 100]
    
    fig_osc.update_layout(
        xaxis_title="Tiempo t (ns)", 
        yaxis_title="Corriente I (mA)", 
        yaxis=dict(range=rango_y),
        template="plotly_dark", 
        height=450, 
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig_osc, use_container_width=True)