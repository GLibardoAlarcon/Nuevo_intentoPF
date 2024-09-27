import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración inicial del layout y tema
st.set_page_config(page_title="Dashboard Interactivo de Análisis de Datos", layout="wide")

# Encabezado principal con formato
st.markdown("""
# *Presentación Interactiva de Análisis de Datos* 📊
Este dashboard interactivo presenta diferentes análisis relacionados con precios de reventa de autos, viajes en taxis amarillos y costos operacionales de vehículos.
Navega por los diferentes análisis para explorar las gráficas y análisis asociados. Utiliza el menú lateral para seleccionar y visualizar cada uno.
""", unsafe_allow_html=True)

# Sidebar para la selección de análisis
st.sidebar.header("Selecciona un Análisis:")
analisis = st.sidebar.selectbox(
    'Selecciona el análisis',
    ('Análisis de Precios de Reventa de Autos', 
     'Análisis de Viajes en Taxis Amarillos', 
     'Análisis de Costos Operacionales de Vehículos')
)

# Cargar los datasets utilizando rutas relativas
try:
    df_car_resale = pd.read_csv('./Data/car_resale_prices_clean.csv')
    df_yellow_taxi = pd.read_parquet('./Data/yellow_tripdata.parquet')
    df_vehicle_costs = pd.read_csv('./Data/costo_operacional_vehiculos_clean.csv')
    st.success("Datasets cargados correctamente")
except Exception as e:
    st.error(f"Error al cargar los datasets: {e}")

# Inicializar variables en session_state si no están presentes
if 'autos_recomendados' not in st.session_state:
    st.session_state.autos_recomendados = pd.DataFrame()  # Para almacenar autos recomendados
if 'auto_seleccionado' not in st.session_state:
    st.session_state.auto_seleccionado = None  # Para almacenar el auto seleccionado

# Función para categorizar los vehículos
def categorize_vehicle(row):
    if row['Fuel_Type'] in ['Diesel', 'Petrol', 'Petrol/LPG']:
        return 'Convencional'
    elif row['Fuel_Type'] in ['Electricity', 'Electric']:
        return 'Eléctrico'
    else:
        return 'Híbrido'

# Aplicar la función al dataframe
df_car_resale['Vehicle_Type'] = df_car_resale.apply(categorize_vehicle, axis=1)

