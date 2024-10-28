import streamlit as st
import krakenex
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line
from PIL import Image
from streamlit_echarts import st_pyecharts

# Configuración de la API de Kraken
api = krakenex.API()

# Función para obtener datos OHLC
def obtener_datos_ohlc(par, intervalo=60):
    try:
        respuesta = api.query_public('OHLC', {'pair': par, 'interval': intervalo})
        return respuesta['result'][par]
    except Exception as e:
        st.error(f"Error al obtener datos de Kraken: {e}")
        return None

# Función para calcular Bandas de Bollinger
def calcular_bandas_bollinger(df, ventana=20, num_desviaciones=2):
    df_bollinger = df.copy()
    df_bollinger['media_móvil'] = df_bollinger['close'].rolling(window=ventana).mean()
    df_bollinger['desviación'] = df_bollinger['close'].rolling(window=ventana).std()
    df_bollinger['banda_superior'] = df_bollinger['media_móvil'] + (df_bollinger['desviación'] * num_desviaciones)
    df_bollinger['banda_inferior'] = df_bollinger['media_móvil'] - (df_bollinger['desviación'] * num_desviaciones)
    return df_bollinger

# Función para graficar precios
def graficar_precios(df, par_seleccionado):
    grafico = (
        Line(init_opts=opts.InitOpts(width="1000px", height="600px"))
        .add_xaxis(df['fecha'].dt.strftime("%Y-%m-%d %H:%M").tolist())
        .add_yaxis(f"Precio de cierre de {par_seleccionado}", df['close'].tolist(), is_smooth=True, label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Movimiento del par {par_seleccionado}"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(name="Precio de cierre (EUR)"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
        )
    )
    st_pyecharts(grafico)

# Función para graficar Bandas de Bollinger
def graficar_bandas_bollinger(df_bollinger, par_seleccionado):
    grafico_bb = (
        Line(init_opts=opts.InitOpts(width="1000px", height="600px"))
        .add_xaxis(df_bollinger['fecha'].dt.strftime("%Y-%m-%d %H:%M").tolist())
        .add_yaxis("Precio de cierre", df_bollinger['close'].tolist(), is_smooth=True, color="blue", label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("Banda Superior", df_bollinger['banda_superior'].tolist(), is_smooth=True, color="red", linestyle_opts=opts.LineStyleOpts(width=2, type_="dashed"))
        .add_yaxis("Banda Inferior", df_bollinger['banda_inferior'].tolist(), is_smooth=True, color="green", linestyle_opts=opts.LineStyleOpts(width=2, type_="dashed"))
        .add_yaxis("Media Móvil", df_bollinger['media_móvil'].tolist(), is_smooth=True, color="orange")
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Bandas de Bollinger para {par_seleccionado}"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(name="Precio (EUR)"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    st_pyecharts(grafico_bb)

    # Descripciones personalizadas a cada lado
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="color: red; font-weight: bold;">Banda Superior</div>
            <div style="color: green; font-weight: bold;">Banda Inferior</div>
            <div style="color: orange; font-weight: bold;">Media Móvil</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Título y logo
imagen = Image.open('logo_app.png')
st.image(imagen, width=200)
st.title("Visualización del Par de Monedas en Kraken")

# Descripción introductoria
st.markdown(
    """
    Bienvenido a la aplicación de visualización de criptomonedas. 
    Aquí puedes seleccionar un par de monedas para analizar su movimiento y ver indicadores técnicos 
    como las Bandas de Bollinger, que muestran volatilidad y posibles puntos de entrada y salida.
    """
)

# Obtener pares de monedas
try:
    respuesta_pares = api.query_public('AssetPairs')
    todos_pares = list(respuesta_pares['result'].keys())
except Exception as e:
    st.error(f"Error al obtener los pares de monedas: {e}")
    todos_pares = []

# Selección de par de monedas
par_seleccionado = st.selectbox("Selecciona el par de monedas:", todos_pares)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    datos_ohlc = obtener_datos_ohlc(par_seleccionado, intervalo=60)

    if datos_ohlc is not None:
        columnas = ['fecha', 'apertura', 'máximo', 'mínimo', 'cierre', 'vwap', 'volumen', 'conteo']
        df_precios = pd.DataFrame(datos_ohlc, columns=columnas)
        df_precios['fecha'] = pd.to_datetime(df_precios['fecha'], unit='s')

        st.session_state['df_precios'] = df_precios

        # Graficar precios
        graficar_precios(df_precios, par_seleccionado)

        # Calcular y guardar Bandas de Bollinger
        df_bollinger = calcular_bandas_bollinger(df_precios)
        st.session_state['df_bollinger'] = df_bollinger

# Botón para mostrar Bandas de Bollinger
if st.button("Mostrar Bandas de Bollinger"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        
        if df_bollinger['media_móvil'].notna().any():
            graficar_bandas_bollinger(df_bollinger, par_seleccionado)
        else:
            st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")



