import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===================== CONFIG =====================
st.set_page_config(
    page_title="Analisis Crudo Colombia",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    return pd.read_parquet("./data_processed/crudo_limpio.parquet")

df = load_data()

# ===================== MAPEO DE MESES (para evitar errores de fecha) =====================
meses_dict = {
    'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
    'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
    'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
}

# ===================== SIDEBAR =====================
st.sidebar.header("Filtros")
todos_los_años = sorted(df['AÑO'].unique())
año_default = [2022]

años = st.sidebar.multiselect(
    "Año (obligatorio)",
    options=todos_los_años,
    default=año_default,
    help="Selecciona uno o varios años."
)


if not años:
    años = [todos_los_años[-1]] 
    st.sidebar.warning("Debes seleccionar al menos un año.")
    st.error("Error: Debes seleccionar al menos un año para continuar.")


departamentos = st.sidebar.multiselect("Departamentos", options=df['DEPARTAMENTO'].unique())
operadoras = st.sidebar.multiselect("Operadoras", options=df['OPERADORA'].unique())




# Aplicar filtros
datos = df.copy()
if años: 
    datos = datos[datos['AÑO'].isin(años)]
if departamentos: 
    datos = datos[datos['DEPARTAMENTO'].isin(departamentos)]
if operadoras: 
    datos = datos[datos['OPERADORA'].isin(operadoras)]

total_barriles = datos['PRODUCCION'].sum()

# ===================== HEADER =====================
años_str = f"{min(años)}–{max(años)}" if len(años) > 1 else str(años[0])

st.title(f"Producción de Crudo en Colombia periodo: {años_str}")
st.markdown("Datos ANH • Producción mensual promedio")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Producción total en {años_str}",f"{total_barriles:,.0f}")
with col2:
    st.metric(f"Campos de produccion activos en {años_str}", datos['CAMPO'].nunique())
with col3:
    if años:
        # Contamos cuántos días reales hay en los años seleccionados
        dias_totales = 0
        for año in años:
            if año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
                dias_totales += 366
            else:
                dias_totales += 365
        
        if dias_totales > 0:
            promedio_diario = total_barriles // dias_totales
            años_str = f"{min(años)}–{max(años)}" if len(años) > 1 else str(años[0])
            st.metric(f"Promedio diario {años_str}", f"{promedio_diario:,.0f} bpd")
        else:
            st.metric("Promedio diario", "N/D")
    else:
        st.metric("Promedio diario", "N/D")


# ===================== PESTAÑAS =====================
tab1, tab2, tab3, tab4, tab5, tab6,tab7 = st.tabs(["Resumen", "Top Campos", "Departamentos", "Operadoras", "Declinación", "Mapa de calor","Predicciones"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        anual = datos.groupby('AÑO')['PRODUCCION'].sum().reset_index()
        fig = px.bar(anual, x='AÑO', y='PRODUCCION', title="Producción anual", text_auto='.3s')
        st.plotly_chart(fig, width='stretch')  

    with col2:
        
        temp = datos.copy()
        temp['MES_NUM'] = temp['MES'].map(meses_dict)
        temp['Fecha'] = pd.to_datetime(temp['AÑO'].astype(str) + '-' + temp['MES_NUM'])
        mensual = temp.groupby('Fecha')['PRODUCCION'].sum().reset_index()
        
        fig = px.line(mensual, x='Fecha', y='PRODUCCION', markers=True, title="Evolución mensual")
        st.plotly_chart(fig, width='stretch')  

with tab2:
    top_n = st.slider("Top campos", 5, 30, 15)
    top = (datos.groupby(['CAMPO','OPERADORA','DEPARTAMENTO'])['PRODUCCION']
           .sum().sort_values(ascending=False).head(top_n).reset_index())
    fig = px.bar(top, x='PRODUCCION', y='CAMPO', orientation='h',
                 color='OPERADORA', hover_data=['DEPARTAMENTO'],
                 title=f"Top {top_n} campos en {años_str}")
    fig.update_layout(
        height=600
    )
    st.plotly_chart(fig, width='stretch')

with tab3:
    depto = datos.groupby('DEPARTAMENTO')['PRODUCCION'].sum().sort_values(ascending=False)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(values=depto.values, names=depto.index, title=f"Participación por departamento en {años_str}")
        st.plotly_chart(fig, width='stretch')
    with col2:
        fig = px.bar(depto.reset_index(), x='DEPARTAMENTO', y='PRODUCCION')
        st.plotly_chart(fig, width='stretch')

with tab4:
    op = datos.groupby('OPERADORA')['PRODUCCION'].sum().nlargest(12)
    fig = px.treemap(op.reset_index(), path=['OPERADORA'], values='PRODUCCION',
                     title="Top 12 operadoras")
    st.plotly_chart(fig, width='stretch')

with tab5:
    campo = st.selectbox("Campo para declinación", options=sorted(datos['CAMPO'].unique()))
    decl = datos[datos['CAMPO']==campo].copy()
    decl['MES_NUM'] = decl['MES'].map(meses_dict)
    decl['Fecha'] = pd.to_datetime(decl['AÑO'].astype(str) + '-' + decl['MES_NUM'])
    decl_mensual = decl.groupby('Fecha')['PRODUCCION'].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=decl_mensual['Fecha'], y=decl_mensual['PRODUCCION'],
                             mode='lines+markers', line=dict(width=3)))
    fig.update_layout(title=f"Declinación – {campo}", xaxis_title="", yaxis_title="Barriles/mes")
    st.plotly_chart(fig, width='stretch')

with tab6:
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
   
        st.subheader("Producción de Crudo por Departamento – Mapa de Calor")
  

        # === 1. Todos los departamentos de Colombia===
        todos_deptos = [
            'AMAZONAS', 'ANTIOQUIA', 'ARAUCA', 'ATLANTICO', 'BOLIVAR', 'BOYACA', 'CALDAS','BOGOTA D.C.',
            'CAQUETA', 'CASANARE', 'CAUCA', 'CESAR', 'CHOCO', 'CORDOBA', 'CUNDINAMARCA',
            'GUAINIA', 'GUAVIARE', 'HUILA', 'LA GUAJIRA', 'MAGDALENA', 'META', 'NARIÑO',
            'NORTE DE SANTANDER', 'PUTUMAYO', 'QUINDIO', 'RISARALDA', 'SAN ANDRES Y PROVIDENCIA',
            'SANTANDER', 'SUCRE', 'TOLIMA', 'VALLE DEL CAUCA', 'VAUPES', 'VICHADA'
        ]

        # Producción por departamento 
        prod_depto = datos.groupby('DEPARTAMENTO')['PRODUCCION'].sum().reindex(todos_deptos, fill_value=0).reset_index()
        prod_depto.columns = ['DEPARTAMENTO', 'PRODUCCION']

        # === 2. GeoJSON oficial ===
        import requests
        import json

        # ONLINE
        geojson_colombia = requests.get(
            "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
        ).json()

        # === 3. Choropleth estilo 
        fig = px.choropleth_map( 
        prod_depto,
        geojson=geojson_colombia,
        locations='DEPARTAMENTO',
        featureidkey="properties.NOMBRE_DPT",
        color='PRODUCCION',

        color_continuous_scale='Blues',
        range_color=(0, prod_depto['PRODUCCION'].quantile(0.95)),
        map_style="white-bg", 
        zoom=4.4,
        center={"lat": 4.5709, "lon": -74.2973},
        opacity=0.8,
        labels={'PRODUCCION': 'Barriles totales'},
        hover_name='DEPARTAMENTO',
        hover_data={'PRODUCCION': ':,', 'DEPARTAMENTO': False}
    )

        fig.update_traces(
            marker_line_width=1.2,
            marker_line_color="black"
        )

        fig.update_layout(
            map_style="white-bg",
            mapbox_zoom=4.6,
            mapbox_center={"lat": 4.5709, "lon": -74.2973},
            margin={"r":0, "t":50, "l":0, "b":0},
            height=700,
            coloraxis_colorbar=dict(
                title="Barriles",
                tickformat=',',
                x=1,
                len=1
            )
        )
        st.plotly_chart(fig, width='content')

st.sidebar.success("Dashboard funcional")
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="Descargar datos filtrados (CSV)",
    data=datos.to_csv(index=False).encode(),
    file_name=f"crudo_filtrado_{pd.Timestamp('today').strftime('%Y%m%d')}.csv",
    mime="text/csv"
)