# Análisis de Precios de Reventa de Autos
if analisis == 'Análisis de Precios de Reventa de Autos':
    st.header('📈 Análisis de Precios de Reventa de Autos')
    st.markdown("""
    *Descripción*: Este análisis muestra la distribución de los precios de reventa de autos por año de registro y permite filtrar autos según el presupuesto y tipo de combustible.
    """)
    
    # Crear una nueva columna para agrupar los años en rangos de 5 años
    df_car_resale['Year_Category'] = pd.cut(df_car_resale['Registered_Year'],
                                            bins=[1990, 1995, 2000, 2005, 2010, 2015, 2020],
                                            labels=['1990-1995', '1996-2000', '2001-2005', '2006-2010', '2011-2015', '2016-2020'])

    # Layout mejorado: Usamos columnas para mostrar gráficas y filtros
    col1, col2 = st.columns([2, 1])
    # Asegurarse de que los años de registro sean válidos (positivos y no nulos)
    df_car_resale2 = df_car_resale[df_car_resale['Registered_Year'] > 0]
    df_car_resale2['Registered_Year'] = df_car_resale2['Registered_Year'].astype(int)
    
    with col1:
        st.subheader("Distribución de Precios de Reventa por Año de Registro")
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='Registered_Year', y='Resale_Price', data=df_car_resale2, palette="Blues")
        plt.title("Distribución de Precios de Reventa por Año de Registro", fontsize=16)
        plt.xlabel("Año de Registro", fontsize=12)
        plt.ylabel("Precio de Reventa (USD)", fontsize=12)
        
        # Formatear las etiquetas del eje X para que sean solo números enteros
        x_labels = df_car_resale2['Registered_Year'].unique().astype(int)
        plt.xticks(ticks=range(len(x_labels)), labels=x_labels, rotation=45)
    
        st.pyplot(plt)

    st.subheader("Filtrar autos por presupuesto y tipo de combustible")
    presupuesto_cliente = st.number_input("Ingresa tu presupuesto (USD)", min_value=0, value=5000, step=1000)

    # Filtrar por tipo de combustible
    tipos_combustible = df_car_resale['Fuel_Type'].unique().tolist()
    tipos_combustible.append('Todos')  # Opción para seleccionar todos los tipos
    tipo_combustible_seleccionado = st.selectbox("Selecciona el tipo de combustible", tipos_combustible, index=len(tipos_combustible)-1)

    # Botón para ejecutar la búsqueda de autos recomendados
    if st.button("Buscar autos recomendados"):
        # Aplicar filtro de presupuesto
        autos_recomendados = df_car_resale[df_car_resale['Resale_Price'] <= presupuesto_cliente]
        
        # Filtrar por tipo de combustible si no se ha seleccionado "Todos"
        if tipo_combustible_seleccionado != 'Todos':
            autos_recomendados = autos_recomendados[autos_recomendados['Fuel_Type'] == tipo_combustible_seleccionado]
        
        # Mostrar los 5 autos recomendados más cercanos al presupuesto
        autos_recomendados = autos_recomendados.sort_values(by='Resale_Price', ascending=False).head(1)
        
        if not autos_recomendados.empty:
            st.markdown(f"### Auto recomendado dentro del presupuesto de *${presupuesto_cliente}*:")
            st.dataframe(autos_recomendados[['Full_Name', 'Registered_Year', 'Fuel_Type', 'Resale_Price']])
            
            
            # Mostrar detalles del auto recomendado
            auto_detalles = autos_recomendados.iloc[0]
            st.markdown(f"### Detalles del auto recomendado: **{auto_detalles['Full_Name']}**")
            st.markdown(
                f"""
                - **Año de Registro:** {int(auto_detalles['Registered_Year'])}
                - **Transmisión:** {auto_detalles['Transmission_Type']}
                - **Tipo de Combustible:** {auto_detalles['Fuel_Type']}
                - **Categoría de Combustible:** {auto_detalles['Vehicle_Type']}
                - **Potencia Máxima:** {auto_detalles['Max_Power']}
                - **Precio de Reventa:** **${auto_detalles['Resale_Price']:,.2f}**
                """
            )
        else:
            st.text(f"No se encontraron autos dentro del presupuesto de ${presupuesto_cliente}.")
            
# Análisis de Viajes en Taxis Amarillos
elif analisis == 'Análisis de Viajes en Taxis Amarillos':
    st.header('🚕 Análisis de Viajes en Taxis Amarillos')
    st.markdown("""
    *Descripción*: Este análisis muestra la cantidad de viajes realizados por taxis amarillos a lo largo del tiempo.
    """)

    grafico_taxis = st.selectbox(
        'Selecciona la gráfica para Viajes en Taxis Amarillos',
        ('Cantidad de Viajes por Año', 'Distancia vs Duración del Viaje')
    )

    if grafico_taxis == 'Cantidad de Viajes por Año':
        st.subheader("Cantidad de Viajes por Año")
        df_yellow_taxi['pickup_year'] = pd.to_datetime(df_yellow_taxi['pickup_datetime']).dt.year
        plt.figure(figsize=(10, 5))
        sns.countplot(x='pickup_year', data=df_yellow_taxi)
        plt.title("Cantidad de Viajes por Año")
        plt.xlabel("Año")
        plt.ylabel("Número de Viajes")
        st.pyplot(plt)
    
    elif grafico_taxis == 'Distancia vs Duración del Viaje':
        st.subheader("Relación entre Distancia y Duración del Viaje")
        plt.figure(figsize=(10, 5))
        sns.scatterplot(x='trip_distance', y='trip_duration', data=df_yellow_taxi)
        plt.title("Distancia vs Duración del Viaje")
        plt.xlabel("Distancia del Viaje (millas)")
        plt.ylabel("Duración del Viaje (minutos)")
        st.pyplot(plt)

