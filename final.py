import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import json

class AnalizadorBollinger:
    def __init__(self, ventana: int = 20, std_dev: float = 2):
        self.ventana = ventana
        self.std_dev = std_dev

    def calcular_bandas(self, df: pd.DataFrame) -> pd.DataFrame:
        df['media_movil'] = df['close'].rolling(window=self.ventana).mean()
        df['std_dev'] = df['close'].rolling(window=self.ventana).std()
        df['banda_superior'] = df['media_movil'] + (df['std_dev'] * self.std_dev)
        df['banda_inferior'] = df['media_movil'] - (df['std_dev'] * self.std_dev)
        
        # Convertimos solo las columnas numéricas a float para evitar problemas
        columnas_numericas = ['close', 'media_movil', 'std_dev', 'banda_superior', 'banda_inferior']
        df[columnas_numericas] = df[columnas_numericas].astype(float)

        return df

    def calcular_senales(self, df_bollinger: pd.DataFrame) -> pd.DataFrame:
        # Añadimos la columna 'signal' solo para las señales de compra/venta
        df_bollinger['signal'] = 0
        df_bollinger.loc[df_bollinger['close'] < df_bollinger['banda_inferior'], 'signal'] = 1  # Señal de compra
        df_bollinger.loc[df_bollinger['close'] > df_bollinger['banda_superior'], 'signal'] = -1 # Señal de venta

        return df_bollinger

def obtener_datos(par: str, desde: str, hasta: str) -> pd.DataFrame:
    url = f'https://api.kraken.com/0/public/OHLC?pair={par}&since={desde}'
    response = requests.get(url)
    data = json.loads(response.text)

    if 'result' in data:
        # Procesar el resultado para convertirlo en un DataFrame
        ohlc_data = data['result'][par]
        df = pd.DataFrame(ohlc_data, columns=['open_time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
        df.set_index('open_time', inplace=True)
        
        # Convertir columnas relevantes a float
        df[['open', 'high', 'low', 'close', 'vwap', 'volume']] = df[['open', 'high', 'low', 'close', 'vwap', 'volume']].astype(float)

        return df
    else:
        st.error("Error al obtener datos de Kraken")
        return pd.DataFrame()  # Retornar un DataFrame vacío en caso de error

def graficar_velas(df: pd.DataFrame, par: str):
    # Gráfico de velas
    fig, ax = plt.subplots(figsize=(10, 5))
    for i in range(len(df)):
        color = 'green' if df['close'][i] >= df['open'][i] else 'red'
        ax.bar(df.index[i], df['close'][i] - df['open'][i], bottom=df['open'][i], color=color, width=0.001)
        ax.bar(df.index[i], df['high'][i] - df['close'][i] if color == 'green' else df['high'][i] - df['open'][i],
               bottom=df['close'][i] if color == 'green' else df['open'][i], color=color, width=0.001)
        ax.bar(df.index[i], df['low'][i] - df['open'][i] if color == 'green' else df['low'][i] - df['close'][i],
               bottom=df['open'][i] if color == 'green' else df['close'][i], color=color, width=0.001)
        
    ax.set_title(f'Gráfico de Velas de {par}')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio')
    plt.xticks(rotation=45)
    st.pyplot(fig)

def graficar_bollinger(df: pd.DataFrame):
    # Gráfico de Bandas de Bollinger
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df['close'], label='Precio de Cierre', color='blue')
    ax.plot(df.index, df['banda_superior'], label='Banda Superior', color='orange')
    ax.plot(df.index, df['banda_inferior'], label='Banda Inferior', color='red')
    ax.fill_between(df.index, df['banda_superior'], df['banda_inferior'], color='lightgrey', alpha=0.5)
    
    ax.set_title('Bandas de Bollinger')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

def main():
    st.title('Análisis de Criptomonedas')
    
    # Selector de par de monedas
    par = st.selectbox('Selecciona el par de monedas', ['BTCUSD', 'ETHUSD', 'XRPUSD'])
    
    # Fechas
    desde = st.date_input('Desde', pd.to_datetime('2023-01-01'))
    hasta = st.date_input('Hasta', pd.to_datetime('today'))
    
    # Obtener datos
    df = obtener_datos(par, desde.timestamp(), hasta.timestamp())
    
    if not df.empty:
        analizador = AnalizadorBollinger()
        df_bollinger = analizador.calcular_bandas(df)
        df_bollinger = analizador.calcular_senales(df_bollinger)

        # Graficar velas y Bandas de Bollinger
        graficar_velas(df, par)
        graficar_bollinger(df_bollinger)

if __name__ == "__main__":
    main()
