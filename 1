import streamlit as st
import krakenex
import pandas as pd
import matplotlib.pyplot as plt

# Configurar la API de Kraken
api = krakenex.API()

# Título de la aplicación
st.title("Visualización del Par de Monedas en Kraken")

# Obtener todos los pares de criptomonedas
resp_pairs = api.query_public('AssetPairs')
all_pairs = list(resp_pairs['result'].keys())

# Input de usuario: selección de par de monedas
selected_pair = st.selectbox("Selecciona el par de criptomonedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    # Descargar datos del par seleccionado
    resp = api.query_public('OHLC', {'pair': selected_pair, 'interval': 60})
    ohlc_data = resp['result'][selected_pair]
    
    # Convertir a DataFrame
    columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
    df = pd.DataFrame(ohlc_data, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Graficar el movimiento del par seleccionado
    st.write(f"Graficando el par {selected_pair}")
    fig, ax = plt.subplots()
    ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio de cierre')
    ax.set_title(f'Movimiento del par {selected_pair}')
    ax.legend()
    ax.grid()
    
    st.pyplot(fig)
