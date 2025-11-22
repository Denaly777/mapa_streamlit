import streamlit as st
import pandas as pd
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium

# 1. Configuración de la página
st.set_page_config(layout="wide")
st.title("📍 Barrios de Madrid (Polígonos)")
st.markdown("Haz clic en un barrio para ver la información en el panel derecho.")

# --- DATOS DE EJEMPLO (POLÍGONOS) ---
# Coordenadas aproximadas de algunos barrios/zonas
data = {
    'nombre': ['Sol', 'Malasaña', 'Retiro'],
    # Cada 'coords' es una lista de [lat, lon] que define el polígono
    'coords': [
        [ # Sol (aproximado)
           [40.43741, -3.638878], [40.432445, -3.649006], [40.431792, -3.660336], [40.423559, -3.63905], [40.423951, -3.63184], [40.425258, -3.629093], [40.43741, -3.638878]
        ],
        [ # Malasaña (Universidad) (aproximado)
            [40.4260, -3.7080], [40.4280, -3.7020], 
            [40.4230, -3.7010], [40.4210, -3.7060], [40.4260, -3.7080]
        ],
        [ # Parque del Retiro (aproximado)
            [40.4200, -3.6800], [40.4200, -3.6900], 
            [40.4080, -3.6900], [40.4080, -3.6800], [40.4200, -3.6800]
        ]
    ],
    'descripcion': [
        'El corazón turístico y comercial de Madrid, donde se encuentra el Km 0.',
        'Barrio bohemio y moderno, famoso por su vida nocturna y cultura pop.',
        'El pulmón verde del centro de Madrid, ideal para pasear y relajarse.'
    ],
    'imagen_url': [
        'https://i.ibb.co/6P6XyRk/gran-via.jpg', # Placeholder
        'https://i.ibb.co/5cQ3N6s/plaza-espana.jpg', # Placeholder
        'https://i.ibb.co/3sS7L7W/sevilla-catedral.jpg' # Placeholder
    ]
}

df = pd.DataFrame(data)

# --- BUSCADOR ---
st.subheader("Buscador")
opciones = ['Todos'] + sorted(df['nombre'].unique().tolist())
seleccion = st.selectbox("Selecciona un barrio:", opciones)

if seleccion != 'Todos':
    df_display = df[df['nombre'] == seleccion]
else:
    df_display = df

# --- CREACIÓN DEL MAPA FOLIUM ---
# Calculamos el centro aproximado
if not df_display.empty:
    # Tomamos el primer punto del primer polígono para centrar
    primer_poligono = df_display.iloc[0]['coords']
    centro_mapa = primer_poligono[0]
    zoom = 14 if seleccion != 'Todos' else 13
else:
    centro_mapa = [40.4168, -3.7038]
    zoom = 13

m = folium.Map(location=centro_mapa, zoom_start=zoom)

# 4. Añadir los polígonos existentes
for index, row in df_display.iterrows():
    folium.Polygon(
        locations=row['coords'],
        color="blue",
        weight=2,
        fill=True,
        fill_opacity=0.4,
        tooltip=row['nombre']
    ).add_to(m)

# --- HERRAMIENTA DE DIBUJO ---
draw = Draw(
    export=True,
    filename='my_data.geojson',
    position='topleft',
    draw_options={'polyline': False, 'circle': False, 'marker': True, 'circlemarker': False, 'rectangle': True, 'polygon': True},
    edit_options={'poly': {'allowIntersection': False}}
)
draw.add_to(m)

# 5. Mostrar el mapa y el panel en columnas
col_map, col_info = st.columns([3, 1])

with col_map:
    # Se añade return_on_hover=False para evitar recargas excesivas
    map_output = st_folium(m, width=None, height=500)

with col_info:
    st.header("Detalles del Barrio")
    
    # Verificar si se ha dibujado algo nuevo
    if map_output and map_output.get("all_drawings"):
        st.subheader("Nuevo Elemento Dibujado")
        drawings = map_output["all_drawings"]
        if drawings:
            last_drawing = drawings[-1]
            geometry_type = last_drawing['geometry']['type']
            coords = last_drawing['geometry']['coordinates']
            st.write(f"Tipo: {geometry_type}")
            st.write(f"Coordenadas: {coords}")
    
    # Verificar si se ha hecho clic en algún objeto existente
    elif map_output and map_output.get("last_object_clicked_tooltip"):
        clicked_tooltip = map_output.get("last_object_clicked_tooltip")
        
        if clicked_tooltip:
            selected_row = df[df['nombre'] == clicked_tooltip]
            
            if not selected_row.empty:
                row = selected_row.iloc[0]
                st.subheader(row['nombre'])
                st.image(row['imagen_url'], use_column_width=True)
                st.write(row['descripcion'])
            else:
                st.info("No se encontraron datos para la selección.")
    else:
        st.info("Selecciona un barrio o dibuja en el mapa.")

st.sidebar.header("Barrios Añadidos")
st.sidebar.write(df['nombre'])