# Análisis de Costos Operacionales de Vehículos
elif analisis == 'Análisis de Costos Operacionales de Vehículos':
    # Filtrar para eliminar cualquier fila que tenga 'Electricity'
    df_vehicle_costs = df_vehicle_costs[df_vehicle_costs['Fuel_Type'] != 'Electricity']

    st.header('🚗 Análisis de Costos Operacionales de Vehículos')
    st.markdown("""
    *Descripción*: Este análisis muestra los costos operacionales de vehículos según su tipo de combustible.
    """)

    # Selección de la gráfica para mostrar
    grafico_costos = st.selectbox(
        'Selecciona la gráfica para Costos Operacionales',
        ('Costos Operacionales por Tipo de Combustible',)
    )

    if grafico_costos == 'Costos Operacionales por Tipo de Combustible':
        st.subheader("Costos Operacionales por Tipo de Combustible")
        
        # Definir el tamaño del gráfico
        plt.figure(figsize=(10, 5))

        # Paleta de colores para las barras (usamos una paleta de colores variada)
        palette = sns.color_palette("husl", len(df_vehicle_costs['Fuel_Type'].unique()))

        # Gráfico de barras con colores variados
        sns.barplot(x='Fuel_Type', y='Fuel_Cost', data=df_vehicle_costs, ci=None, palette=palette)
        
        # Ajustar título y etiquetas
        plt.title("Costos Operacionales por Tipo de Combustible", fontsize=16)
        plt.xlabel("Tipo de Combustible", fontsize=12)
        plt.ylabel("Costo de Combustible (GBP)", fontsize=12)
        
        # Rotar etiquetas para mejorar la legibilidad
        plt.xticks(rotation=45, ha='right')

        # Mostrar gráfico en Streamlit
        st.pyplot(plt)

        # Comparación de tipos de combustible (tabla con valores promedio)
        st.subheader("Comparación de Costos de Combustibles")
        fuel_comparison = df_vehicle_costs.groupby('Fuel_Type')['Fuel_Cost'].mean().reset_index()
        st.table(fuel_comparison)

        # Aplicar la función al dataframe
        df_vehicle_costs['Vehicle_Type'] = df_vehicle_costs.apply(categorize_vehicle, axis=1)

        # Sumar costos por tipo de vehículo
        total_cost_conventional = df_vehicle_costs[df_vehicle_costs['Vehicle_Type'] == 'Convencional']['Total_Cost'].sum()
        total_cost_electric_hybrid = df_vehicle_costs[df_vehicle_costs['Vehicle_Type'].isin(['Eléctrico', 'Híbrido'])]['Total_Cost'].sum()

        # Calcular el KPI
        kpi = (total_cost_electric_hybrid / total_cost_conventional) * 100
        
        # Mostrar el KPI de manera estética
        st.markdown("### Ahorro en Costos Operativos")
        st.metric(label="Ahorro de Costos Operativos (%)", value=f"{kpi:.2f}%", delta="vs. Convencional")

        # Gráfico circular para mostrar la comparación
        labels = ['Ahorro (Eléctrico/Híbrido)', 'Costo Convencional']
        sizes = [total_cost_electric_hybrid, total_cost_conventional]
        colors = ['#4CAF50', '#FFC107']  # Colores para el gráfico
        
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('Comparación de Costos Operacionales', fontsize=16)
        plt.axis('equal')  # Para que el gráfico sea un círculo
        
        # Mostrar el gráfico en Streamlit
        st.pyplot(plt)