import streamlit as st
import pandas as pd
import folium
from folium.plugins import Draw, MarkerCluster # <--- 1. Importamos MarkerCluster
from streamlit_folium import st_folium
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import random

# 1. Configuración de la página
st.set_page_config(layout="wide")

# ==============================================================================
# 1. CONFIGURACIÓN Y AUTENTICACIÓN
# ==============================================================================

try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Archivo de configuración 'config.yaml' no encontrado. Asegúrate de crearlo.")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 2. Pantalla de Login
try:
    authenticator.login('main')
except Exception as e:
    st.error(e)

if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
elif st.session_state["authentication_status"]:
    # --- APLICACIÓN PRINCIPAL ---
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Welcome *{st.session_state["name"]}*')

    st.title("Barrios de Madrid con clustering")
    st.markdown("Haz clic en un barrio para ver la información en el panel derecho.")

    # --- DATOS DE EJEMPLO (POLÍGONOS) ---
    # Generar 10 ubicaciones aleatorias en España
    nombres = []
    coords_list = []
    descripciones = []
    imagenes_urls = []
    
    # Lista de imágenes de ejemplo para asignar aleatoriamente
    ejemplos_img = [
        'https://i.ibb.co/6P6XyRk/gran-via.jpg', 
        'https://i.ibb.co/5cQ3N6s/plaza-espana.jpg', 
        'https://i.ibb.co/3sS7L7W/sevilla-catedral.jpg' 
    ]

    for i in range(10):
        nombres.append(f"Lugar Aleatorio {i+1}")
        
        # Coordenadas aproximadas de España (Latitud: 36 a 43.5, Longitud: -9 a 3)
        lat = random.uniform(36.0, 43.5)
        lon = random.uniform(-9.0, 3.0)
        
        # Crear un polígono pequeño (cuadrado) alrededor del punto aleatorio
        offset = 0.05  # Tamaño del polígono
        poligono = [
            [lat + offset, lon - offset],
            [lat + offset, lon + offset],
            [lat - offset, lon + offset],
            [lat - offset, lon - offset],
            [lat + offset, lon - offset] # Cerrar el polígono
        ]
        coords_list.append(poligono)
        
        descripciones.append(f"Esta es una descripción generada automáticamente para el Lugar {i+1} situado en España.")
        imagenes_urls.append(random.choice(ejemplos_img))

    data = {
        'nombre': nombres,
        'coords': coords_list,
        'descripcion': descripciones,
        'imagen_url': imagenes_urls
    }

    df = pd.DataFrame(data)

    # --- BUSCADOR ---
    col_search, _ = st.columns([1, 3])
    with col_search:
        st.subheader("Buscador")
        opciones = ['Todos'] + sorted(df['nombre'].unique().tolist())
        seleccion = st.selectbox("Selecciona un barrio:", opciones)

    if seleccion != 'Todos':
        df_display = df[df['nombre'] == seleccion]
    else:
        df_display = df

    # --- CREACIÓN DEL MAPA FOLIUM ---
    if not df_display.empty:
        primer_poligono = df_display.iloc[0]['coords']
        centro_mapa = primer_poligono[0]
        zoom = 14 if seleccion != 'Todos' else 13
    else:
        centro_mapa = [40.4168, -3.7038]
        zoom = 13

    m = folium.Map(location=centro_mapa, zoom_start=zoom)

    # --- CLUSTERING ---
    # 2. Creamos el grupo de clusters y lo añadimos al mapa
    marker_cluster = MarkerCluster().add_to(m)

    # 4. Añadir los polígonos existentes
    for index, row in df_display.iterrows():
        # Calcular centroide para el marcador
        points = row['coords']
        if points:
            lat_c = sum(p[0] for p in points) / len(points)
            lon_c = sum(p[1] for p in points) / len(points)
            centroid = [lat_c, lon_c]
            
            # 3. Añadimos un marcador al cluster (para que funcione el clustering)
            folium.Marker(
                location=centroid,
                tooltip=row['nombre'],
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

        # Añadimos el polígono al mapa (para ver el área)
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
        map_output = st_folium(m, width=None, height=500)

    with col_info:
        st.header("Detalles del Barrio")
        
        if map_output and map_output.get("all_drawings"):
            st.subheader("Nuevo Elemento Dibujado")
            drawings = map_output["all_drawings"]
            if drawings:
                last_drawing = drawings[-1]
                geometry_type = last_drawing['geometry']['type']
                coords = last_drawing['geometry']['coordinates']
                st.write(f"Tipo: {geometry_type}")
                st.write(f"Coordenadas: {coords}")
        
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
