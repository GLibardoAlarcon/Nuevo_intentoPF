import streamlit as st
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Configurar del modelo Ml1
st.set_page_config(
    page_title="Sistema de Vehículos Eficientes",
    page_icon="🚗",
    layout="centered",
)

#Segundo modelo de ML1 
# Imagen de la empresa
# Definir estilo CSS personalizado para el logotipo
st.markdown("""
    <style>
    .image-container {
        text-align: center;
        margin-top: 20px;
        margin-bottom: 40px;
    }
    .image-container img {
        width: 150px;  /* Ajustar el tamaño de la imagen */
        border-radius: 50%;  /* Hacerla circular */
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);  /* Añadir sombra */
    }
    </style>
    <div class="image-container">
        <img src="https://pbs.twimg.com/profile_images/1042867341476995078/antCC8gJ_400x400.jpg" alt="Logo">
    </div>
    """, unsafe_allow_html=True)

# Cargamos el modelo guardado 
modelo_ML1 = joblib.load('./Modelos_ML/Modelo_ML1.joblib')
# Cargamos el dataset
df_Vehiculos = pd.read_parquet('./Data/Df_vfed.parquet')
df_Vehiculos_N = df_Vehiculos[df_Vehiculos['Year'] > 2010]
df_Vehiculos_F = df_Vehiculos_N[df_Vehiculos_N['CO2 (p/mile)'] >= 0]
# Realizamos una función para categorizar los vehículos
def categorizar_vehiculos(row):
    if row['Alternative Fuel'] == 'Electricity':
        return 'Híbrido'
    elif row['Fuel'] == 'Electricity':
        return 'Eléctrico'
    elif row['Alternative Fuel'] in ['E85', 'No'] and row['Fuel'] != 'Natural Gas' and row['CO2 (p/mile)'] > 0:
        return 'Comvencional'
    else:
        return 'Gas'    
# Aplicamos la función 
df_Vehiculos_F['Categoria'] = df_Vehiculos_F.apply(categorizar_vehiculos, axis=1)
#  Creamos una columna unica 
df_Vehiculos_F['Vehículo_unico'] = df_Vehiculos_F['Manufacturer'] + ' ' + df_Vehiculos_F['Model']+ ' ' + df_Vehiculos_F['Year'].astype(str)
# 2P
#Obtenemos las marcas de los vehículos 
Marcas = df_Vehiculos_F['Manufacturer'].unique().tolist()
# Agregamos Todos 
Marcas.insert(0, 'Todos')
#Creamos una lista de los años
anios_unicos = list(range(2011, 2024))
# Agregamos unicos
anios_unicos.insert(0, 'Todos')
# Titulo 
st.title("Análisis de Eficiencia de Vehículos")
st.write("Bienvenido a la plataforma de análisis de eficiencia energética para vehículos.")

# Entrada de usuario: año y fabricante
año = st.selectbox('Seleccione el año del Vehículo', anios_unicos, help="Elige un año de la lista")
fabricante = st.selectbox('Seleccione la marca del vehículo', Marcas, help="Elige una marca de vehículo")

