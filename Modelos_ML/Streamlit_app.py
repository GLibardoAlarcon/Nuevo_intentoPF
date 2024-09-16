import streamlit as st
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Cargar el modelo
model = joblib.load('./Modelos_ML/modelo_rf.joblib')

# Título de la app
st.title("Predicción del Tipo de Vehículo")

# Crear un formulario para los inputs del usuario
fuel_cost = st.number_input("Costo de combustible ($):", min_value=0.0, step=0.1)
electric_cost = st.number_input("Costo eléctrico ($):", min_value=0.0, step=0.1)
noise_level = st.number_input("Nivel de ruido (dB):", min_value=0.0, step=0.1)

# Cuando el usuario hace clic en el botón "Predecir"
if st.button('Predecir'):
    # Crear el dataframe con los inputs del usuario
    user_input = pd.DataFrame([[fuel_cost, electric_cost, noise_level]],
                              columns=['Fuel_Cost', 'Electric_Cost', 'Noise_Level'])

    # Hacer la predicción
    prediction = model.predict(user_input)
    
    # Mostrar el resultado
    st.write(f"El tipo de vehículo predicho es: {prediction[0]}")

# Cargamos el modelo guardado 
modelo_ML1 = joblib.load('./Modelos_ML/Modelo_ML1.joblib')

# Titulo 
st.title('Recomendación de vehículos con mayor eficiencia energetica')

# Entrada de usuario: año y fabricante
año = st.number_input('Ingrese el año', min_value=2011, max_value=2024)
fabricante = st.text_input('Ingrese la marca')

# Boton para ejecutar la predicción
if st.button('Obtener recomendaciones'):
    # Cargamos el dataset
    df_Vehiculos = pd.read_parquet('../Data/df_vfed.parquet')
    df_Vehiculos_N = df_Vehiculos[df_Vehiculos['Year'] > 2010]
    df_Vehiculos_N.loc[df_Vehiculos_N['CO2 (p/mile)'] < 0, 'CO2 (p/mile)'] = 0
    
    # Filtrar vehiculos por año y fabricante
    Vehiculos_filtrado = df_Vehiculos_N[(df_Vehiculos_N['Year'] == año) & (df_Vehiculos_N['Manufacturer'] == fabricante)]

    # Verificar si hay vehículos que cumplar con esta condición 
    if len(Vehiculos_filtrado) > 0:
        #Estandarizamos las caracteristicas
        X = Vehiculos_filtrado[['Year', 'Miles per gallon (mpg)', 'CO2 (p/mile)', 'FuelCost']]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        # Hacemos las predicciones con el modelo 
        predicciones = modelo_ML1.predict(X_scaled)
        # Añadimos las predicciones al dataframe
        Vehiculos_filtrado['Eficiencia'] = predicciones
        # Ordenas por eficiencia de mayor a menor
        vehiculos_recomendados = Vehiculos_filtrado.sort_values(by='Eficiencia', ascending=False).head(5)
        # Mostrar los 5 vehículos recomendados 
        st.write('Los 5 vehículos mas eficientes energeticamente son:')
        st.dataframe(vehiculos_recomendados[['Year', 'Manufacturer', 'Miles per gallon (mpg)', 'CO2 (p/mile)', 'FuelCost', 'Fuel', 'Category']])
    else:
        st.write('No se encontraron vehículos que cumplan con ese citerio')