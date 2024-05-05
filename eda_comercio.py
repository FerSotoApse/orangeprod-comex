import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


def eda_comercio():

    with st.expander(label = "DataFrame - Flujo comercial de naranjas españolas - 2002 a 2023", expanded = False):
        df_comex = pd.read_csv(filepath_or_buffer = "sources/comex_2002_2024.csv", encoding="latin-1")

    # estructura de querys en sidebar ---------------------
    vista = st.sidebar.radio(label = "Vistas de flujo comercial",
                     options = ('Transporte', 'Paises'),
                     index = 0,
                     disabled = False,
                     horizontal = True,
                     )    
    year_query = st.sidebar.slider(label     = "Año",
                                   min_value = 2002,
                                   max_value = 2023,
                                   value     = 2023,
                                   step      = 1)

    st.header("Flujo comercial de naranjas")
    # cierre querys generales del sidebar ------------------ 

    # parte 1 flujo comercial: mapa, modo de transporte y volumen en toneladas al año
    if vista == 'Transporte':
        selectperiod_query = st.sidebar.radio(label = "Periodo de Modo de Transporte",
                                      options = ('Anual','Mensual'),
                                      index = 0,
                                      disabled = False,
                                      horizontal = True,
                                      )
        if selectperiod_query == 'Mensual':
            month_query = st.sidebar.slider(label     = "Mes",
                                           min_value  = 1,
                                           max_value  = 12,
                                           value      = 1,
                                           step       = 1)
            months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
            month_desc = months[month_query-1]
            if month_query < 10:
                month_query = f"0{month_query}"
        flow_query = st.sidebar.radio(label = "Mapa: Exportación - Importación",
                                      options = ('X','M'),
                                      index = 0,
                                      disabled = False,
                                      horizontal = True,
                                      )

        tcol1, tcol2 = st.columns([2,2])
        # consultas para crear el mapa de burbujas de exportacion e importacion
        with tcol1:
            with st.container():
                if selectperiod_query == 'Anual':
                    map_query = df_comex[df_comex["FlowCode"]== flow_query][df_comex['datetime']>=f"{year_query}-01"][df_comex['datetime']<=f"{year_query}-12"]
                    map_query_group = map_query.groupby(['FlowDesc','PartnerDesc','PartnerISO']).sum()
                    map_query_sum_1 = map_query_group['Toneladas'].values
                    map_query_sum_2 = map_query_group['Fobvalue'].values
                    map_query_sum_3 = map_query_group['Cifvalue'].values

                    map_query_plot = pd.DataFrame(
                        {
                            'PartnerDesc' : pd.Series([map_query_group.index[i][1] for i in range(len(map_query_group))]),
                            'PartnerISO' : pd.Series([map_query_group.index[i][2] for i in range(len(map_query_group))]),
                            'Toneladas': map_query_sum_1,
                            'Fobvalue' : map_query_sum_2,
                            'Cifvalue' : map_query_sum_3
                        })

                    fig_scattergeo_comex = px.scatter_geo(map_query_plot,
                                           locations='PartnerISO',
                                           size='Toneladas',
                                           color='Toneladas',
                                           color_continuous_scale=px.colors.sequential.Oranges,
                                           hover_name='PartnerDesc',
                                           hover_data=['Fobvalue' if flow_query=='X' else 'Cifvalue'],
                                           projection='natural earth',
                                           fitbounds="geojson",
                                           title = f"Mapa de {'exportaciones de naranjas desde' if flow_query=='X' else 'importaciones de naranjas de'} España en {year_query}",
                                           template = 'plotly_dark'
                                           )

                    st.plotly_chart(figure_or_data = fig_scattergeo_comex, use_container_width = True)

                else:
                    map_query_month = df_comex[df_comex["FlowCode"]== flow_query][df_comex['datetime']==f"{year_query}-{month_query}-01"]
                    map_query_month_group = map_query_month.groupby(['FlowDesc','PartnerDesc','PartnerISO']).sum()
                    map_query_month_sum_1 = map_query_month_group['Toneladas'].values
                    map_query_month_sum_2 = map_query_month_group['Fobvalue'].values
                    map_query_month_sum_3 = map_query_month_group['Cifvalue'].values

                    map_query_month_plot = pd.DataFrame(
                        {
                            'PartnerDesc' : pd.Series([map_query_month_group.index[i][1] for i in range(len(map_query_month_group))]),
                            'PartnerISO' : pd.Series([map_query_month_group.index[i][2] for i in range(len(map_query_month_group))]),
                            'Toneladas': map_query_month_sum_1,
                            'Fobvalue' : map_query_month_sum_2,
                            'Cifvalue' : map_query_month_sum_3
                        })

                    fig_scattergeo_comex_month = px.scatter_geo(map_query_month_plot,
                                                 locations='PartnerISO',
                                                 size='Toneladas',
                                                 color='Toneladas',
                                                 color_continuous_scale=px.colors.sequential.Oranges,
                                                 hover_name='PartnerDesc',
                                                 hover_data=['Fobvalue' if flow_query=='X' else 'Cifvalue'],
                                                 projection='natural earth',
                                                 fitbounds="geojson",
                                                 title = f"Mapa de {'exportaciones de naranjas desde' if flow_query=='X' else 'importaciones de naranjas de'} España en {month_desc} de {year_query}",
                                                 template = 'plotly_dark'
                                                 )

                    st.plotly_chart(figure_or_data = fig_scattergeo_comex_month, use_container_width = True)
                st.write("Las exportaciones se centran hacia Europa, mientras las importaciones provienen principalmente de África y Sudamérica.")
                
        with tcol2:
            with st.container():
                if selectperiod_query == 'Anual':
                    fig_tm_comex_anual = px.treemap(df_comex[df_comex['datetime']>=f"{year_query}-01-01"][df_comex['datetime']<=f"{year_query}-12-01"],
                                                    path=[px.Constant("Total comercio de naranjas"), 'FlowDesc', 'MotDesc', 'PartnerISO'],
                                                    hover_name='PartnerDesc',
                                                    hover_data=['Toneladas'],
                                                    title= f"Total de naranjas por modo de transporte, importadas y exportadas, en {year_query}",
                                                    template= 'plotly_dark'
                                                    )
                    fig_tm_comex_anual.update_layout(treemapcolorway = ["DarkOrange", "NavajoWhite"])

                    st.plotly_chart(figure_or_data = fig_tm_comex_anual, use_container_width = True)

                else:
                    fig_tm_comex_mensual = px.treemap(df_comex[df_comex["datetime"]==f"{year_query}-{month_query}-01"],
                                                      path=[px.Constant("Total comercio de naranjas"), 'FlowDesc', 'MotDesc', 'PartnerISO'],
                                                      hover_name='PartnerDesc',
                                                      hover_data= ['Toneladas'],
                                                      title= f"Total de naranjas por modo de transporte, importadas y exportadas, en {month_desc} de {year_query}",
                                                      template= 'plotly_dark'
                                                      )
                    fig_tm_comex_mensual.update_layout(treemapcolorway = ["DarkOrange", "NavajoWhite"])
                    st.plotly_chart(figure_or_data = fig_tm_comex_mensual, use_container_width = True)
                                                
                st.write("Las exportaciones se realizan principalmente por carretera, por cercanía a los países que más importan naranjas españolas, desde 2016 comienza a diversificarse los modos de transporte y los países de destino.")
                st.write("Las importaciones provienen principalmente de países cercanos, equiparando en proporción durante los meses fuera de temporada, a través de carreteras y vías marítimas.")
        
        # query de flujo comercial (depende solo de años)
        query_cmx_anual = df_comex[df_comex['datetime']>=f"{year_query}-01"][df_comex['datetime']<=f"{year_query}-12"]
        query_cmx_anual_group = query_cmx_anual.groupby(['FlowDesc','datetime']).sum()
        query_cmx_anual_sum = query_cmx_anual_group['Toneladas'].values
        query_cmx_anual_plot = pd.DataFrame(
        {
            'datetime' : pd.Series([query_cmx_anual_group.index[i][1] for i in range(len(query_cmx_anual_group))]),
            'FlowDesc' : pd.Series([query_cmx_anual_group.index[i][0] for i in range(len(query_cmx_anual_group))]),
            'Toneladas': query_cmx_anual_sum
        })

        # grafico de barras de flujo comercial anual
        fig_cmx_anual= px.bar(query_cmx_anual_plot,
                       x= 'datetime',
                       y= 'Toneladas',
                       color = 'FlowDesc',
                       color_discrete_sequence= ['darkorange','navajowhite'],
                       barmode = "group",
                       #log_y = True,
                       title = f"Comercio de naranjas anual, agregado en meses, en {year_query}",
                       text_auto = True,
                       template = "plotly_dark")

        fig_cmx_anual.update_traces(textangle = 0,
                                    textposition = 'outside')
        # referencia de temporadas temprana y tardía
        fig_cmx_anual.add_vrect(x0=f"{year_query}-10-10",
                                x1=f"{year_query}-12-31",
                                row=1,
                                fillcolor="NavajoWhite",
                                annotation_text="recolección temprana",
                                annotation_position="top left",
                                opacity=0.1,
                                line_width=0)
        fig_cmx_anual.add_vrect(x0=f"{year_query}-01-01",
                                x1=f"{year_query}-03-15",
                                row=1,
                                fillcolor="NavajoWhite",
                                opacity=0.1,
                                line_width=0)
        fig_cmx_anual.add_vrect(x0=f"{year_query}-02-01",
                                x1=f"{year_query}-07-31",
                                row=1,
                                fillcolor="DarkOrange",
                                annotation_text="recolección tardía",
                                annotation_position="top right",
                                opacity=0.1,
                                line_width=0)
        st.plotly_chart(figure_or_data = fig_cmx_anual, use_container_width = True)
        st.write("Las exportaciones son de mayor volumen durante los meses de recolección temprana, decayendo durante la recolección tardía. Las exportaciones fuera de temporada corresponden principalmente a naranjas secas y algunas variedades que quedan resagadas")

    # Parte 2 de flujo comercial: distribucion y serie de tiempo por paises   
    elif vista == 'Paises':
        # sidebar de vista de distribucion de comercio por paises ------------------------------
        # consulta mensual
        month_query = st.sidebar.slider(label     = "Mes",
                                       min_value  = 1,
                                       max_value  = 12,
                                       value      = 1,
                                       step       = 1)
        months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        month_desc = months[month_query-1]
        if month_query < 10:
            month_query = f"0{month_query}"
        # elige en sidebar ver graficos de exportacion o de importacion
        flow_query = st.sidebar.radio(label = "Exportación - Importación",
                                       options = ('X', 'M'),
                                       index = 0,
                                       disabled = False,
                                       horizontal = True,
                                       )
        # aplica escala logaritmica en histograma
        s_log = st.sidebar.checkbox("Escala Logarítmica")
        # cierre sidebar --------------------------------------------------------------------------

        # grafico de barras de flujo comercial separado por flujo comercial, agrupado en paises
        fig_cmx_iso = px.bar(df_comex[df_comex['FlowCode']== flow_query][df_comex['datetime']>=f"{year_query}-01"][df_comex['datetime']<=f"{year_query}-12"],
                             x="datetime",
                             y=["Toneladas"],
                             color = "PartnerISO",
                             color_discrete_sequence=px.colors.sequential.Oranges,
                             hover_name = "PartnerDesc",
                             hover_data=["Fobvalue","Cifvalue"],
                             barmode="overlay",
                             title = f"{'Exportación de naranjas' if flow_query=='X' else 'Importación de naranjas'} España a lo largo de {year_query}, desagregado por países",
                             template = 'plotly_dark')
        # referencia de temporadas temprana y tardía
        fig_cmx_iso.add_vrect(x0=f"{year_query}-10-10",
                              x1=f"{year_query}-12-31",
                              row=1,
                              fillcolor="NavajoWhite",
                              annotation_text="recolección temprana",
                              annotation_position="top left",
                              opacity=0.1,
                              line_width=0)
        fig_cmx_iso.add_vrect(x0=f"{year_query}-01-01",
                              x1=f"{year_query}-03-15",
                              row=1,
                              fillcolor="NavajoWhite",
                              opacity=0.1,
                              line_width=0)
        fig_cmx_iso.add_vrect(x0=f"{year_query}-02-01",
                              x1=f"{year_query}-07-31",
                              row=1,
                              fillcolor="DarkOrange",
                              annotation_text="recolección tardía",
                              annotation_position="top right",
                              opacity=0.1,
                              line_width=0)
        st.plotly_chart(figure_or_data = fig_cmx_iso, use_container_width = True)
        st.write("Los 2 mayores importadores de naranjas españolas son Alemania y Francia, mientras que España importa durante temporada tardía a países como Portugal, Sudáfrica y Argentina, además de otros países cercanos.")
        
        # histograma de importacion y exportacion mensual, por paises
        if s_log == False:
            title_escala = f"{'Exportación de naranjas' if flow_query=='X' else 'Importación de naranjas'}, distribuido por países, en {month_desc} de {year_query} (escala real)"
        else:
            title_escala = f"{'Exportación de naranjas' if flow_query=='X' else 'Importación de naranjas'}, distribuido por países, en {month_desc} de {year_query}, en escala logarítmica (media: {df_comex[df_comex['datetime']==f'{year_query}-{month_query}-01'][df_comex['FlowCode']== flow_query]['Toneladas'].mean().round(2)})"

        fig_cmx_iso_hist = px.histogram(df_comex[df_comex['FlowCode']== flow_query][df_comex['datetime']==f"{year_query}-{month_query}-01"],
                             x="PartnerISO",
                             y="Toneladas",
                             log_y=s_log,
                             color = "PartnerISO",
                             color_discrete_sequence=px.colors.sequential.Oranges_r,
                             hover_name= "PartnerDesc",
                             hover_data=["Fobvalue","Cifvalue"],
                             title = title_escala,
                             template = 'plotly_dark')

        fig_cmx_iso_hist.add_hline(y= df_comex[df_comex['datetime']==f"{year_query}-{month_query}-01"][df_comex['FlowCode']== flow_query]['Toneladas'].mean(),
                                     line_dash= "dot",
                                     col = 1,
                                     annotation_text=(f"{'Exportación' if flow_query=='X' else 'Importación'} media: {df_comex[df_comex['datetime']==f'{year_query}-{month_query}-01'][df_comex['FlowCode']== flow_query]['Toneladas'].mean().round(2)}"),
                                     annotation_position= "top left")

        st.plotly_chart(figure_or_data = fig_cmx_iso_hist, use_container_width = True)


if __name__ == "__eda_comercio__":
    eda_comercio()