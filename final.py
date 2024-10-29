import streamlit as st
import krakenex
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

# Configurar la API de Kraken
api = krakenex.API()

# Clase para análisis financiero
class AnalisisFinanciero:
    def __init__(self, pair):
        self.pair = pair
        self.df_precios = None
        self.df_bollinger = None

    def obtener_datos_ohlc(self, interval=60):
        try:
            resp = api.query_public('OHLC', {'pair': self.pair, 'interval': interval})
            self.df_precios = pd.DataFrame(resp['result'][self.pair], columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            self.df_precios['time'] = pd.to_datetime(self.df_precios['time'], unit='s')
            return self.df_precios
        except Exception as e:
            st.error(f"Error al obtener datos de Kraken: {e}")
            return None

    def calcular_bandas_bollinger(self, ventana=20, num_sd=2):
        if self.df_precios is not None:
            df_bollinger = self.df_precios.copy()
            df_bollinger['media_móvil'] = df_bollinger['close'].rolling(window=ventana).mean()
            df_bollinger['desviación_estándar'] = df_bollinger['close'].rolling(window=ventana).std()
            df_bollinger['banda_superior'] = df_bollinger['media_móvil'] + (df_bollinger['desviación_estándar'] * num_sd)
            df_bollinger['banda_inferior'] = df_bollinger['media_móvil'] - (df_bollinger['desviación_estándar'] * num_sd)

            # Convertir las columnas relevantes a float
            df_bollinger['close'] = df_bollinger['close'].astype(float)
            df_bollinger['banda_inferior'] = df_bollinger['banda_inferior'].astype(float)
            df_bollinger['banda_superior'] = df_bollinger['banda_superior'].astype(float)

            self.df_bollinger = df_bollinger
            return df_bollinger
        else:
            st.warning("No hay datos de precios disponibles para calcular Bandas de Bollinger.")
            return None

    def calcular_senales(self):
        if self.df_bollinger is not None:
            self.df_bollinger['signal'] = 0
            self.df_bollinger = self.df_bollinger.dropna(subset=['close', 'banda_inferior', 'banda_superior'])

            # Cálculo de señales
            self.df_bollinger.loc[self.df_bollinger['close'] < self.df_bollinger['banda_inferior'], 'signal'] = 1  # Señal de compra
            self.df_bollinger.loc[self.df_bollinger['close'] > self.df_bollinger['banda_superior'], 'signal'] = -1  # Señal de venta
            return self.df_bollinger
        else:
            st.warning("No hay datos de Bandas de Bollinger disponibles para calcular señales.")
            return None

    def graficar_datos(self):
        if self.df_precios is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.df_precios['time'], y=self.df_precios['close'], mode='lines', name=f'Precio de cierre de {self.pair}', line=dict(color='blue')))
            fig.update_layout(
                title=f'Movimiento del par {self.pair}',
                xaxis_title='Fecha',
                yaxis_title='Precio de cierre (EUR)',
                hovermode="x unified"
            )
            return fig
        else:
            st.warning("No hay datos de precios disponibles para graficar.")
            return None

    def graficar_bandas_bollinger(self):
        if self.df_bollinger is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.df_bollinger['time'], y=self.df_bollinger['banda_superior'], mode='lines', name='Banda Superior', line=dict(color='red', dash='dot')))
            fig.add_trace(go.Scatter(x=self.df_bollinger['time'], y=self.df_bollinger['banda_inferior'], mode='lines', name='Banda Inferior', line=dict(color='green', dash='dot')))
            fig.add_trace(go.Scatter(x=self.df_bollinger['time'], y=self.df_bollinger['media_móvil'], mode='lines', name='Media Móvil', line=dict(color='orange')))
            fig.update_layout(
                title=f'Bandas de Bollinger para {self.pair}',
                xaxis_title='Fecha',
                yaxis_title='Precio (EUR)',
                hovermode="x unified",
            )
            return fig
        else:
            st.warning("No hay datos de Bandas de Bollinger disponibles para graficar.")
            return None

    def graficar_senales(self):
        if self.df_bollinger is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.df_bollinger['time'], y=self.df_bollinger['close'], mode='lines', name='Precio de cierre', line=dict(color='blue')))
            
            # Añadir señales de compra y venta
            buy_signals = self.df_bollinger[self.df_bollinger['signal'] == 1]
            sell_signals = self.df_bollinger[self.df_bollinger['signal'] == -1]
            
            fig.add_trace(go.Scatter(x=buy_signals['time'], y=buy_signals['close'], mode='markers', name='Señal de Compra', marker=dict(color='green', symbol='triangle-up', size=10)))
            fig.add_trace(go.Scatter(x=sell_signals['time'], y=sell_signals['close'], mode='markers', name='Señal de Venta', marker=dict(color='red', symbol='triangle-down', size=10)))
            
            fig.update_layout(
                title=f'Señales de Compra y Venta para {self.pair}',
                xaxis_title='Fecha',
                yaxis_title='Precio (EUR)',
                hovermode="x unified",
            )
            return fig
        else:
            st.warning("No hay datos de Bandas de Bollinger disponibles para graficar señales.")
            return None

# Título de la aplicación y logo
image = Image.open('logo_app.png')
st.image(image, width=200)
st.title("Visualización del Par de Monedas en Kraken")
st.write("Esta aplicación permite seleccionar un par de monedas de Kraken, visualizar su precio histórico en diferentes formatos, y calcular Bandas de Bollinger para identificar señales de compra y venta.")

# Obtener todos los pares de criptomonedas
try:
    resp_pairs = api.query_public('AssetPairs')
    all_pairs = list(resp_pairs['result'].keys())
except Exception as e:
    st.error(f"Error al obtener los pares de monedas: {e}")
    all_pairs = []

# Input de usuario: selección de par de monedas
par_seleccionado = st.selectbox("Selecciona el par de monedas:", all_pairs)

# Crear objeto de análisis financiero
analisis = AnalisisFinanciero(par_seleccionado)

# Botón para descargar y graficar datos
if st.button("Descargar y graficar datos"):
    df_precios = analisis.obtener_datos_ohlc(interval=60)
    if df_precios is not None:
        st.session_state['df_precios'] = df_precios
        fig = analisis.graficar_datos()
        st.write("Esta gráfica muestra el movimiento histórico del precio de cierre para el par de monedas seleccionado.")
        st.plotly_chart(fig)
        df_bollinger = analisis.calcular_bandas_bollinger()
        st.session_state['df_bollinger'] = df_bollinger

# Mostrar las Bandas de Bollinger al presionar el botón
if st.button("Mostrar Bandas de Bollinger"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session_state['df_bollinger']
        if df_bollinger['media_móvil'].notna().any():
            fig_bb = analisis.graficar_bandas_bollinger()
            st.write("Esta gráfica muestra las Bandas de Bollinger para el par seleccionado, incluyendo la media móvil y las bandas superior e inferior de variabilidad.")
            st.plotly_chart(fig_bb)
        else:
            st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")

# Mostrar señales de compra/venta al presionar el botón
if st.button("Mostrar Señales de Compra y Venta"):
    if 'df_bollinger' not in st.session_state:
        st.warning("Primero descarga y grafica los datos del par de monedas.")
    else:
        df_bollinger = st.session
