
import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Operativo ClimaSur", layout="wide")

@st.cache_data
def load_and_process_data():
    # Carga de archivos (asegúrate de que los CSV estén en la misma carpeta)
    path_muestras = '../muestras/'
       
    df_inter = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_intervenciones.csv'))
    df_horas = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_intervenciones_horas.csv'))
    df_mat = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_intervenciones_materiales.csv'))
    df_desp = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_desplazamientos.csv'))


    # Procesamiento de costes y ventas
    coste_h = df_horas.groupby('COD_INCIDENCIA')[['COSTE', 'VENTA']].sum()
    
    df_mat['total_c'] = df_mat['UNIDADES'] * df_mat['PRECIO_COSTE']
    df_mat['total_v'] = df_mat['UNIDADES'] * df_mat['PRECIO_VENTA']
    coste_m = df_mat.groupby('COD_INCIDENCIA')[['total_c', 'total_v']].sum()
    
    coste_d = df_desp.groupby('COD_INCIDENCIA')[['PRECIO_COSTE', 'PRECIO_VENTA']].sum()

    # Consolidación en un solo DataFrame
    df = df_inter[['COD_INCIDENCIA', 'ESTADO', 'PROVINCIA_SEDE', 'DEPARTAMENTO', 'CLIENTE']].copy()
    df = df.merge(coste_h, on='COD_INCIDENCIA', how='left')
    df = df.merge(coste_m, on='COD_INCIDENCIA', how='left')
    df = df.merge(coste_d, on='COD_INCIDENCIA', how='left').fillna(0)

    # Cálculo de Totales y Margen
    df['Coste_Total'] = df['COSTE'] + df['total_c'] + df['PRECIO_COSTE_y'] if 'PRECIO_COSTE_y' in df else df['COSTE'] + df['total_c'] + df['PRECIO_COSTE']
    df['Venta_Total'] = df['VENTA'] + df['total_v'] + df['PRECIO_VENTA_y'] if 'PRECIO_VENTA_y' in df else df['VENTA'] + df['total_v'] + df['PRECIO_VENTA']
    df['Margen'] = df['Venta_Total'] - df['Coste_Total']
    
    return df

df_master = load_and_process_data()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Operación")

# Filtro por Provincia
provincias = ["Todas"] + sorted(df_master['PROVINCIA_SEDE'].unique().tolist())
prov_sel = st.sidebar.selectbox("Selecciona Provincia", provincias)

# Filtro por Estado
estados = ["Todos"] + sorted(df_master['ESTADO'].unique().tolist())
estado_sel = st.sidebar.multiselect("Filtrar por Estado", estados, default="Todos")

# Aplicar Filtros
df_filtered = df_master.copy()
if prov_sel != "Todas":
    df_filtered = df_filtered[df_filtered['PROVINCIA_SEDE'] == prov_sel]

if "Todos" not in estado_sel and len(estado_sel) > 0:
    df_filtered = df_filtered[df_filtered['ESTADO'].isin(estado_sel)]

# --- CUERPO PRINCIPAL ---
st.title("📊 ClimaSur: Análisis de Rentabilidad")

# Métricas destacadas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Incidencias", len(df_filtered))
m2.metric("Facturación", f"{df_filtered['Venta_Total'].sum():,.2f} €")
m3.metric("Margen Neto", f"{df_filtered['Margen'].sum():,.2f} €")
m4.metric("Margen %", f"{(df_filtered['Margen'].sum()/df_filtered['Venta_Total'].sum()*100 if df_filtered['Venta_Total'].sum() > 0 else 0):.1f}%")

st.divider()

# Gráficos Dinámicos
c1, c2 = st.columns(2)

with c1:
    st.subheader("Rentabilidad por Cliente (Top 10)")
    top_clientes = df_filtered.groupby('CLIENTE')['Margen'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(top_clientes, x='Margen', y='CLIENTE', orientation='h', 
                     color='Margen', color_continuous_scale='Greens')
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("Distribución de Estados")
    fig_pie = px.pie(df_filtered, names='ESTADO', hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)

# Alerta de Anomalías
st.subheader("Detección de Anomalías (Margen Negativo o Cero)")
anomalias = df_filtered[df_filtered['Margen'] <= 0][['COD_INCIDENCIA', 'CLIENTE', 'ESTADO', 'Coste_Total', 'Venta_Total', 'Margen']]
if not anomalias.empty:
    st.warning(f"Se han detectado {len(anomalias)} intervenciones con rentabilidad nula o negativa.")
    st.dataframe(anomalias.style.highlight_min(axis=0, subset=['Margen'], color='#ffcccc'), use_container_width=True)
else:
    st.success("No se detectan anomalías financieras en la selección actual.")