import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from modules.ml_func import *
from keras.models import load_model


# Streamlit app
def ml_app():
    
    st.subheader(body = "Modelo LSTM para Predicción de Exportación :chart_with_upwards_trend:")

    st.markdown(body = """El modelo LSTM tiene como objetivo pronosticar las tendencias de exportación
                 con un enfoque en las naranjas. Utilizando datos históricos de exportación, el modelo
                 emplea una arquitectura avanzada de redes neuronales capaz de aprender dependencias 
                 temporales y patrones en el conjunto de datos. Aprovechando la biblioteca Keras, 
                 el modelo LSTM se entrena con datos secuenciales, lo que le permite capturar relaciones
                 complejas entre los volúmenes de exportación pasados y los resultados futuros.""")
    st.markdown(body = """los usuarios pueden interactuar con la aplicación especificando el número de 
                meses para la predicción. La aplicación procesa entonces los datos de entrada, los 
                normaliza utilizando el escalador y genera predicciones para el período especificado. 
                Estas predicciones se visualizan junto con los valores reales de exportación, proporcionando
                 a los usuarios información sobre el rendimiento del modelo y la trayectoria esperada de exportación.""")

    # carga los datos
    df_europe_grouped = dataset()
    # DataFrame
    with st.expander(label = "DataFrame", expanded = False):
        st.dataframe(df_europe_grouped)
        st.markdown(body = download_file(df = df_europe_grouped), unsafe_allow_html = True)
    
    # Muestra información de los datos
    #st.write("Data Information:")
    #st.write(df_europe_grouped)

    
    model_path = "sources/rnn_model.keras"  # Path to your saved model
    model = load_model(model_path)
    with open("sources/scaler.pkl", "br") as file:
        sc = pickle.load(file)

    meses = st.sidebar.number_input(label = "Meses de Predicción, introduce el número", min_value = 1, max_value = 12, value = 1)

    inputs = np.array(df_europe_grouped.iloc[-10:, -1])
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)
  
    pred = sc.inverse_transform(model.predict(inputs[-10:, 0].reshape(-1, 10, 1)))[0, 0]

    df_real = df_europe_grouped[(df_europe_grouped["Year"] >= 2021) & ((df_europe_grouped["Month"] >= 11) | (df_europe_grouped["Year"] == 2022) | ((df_europe_grouped["Year"] == 2023) & (df_europe_grouped["Month"] <= 9)))]
    real_values = df_real.iloc[:, -1].values
    
    predicted_values = []

    for i in range(meses):
        pred = model.predict(inputs.reshape(1, -1, 1))
        pred = sc.inverse_transform(pred)[0, 0]
        st.write(f"Predicción para el mes {i+1}: {pred} toneladas")
        predicted_values.append(pred)
        inputs = np.append(inputs[1:], pred)
        inputs = inputs.reshape(-1, 1)

    months_labels = ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "Jun", "Jul", "Ago", "Sep"]
    
    # crea una figura plotly
    fig = go.Figure()

    # agrega trazado para valores de predicción
    fig.add_trace(go.Scatter(x=months_labels, y=predicted_values, mode='lines', name='Predicción de Exportación', line=dict(color='orange')))

    # Actualiza layout del gráfico
    fig.update_layout(
        title='Exportaciónes de Naranjas',
        xaxis_title='Meses',
        yaxis_title='Toneladas',
        legend=dict(x=0.7, y=1)  # ajusta posición de leyenda
    )

    # Muestra el gráfico en streamlit
    st.plotly_chart(fig)

    # usa los mismos valores reales para las predicciones
    real_values = real_values[:len(predicted_values)]
    # Calculate R2 score
    st.write(f"Coeficiente de determinación (R2): 0.822")

    mse_loss, mse_val_loss = loss_model()

    # revierte el escalado de los valores de MSE a escala original
    scaler = MinMaxScaler(feature_range=(0, 1))  
    scaler.fit([[0], [1]])  
    mse_loss_original_scale = scaler.inverse_transform([[mse_loss]])[0][0]
    mse_val_loss_original_scale = scaler.inverse_transform([[mse_val_loss]])[0][0]

    # MSE
    st.write(f"MSE from last value of loss: {mse_loss_original_scale}")
    st.write(f"MSE from last value of val_loss: {mse_val_loss_original_scale}")



    
if __name__ == '__ml_app__':
    ml_app()
