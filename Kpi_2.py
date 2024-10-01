# Importación de librerias
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Importamos el dataset 
df_costo = pd.read_csv('./Data/costo_operacional_vehiculos_clean.csv')

# Función para categorizar los vehículos
def categorize_vehicle(row):
    if row['Fuel_Type'] in ['Diesel', 'Petrol', 'Petrol/LPG']:
        return 'Convencional'
    elif row['Fuel_Type'] == 'Electricity':
        return 'Eléctrico'
    else:
        return 'Híbrido'
# Aplicamos la función para categorizar los vehículos
df_costo['Vehicle_Type'] = df_costo.apply(categorize_vehicle, axis=1)

# Sidebar con filtros
st.sidebar.title("Opciones de Filtro")

# Filtramos por vehículo y tipo de vehículo 
Fabricantes = df_costo['Manuf'].unique().tolist()
Tipos_vehiculos = df_costo['Vehicle_Type'].unique().tolist()
#Insertamnos la opción de todos
Fabricantes.insert(0, 'Todos')
Tipos_vehiculos.insert(0, 'Todos')
# Interacción con el usuario 
Fabricante_selec = st.sidebar.selectbox('Seleccione un fabricante', Fabricantes)
Tipos_v_selec = st.sidebar.selectbox('Seleccione el tipo de vehículo', Tipos_vehiculos)

#Filtrar el dataset con los datos seleccionados 
# Filtrar dataset con los filtros seleccionados
df_filtrado = df_costo.copy()
if Fabricante_selec != 'Todos' :
    df_filtrado = df_filtrado[df_filtrado['Manuf'] == Fabricante_selec]
if Tipos_v_selec != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Vehicle_Type'] == Tipos_v_selec]


# Promedio de costo de cada tipo de combustible
costo_promedio_convencional = df_filtrado[df_filtrado['Vehicle_Type'] == 'Convencional']['Total_Cost'].mean()
costo_promedio_electrico = df_filtrado[df_filtrado['Vehicle_Type'] == 'Eléctrico']['Total_Cost'].mean()
costo_promedio_hibrido = df_filtrado[df_filtrado['Vehicle_Type'] == 'Híbrido']['Total_Cost'].mean()

# Calcular reducciones
reduccion_electrico = costo_promedio_convencional - costo_promedio_electrico if costo_promedio_electrico else None
reduccion_hibrido = costo_promedio_convencional - costo_promedio_hibrido if costo_promedio_hibrido else None

# Calcular porcentaje de ahorro
porcentaje_ahorro_electrico = (reduccion_electrico / costo_promedio_convencional) * 100 if reduccion_electrico else None
porcentaje_ahorro_hibrido = (reduccion_hibrido / costo_promedio_convencional) * 100 if reduccion_hibrido else None

# Título
st.title(f"Dashboard de Costos Operativos - {Fabricante_selec}")

# Mostrar KPIs en columnas para un estilo más visual
col1, col2, col3 = st.columns(3)

if reduccion_electrico:
    col1.metric(label="Reducción de costos (Eléctricos)", value=f"${reduccion_electrico:.2f}")
    col2.metric(label="Ahorro porcentual (Eléctricos)", value=f"{porcentaje_ahorro_electrico:.2f}%")
if reduccion_hibrido:
    col3.metric(label="Reducción de costos (Híbridos)", value=f"${reduccion_hibrido:.2f}")
    col2.metric(label="Ahorro porcentual (Híbridos)", value=f"{porcentaje_ahorro_hibrido:.2f}%")

# Gráfico con Plotly para comparación de costos
st.subheader(f"Comparación de Costos Operativos por Tipo de Vehículo ({Fabricante_selec})")

fig = px.bar(df_filtrado, x='Vehicle_Type', y='Total_Cost', color='Vehicle_Type',
             color_discrete_map={'Eléctrico': '#f9f9f9', 'Híbrido': '#FEC601', 'Convencional': '#333333'},
             title="Costos Operativos por Tipo de Vehículo",
             labels={'Total_Cost': 'Costo Operativo Anual', 'Vehicle_Type': 'Tipo de Vehículo'})

fig.update_layout(
    plot_bgcolor='#1E1E1E', 
    paper_bgcolor='#1E1E1E',
    font_color="#333333",
    title_font=dict(size=20, color='#1E1E1E')
)

st.plotly_chart(fig)