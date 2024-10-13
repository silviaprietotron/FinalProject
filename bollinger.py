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

# Función para calcular Bandas de Bollinger
def calculate_bollinger_bands(df, window=20, num_sd=2):
    df['rolling_mean'] = df['close'].rolling(window=window).mean()
    df['rolling_std'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['rolling_mean'] + (df['rolling_std'] * num_sd)
    df['lower_band'] = df['rolling_mean'] - (df['rolling_std'] * num_sd)

# Función para graficar datos de precios
def plot_data(df, selected_pair):
    fig, ax = plt.subplots(figsize=(20, 10))

    # Graficar la serie de tiempo de 'close'
    ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)

    # Ajustes visuales
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio de cierre (EUR)', fontsize=12)
    ax.set_title(f'Movimiento del par {selected_pair}', fontsize=16)

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

    return fig

# Función para graficar Bandas de Bollinger
def plot_bollinger_bands(df, selected_pair):
    fig_bb, ax_bb = plt.subplots(figsize=(20, 10))

    # Graficar el precio de cierre
    ax_bb.plot(df['time'], df['close'], label='Precio de Cierre', color='blue')
    
    # Graficar las Bandas de Bollinger
    ax_bb.plot(df['time'], df['upper_band'], label='Banda Superior', color='red', linestyle='--')
    ax_bb.plot(df['time'], df['lower_band'], label='Banda Inferior', color='green', linestyle='--')
    ax_bb.plot(df['time'], df['rolling_mean'], label='Media Móvil', color='orange')

    # Ajustes visuales
    ax_bb.set_xlabel('Fecha', fontsize=12)
    ax_bb.set_ylabel('Precio (EUR)', fontsize=12)
    ax_bb.set_title(f'Bandas de Bollinger para {selected_pair}', fontsize=16)
    ax_bb.grid(True)
    ax_bb.legend()

    return fig_bb

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

    # Graficar los datos de precios
    fig = plot_data(df, selected_pair)

    # Mostrar el gráfico de precios en Streamlit
    st.pyplot(fig)

    # Calcular las Bandas de Bollinger
    calculate_bollinger_bands(df)

    # Botón para mostrar Bandas de Bollinger
    if st.button("Mostrar Bandas de Bollinger"):
        fig_bb = plot_bollinger_bands(df, selected_pair)

        # Mostrar el gráfico de Bandas de Bollinger
        st.pyplot(fig_bb)