with tab7:
    st.markdown("## Predicciones y Análisis de Declinación (2013–2027)")
    pred_tab1, pred_tab2, pred_tab3 = st.tabs([
        "Producción Nacional", 
        "Declinación por Departamento", 
        "Campos que Declinarán Más Rápido"
    ])
    
    # ==============================================
    # 1. PRODUCCIÓN NACIONAL (2013–2027)
    # ==============================================
    with pred_tab1:
        st.subheader("Predicción Producción Nacional Colombia")

        # Datos históricos nacionales
        nacional_hist = df.groupby(['AÑO', 'MES'])['PRODUCCION'].sum().reset_index()
        nacional_hist['Fecha'] = pd.to_datetime(nacional_hist['AÑO'].astype(str) + '-' + nacional_hist['MES'].map(meses_dict))
        nacional_hist = nacional_hist.groupby('Fecha')['PRODUCCION'].sum().reset_index()
        nacional_hist = nacional_hist.rename(columns={'Fecha': 'ds', 'PRODUCCION': 'y'})

        from prophet import Prophet
        m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        m.fit(nacional_hist)

        futuro = m.make_future_dataframe(periods=60, freq='ME')  # 5 años más
        forecast = m.predict(futuro)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=nacional_hist['ds'], y=nacional_hist['y'], mode='markers', name='Histórico'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicción'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill=None, mode='lines', line_color='rgba(0,0,0,0)'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='lines', line_color='#B9EAEB', name='95% confianza'))
        fig.update_layout(title="Predicción Producción Nacional (2013–2027)", height=500)
        st.plotly_chart(fig, width='stretch')

        pred_2025 = forecast[forecast['ds'].dt.year == 2025]['yhat'].sum()
        st.metric("Predicción 2025", f"{pred_2025:,.0f} barriles", delta=f"{(pred_2025/nacional_hist['y'].sum()*10):+.1f}% vs histórico")

    # ==============================================
    # 2. DECLINACIÓN POR DEPARTAMENTO
    # ==============================================
    with pred_tab2:
        st.subheader("Declinación por Departamento (2013–2027)")

        depto_sel = st.selectbox("Departamento", options=sorted(df['DEPARTAMENTO'].unique()), key="depto_pred")

        depto_data = df[df['DEPARTAMENTO'] == depto_sel].copy()
        depto_mensual = depto_data.groupby(['AÑO', 'MES'])['PRODUCCION'].sum().reset_index()
        depto_mensual['Fecha'] = pd.to_datetime(depto_mensual['AÑO'].astype(str) + '-' + depto_mensual['MES'].map(meses_dict))
        depto_mensual = depto_mensual.groupby('Fecha')['PRODUCCION'].sum().reset_index()
        depto_mensual = depto_mensual.rename(columns={'Fecha': 'ds', 'PRODUCCION': 'y'})

        if len(depto_mensual) > 12:
            m = Prophet(yearly_seasonality=True)
            m.fit(depto_mensual)
            futuro = m.make_future_dataframe(periods=60, freq='ME')
            forecast = m.predict(futuro)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=depto_mensual['ds'], y=depto_mensual['y'], mode='lines+markers', name='Histórico'))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicción', line=dict(dash='dash')))
            fig.update_layout(title=f"Declinación – {depto_sel}", height=500)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Datos insuficientes para predecir este departamento.")

    # ==============================================
    # 3. CAMPOS QUE DECLINARÁN MÁS RÁPIDO
    # ==============================================
    with pred_tab3:
        st.subheader("Campos con Mayor Tasa de Declinación (2020–2022)")

        # Solo campos con datos recientes
        recientes = df[df['AÑO'] >= 2020].groupby('CAMPO')['PRODUCCION'].sum()
        campos_activos = recientes[recientes > 1000000].index  # al menos 1M barriles

        declinacion = []
        for campo in campos_activos:
            data = df[df['CAMPO'] == campo]
            if len(data['AÑO'].unique()) >= 3:
                prod_2020 = data[data['AÑO'] == 2020]['PRODUCCION'].sum()
                prod_2022 = data[data['AÑO'] == 2022]['PRODUCCION'].sum()
                if prod_2020 > 100000:  # evitar división por cero
                    tasa = (prod_2022 - prod_2020) / prod_2020 * 100
                    declinacion.append({'CAMPO': campo, 'Tasa': tasa, '2020': prod_2020, '2022': prod_2022})

  

st.sidebar.caption(f"Hecho con datos de ANH {años_str}")