import streamlit as st

import numpy as np
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

def eda_produccion():

    with st.expander(label = "DataFrame - Producción de naranjas españolas - 2002 a 2022", expanded = False):
        df_prod = pd.read_csv(filepath_or_buffer = "sources/produccion_naranjas_2002_2022.csv")
        df_prod["Eficiencia"]= (df_prod["Producción Total"]/df_prod["Superficie Plantación"]).round(2)
     #   st.dataframe(df_prod)
    with st.expander(label = "Mapa de regiones productivas de naranjas", expanded = False):
        df_map = pd.read_csv(filepath_or_buffer = "sources/Map.csv")
        #st.dataframe(df_map)

    # estructura sidebar -------------------------------------------
    year_query = st.sidebar.slider(label     = "Año",
                                   min_value = 2002,
                                   max_value = 2022,
                                   value     = 2022,
                                   step      = 1)
    # Radio Buttons
    vista = st.sidebar.radio(label = "Datos totales o por comunidades",
                             options = ("Producción", "Eficiencia"),
                             index = 0,
                             disabled = False,
                             horizontal = True,
                      )
    # desplegable de comunidades
    query_prod_comunidad = df_prod[df_prod['Año']== year_query]
    comunidades = [comunidad for comunidad in df_prod['Comunidad'].unique()]
    autonomic_query = st.sidebar.selectbox("Comunidades autónomas", options = comunidades)
    # escala logaritmica
    st.sidebar.write('Para producción total, producción/plantación y provincias')
    s_log = st.sidebar.checkbox("Escala Logarítmica")
    # activa overlay
    st.sidebar.write('Para provincias agrupadas')
    bar_mode = st.sidebar.checkbox("Overlay")
    if bar_mode == True:
        bar_overlay= 'overlay'
    else:
        bar_overlay = 'group'
    # fin sidebar general ------------------------------------------ 

    st.header("Total de Producción de Naranjas :tangerine:")
    # para mostrar solo graficos totales
    if vista == "Producción":
        st.write("Las comunidades principales en producción de naranjas se encuentran en zonas costeras, con excepción de Asturias y País Vasco, siendo las naranjas provenientes mayoritariamente de la Comunidad Valenciana y Andalucía.")
        pcol1, pcol2 = st.columns([2,1])
        with pcol1:

            query_prod_comunidad = df_prod[df_prod['Año']== year_query]
            query_prod_comunidad_group = query_prod_comunidad.groupby('Comunidad').sum()
            query_prod_comunidad_sum = query_prod_comunidad_group['Producción Total'].values
            query_prod_comunidad_plot = pd.DataFrame(
                {
                    'Comunidad' : pd.Series([query_prod_comunidad_group.index[i] for i in range(len(query_prod_comunidad_group))]),
                    'Producción Total': query_prod_comunidad_sum
                })
            if s_log == False:
                title_escala = f"Total anual producido por comunidad, en {year_query}"
            else:
                title_escala = f"Total anual producido por comunidad, en {year_query}, en escala logarítmica (media: {query_prod_comunidad_sum.mean().round(2)})"

            fig_prod_comunidad = px.histogram(query_prod_comunidad_plot,
                                              x = 'Comunidad',
                                              y = "Producción Total",
                                              color = 'Comunidad',
                                              color_discrete_sequence=px.colors.sequential.Oranges,
                                              log_y = s_log,
                                              title = title_escala,
                                              template = 'plotly_dark'
                                               )
            fig_prod_comunidad.add_hline(y= query_prod_comunidad_sum.mean(),
                                         line_dash= "dot",
                                         annotation_text=(f"Producción media: {query_prod_comunidad_sum.mean().round(2)}"),
                                         annotation_position= "top left")

            st.plotly_chart(figure_or_data = fig_prod_comunidad, use_container_width = True)

        # para mostrar graficos desagregados
        with pcol2:
            fig_prod_provincias = px.histogram(query_prod_comunidad[query_prod_comunidad['Comunidad']==autonomic_query],
                                              x = 'Provincias',
                                              y = "Producción Total",
                                              color = "Provincias",
                                              color_discrete_sequence=px.colors.sequential.Oranges_r,
                                              #log_y = True,
                                              title = f"Total anual producido por provincia, dentro de {autonomic_query}, en {year_query}",
                                              template = 'plotly_dark'
                                               )
            fig_prod_provincias.add_hline(y= query_prod_comunidad[query_prod_comunidad['Comunidad']==autonomic_query]['Producción Total'].mean(),
                                         line_dash= "dot",
                                         annotation_text=(f"Producción media: {query_prod_comunidad[query_prod_comunidad['Comunidad']==autonomic_query]['Producción Total'].mean().round(2)}"),
                                         annotation_position= "top left")

            st.plotly_chart(figure_or_data = fig_prod_provincias, use_container_width = True)

        pcol3, pcol4 = st.columns([2,2])
        with pcol3:
            # Filtramos dataframe por año selecionado
            year_data = df_map[df_map["Año"] == year_query]

            # Mapa de Folium centrada en España
            m = folium.Map(location=[40.4168, 0.0], zoom_start=5.5)

            icon_image = "sources/orange.png"
            for index, row in year_data.iterrows():
                display_info = f"Año: {year_query}, Provincia: {row['Provincias']}, Producción: {row['Producción Total']} toneladas"
                coords = (row["Latitude"], row["Longitude"])
                folium.Marker(coords, icon=folium.CustomIcon(icon_image, icon_size=(50, 50)), popup=display_info).add_to(m)
            st_folium(fig = m, width = 1000)

        with pcol4:
            # correlación anual por comunidades [df_prod["Comunidad"]== autonomic_query]
            df_prod_cols = ['temp', 'dew', 'humidity', 'precip', 'solarradiation', 'solarenergy', 'hours_of_light', 'Provincias', 'Comunidad','Superficie Plantación', 'Producción Total', 'Eficiencia']
            fig_corr_anual = px.imshow(df_prod[df_prod["Año"]== year_query][df_prod['Eficiencia']!=np.inf][df_prod_cols]._get_numeric_data().corr().round(2),
                                       text_auto = True,
                                       color_continuous_scale= px.colors.diverging.Geyser,
                                       title= f"Correlación de variables climáticas y de producción, en {year_query}",
                                       template = 'plotly_dark'
                                       )
            fig_corr_anual.update_layout(
                                        width  = 600,
                                        height = 600)
            st.plotly_chart(figure_or_data = fig_corr_anual, use_container_width = True)

    elif vista == "Eficiencia":
        # agrega parametros en sidebar para eficiencia
        comun_prov = st.sidebar.radio(label = "Provincias individuales o agrupadas",
                                      options = ("Comunidad", "Provincia"),
                                      index = 0,
                                      disabled = False,
                                      horizontal = True,
                          )
        if comun_prov == 'Provincia':
            # selector de provincias
            provincias = [provincia for provincia in df_prod[df_prod['Comunidad']== autonomic_query]['Provincias'].unique()]
            province_query = st.sidebar.selectbox("Provincias", options = provincias)

        # graficos
        gefcol1, gefcol2 = st.columns([2,2])
        with gefcol1:
            # graficos generales de vista de eficiencia
            fig_precip_eficiency = px.scatter(df_prod[df_prod["Comunidad"]==autonomic_query],
                                              x= ("Producción Total"),
                                              y= ("Eficiencia"),
                                              hover_name= "Provincias",
                                              hover_data = ['Producción Total', 'Año'],
                                              size= "precip",
                                              color= "Provincias",
                                              color_discrete_sequence= ['OrangeRed','DarkOrange','Orange','NavajoWhite'],
                                              title= f"Eficiencia expresada en toneladas por hectárea y precipitaciones por provincias de {autonomic_query}",
                                              template = 'plotly_dark')
            st.plotly_chart(figure_or_data = fig_precip_eficiency, use_container_width = True)

        with gefcol2:
            fig_prod_plant = px.scatter(df_prod,
                                        x           = "Producción Total",
                                        y           = "Superficie Plantación",
                                        symbol      = 'Comunidad',
                                        color       = 'Comunidad',
                                        color_discrete_sequence= px.colors.sequential.Oranges,
                                        hover_name  = "Provincias",
                                        log_x       = s_log,
                                        log_y       = s_log,
                                        opacity     = 0.5,
                                        title       = 'Producción total en relación a la superficie de plantación',
                                        template = 'plotly_dark'
                                        )
            st.plotly_chart(figure_or_data = fig_prod_plant, use_container_width = True)

        # comunidades
        if comun_prov == 'Comunidad':
            # eficiencia en toneladas por comunidad
            fig_prod_eficiency_com = px.bar(df_prod[df_prod["Comunidad"]==autonomic_query], #[df_prod["Provincias"]==province_query]
                                        x= ("Año"),
                                        y= ("Eficiencia"),
                                        hover_name= "Provincias",
                                        hover_data = ['Producción Total'],
                                        barmode = bar_overlay,
                                        log_y = False,
                                        color= "Provincias",
                                        color_discrete_sequence= ['OrangeRed','DarkOrange','Orange','NavajoWhite'],
                                        title= f"Eficiencia por años expresada en toneladas por hectárea dentro de {autonomic_query}",
                                        template = 'plotly_dark')

            if df_prod[df_prod['Comunidad']==autonomic_query][df_prod['Eficiencia']!=np.inf]['Eficiencia'].mean() > 0:
                fig_prod_eficiency_com.add_hline(y= df_prod[df_prod['Comunidad']==autonomic_query][df_prod['Eficiencia']!=np.inf]['Eficiencia'].mean(),
                                             line_dash = 'dot',
                                             annotation_text = f"Eficiencia media: {df_prod[df_prod['Comunidad']==autonomic_query][df_prod['Eficiencia']!=np.inf]['Eficiencia'].mean().round(2)}",
                                             annotation_position = 'top left')
            st.plotly_chart(figure_or_data = fig_prod_eficiency_com, use_container_width = True)
            st.write('La produccion por hectárea a nivel mundial oscilan entre 7 a 25 ton, España en algunas comunidades destacan con hasta 57ton/ha en la provincia de Barcelona.')
            
            # precipitaciones por comunidad
            fig_precip_com = px.bar(data_frame= df_prod[df_prod["Comunidad"]== autonomic_query], # [df_prod["Provincias"]== province_query]
                                x= "Año",
                                y= "precip",
                                color= "precip",
                                hover_name = 'Provincias',
                                barmode= bar_overlay,
                                color_continuous_scale="Blues",
                                title = f"Precipitaciones por provincias de {autonomic_query}",
                                template = 'plotly_dark'
                                )
            
            if df_prod[df_prod['Comunidad']== autonomic_query]['precip'].mean() > 0:
                fig_precip_com.add_hline(y = df_prod[df_prod["Comunidad"]== autonomic_query]['precip'].mean(),
                                     line_dash = 'dot',
                                     line_color = 'DarkOrange',
                                     annotation_text = f"Precipitación media: {df_prod[df_prod['Comunidad']== autonomic_query]['precip'].mean().round(2)}",
                                     annotation_position = 'top left',
                                     annotation_font_color = 'NavajoWhite'
                                     )
            st.plotly_chart(figure_or_data = fig_precip_com, use_container_width = True)
            st.write('Para poder cubrir requerimientos del recurso hidrico en la mayoria de las provincias, los agricultores recurren a tecnicas de riego, las cuales permiten solventar la escacez de las lluvias según sea el caso, es por ello que las producciones totaltes no se ven afectadas cuando hay pocas precipitaciones.')
            
            # relacion temperatura y produccion por comunidad
            fig_prod_temp_com = px.scatter(df_prod[df_prod['Comunidad']==autonomic_query], #[df_prod['Comunidad]==autonomic_query]
                                       x           = "Producción Total",
                                       y           = "temp",
                                       size        = "Producción Total",
                                       color       = "Provincias",
                                       color_discrete_sequence= ['OrangeRed','DarkOrange','Orange','NavajoWhite'],
                                       hover_name  = "Provincias",
                                       hover_data  = ["Año"],
                                       opacity     = 0.8,
                                       title       = f"Relación entre producción y temperatura, en {autonomic_query}",
                                       template = 'plotly_dark')
            st.plotly_chart(figure_or_data = fig_prod_temp_com, use_container_width = True)
            st.write('Las temperaturas van en concordancia con respecto a los requerimientos de temperatura ideales para la producción de naranjas como fruta subtropical, entre los 15 y 20°C')
        # provincias
        else:
            # eficiencia de produccion por provincia
            fig_prod_eficiency_prov = px.bar(df_prod[df_prod["Provincias"]==province_query], #[df_prod["Provincias"]==province_query]
                                        x= ("Año"),
                                        y= ("Eficiencia"),
                                        hover_name= "Provincias",
                                        hover_data = ['Producción Total'],
                                        log_y = s_log,
                                        color= "Eficiencia",
                                        color_continuous_scale = px.colors.sequential.Oranges,
                                        title= f"Eficiencia por años expresada en toneladas por hectárea dentro de {autonomic_query}",
                                        template = 'plotly_dark')
            if df_prod[df_prod['Provincias']==province_query][df_prod['Eficiencia']!=np.inf]['Eficiencia'].mean() > 0:
                fig_prod_eficiency_prov.add_hline(y= df_prod[df_prod['Provincias']==province_query][df_prod['Eficiencia']!=np.inf]['Eficiencia'].mean(),
                                             line_dash = 'dot',
                                             annotation_text = f"Eficiencia media: {df_prod[df_prod['Provincias']==province_query][df_prod['Eficiencia']!=np.inf]['Eficiencia'].mean().round(2)}",
                                             annotation_position = 'top left')
            st.plotly_chart(figure_or_data = fig_prod_eficiency_prov, use_container_width = True)
            st.write('La produccion por hectárea a nivel mundial oscilan entre 7 a 25 ton, España en algunas comunidades destacan con hasta 57ton/ha en la provincia de Barcelona.')
            
            # precipitaciones por provincia
            fig_precip_prov = px.bar(df_prod[df_prod["Provincias"]== province_query], # [df_prod["Provincias"]== province_query]
                                    x= "Año",
                                    y= "precip",
                                    log_y = s_log,
                                    color= "precip",
                                    color_continuous_scale="Blues",
                                    title = f"Precipitaciones de {province_query} de {autonomic_query}",
                                    template = 'plotly_dark'
                                    )
            if df_prod[df_prod['Provincias']== province_query]['precip'].mean() > 0:
                fig_precip_prov.add_hline(y = df_prod[df_prod['Provincias']== province_query]['precip'].mean(),
                                     line_dash = 'dot',
                                     line_color = 'DarkOrange',
                                     annotation_text = f"Precipitación media: {df_prod[df_prod['Provincias']== province_query]['precip'].mean().round(2)}",
                                     annotation_position = 'top left',
                                     annotation_font_color = 'NavajoWhite'
                                     )
            st.plotly_chart(figure_or_data = fig_precip_prov, use_container_width = True)
            st.write('Para poder cubrir requerimientos del recurso hidrico en la mayoria de las provincias, los agricultores recurren a tecnicas de riego, las cuales permiten solventar la escacez de las lluvias según sea el caso, es por ello que las producciones totaltes no se ven afectadas cuando hay pocas precipitaciones.')
            
            # relacion temperatura y produccion por provincia
            fig_prod_temp_com = px.scatter(df_prod[df_prod['Provincias']==province_query],
                                       x           = "Producción Total",
                                       y           = "temp",
                                       size        = "Producción Total",
                                       color       = 'temp',
                                       color_continuous_scale= px.colors.sequential.Oranges,
                                       hover_data  = ["Año"],
                                       opacity     = 0.8,
                                       title = f"Relación entre producción y temperatura, en {province_query}",
                                       template = 'plotly_dark')
            st.plotly_chart(figure_or_data = fig_prod_temp_com, use_container_width = True)
            st.write('Las temperaturas van en concordancia con respecto a los requerimientos de temperatura ideales para la producción de naranjas como fruta subtropical, entre los 15 y 20°C')

# hasta aqui!!!!-----------------------------------------------------------------
if __name__ == "__eda_produccion__":
    eda_produccion()