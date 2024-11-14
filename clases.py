import streamlit as st
import krakenex
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

# Clase para encapsular la funcionalidad de visualización de Kraken
class VisualizadorKraken:
    def __init__(self):
        self.api = krakenex.API()
        
    # Función para obtener datos OHLC
    def get_ohlc_data(self, pair, interval=60):
        try:
            resp = self.api.query_public('OHLC', {'pair': pair, 'interval': interval})
            return resp['result'][pair]
        except Exception as e:
            st.error(f"Error al obtener datos de Kraken: {e}")
            return None

    # Función para calcular Bandas de Bollinger
    def calcular_bandas_bollinger(self, df, ventana=20, num_sd=2):
        df_bollinger = df.copy()
        df_bollinger['media_móvil'] = df_bollinger['close'].rolling(window=ventana).mean()
        df_bollinger['desviación_estándar'] = df_bollinger['close'].rolling(window=ventana).std()
        df_bollinger['banda_superior'] = df_bollinger['media_móvil'] + (df_bollinger['desviación_estándar'] * num_sd)
        df_bollinger['banda_inferior'] = df_bollinger['media_móvil'] - (df_bollinger['desviación_estándar'] * num_sd)

        #Convertir las columnas relevantes a formato float
        df_bollinger['close'] = df_bollinger['close'].astype(float)
        df_bollinger['banda_inferior'] = df_bollinger['banda_inferior'].astype(float)
        df_bollinger['banda_superior'] = df_bollinger['banda_superior'].astype(float)
        
        return df_bollinger

    # Función para calcular señales de compra/venta
    def calcular_senales(self, df_bollinger):
        df_bollinger['signal'] = 0
        df_bollinger = df_bollinger.dropna(subset=['close', 'banda_inferior', 'banda_superior'])
       
        #Cálculo de las señales
        df_bollinger.loc[df_bollinger['close'] < df_bollinger['banda_inferior'], 'signal'] = 1
        df_bollinger.loc[df_bollinger['close'] > df_bollinger['banda_superior'], 'signal'] = -1
        
        return df_bollinger

    # Función para graficar datos de precios
    def graficar_datos(self, df, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name=f'Precio de cierre de {par_seleccionado}', line=dict(color='blue')))
        fig.update_layout(
            title=f'Movimiento del par {par_seleccionado}',
            xaxis_title='Fecha',
            yaxis_title='Precio de cierre',
            hovermode="x unified"
        )
        return fig

    # Función para graficar Bandas de Bollinger
    def graficar_bandas_bollinger(self, df_bollinger, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['banda_superior'], mode='lines', name='Upper Band', line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['banda_inferior'], mode='lines', name='Lower Band', line=dict(color='green', dash='dot')))
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['media_móvil'], mode='lines', name='Moving Average', line=dict(color='orange')))
        fig.update_layout(
            title=f'Bandas de Bollinger para {par_seleccionado}',
            xaxis_title='Fecha',
            yaxis_title='Precio',
            hovermode="x unified",
        )
        return fig

    # Función para graficar señales de compra/venta
    def graficar_senales(self, df_bollinger, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['close'], mode='lines', name='Precio de cierre', line=dict(color='blue')))
        
        #Añadir señales de compra y venta
        buy_signals = df_bollinger[df_bollinger['signal'] == 1]
        sell_signals = df_bollinger[df_bollinger['signal'] == -1]
        
        fig.add_trace(go.Scatter(x=buy_signals['time'], y=buy_signals['close'], mode='markers', name='Señal de Compra', marker=dict(color='green', symbol='triangle-up', size=10)))
        fig.add_trace(go.Scatter(x=sell_signals['time'], y=sell_signals['close'], mode='markers', name='Señal de Venta', marker=dict(color='red', symbol='triangle-down', size=10)))
       
        fig.update_layout(
            title=f'Señales de Compra y Venta para {par_seleccionado}',
            xaxis_title='Fecha',
            yaxis_title='Precio',
            hovermode="x unified",
        )
        return fig

    # Función para graficar gráfico de velas
    def graficar_velas(self, df, par_seleccionado):
        fig = go.Figure(data=[go.Candlestick(x=df['time'],
                                              open=df['open'],
                                              high=df['high'],
                                              low=df['low'],
                                              close=df['close'])])
        fig.update_layout(
            title=f'Gráfico de Velas para {par_seleccionado}',
            xaxis_title='Fecha',
            yaxis_title='Precio',
            hovermode="x unified",
        )
        return fig

