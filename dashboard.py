import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard Solidaridad - Análisis 2026",
    page_icon="🌱",
    layout="wide"
)

# Estilo para el título
st.markdown("""
    <style>
    .main-title { font-size:36px !important; font-weight: bold; color: #0072CE; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🌱 Dashboard Estratégico: Programa de Productores Aliados</p>', unsafe_allow_html=True)
st.markdown("---")

# 2. CONEXIÓN CON EL EXCEL (Ruta Relativa para GitHub)
@st.cache_data
def load_data():
    # Buscamos el archivo en la misma carpeta del script
    file_name = "Base_final.xlsx"
    
    if not os.path.exists(file_name):
        st.error(f"No se encontró el archivo {file_name} en el repositorio.")
        st.stop()
        
    df = pd.read_excel(file_name)
    
    # Limpieza y conversión de datos para asegurar el funcionamiento
    df['area_ha'] = pd.to_numeric(df['area_ha'], errors='coerce')
    df['produccion_kg'] = pd.to_numeric(df['produccion_kg'], errors='coerce')
    
    # Retornamos solo registros con coordenadas para el mapa
    return df.dropna(subset=['latitud', 'longitud', 'area_ha'])

try:
    df = load_data()
except Exception as e:
    st.error(f"Error técnico al procesar la base: {e}")
    st.stop()

# 3. FILTROS LATERALES
st.sidebar.header("⚙️ Filtros de Análisis")

departamentos = st.sidebar.multiselect(
    "Seleccione Departamentos:",
    options=sorted(df['departamento'].unique()),
    default=sorted(df['departamento'].unique())
)

cultivos = st.sidebar.multiselect(
    "Cadena Productiva:",
    options=df['cadena_productiva'].unique(),
    default=df['cadena_productiva'].unique()
)

# Aplicar filtros
df_filt = df[(df['departamento'].isin(departamentos)) & (df['cadena_productiva'].isin(cultivos))]

# 4. INDICADORES CLAVE (KPIs)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Productores", f"{len(df_filt)}")
m2.metric("Total Hectáreas", f"{df_filt['area_ha'].sum():,.1f} ha")
m3.metric("Producción (Ton)", f"{df_filt['produccion_kg'].sum()/1000:,.1f}")
m4.metric("Ingreso Promedio", f"${df_filt['ingresos_anuales_cop'].mean():,.0f}")

st.markdown("---")

# 5. MAPA TERRITORIAL
st.subheader("📍 Análisis Territorial: Distribución y Escala")
fig_map = px.scatter_mapbox(
    df_filt, 
    lat="latitud", 
    lon="longitud", 
    size="area_ha", 
    color="cadena_productiva",
    hover_name="nombre_completo",
    hover_data=["municipio", "estado_certificacion"],
    zoom=5, 
    height=600
)
fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# 6. GRÁFICOS SECUNDARIOS
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Producción por Departamento")
    fig_prod = px.bar(
        df_filt.groupby('departamento')['produccion_kg'].sum().reset_index(),
        x='departamento', 
        y='produccion_kg',
        color_discrete_sequence=['#0072CE']
    )
    st.plotly_chart(fig_prod, use_container_width=True)

with c2:
    st.subheader("🛡️ Estado de Certificación")
    fig_pie = px.pie(df_filt, names='estado_certificacion', hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)

st.caption("Dashboard generado para la Prueba Técnica - Solidaridad Network Colombia.")