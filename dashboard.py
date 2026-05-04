import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(layout="wide", page_title="Dashboard Solidaridad")

# Colores institucionales (Basado en imagen 5)
COLOR_PALMA = "#55A630" # Verde
COLOR_CAFE = "#2B3A67"  # Azul oscuro
COLOR_CACAO = "#A68A20" # Dorado/Café
COLOR_GENERIC = "#55A630" # Verde para barras generales

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    file_name = "Base_final.xlsx"
    if not os.path.exists(file_name):
        st.error("Archivo Base_final.xlsx no encontrado.")
        st.stop()
    df = pd.read_excel(file_name)
    # Limpieza numérica de seguridad
    df['area_ha'] = pd.to_numeric(df['area_ha'], errors='coerce')
    df['ingresos_anuales_cop'] = pd.to_numeric(df['ingresos_anuales_cop'], errors='coerce')
    df['produccion_kg'] = pd.to_numeric(df['produccion_kg'], errors='coerce')
    return df

df = load_data()

# TÍTULO PRINCIPAL (Basado en imagen 5)
st.markdown("<h1 style='text-align: center; color: #0072CE;'>🌱 Dashboard Estratégico: Programa de Productores Aliados</h1>", unsafe_allow_html=True)

# 3. FILTROS LATERALES
st.sidebar.header("Filtros de Análisis")
deptos = st.sidebar.multiselect("Filtrar por Departamento", options=sorted(df['departamento'].unique()), default=sorted(df['departamento'].unique()))
df_filt = df[df['departamento'].isin(deptos)]

# 4. KPIs SUPERIORES (Métricas según imagen 5)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total Productores", len(df_filt))
with kpi2:
    total_ha = df_filt['area_ha'].sum()
    st.metric("Total Hectáreas", f"{total_ha/1000:,.2f} mil".replace(",", "."))
with kpi3:
    st.metric("Total Departamentos", df_filt['departamento'].nunique())
with kpi4:
    st.metric("Total Municipios", df_filt['municipio'].nunique())

st.markdown("---")

# 5. BLOQUE DE MAPA (Punto 1.3 Análisis Territorial)
st.subheader("📍 Análisis Territorial y Localización")
fig_map = px.scatter_mapbox(
    df_filt.dropna(subset=['latitud', 'longitud']), 
    lat="latitud", 
    lon="longitud", 
    size="area_ha", 
    color="cadena_productiva",
    color_discrete_map={"Cafe": COLOR_CAFE, "Palma De Aceite": COLOR_PALMA, "Cacao": COLOR_CACAO},
    hover_name="nombre_completo",
    zoom=4.5, 
    height=500
)
fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# 6. FILA DE BARRAS (Productividad e Ingresos según imagen 5)
col_bar1, col_bar2 = st.columns(2)

with col_bar1:
    st.subheader("Productividad por cadena_productiva")
    prod_cadena = df_filt.groupby('cadena_productiva')['area_ha'].sum().reset_index()
    fig_h = px.bar(prod_cadena, y='cadena_productiva', x='area_ha', orientation='h',
                   color_discrete_sequence=[COLOR_GENERIC])
    fig_h.update_layout(xaxis_title="", yaxis_title="", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_h, use_container_width=True)

with col_bar2:
    st.subheader("Promedio de ingresos_anuales_cop por estado_certificacion")
    ing_cert = df_filt.groupby('estado_certificacion')['ingresos_anuales_cop'].mean().reset_index()
    fig_v = px.bar(ing_cert, x='estado_certificacion', y='ingresos_anuales_cop',
                   color_discrete_sequence=[COLOR_GENERIC])
    fig_v.update_layout(xaxis_title="", yaxis_title="", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_v, use_container_width=True)

# 7. FILA DE TORTAS (Distribución % según imagen 5)
col_pie1, col_pie2 = st.columns(2)
color_map = {"Cafe": COLOR_CAFE, "Palma De Aceite": COLOR_PALMA, "Cacao": COLOR_CACAO}

with col_pie1:
    st.subheader("% Hectáreas por cadena productiva")
    fig_p1 = px.pie(df_filt, values='area_ha', names='cadena_productiva',
                    color='cadena_productiva', color_discrete_map=color_map)
    fig_p1.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_p1, use_container_width=True)

with col_pie2:
    st.subheader("% Productores por cadena productiva")
    fig_p2 = px.pie(df_filt, names='cadena_productiva',
                    color='cadena_productiva', color_discrete_map=color_map)
    fig_p2.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_p2, use_container_width=True)

# 8. TABLA RESUMEN POR DEPARTAMENTO (Según tabla en imagen 5)
st.markdown("### Resumen Detallado por Departamento")
tabla = df_filt.groupby('departamento').agg(
    Total_Productores=('productor_id', 'count'),
    Total_Hectareas=('area_ha', 'sum'),
    Promedio_Area_Ha=('area_ha', 'mean')
).reset_index()

total_p = tabla['Total_Productores'].sum()
tabla['% Productores'] = (tabla['Total_Productores'] / total_p * 100).round(2)

st.table(tabla.style.format({
    'Total_Hectareas': '{:,.2f}',
    'Promedio_Area_Ha': '{:,.2f}',
    '% Productores': '{:.2f}%'
}))