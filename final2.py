import streamlit as st
import krakenex
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

class KrakenApp:
    def __init__(self):
        # Configurar la API de Kraken
        self.api = krakenex.API()
        self.df_precios = None
        self.df_bollinger = None

    def get_ohlc_data(self, pair, interval=60):
        try:
            resp = self.api.query_public('OHLC', {'pair': pair, 'interval': interval})
            return resp['result'][pair]
        except Exception as e:
            st.error(f"Error al obtener datos de Kraken: {e}")
            return None

    def calcular_bandas_bollinger(self, df, ventana=20, num_sd=2):
        df_bollinger = df.copy()
        df_bollinger['media_móvil'] = df_bollinger['close'].rolling(window=ventana).mean()
        df_bollinger['desviación_estándar'] = df_bollinger['close'].rolling(window=ventana).std()
        df_bollinger['banda_superior'] = df_bollinger['media_móvil'] + (df_bollinger['desviación_estándar'] * num_sd)
        df_bollinger['banda_inferior'] = df_bollinger['media_móvil'] - (df_bollinger['desviación_estándar'] * num_sd)

        df_bollinger['close'] = df_bollinger['close'].astype(float)
        df_bollinger['banda_inferior'] = df_bollinger['banda_inferior'].astype(float)
        df_bollinger['banda_superior'] = df_bollinger['banda_superior'].astype(float)

        return df_bollinger

    def calcular_senales(self, df_bollinger):
        df_bollinger['signal'] = 0
        df_bollinger = df_bollinger.dropna(subset=['close', 'banda_inferior', 'banda_superior'])
        df_bollinger.loc[df_bollinger['close'] < df_bollinger['banda_inferior'], 'signal'] = 1  # Señal de compra
        df_bollinger.loc[df_bollinger['close'] > df_bollinger['banda_superior'], 'signal'] = -1  # Señal de venta
        return df_bollinger

    def graficar_datos(self, df, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['time'], y=df['close'], mode='lines', name=f'Precio de cierre de {par_seleccionado}', line=dict(color='blue')))
        fig.update_layout(title=f'Movimiento del par {par_seleccionado}', xaxis_title='Fecha', yaxis_title='Precio de cierre (EUR)', hovermode="x unified")
        return fig

    def graficar_bandas_bollinger(self, df_bollinger, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['banda_superior'], mode='lines', name='Banda Superior', line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['banda_inferior'], mode='lines', name='Banda Inferior', line=dict(color='green', dash='dot')))
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['media_móvil'], mode='lines', name='Media Móvil', line=dict(color='orange')))
        fig.update_layout(title=f'Bandas de Bollinger para {par_seleccionado}', xaxis_title='Fecha', yaxis_title='Precio (EUR)', hovermode="x unified")
        return fig

    def graficar_senales(self, df_bollinger, par_seleccionado):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_bollinger['time'], y=df_bollinger['close'], mode='lines', name='Precio de cierre', line=dict(color='blue')))
        buy_signals = df_bollinger[df_bollinger['signal'] == 1]
        sell_signals = df_bollinger[df_bollinger['signal'] == -1]
        fig.add_trace(go.Scatter(x=buy_signals['time'], y=buy_signals['close'], mode='markers', name='Señal de Compra', marker=dict(color='green', symbol='triangle-up', size=10)))
        fig.add_trace(go.Scatter(x=sell_signals['time'], y=sell_signals['close'], mode='markers', name='Señal de Venta', marker=dict(color='red', symbol='triangle-down', size=10)))
        fig.update_layout(title=f'Señales de Compra y Venta para {par_seleccionado}', xaxis_title='Fecha', yaxis_title='Precio (EUR)', hovermode="x unified")
        return fig

    def graficar_velas(self, df, par_seleccionado):
        fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
        fig.update_layout(title=f'Gráfico de Velas para {par_seleccionado}', xaxis_title='Fecha', yaxis_title='Precio (EUR)', hovermode="x unified")
        return fig

    def run(self):
        # Título de la aplicación y logo
        image = Image.open('logo_app.png')
        st.image(image, width=200)
        st.title("Visualización del Par de Monedas en Kraken")
        st.write("Esta aplicación permite seleccionar un par de monedas de Kraken, visualizar su precio histórico en diferentes formatos, y calcular Bandas de Bollinger para identificar señales de compra y venta.")

        # Obtener todos los pares de criptomonedas
        try:
            resp_pairs = self.api.query_public('AssetPairs')
            all_pairs = list(resp_pairs['result'].keys())
        except Exception as e:
            st.error(f"Error al obtener los pares de monedas: {e}")
            all_pairs = []

        # Input de usuario: selección de par de monedas
        par_seleccionado = st.selectbox("Selecciona el par de monedas:", all_pairs)

        # Botón para descargar y graficar datos
        if st.button("Descargar y graficar datos"):
            datos_ohlc = self.get_ohlc_data(par_seleccionado, interval=60)
            if datos_ohlc is not None:
                columnas = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
                self.df_precios = pd.DataFrame(datos_ohlc, columns=columnas)
                self.df_precios['time'] = pd.to_datetime(self.df_precios['time'], unit='s')
                st.session_state['df_precios'] = self.df_precios
                
                # Calcular y mostrar datos relevantes
                precio_actual = self.df_precios['close'].iloc[-1]
                precio_anterior = self.df_precios['close'].iloc[-2]
                cambio_porcentual = ((precio_actual - precio_anterior) / precio_anterior) * 100
                
                # Mostrar datos porcentuales
                if cambio_porcentual >= 0:
                    st.markdown(f"<h5 style='color: green;'>Cambio porcentual: {cambio_porcentual:.2f}%</h5>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h5 style='color: red;'>Cambio porcentual: {cambio_porcentual:.2f}%</h5>", unsafe_allow_html=True)

                fig = self.graficar_datos(self.df_precios, par_seleccionado)
                st.write("Esta gráfica muestra el movimiento histórico del precio de cierre para el par de monedas seleccionado.")
                st.plotly_chart(fig)
                self.df_bollinger = self.calcular_bandas_bollinger(self.df_precios)
                st.session_state['df_bollinger'] = self.df_bollinger

        # Mostrar las Bandas de Bollinger al presionar el botón
        if st.button("Mostrar Bandas de Bollinger"):
            if 'df_bollinger' not in st.session_state:
                st.warning("Primero descarga y grafica los datos del par de monedas.")
            else:
                df_bollinger = st.session_state['df_bollinger']
                if df_bollinger['media_móvil'].notna().any():
                    fig_bb = self.graficar_bandas_bollinger(df_bollinger, par_seleccionado)
                    st.write("Esta gráfica muestra las Bandas de Bollinger para el par seleccionado.")
                    st.plotly_chart(fig_bb)
                else:
                    st.warning("No hay suficientes datos para calcular las Bandas de Bollinger.")

        # Mostrar señales de compra/venta al presionar el botón
        if st.button("Mostrar Señales de Compra y Venta"):
            if 'df_bollinger' not in st.session_state:
                st.warning("Primero descarga y grafica los datos del par de monedas.")
            else:
                df_bollinger = st.session_state['df_bollinger']
                df_bollinger = self.calcular_senales(df_bollinger)
                fig_senales = self.graficar_senales(df_bollinger, par_seleccionado)
                st.write("Esta gráfica muestra las señales de compra y venta para el par seleccionado.")
                st.plotly_chart(fig_senales)

        # Mostrar gráfico de velas
        if st.button("Mostrar Gráfico de Velas"):
            if 'df_precios' not in st.session_state:
                st.warning("Primero descarga y grafica los datos del par de monedas.")
            else:
                fig_velas = self.graficar_velas(self.df_precios, par_seleccionado)
                st.write("Este gráfico de velas muestra el precio de apertura, cierre, máximo y mínimo para el par seleccionado.")
                st.plotly_chart(fig_velas)

if __name__ == "__main__":
    app = KrakenApp()
    app.run()

