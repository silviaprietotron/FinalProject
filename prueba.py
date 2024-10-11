import streamlit as st
import krakenex
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image

#Primera Parte: Lectura y Representación del movimiento del Par de Monedas.

# Configurar la API de Kraken
api = krakenex.API()

# Título de la aplicación y logo
image= Image.open('logo_app.png')
st.image(image, width=200)
st.title("Visualización del Par de Monedas en Kraken")

# Obtener todos los pares de criptomonedas
resp_pairs = api.query_public('AssetPairs')
all_pairs = list(resp_pairs['result'].keys())

# Input de usuario: selección de par de monedas
selected_pair = st.selectbox("Selecciona el par de monedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    # Descargar datos del par seleccionado
    resp = api.query_public('OHLC', {'pair': selected_pair, 'interval': 60}) #solicita datos de tipo OHLC a la API de Kraken, cada 60 minutos.
    ohlc_data = resp['result'][selected_pair]

    # Convertir a DataFrame
    columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
    df = pd.DataFrame(ohlc_data, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Crear el gráfico 
    st.write(f"Graficando el par {selected_pair}")
    fig, ax = plt.subplots(figsize=(20, 25))  # Ajusta el tamaño del gráfico

    # Graficar el precio de cierre vs fechas
    ax.plot(df['time'], df['close'], label=f'{selected_pair} - Precio de Cierre')

    # Formatear eje X: Mostrar fechas cada 5 días
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Formatear etiquetas del eje Y para mostrar solo precios correspondientes a esas fechas
    selected_dates = df['time'][::5]  # Selecciona cada 5 días
    selected_prices = df['close'][::5]
    ax.set_xticks(selected_dates)
    ax.set_yticks(selected_prices)

    # Etiquetas y título
    plt.xlabel('Fecha')
    plt.ylabel('Precio de Cierre')
    plt.title(f'Evolución del Precio de Cierre de {selected_pair}')
    plt.xticks(rotation=45, ha='right')  # Rotar fechas para mejor legibilidad
    plt.tight_layout()

    # Mostrar gráfico en Streamlit
    st.pyplot(fig)

