import streamlit as st
import krakenex
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from matplotlib.ticker import MaxNLocator

# Configurar la API de Kraken
api = krakenex.API()

# Función para obtener datos OHLC
def obtener_datos_ohlc(par, intervalo=60):
    try:
        resp = api.query_public('OHLC', {'pair': par, 'interval': intervalo})
        return resp['result'][par]
    except Exception as e:
        st.error(f"Error al obtener datos de Kraken: {e}")
        return None

# Función para calcular Bandas de Bollinger
def calcular_bandas_bollinger(df, ventana=20, num_sd=2):
    df_bollinger = df.copy()
    df_bollinger['media_movil'] = df_bollinger['cierre'].rolling(window=ventana).mean()
    df_bollinger['desviacion_estandar'] = df_bollinger['cierre'].rolling(window=ventana).std()
    df_bollinger['banda_superior'] = df_bollinger['media_movil'] + (df_bollinger['desviacion_estandar'] * num_sd)
    df_bollinger['banda_inferior'] = df_bollinger['media_movil'] - (df_bollinger['desviacion_estandar'] * num_sd)
    return df_bollinger

# Función para graficar datos de precios
def graficar_datos(df, par_seleccionado):
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(df['tiempo'], df['cierre'], label=f'Precio de cierre de {par_seleccionado}', color='blue', linewidth=2)
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio de cierre (EUR)', fontsize=12)
    ax.set_title(f'Movimiento del par {par_seleccionado}', fontsize=16)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    fig.autofmt_xdate()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'€{x:.2f}'))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)
    return fig

# Función para graficar Bandas de Bollinger
def graficar_bandas_bollinger(df_bollinger, par_seleccionado):
    df_bollinger['banda_inferior'] = pd.to_numeric(df_bollinger['banda_inferior'], errors='coerce')
    df_bollinger['cierre'] = pd.to_numeric(df_bollinger['cierre'], errors='coerce')
    df_bollinger = df_bollinger.dropna(subset=['banda_inferior', 'cierre'])
    fig_bb, ax_bb = plt.subplots(figsize=(20, 10))
    ax_bb.plot(df_bollinger['tiempo'], df_bollinger['cierre'], label='Precio de Cierre', color='blue')
    if 'banda_superior' in df_bollinger and 'banda_inferior' in df_bollinger:
        ax_bb.plot(df_bollinger['tiempo'], df_bollinger['banda_superior'], label='Banda Superior', color='red', linestyle='--')
        ax_bb.plot(df_bollinger['tiempo'], df_bollinger['banda_inferior'], label='Banda Inferior', color='green', linestyle='--')
        ax_bb.plot(df_bollinger['tiempo'], df_bollinger['media_movil'], label='Media Móvil', color='orange')
    ax_bb.set_ylim(min(df_bollinger['banda_inferior'].min(), df_bollinger['cierre'].min()) * 0.95,
                   max(df_bollinger['banda_superior'].max(), df_bollinger['cierre'].max()) * 1.05)
    ax_bb.set_xlabel('Fecha', fontsize=12)
    ax_bb.set_ylabel('Precio (EUR)', fontsize=12)
    ax_bb.set_title(f'Bandas de Bollinger para {par_seleccionado}', fontsize=16)
    ax_bb.grid(True)
    ax_bb.legend()
    return fig_bb

# Título, logo y texto introductorio de la aplicación
imagen = Image.open('logo_app.png')
st.image(imagen, width=200)
st.title("Visualización del Par de Monedas en Kraken")
st.write("Bienvenido a esta aplicación que te permite visualizar los precios de pares de monedas en Kraken. "
         "Podrás ver el movimiento de precios y calcular las Bandas de Bollinger, que ayudan a identificar "
         "posibles puntos de compra y venta.")

# Obtener todos los pares de criptomonedas
try:
    respuesta_pares = api.query_public('AssetPairs')
    todos_pares = list(respuesta_pares['result'].keys())
except Exception as e:
    st.error(f"Error al obtener los pares de monedas: {e}")
    todos_pares = []

# Input de usuario: selección de par de monedas
par_seleccionado = st.selectbox("Selecciona el par de monedas:", todos_pares)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    datos_ohlc = obtener_datos_ohlc(par_seleccionado, intervalo=60)
    if datos_ohlc is not None:
        columnas = ['tiempo', 'apertura', 'alto', 'bajo', 'cierre', 'vwap', 'volumen', 'conteo']
        df_precios = pd.DataFrame(datos_ohlc, columns=columnas)
        df_precios['tiempo'] = pd.to_datetime(df_precios['tiempo'], unit='s')
        st.session_state['df_precios'] = df_precios
        fig = graficar_datos(df_precios, par_seleccionado)
        st.pyplot(fig)
        df_bollinger = calcular_bandas_bollinger(df_precios)
        st.session_state['df_bollinger'] = df_bollinger

# Mostrar las Bandas de Bollinger al presionar el botón
if st.button("Mostrar Bandas de Bollinger"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        if df_bollinger['media_movil'].notna().any():
            fig_bb = graficar_bandas_bollinger(df_bollinger, par_seleccionado)
            st.pyplot(fig_bb)
        else:
            st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")
