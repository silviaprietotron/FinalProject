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
def get_ohlc_data(pair, interval=60):
    resp = api.query_public('OHLC', {'pair': pair, 'interval': interval})
    return resp['result'][pair]

# Función para graficar datos
def plot_data(df, selected_pair):
    fig, ax = plt.subplots(figsize=(20, 10))  # Ajusta el tamaño del gráfico

    # Graficar la serie de tiempo de 'close'
    ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)

    # Ajustes visuales
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio de cierre (EUR)', fontsize=12)
    ax.set_title(f'Movimiento del par {selected_pair}', fontsize=16)

    # Formato de fechas en el eje x
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Mostrar cada 5 días
    fig.autofmt_xdate()  # Rotar las fechas para mejor visibilidad

    # Formato de precios en el eje y
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'€{x:.2f}'))  # Formato de moneda

    # Añadir rejilla, leyenda y estilo
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)

    return fig

# Título de la aplicación y logo
image = Image.open('logo_app.png')
st.image(image, width=200)
st.title("Visualización del Par de Monedas en Kraken")

# Obtener todos los pares de criptomonedas
resp_pairs = api.query_public('AssetPairs')
all_pairs = list(resp_pairs['result'].keys())

# Input de usuario: selección de par de monedas
selected_pair = st.selectbox("Selecciona el par de monedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    # Descargar datos del par seleccionado con intervalo fijo de 60 segundos
    ohlc_data = get_ohlc_data(selected_pair, interval=60)

    # Convertir a DataFrame
    columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
    df = pd.DataFrame(ohlc_data, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Graficar los datos
    fig = plot_data(df, selected_pair)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

# Función para calcular Bandas de Bollinger
def bandas_bollinger(df, ventana=20, factor_std=2):
    df['Media Móvil'] = df['close'].rolling(window=ventana).mean()
    df['Banda Superior'] = df['Media Móvil'] + factor_std * df['close'].rolling(window=ventana).std()
    df['Banda Inferior'] = df['Media Móvil'] - factor_std * df['close'].rolling(window=ventana).std()
    return df

# Botón para mostrar Bandas de Bollinger
if st.button("Añadir Bandas de Bollinger"):
    df = bandas_bollinger(df)

    # Añadir las Bandas de Bollinger al gráfico existente
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)
    ax.plot(df['time'], df['Banda Superior'], label='Banda Superior', color='red', linestyle='--')
    ax.plot(df['time'], df['Banda Inferior'], label='Banda Inferior', color='green', linestyle='--')
    ax.fill_between(df['time'], df['Banda Inferior'], df['Banda Superior'], color='gray', alpha=0.2)

    # Ajustes visuales
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio de cierre (EUR)', fontsize=12)
    ax.set_title(f'Movimiento del par {selected_pair} con Bandas de Bollinger', fontsize=16)

    # Formato de fechas en el eje x
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    fig.autofmt_xdate()

    # Formato de precios en el eje y
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'€{x:.2f}'))

    # Añadir rejilla, leyenda y estilo
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)





