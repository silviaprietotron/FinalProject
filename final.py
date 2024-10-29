import streamlit as st
import krakenex
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

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

# Clase para el análisis de Bandas de Bollinger
class AnalisisBollinger:
    def __init__(self, df):
        self.df = df

    def calcular_bandas_bollinger(self, ventana=20, num_sd=2):
        df_bollinger = self.df.copy()
        df_bollinger['media_móvil'] = df_bollinger['close'].rolling(window=ventana).mean()
        df_bollinger['desviación_estándar'] = df_bollinger['close'].rolling(window=ventana).std()
        df_bollinger['banda_superior'] = df_bollinger['media_móvil'] + (df_bollinger['desviación_estándar'] * num_sd)
        df_bollinger['banda_inferior'] = df_bollinger['media_móvil'] - (df_bollinger['desviación_estándar'] * num_sd)

        # Convertir las columnas relevantes a float
        df_bollinger['close'] = df_bollinger['close'].astype(float)
        df_bollinger['banda_inferior'] = df_bollinger['banda_inferior'].astype(float)
        df_bollinger['banda_superior'] = df_bollinger['banda_superior'].astype(float)
        
        return df_bollinger

    def calcular_senales(self):
        self.df['signal'] = 0
        self.df = self.df.dropna(subset=['close', 'banda_inferior', 'banda_superior'])
        
        # Cálculo de señales
        self.df.loc[self.df['close'] < self.df['banda_inferior'], 'signal'] = 1  # Señal de compra
        self.df.loc[self.df['close'] > self.df['banda_superior'], 'signal'] = -1  # Señal de venta
        
        return self.df

    def graficar_bandas_bollinger(self, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.df['time'], y=self.df['banda_superior'], mode='lines', name='Banda Superior', line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter(x=self.df['time'], y=self.df['banda_inferior'], mode='lines', name='Banda Inferior', line=dict(color='green', dash='dot')))
        fig.add_trace(go.Scatter(x=self.df['time'], y=self.df['media_móvil'], mode='lines', name='Media Móvil', line=dict(color='orange')))
        fig.update_layout(
            title=f'Bandas de Bollinger para {par_seleccionado}',
            xaxis_title='Fecha',
            yaxis_title='Precio (EUR)',
            hovermode="x unified",
        )
        return fig

# Función para graficar datos de precios
def graficar_datos(df, par_seleccionado):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name=f'Precio de cierre de {par_seleccionado}', line=dict(color='blue')))
    fig.update_layout(
        title=f'Movimiento del par {par_seleccionado}',
        xaxis_title='Fecha',
        yaxis_title='Precio de cierre (EUR)',
        hovermode="x unified"
    )
    return fig

# Función para graficar señales de compra/venta
def graficar_senales(df_bollinger, par_seleccionado):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['close'], mode='lines', name='Precio de cierre', line=dict(color='blue')))
    
    # Añadir señales de compra y venta
    buy_signals = df_bollinger[df_bollinger['signal'] == 1]
    sell_signals = df_bollinger[df_bollinger['signal'] == -1]
    
    fig.add_trace(go.Scatter(x=buy_signals['time'], y=buy_signals['close'], mode='markers', name='Señal de Compra', marker=dict(color='green', symbol='triangle-up', size=10)))
    fig.add_trace(go.Scatter(x=sell_signals['time'], y=sell_signals['close'], mode='markers', name='Señal de Venta', marker=dict(color='red', symbol='triangle-down', size=10)))
    
    fig.update_layout(
        title=f'Señales de Compra y Venta para {par_seleccionado}',
        xaxis_title='Fecha',
        yaxis_title='Precio (EUR)',
        hovermode="x unified",
    )
    return fig

# Función para graficar gráfico de velas
def graficar_velas(df, par_seleccionado):
    fig = go.Figure(data=[go.Candlestick(x=df['time'],
                                          open=df['open'],
                                          high=df['high'],
                                          low=df['low'],
                                          close=df['close'])])
    fig.update_layout(
        title=f'Gráfico de Velas para {par_seleccionado}',
        xaxis_title='Fecha',
        yaxis_title='Precio (EUR)',
        hovermode="x unified",
    )
    return fig

# Título de la aplicación y logo
image = Image.open('logo_app.png')
st.image(image, width=200)
st.title("Visualización del Par de Monedas en Kraken")
st.write("Esta aplicación permite seleccionar un par de monedas de Kraken, visualizar su precio histórico en diferentes formatos, y calcular Bandas de Bollinger para identificar señales de compra y venta. Las Bandas de Bollinger incluyen la media móvil y las bandas superior e inferior, que representan la variabilidad del precio. La aplicación tiene como objetivo facilitar el análisis visual y técnico de las criptomonedas deseadas.")

# Obtener todos los pares de criptomonedas
try:
    resp_pairs = api.query_public('AssetPairs')
    all_pairs = list(resp_pairs['result'].keys())
except Exception as e:
    st.error(f"Error al obtener los pares de monedas: {e}")
    all_pairs = []

# Input de usuario: selección de par de monedas
par_seleccionado = st.selectbox("Selecciona el par de monedas:", all_pairs)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    datos_ohlc = get_ohlc_data(par_seleccionado, interval=60)
    if datos_ohlc is not None:
        columnas = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df_precios = pd.DataFrame(datos_ohlc, columns=columnas)
        df_precios['time'] = pd.to_datetime(df_precios['time'], unit='s')
        st.session_state['df_precios'] = df_precios
        fig = graficar_datos(df_precios, par_seleccionado)
        st.write("Esta gráfica muestra el movimiento histórico del precio de cierre para el par de monedas seleccionado.")
        st.plotly_chart(fig)
        
        # Crear instancia de la clase AnalisisBollinger
        analisis = AnalisisBollinger(df_precios)
        df_bollinger = analisis.calcular_bandas_bollinger()
        st.session_state['df_bollinger'] = df_bollinger

# Mostrar las Bandas de Bollinger al presionar el botón
if st.button("Mostrar Bandas de Bollinger"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        if df_bollinger['media_móvil'].notna().any():
            fig_bb = analisis.graficar_bandas_bollinger(par_seleccionado)
            st.write("Esta gráfica muestra las Bandas de Bollinger para el par seleccionado, incluyendo la media móvil y las bandas superior e inferior de variabilidad.")
            st.plotly_chart(fig_bb)
        else:
            st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")

# Mostrar señales de compra/venta al presionar el botón
if st.button("Mostrar Señales de Compra y Venta"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        df_bollinger_con_senales = analisis.calcular_senales()
        fig_senales = graficar_senales(df_bollinger_con_senales, par_seleccionado)
        st.write("Esta gráfica muestra las señales de compra y venta para el par seleccionado.")
        st.plotly_chart(fig_senales)

# Mostrar gráfico de velas al presionar el botón
if st.button("Mostrar Gráfico de Velas"):
    if 'df_precios' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_precios = st.session_state['df_precios']
        fig_velas = graficar_velas(df_precios, par_seleccionado)
        st.write("Este es el gráfico de velas para el par seleccionado, que muestra los movimientos de precios en diferentes intervalos.")
        st.plotly_chart(fig_velas)
