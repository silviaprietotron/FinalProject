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

class BandasBollinger:
    def __init__(self, df, ventana=20, num_desv=2):
        self.df = df
        self.ventana = ventana
        self.num_desv = num_desv

    def calcular_bandas(self):
        """Calcula las Bandas de Bollinger y las añade al DataFrame."""
        self.df['media_movil'] = self.df['close'].rolling(window=self.ventana).mean()
        self.df['desviacion_estandar'] = self.df['close'].rolling(window=self.ventana).std()
        self.df['banda_superior'] = self.df['media_movil'] + (self.df['desviacion_estandar'] * self.num_desv)
        self.df['banda_inferior'] = self.df['media_movil'] - (self.df['desviacion_estandar'] * self.num_desv)
        return self.df

    def plot_bollinger(df, selected_pair):
        fig, ax = plt.subplots(figsize=(20, 10))  # Ajusta el tamaño del gráfico

        # Graficar la serie de tiempo de 'close'
        ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)

        # Graficar las Bandas de Bollinger
        ax.plot(df['time'], df['banda_superior'], label='Banda superior', linestyle='--', color='red', linewidth=1.5)
        ax.plot(df['time'], df['banda_inferior'], label='Banda inferior', linestyle='--', color='green', linewidth=1.5)

        # Ajustes visuales
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Precio de cierre (EUR)', fontsize=12)
        ax.set_title(f'Bandas de Bollinger para {selected_pair}', fontsize=16)

        # Formato de fechas en el eje x
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Mostrar cada 5 días
        fig.autofmt_xdate()  # Rotar las fechas para mejor visibilidad
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'€{x:.2f}'))  # Formato de moneda

        # Añadir rejilla, leyenda y estilo
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(fontsize=12)

        return fig


    bb = BandasBollinger(df)
    df_bollinger = bb.calcular_bandas()
    
if st.button("Mostrar Bandas de Bollinger"):
    if 'df_bollinger' in locals():  # Verifica que df_bollinger existe
        # Graficar las Bandas de Bollinger
        fig_bollinger = plot_bollinger(df_bollinger, selected_pair)
        st.pyplot(fig_bollinger)
    else:
        st.warning("Primero, descarga y grafica los datos para poder mostrar las Bandas de Bollinger.")
