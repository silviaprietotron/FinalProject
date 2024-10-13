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
def calculate_bollinger_bands(df, window=20):
    df['SMA'] = df['close'].rolling(window=window).mean()  # Media móvil simple
    df['STD'] = df['close'].rolling(window=window).std()   # Desviación estándar
    df['Upper Band'] = df['SMA'] + (df['STD'] * 2)         # Banda superior
    df['Lower Band'] = df['SMA'] - (df['STD'] * 2)         # Banda inferior
    return df

# Función para graficar datos y Bollinger
def plot_data(df, selected_pair, show_bollinger=False):
    fig, ax = plt.subplots(figsize=(20, 10))  # Ajusta el tamaño del gráfico

    # Graficar la serie de tiempo de 'close'
    ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)

    # Mostrar las Bandas de Bollinger si está activado
    if show_bollinger:
        ax.plot(df['time'], df['Upper Band'], label='Banda Superior', color='green', linestyle='--', linewidth=1.5)
        ax.plot(df['time'], df['Lower Band'], label='Banda Inferior', color='red', linestyle='--', linewidth=1.5)

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

    # Mostrar botón para añadir las Bandas de Bollinger
    if st.button("Mostrar Bandas de Bollinger"):
        # Calcular las Bandas de Bollinger
        df = calculate_bollinger_bands(df)

        # Graficar nuevamente con Bandas de Bollinger
        fig_bollinger = plot_data(df, selected_pair, show_bollinger=True)

        # Mostrar el gráfico con Bandas de Bollinger
        st.pyplot(fig_bollinger)






