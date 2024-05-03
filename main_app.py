import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium

from modules.page_config_dict import PAGE_CONFIG
from eda_produccion import eda_produccion
from eda_comercio import eda_comercio
from ml_app import ml_app

st.set_page_config(**PAGE_CONFIG)

def main():

    st.title('Naranjas en España:flag-es::tangerine:')

    # dataset comex de naranjas
    with st.expander(label = "DataFrame - Flujo comercial de naranjas españolas - 2002 a 2023", expanded = False):
        df_comex = pd.read_csv(filepath_or_buffer = "sources/comex_2002_2024.csv", encoding="latin-1")
    #    st.dataframe(df_comex)
    # dataset comex y prod
    with st.expander(label = "DataFrame - Producción y comercio de naranjas españolas - 2002 a 2022", expanded = True):
        df_cmx_prd = pd.read_csv(filepath_or_buffer = "sources/comex_prod_2002_2022.csv", encoding="latin-1")
    #     st.dataframe(df_cmx_prd)
    # dataset produccion df_prod = pd.read_csv(f"{ruta_recursos}produccion_naranjas_2002_2022.csv")
    with st.expander(label = "DataFrame - Producción de naranjas españolas - 2002 a 2022", expanded = False):
        df_prod = pd.read_csv(filepath_or_buffer = "sources/produccion_naranjas_2002_2022.csv")
     #   st.dataframe(df_prod)
    # carta gantt referencial df_recol = pd.read_csv(f"{ruta_recursos}periodos_recoleccion_naranjas.csv", encoding="latin-1")
    with st.expander(label = "Carta Gantt - Referencia recolección de naranjas", expanded = False):
        df_recol = pd.read_csv(filepath_or_buffer = "sources/periodos_recoleccion_naranjas.csv", encoding="latin-1")
    #   st.dataframe(df_recol)
    with st.expander(label = "Folium - Geolocalización de zonas con naranjas", expanded = False):
        df = pd.read_csv(filepath_or_buffer = "sources/Map.csv")
    #   st.dataframe(df)

# INICIO SIDEBAR -------------------------------------------------------------------------------------------------------

    # selector de secciones de proyecto
    st.sidebar.markdown("### Vistas de exploración de datos y de proyecciones.")
    seccion = ["Presentación", "Producción", "Flujo comercial", "Proyección de exportaciones"]
    choose_section = st.sidebar.selectbox("Sección", options = seccion)

# FIN SIDEBAR -------------------------------------------------------------------------------------------------

