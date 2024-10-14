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
    try:
        resp = api.query_public('OHLC', {'pair': pair, 'interval': interval})
        return resp['result'][pair]
    except Exception as e:
        st.error(f"Error al obtener datos de Kraken: {e}")
        return None

# Función para calcular Bandas de Bollinger
def calculate_bollinger_bands(df, window=20, num_sd=2):
    bollinger_df = df.copy()  # Copiar el DataFrame original para Bollinger Bands
    bollinger_df['rolling_mean'] = bollinger_df['close'].rolling(window=window).mean()
    bollinger_df['rolling_std'] = bollinger_df['close'].rolling(window=window).std()
    bollinger_df['upper_band'] = bollinger_df['rolling_mean'] + (bollinger_df['rolling_std'] * num_sd)
    bollinger_df['lower_band'] = bollinger_df['rolling_mean'] - (bollinger_df['rolling_std'] * num_sd)
    return bollinger_df

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
def plot_bollinger_bands(bollinger_df, selected_pair):
    fig_bb, ax_bb = plt.subplots(figsize=(20, 10))

    # Graficar el precio de cierre
    ax_bb.plot(bollinger_df['time'], bollinger_df['close'], label='Precio de Cierre', color='blue')

    # Graficar las Bandas de Bollinger
    if 'upper_band' in bollinger_df and 'lower_band' in bollinger_df:
        ax_bb.plot(bollinger_df['time'], bollinger_df['upper_band'], label='Banda Superior', color='red', linestyle='--')
        ax_bb.plot(bollinger_df['time'], bollinger_df['lower_band'], label='Banda Inferior', color='green', linestyle='--')
        ax_bb.plot(bollinger_df['time'], bollinger_df['rolling_mean'], label='Media Móvil', color='orange')

    # Ajustar los límites del eje Y
    ax_bb.set_ylim(min(bollinger_df['lower_band'].min(), bollinger_df['close'].min()) * 0.95,
                   max(bollinger_df['upper_band'].max(), bollinger_df['close'].max()) * 1.05)

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
try:
    resp_pairs = api.query_public('AssetPairs')
    all_pairs = list(resp_pairs['result'].keys())
except Exception as e:
    st.error(f"Error al obtener los pares de monedas: {e}")
    all_pairs = []

# Input de usuario: selección de par de monedas
selected_pair = st.selectbox("Selecciona el par de monedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    # Descargar datos del par seleccionado con intervalo fijo de 60 segundos
    ohlc_data = get_ohlc_data(selected_pair, interval=60)

    if ohlc_data is not None:
        # Convertir a DataFrame
        columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df_prices = pd.DataFrame(ohlc_data, columns=columns)  # DataFrame para precios normales
        df_prices['time'] = pd.to_datetime(df_prices['time'], unit='s')

        # Guardar los DataFrames en session_state
        st.session_state['df_prices'] = df_prices

        # Graficar los datos de precios
        fig = plot_data(df_prices, selected_pair)
        st.pyplot(fig)

        # Calcular las Bandas de Bollinger
        df_bollinger = calculate_bollinger_bands(df_prices)
        st.session_state['df_bollinger'] = df_bollinger  # Guardar Bollinger en session_state

# Mostrar las Bandas de Bollinger al presionar el botón
if 'df_bollinger' in st.session_state:
    if st.button("Mostrar Bandas de Bollinger"):
        df_bollinger = st.session_state['df_bollinger']

        # Verificar que las Bandas de Bollinger se hayan calculado
        if df_bollinger['rolling_mean'].notna().any():
            fig_bb = plot_bollinger_bands(df_bollinger, selected_pair)
            st.pyplot(fig_bb)
        else:
            st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")
