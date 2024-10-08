import streamlit as st
import krakenex
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

    # Añadir una media móvil (por ejemplo, de 20 periodos)
    df['SMA_20'] = df['close'].rolling(window=20).mean()

    # Verificar si la media móvil se calculó correctamente
    if df['SMA_20'].isnull().all():
        st.warning("No se pudo calcular la media móvil. Asegúrate de tener suficientes datos.")
    else:
        # Crear el gráfico sofisticado
        st.write(f"Graficando el par {selected_pair}")
        fig, ax = plt.subplots(figsize=(10, 6))  # Ajusta el tamaño del gráfico

        # Graficar la serie de tiempo de 'close'
        ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)

        # Graficar la media móvil
        ax.plot(df['time'], df['SMA_20'], label='Media móvil 20 periodos', color='orange', linestyle='--', linewidth=2)

        # Ajustes visuales
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Precio de cierre', fontsize=12)
        ax.set_title(f'Movimiento del par {selected_pair}', fontsize=16)

        # Ajustar el formato del eje Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}'))  # Formato de dos decimales
        ax.set_ylim([df['close'].min() - 100, df['close'].max() + 100])  # Espacio adicional en el eje Y

        # Formato de fechas en el eje x
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Mostrar cada 5 días
        fig.autofmt_xdate()  # Rotar las fechas para mejor visibilidad

        # Añadir rejilla, leyenda y estilo
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(fontsize=12)

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)


