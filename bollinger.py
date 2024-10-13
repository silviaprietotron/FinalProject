





# Función para calcular Bandas de Bollinger
def bandas_bollinger(df, ventana=20, factor_std=2):
    df['Media Móvil'] = df['close'].rolling(window=ventana).mean()
    df['Banda Superior'] = df['Media Móvil'] + factor_std * df['close'].rolling(window=ventana).std()
    df['Banda Inferior'] = df['Media Móvil'] - factor_std * df['close'].rolling(window=ventana).std()
    return df

# Botón para mostrar Bandas de Bollinger
if st.button("Añadir Bandas de Bollinger"):
    df = bandas_bollinger(df)

    # Añadir las Bandas de Bollinger al gráfico existente
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(df['time'], df['close'], label=f'Precio de cierre de {selected_pair}', color='blue', linewidth=2)
    ax.plot(df['time'], df['Banda Superior'], label='Banda Superior', color='red', linestyle='--')
    ax.plot(df['time'], df['Banda Inferior'], label='Banda Inferior', color='green', linestyle='--')
    ax.fill_between(df['time'], df['Banda Inferior'], df['Banda Superior'], color='gray', alpha=0.2)

    # Ajustes visuales
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio de cierre (EUR)', fontsize=12)
    ax.set_title(f'Movimiento del par {selected_pair} con Bandas de Bollinger', fontsize=16)

    # Formato de fechas en el eje x
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    fig.autofmt_xdate()

    # Formato de precios en el eje y
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'€{x:.2f}'))

    # Añadir rejilla, leyenda y estilo
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=12)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)





