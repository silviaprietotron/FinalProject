import streamlit as st
import krakenex
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configurar la API de Kraken
api = krakenex.API()

# Título de la aplicación
st.title("Visualización de Pares de Monedas en Kraken")

# Obtener todos los pares de criptomonedas
resp_pairs = api.query_public('AssetPairs')
all_pairs = list(resp_pairs['result'].keys())

# Input de usuario: selección de los pares de monedas
selected_pair1 = st.selectbox("Selecciona el primer par de criptomonedas:", all_pairs)
selected_pair2 = st.selectbox("Selecciona el segundo par de criptomonedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    # Descargar datos de los pares seleccionados
    resp1 = api.query_public('OHLC', {'pair': selected_pair1, 'interval': 60})  # Solicita datos de tipo OHLC a la API de Kraken, cada 60 minutos.
    ohlc_data1 = resp1['result'][selected_pair1]

    resp2 = api.query_public('OHLC', {'pair': selected_pair2, 'interval': 60})  # Solicita datos de tipo OHLC a la API de Kraken, cada 60 minutos.
    ohlc_data2 = resp2['result'][selected_pair2]

    # Convertir a DataFrame
    columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
    df1 = pd.DataFrame(ohlc_data1, columns=columns)
    df1['time'] = pd.to_datetime(df1['time'], unit='s')

    df2 = pd.DataFrame(ohlc_data2, columns=columns)
    df2['time'] = pd.to_datetime(df2['time'], unit='s')

    # Crear el gráfico 
    st.write(f"Graficando los pares {selected_pair1} y {selected_pair2}")
    fig, ax = plt.subplots(figsize=(15, 12))  # Ajusta el tamaño del gráfico

    # Graficar la serie de tiempo de 'close' para ambos pares
    ax.plot(df1['time'], df1['close'], label=f'Precio de cierre de {selected_pair1}', color='blue', linewidth=2)
    ax.plot(df2['time'], df2['close'], label=f'Precio de cierre de {selected_pair2}', color='orange', linewidth=2)

    # Ajustes visuales
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio de cierre', fontsize=12)
    ax.set_title(f'Movimiento de los pares {selected_pair1} y {selected_pair2}', fontsize=16)

    # Formato de fechas en el eje x
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Mostrar cada 5 días
    fig.autofmt_xdate()  # Rotar las fechas para mejor visibilidad

    # Ajustar el eje y para no mostrar los valores
    ax.set_yticks([])  # Esto eliminará los ticks en el eje y

    # Añadir rejilla, leyenda y estilo
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

