import streamlit as st
import pandas as pd
import folium
from folium.plugins import Draw, MarkerCluster # <--- 1. Importamos MarkerCluster
from streamlit_folium import st_folium
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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
    data = {
    'nombre': [
        'Sol', 'Malasaña', 'Retiro', 
        'La Latina', 'Chueca', 'Barrio de Salamanca', 
        'Lavapiés', 'Chamberí', 'Moncloa', 'Madrid Río',
        # Nuevas entradas - Asturias (5)
        'Gijón - Playa de San Lorenzo', 'Oviedo - Casco Antiguo', 'Lagos de Covadonga', 
        'Cangas de Onís - Puente Romano', 'Ribadesella',
        # Nuevas entradas - Cataluña (5)
        'Barcelona - Barrio Gótico', 'Girona - Casas del Oñar', 'Tarragona - Anfiteatro', 
        'Sitges - Playa de Sant Sebastià', 'Montserrat',
        # Nuevas entradas - Otras Comunidades (10)
        'Sevilla - Giralda y Catedral', 'Granada - Alhambra', 'Bilbao - Museo Guggenheim',
        'San Sebastián - Playa de La Concha', 'Santiago de Compostela - Catedral',
        'Valencia - Ciudad de las Artes y las Ciencias', 'Cáceres - Ciudad Vieja',
        'Toledo - Casco Histórico', 'Pamplona - Plaza del Castillo', 'Palma de Mallorca - Catedral'
    ],
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
        ],
        [ # La Latina (aproximado)
            [40.4140, -3.7120], [40.4140, -3.7060],
            [40.4080, -3.7060], [40.4080, -3.7120], [40.4140, -3.7120]
        ],
        [ # Chueca (aproximado)
            [40.4250, -3.7000], [40.4250, -3.6940],
            [40.4200, -3.6940], [40.4200, -3.7000], [40.4250, -3.7000]
        ],
        [ # Barrio de Salamanca (aproximado)
            [40.4350, -3.6900], [40.4350, -3.6700],
            [40.4250, -3.6700], [40.4250, -3.6900], [40.4350, -3.6900]
        ],
        [ # Lavapiés (aproximado)
            [40.4120, -3.7040], [40.4120, -3.6980],
            [40.4060, -3.6980], [40.4060, -3.7040], [40.4120, -3.7040]
        ],
        [ # Chamberí (aproximado)
            [40.4400, -3.7100], [40.4400, -3.6900],
            [40.4300, -3.6900], [40.4300, -3.7100], [40.4400, -3.7100]
        ],
        [ # Moncloa (aproximado)
            [40.4400, -3.7250], [40.4400, -3.7120],
            [40.4300, -3.7120], [40.4300, -3.7250], [40.4400, -3.7250]
        ],
        [ # Madrid Río (aproximado)
            [40.4000, -3.7200], [40.4000, -3.6900],
            [40.3900, -3.6900], [40.3900, -3.7200], [40.4000, -3.7200]
        ],
        # Nuevas Coordenadas - Asturias (5)
        [[43.5468, -5.6565]], # Gijón - Playa de San Lorenzo (Punto)
        [[43.3619, -5.8449]], # Oviedo - Casco Antiguo (Punto)
        [[43.2736, -4.9806]], # Lagos de Covadonga (Punto)
        [[43.3516, -5.0743]], # Cangas de Onís - Puente Romano (Punto)
        [[43.4616, -5.0600]], # Ribadesella (Punto)
        # Nuevas Coordenadas - Cataluña (5)
        [[41.3823, 2.1764]], # Barcelona - Barrio Gótico (Punto)
        [[41.9831, 2.8239]], # Girona - Casas del Oñar (Punto)
        [[41.1171, 1.2562]], # Tarragona - Anfiteatro (Punto)
        [[41.2330, 1.8080]], # Sitges - Playa de Sant Sebastià (Punto)
        [[41.6027, 1.8364]], # Montserrat (Punto)
        # Nuevas Coordenadas - Otras Comunidades (10)
        [[37.3860, -5.9965]], # Sevilla - Giralda y Catedral (Punto)
        [[37.1760, -3.5930]], # Granada - Alhambra (Punto)
        [[43.2687, -2.9348]], # Bilbao - Museo Guggenheim (Punto)
        [[43.3175, -1.9866]], # San Sebastián - Playa de La Concha (Punto)
        [[42.8804, -8.5458]], # Santiago de Compostela - Catedral (Punto)
        [[39.4650, -0.3556]], # Valencia - Ciudad de las Artes y las Ciencias (Punto)
        [[39.4751, -6.3725]], # Cáceres - Ciudad Vieja (Punto)
        [[39.8567, -4.0245]], # Toledo - Casco Histórico (Punto)
        [[42.8166, -1.6441]], # Pamplona - Plaza del Castillo (Punto)
        [[39.5694, 2.6502]]  # Palma de Mallorca - Catedral (Punto)
    ],
    'descripcion': [
        'El corazón turístico y comercial de Madrid, donde se encuentra el Km 0.',
        'Barrio bohemio y moderno, famoso por su vida nocturna y cultura pop.',
        'El pulmón verde del centro de Madrid, ideal para pasear y relajarse.',
        'Barrio castizo por excelencia, famoso por el Rastro y sus tapas.',
        'Conocido por su ambiente LGTBI+, tiendas de moda y animada vida nocturna.',
        'Una de las zonas más exclusivas, con la Milla de Oro y edificios señoriales.',
        'Barrio multicultural y bohemio, lleno de arte urbano y gastronomía internacional.',
        'Zona residencial tradicional con arquitectura aristocrática y la plaza de Olavide.',
        'Ambiente universitario, cerca de la Ciudad Universitaria y el Faro de Moncloa.',
        'Gran parque lineal a lo largo del Manzanares, ideal para deporte y ocio familiar.',
        # Nuevas Descripciones - Asturias (5)
        'El arenal urbano más famoso de Gijón, ideal para paseos y surf.',
        'El corazón de la capital asturiana, con la Catedral y la ruta de la sidra.',
        'Impresionantes lagos glaciares en los Picos de Europa, icono del Parque Nacional.',
        'Antigua calzada romana y emblemático puente con la Cruz de la Victoria colgante.',
        'Encantador pueblo costero famoso por su descenso internacional en canoa y su casco histórico.',
        # Nuevas Descripciones - Cataluña (5)
        'El distrito más antiguo de Barcelona, con estrechas calles medievales y la Catedral.',
        'Famosas casas de colores colgadas sobre el río Oñar, postal de la ciudad.',
        'Espectacular ruina romana frente al mar Mediterráneo, testigo de la Tarraco imperial.',
        'Famosa playa de Sitges, conocida por su ambiente festivo, palmeras y el barrio de pescadores.',
        'Montaña mágica con formas singulares que alberga un monasterio benedictino y un parque natural.',
        # Nuevas Descripciones - Otras Comunidades (10)
        'Conjunto monumental Patrimonio de la Humanidad, emblema de Sevilla con su minarete alzado.',
        'Impresionante complejo palaciego y fortaleza, joya del arte nazarí y andaluz.',
        'Famoso museo de arte contemporáneo con una arquitectura vanguardista de titanio.',
        'Una de las playas urbanas más bellas de Europa, con su característica barandilla blanca.',
        'Destino de peregrinación, hogar de la tumba del Apóstol Santiago y final del Camino.',
        'Complejo arquitectónico futurista, obra de Calatrava, dedicado a la ciencia y la cultura.',
        'Conjunto histórico-artístico medieval amurallado, con un gran estado de conservación.',
        'Ciudad de las Tres Culturas, con un legado monumental de mezquitas, sinagogas e iglesias.',
        'El corazón social y neurálgico de Pamplona, centro de reunión y referencia en Sanfermines.',
        'Imponente catedral gótica de Mallorca, conocida como La Seu, frente a la bahía.'
    ],
    'imagen_url': [
        'https://i.ibb.co/6P6XyRk/gran-via.jpg', 
        'https://i.ibb.co/5cQ3N6s/plaza-espana.jpg', 
        'https://i.ibb.co/3sS7L7W/sevilla-catedral.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Madrid_-_La_Latina_-_Plaza_de_la_Cebada.jpg/640px-Madrid_-_La_Latina_-_Plaza_de_la_Cebada.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Plaza_de_Chueca_%28Madrid%29_01.jpg/640px-Plaza_de_Chueca_%28Madrid%29_01.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Calle_de_Serrano_%28Madrid%29_01.jpg/640px-Calle_de_Serrano_%28Madrid%29_01.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Calle_de_Argumosa_%28Madrid%29_02.jpg/640px-Calle_de_Argumosa_%28Madrid%29_02.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Plaza_de_Olavide_%28Madrid%29_03.jpg/640px-Plaza_de_Olavide_%28Madrid%29_03.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Faro_de_Moncloa_%28Madrid%29_04.jpg/640px-Faro_de_Moncloa_%28Madrid%29_04.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Madrid_R%C3%ADo_-_Puente_de_Arganzuela.jpg/640px-Madrid_R%C3%ADo_-_Puente_de_Arganzuela.jpg',
        # Nuevas URLs - Asturias (5)
        'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Playa_de_San_Lorenzo_%28Gij%C3%B3n%29.jpg/640px-Playa_de_San_Lorenzo_%28Gij%C3%B3n%29.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Catedral_de_San_Salvador_de_Oviedo_%28fachada%29.jpg/640px-Catedral_de_San_Salvador_de_Oviedo_%28fachada%29.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Lagos_de_Covadonga_-_Lago_Ercina.jpg/640px-Lagos_de_Covadonga_-_Lago_Ercina.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Puente_romano_de_Cangas_de_On%C3%ADs.jpg/640px-Puente_romano_de_Cangas_de_On%C3%ADs.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Ribadesella_vista_desde_el_Puente.JPG/640px-Ribadesella_vista_desde_el_Puente.JPG',
        # Nuevas URLs - Cataluña (5)
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Barcelona_-_Barri_G%C3%B2tic_-_Pla%C3%A7a_de_Sant_Felip_Neri.jpg/640px-Barcelona_-_Barri_G%C3%B2tic_-_Pla%C3%A7a_de_Sant_Felip_Neri.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Girona-Houses_on_the_River_Onyar.jpg/640px-Girona-Houses_on_the_River_Onyar.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Anfiteatro_romano_de_Tarragona.jpg/640px-Anfiteatro_romano_de_Tarragona.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Sitges_-_Playa_Sant_Sebasti%C3%A0_y_Iglesia.jpg/640px-Sitges_-_Playa_Sant_Sebasti%C3%A0_y_Iglesia.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Montserrat_-_Visi%C3%B3_del_Monestir.jpg/640px-Montserrat_-_Visi%C3%B3_del_Monestir.jpg',
        # Nuevas URLs - Otras Comunidades (10)
        'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Catedral_de_Sevilla_y_Giralda_al_atardecer.jpg/640px-Catedral_de_Sevilla_y_Giralda_al_atardecer.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Palacios_Nazaries_%28Granada%29.jpg/640px-Palacios_Nazaries_%28Granada%29.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Museo_Guggenheim_Bilbao.jpg/640px-Museo_Guggenheim_Bilbao.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Playa_de_la_Concha_-_Donostia-San_Sebasti%C3%A1n.jpg/640px-Playa_de_la_Concha_-_Donostia-San_Sebasti%C3%A1n.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Santiago_de_Compostela_-_Catedral_fachada.jpg/640px-Santiago_de_Compostela_-_Catedral_fachada.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Ciudad_de_las_Artes_y_las_Ciencias_-_Valencia.jpg/640px-Ciudad_de_las_Artes_y_las_Ciencias_-_Valencia.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Plaza_de_Santa_Mar%C3%ADa_%28C%C3%A1ceres%29.jpg/640px-Plaza_de_Santa_Mar%C3%ADa_%28C%C3%A1ceres%29.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Puente_de_San_Mart%C3%ADn%2C_Toledo.jpg/640px-Puente_de_San_Mart%C3%ADn%2C_Toledo.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Plaza_del_Castillo_-_Pamplona.jpg/640px-Plaza_del_Castillo_-_Pamplona.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Palma_-_Catedral.jpg/640px-Palma_-_Catedral.jpg'
    ]
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
    if seleccion == 'Todos':
        centro_mapa = [40.4637, -3.7492] # Centro aproximado de España
        zoom = 6 # Zoom alejado para ver todo el país
    elif not df_display.empty:
        primer_poligono = df_display.iloc[0]['coords']
        centro_mapa = primer_poligono[0]
        zoom = 14
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
        # Solo si tiene más de 2 puntos (es un polígono real)
        if len(points) > 2:
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