# Boton para ejecutar la predicción
if st.button('Obtener recomendacion'):
    # Condición si el usuario escoge tanto el año como el fabricante
    if año != 'Todos' and fabricante != 'Todos':
         # Filtrar vehiculos por año y fabricante
         Vehiculos_filtrado = df_Vehiculos_F[(df_Vehiculos_F['Year'] == año) & (df_Vehiculos_F['Manufacturer'] == fabricante)]
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
             st.session_state['dataset'] = vehiculos_recomendados
             # Mostrar los 5 vehículos recomendados 
             st.write('Los 5 vehículos mas eficientes energeticamente son:')
             st.dataframe(vehiculos_recomendados[['Year', 'Vehículo_unico']])
         else: 
             st.write('No se encontraron vehículos que cumplan con ese citerio')
    # Condición si solo escoge al fabricante
    elif fabricante != 'Todos' and año == 'Todos':
         # Filtrar vehiculos por fabricante
         Vehiculos_filtrado = df_Vehiculos_F[df_Vehiculos_F['Manufacturer'] == fabricante]
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
             st.session_state['dataset'] = vehiculos_recomendados
             # Mostrar los 5 vehículos recomendados 
             st.write('Los 5 vehículos mas eficientes energeticamente son:')
             st.dataframe(vehiculos_recomendados[['Year', 'Vehículo_unico']])
         else: 
             st.write('No se encontraron vehículos que cumplan con ese citerio')
    # Condición si solo elige año
    elif año != 'Todos' and fabricante == 'Todos':
         # Filtrar vehiculos por año 
         Vehiculos_filtrado = df_Vehiculos_F[df_Vehiculos_F['Year'] == año]
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
             st.session_state['dataset'] = vehiculos_recomendados
             # Mostrar los 5 vehículos recomendados 
             st.write('Los 5 vehículos mas eficientes energeticamente son:')
             st.dataframe(vehiculos_recomendados[['Year', 'Vehículo_unico']])
         else: 
             st.write('No se encontraron vehículos que cumplan con ese citerio')
    else:
         # Sin filtro
         Vehiculos_filtrado = df_Vehiculos_F
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
             st.session_state['dataset'] = vehiculos_recomendados
             # Mostrar los 5 vehículos recomendados 
             st.write('Los 5 vehículos mas eficientes energeticamente son:')
             st.dataframe(vehiculos_recomendados[['Year', 'Vehículo_unico']])
         else: 
             st.write('No se encontraron vehículos que cumplan con ese citerio')

st.title('Costo enérgetico por millas')
if 'dataset' in st.session_state and not st.session_state['dataset'].empty:
     dataset = st.session_state['dataset']
     # Usar las filas como opción múltiple
     Vehiculos = dataset['Vehículo_unico'].tolist()
     Vehiculos.insert(0, 'Seleccion')
     seleccion = st.selectbox('Selecciona un vehículo:', Vehiculos)
      # Mostrar selección
     if seleccion != 'Seleccion':
        # Filtrar el dataset para mostrar solo las filas seleccionadas
        seleccionados = dataset[dataset['Vehículo_unico'] == seleccion].iloc[0]
        st.write("Detalles del vehículo")
        st.write(f"Vehículo seleccionado: {seleccionados['Vehículo_unico']}")
        st.write(f"Costo de combustible por galón: ${seleccionados['FuelCost']} US")
        st.write(f"Emisiones de CO2 por milla: {seleccionados['CO2 (p/mile)']} g/milla")
        st.write(f"Millas por galón: {seleccionados['Miles per gallon (mpg)']} mpg")
        st.write(f"Categoria del vehículo: {seleccionados['Categoria']}")
        st.write(f"Modelo: {seleccionados['Year']}")

        # Insertar una imagen del vehículo
        # URL de la imagen (ejemplo)
        image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTAynn1hP5HC3WnHtWHmrcMPpzVRpkYq9ZWQg&s"
        # Mostrar la imagen desde la URL con un caption dinámico basado en el vehículo seleccionado
        st.image(image_url, caption=f"Imagen del vehículo: {seleccionados['Vehículo_unico']}", width=400)

        # Pedir al usuario que ingrese la cantidad de Kilometros
        st.write('**Consumo energetico por kilometros**')
        Kilometros = st.number_input('Ingresa la cantidad de Kilometros', min_value=0, max_value=1000000)
        # Realizar cálculos
        Km_por_Litro = seleccionados['Miles per gallon (mpg)'] * 0.425144
        # Convertir CO2 por milla a CO2 por kilómetro
        co2_total_km = seleccionados['CO2 (p/mile)'] / 1.60934
        # Hacemos calculos
        combustible_usado = Kilometros / Km_por_Litro  # Cantidad de litros por kilometro
        costo_total_combustible = combustible_usado * seleccionados['FuelCost']  # Costo total de combustible
        CO2_total = Kilometros * co2_total_km  # Emisiones de CO2 totales
        # Mostrar los resultados
        st.write(f"Para {Kilometros} kilometros, el vehículo {seleccionados['Vehículo_unico']} gastará:")
        st.write(f"- {combustible_usado:.2f} litros de combustible")
        st.write(f"- Un costo total de combustible de ${costo_total_combustible:.2f} US")
        st.write(f"- Emitirá un total de {CO2_total:.2f} gramos de CO2")
     else:
         st.write('No se a elegido vehículo')
else:
    st.write("No se ha generado ninguna recomendación")