# BLOQUE DE TABS ----------------------------------------------------------------------------------------------
    if choose_section == "Presentación":
        st.subheader(body = "Sobre las naranjas :tangerine:")
        st.write("La naranja fue introducida en España por los árabes durante su dominación en la península ibérica, alrededor del siglo VIII. Fueron ellos quienes llevaron la naranja dulce (Citrus sinensis) desde Asia hasta Europa. Sin embargo, la expansión y el cultivo comercial de las naranjas en España se desarrollaron principalmente en las regiones de Valencia y Andalucía durante los siglos XVIII y XIX. Estas regiones pronto se convirtieron en los principales productores de naranjas en España, gracias a su clima favorable y sus condiciones geográficas.")
        st.write("La naranja (citrus sinensis) es una especie subtropical. Por consiguiente, el factor limitante más importante es la temperatura mínima, ya que no tolera las inferiores a -3ºC. No tolera las heladas, sufren, las flores, frutos y la vegetación, estas que pueden desaparecer totalmente. Presenta escasa resistencia al frío (a los 3-5ºC bajo cero la planta muere). No requiere horas-frío para la floración. No presenta reposo invernal, sino una parada del crecimiento por las bajas temperaturas (quiescencia), que provocan la inducción de ramas que florecen en primavera.")

        tab_pres1, tab_pres2, tab_pres3 = st.tabs(["Temporadas de recolección", "Producción y comercio", "Data y créditos"])
        
        # TAB 1: Temporadas de recolección

        fig_chart_recoleccion = px.timeline(df_recol,
                                x_start= 'Inicio',
                                x_end = 'Fin',
                                y = 'Variedad',
                                color='Grupo',
                                color_discrete_sequence=["NavajoWhite","OrangeRed", "DarkOrange"],
                                template="plotly_dark",
                                title= "Referencia de periodos de recolección de naranjas"
                                )
        fig_chart_recoleccion.add_vrect(x0="2022-10-10",
                                        x1="2022-12-31",
                                        row=1,
                                        fillcolor="NavajoWhite",
                                        annotation_text="recolección temprana",
                                        annotation_position="top left",
                                        opacity=0.1,
                                        line_width=0)
        fig_chart_recoleccion.add_vrect(x0="2022-01-01",
                                        x1="2022-03-15",
                                        row=1,
                                        fillcolor="NavajoWhite",
                                        opacity=0.1,
                                        line_width=0)
        fig_chart_recoleccion.add_vrect(x0="2022-02-01",
                                        x1="2022-07-31",
                                        row=1,
                                        fillcolor="DarkOrange",
                                        annotation_text="recolección tardía",
                                        annotation_position="top right",
                                        opacity=0.1,
                                        line_width=0)

        tab_pres1.plotly_chart(figure_or_data = fig_chart_recoleccion, use_container_width = True)

        tab_pres1.write("Existen dos periodos generales de recolección: la recolección temprana empieza en octubre y acaba a mediados de marzo, y la recolección de frutos tardíos se superpone con el final de los frutos tempranos, comenzando a inicios de febrero, hasta finales de julio.")
        tab_pres1.write("Las naranjas se agrupan en Navel y navelinas, que son en su mayoría naranjas de mesa por su acidez, las Sanguinas, que poseen una pigmentación rojiza más intensa, y las Naranjas Blancas, de un anaranjado más claro que las Navel y, junto a las Dulces, son ideales para jugos")

        # TAB 2: vista general de produccion y comercio
        fig_cmx_prod = px.bar(df_cmx_prd,
                              x                       = "año",
                              y                       = ['produccion_anual','exportacion_anual','importacion_anual'],
                              color_discrete_sequence = ['darkorange','orange','navajowhite'],
                              barmode                 = "overlay",
                              title                   = "Total de producción, importación y exportación, entre 2002 y 2022",
                              text_auto               = True,
                              template                = "plotly_dark")

        fig_cmx_prod.update_traces(textangle          = 0,
                                   textposition       = 'outside')
        tab_pres2.plotly_chart(figure_or_data = fig_cmx_prod, use_container_width = True)
        tab_pres2.write("La proporción entre producción de naranjas y comercio internacional entre España y el mundo a lo largo de los años se ha mantenido similar, pero viéndose afectada por factores climáticos.")
        tab_pres2.write("La capacidad productiva interna permite un gran abastecimiento a lo largo del año, incluyendo los meses sin recolección, necesitando importar sólo para cubrir estos pocos meses fuera de temporada")


        # TAB 3: dataframes
        tab_pres3.write("Los datos fueron recopilados de COMTRADE de la Unión Europea, VisualCrossing para datos climáticos y los datos de producción del Ministerio de Agricultura, Pesca y Alimentación de España. Las fechas de recolección de la carta Gantt fueron obtenidas del Ayuntamiento Palma del Rio con apoyo de agricultores y comercio (Agrológica, Naranjas Bou, Vivero Guanino).")
        tab_pres3.markdown(body = "fuente de comercio y transporte de naranjas (COMTRADE)") # , unsafe_allow_html = True
        tab_pres3.dataframe(df_comex)
        tab_pres3.markdown(body = "fuente de produccion de naranjas") # , unsafe_allow_html = True
        tab_pres3.dataframe(df_prod)
        tab_pres3.write('Creado por Alissa Zogorodnykh, Fernanda Soto y Jose David Mendez.')

# CIERRE DE BLOQUE --------------------------------------------------------------------------------------------
    elif choose_section == "Producción":
        eda_produccion()

    elif choose_section == "Flujo comercial":
        eda_comercio()

    elif choose_section == "Proyección de exportaciones":
        ml_app()

    pass
if __name__ == "__main__":
    main()