# Crear instancia de la clase
visualizador = VisualizadorKraken()

# Título de la aplicación y logo
image = Image.open('logo_app.png')
st.image(image, width=200)
st.title("Visualización del Movimiento de un Par de Monedas en Kraken")
st.write("Esta aplicación permite seleccionar un par de monedas de Kraken, visualizar su precio histórico en diferentes formatos, y calcular Bandas de Bollinger para identificar señales de compra y venta. Las Bandas de Bollinger incluyen la media móvil y las bandas superior e inferior, que representan la variabilidad del precio. La aplicación tiene como objetivo facilitar el análisis visual y técnico de las criptomonedas deseadas.")

# Obtener todos los pares de criptomonedas
try:
    resp_pairs = visualizador.api.query_public('AssetPairs')
    all_pairs = list(resp_pairs['result'].keys())
except Exception as e:
    st.error(f"Error al obtener los pares de monedas: {e}")
    all_pairs = []

# Input de usuario: selección de par de monedas
par_seleccionado = st.selectbox("Selecciona el par de monedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    datos_ohlc = visualizador.get_ohlc_data(par_seleccionado, interval=60)
    if datos_ohlc is not None:
        columnas = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df_precios = pd.DataFrame(datos_ohlc, columns=columnas)
        df_precios['time'] = pd.to_datetime(df_precios['time'], unit='s')
        st.session_state['df_precios'] = df_precios
        fig = visualizador.graficar_datos(df_precios, par_seleccionado)
        st.plotly_chart(fig)
        df_bollinger = visualizador.calcular_bandas_bollinger(df_precios)
        st.session_state['df_bollinger'] = df_bollinger

# Mostrar las Bandas de Bollinger
if st.button("Mostrar Bandas de Bollinger"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        if df_bollinger['media_móvil'].notna().any():
            fig_bb = visualizador.graficar_bandas_bollinger(df_bollinger, par_seleccionado)
            st.write("Esta gráfica muestra las Bandas de Bollinger para el par seleccionado, incluyendo la media móvil y las bandas superior e inferior de variabilidad.")
            st.plotly_chart(fig_bb)
        else:
            st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")

# Mostrar señales de compra/venta
if st.button("Mostrar Señales de Compra y Venta"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        df_bollinger = visualizador.calcular_senales(df_bollinger)

        # Mostrar señales de compra y venta
        compra_count = df_bollinger[df_bollinger['signal'] == 1].shape[0]
        venta_count = df_bollinger[df_bollinger['signal'] == -1].shape[0]
        
        st.write(f"**Señales de Compra:** {compra_count}")
        st.write(f"**Señales de Venta:** {venta_count}")
        
        fig_senales = visualizador.graficar_senales(df_bollinger, par_seleccionado)
        st.write("Esta gráfica muestra las señales de compra y venta basadas en las Bandas de Bollinger.")
        st.plotly_chart(fig_senales)

# Mostrar gráfico de velas
if st.button("Mostrar Gráfico de Velas"):
    if 'df_precios' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_precios = st.session_state['df_precios']
        fig_velas = visualizador.graficar_velas(df_precios, par_seleccionado)
        st.write("Este gráfico muestra la representación de velas del movimiento del par de monedas seleccionado.")
        st.plotly_chart(fig_velas)
