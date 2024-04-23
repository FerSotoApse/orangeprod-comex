import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from sklearn.preprocessing import MinMaxScaler


@st.cache_data
def dataset():
    # Load CSV data
    df = pd.read_csv("sources/export_transport.csv")
    
    # Filtramos los datos
    df = df[(df["PartnerISO"] != "W00") & (df["Partner2ISO"] != "W00") & (df["CustomsDesc"] != "TOTAL CPC") & (df["MotDesc"] != "TOTAL MOT")]
    # Desahacemos de la columnas innecesarias 
    columns_to_drop = ["Unnamed: 0", "Period", "IsReported", "LegacyEstimationFlag", "IsAggregate", "PrimaryValue", "Fobvalue",
                    "IsGrossWgtEstimated", "GrossWgt", "IsNetWgtEstimated", "IsAltQtyEstimated", "AtlQty", "AltQtyUnitAbbr", "AltQtyUnitCode",
                    "IsQtyEstimated", "Qty", "QtyUnitAbbr", "QtyUnitCode", "CustomsDesc", "IsLeaf", "AggrLevel", "CmdDesc", "CmdCode",
                     "IsOriginalClassification", "Partner2Desc", "Partner2ISO", "MosCode", "ReporterISO", "ReporterDesc",
                    "FlowDesc", "MotCode", "MotDesc"]
    df = df.drop(columns_to_drop, axis=1)

    # Creamos diccionario para tener datos accesibles en español con los paises y codigos ISO
    country_mapping = {
        "AFG": "Afganistan",
        "DEU": "Alemania",
        "AND": "Andorra",
        "AGO": "Angola",
        "SAU": "Arabia Saudí",
        "DZA": "Argelia",
        "ARG": "Argentina",
        "ARM": "Armenia",
        "AUS": "Australia",
        "AUT": "Austria",
        "AZE": "Azerbaiyán",
        "BHR": "Bahrein",
        "BGD": "Bangladesh",
        "BLR": "Bielorusia",
        "BIH": "Bosnia-Herzegovina",
        "BRA": "Brasil",
        "BGR": "Bulgaria",
        "BFA": "Burkina Faso",
        "BEL": "Bélgica",
        "CPV": "Cabo Verde",
        "KHM": "Camboya (Campuchea)",
        "CMR": "Camerún",
        "CAN": "Canadá",
        "TCD": "Chad",
        "CHN": "China",
        "CYP": "Chipre",
        "COL": "Colombia",
        "COG": "Congo",
        "KOR": "Corea del Sur",
        "CRI": "Costa Rica",
        "CIV": "Costa de Marfil",
        "HRV": "Croacia",
        "CUB": "Cuba",
        "CUW": "Curazao",
        "DNK": "Dinamarca",
        "ECU": "Ecuador",
        "EGY": "Egipto",
        "SLV": "El Salvador",
        "ARE": "Emiratos Árabes Unidos",
        "ERI": "Eritrea",
        "SVK": "Eslovaquia",
        "SVN": "Eslovenia",
        "USA": "Estados Unidos",
        "EST": "Estonia",
        "FIN": "Finlandia",
        "FRA": "Francia",
        "GAB": "Gabón",
        "GMB": "Gambia",
        "GEO": "Georgia",
        "GHA": "Ghana",
        "GIB": "Gibraltar",
        "GRC": "Grecia",
        "GTM": "Guatemala",
        "GIN": "Guinea",
        "GNB": "Guinea Bissau",
        "GNQ": "Guinea Ecuatorial",
        "HTI": "Haití",
        "HND": "Honduras",
        "HKG": "Hong-Kong",
        "HUN": "Hungría",
        "IND": "India",
        "IDN": "Indonesia",
        "IRL": "Irlanda",
        "IRN": "Irán",
        "ISL": "Islandia",
        "ITA": "Italia",
        "JPN": "Japón",
        "JOR": "Jordania",
        "KAZ": "Kazajstán",
        "KEN": "Kenia",
        "KWT": "Kuwait",
        "KGZ": "Kirguistán",
        "LVA": "Letonia",
        "LBR": "Liberia",
        "LBY": "Libia",
        "LTU": "Lituania",
        "LUX": "Luxemburgo",
        "LBN": "Líbano",
        "MKD": "Macedonia",
        "MYS": "Malasia",
        "MDV": "Maldivas",
        "MLI": "Mali",
        "MLT": "Malta",
        "MAR": "Marruecos",
        "MRT": "Mauritania",
        "MUS": "Mauricio",
        "MYT": "Mayotte",
        "MDA": "Moldavia",
        "MNG": "Mongolia",
        "MNE": "Montenegro",
        "NGA": "Nigeria",
        "NOR": "Noruega",
        "NZL": "Nueva Zelanda",
        "OMN": "Omán",
        "PAN": "Panamá",
        "NLD": "Países Bajos",
        "PER": "Perú",
        "POL": "Polonia",
        "PRT": "Portugal",
        "QAT": "Qatar",
        "COD": "R.D. del Congo",
        "GBR": "Reino Unido",
        "CAF": "República Centroafricana",
        "CZE": "República Checa",
        "ROU": "Rumanía",
        "RUS": "Rusia",
        "SEN": "Senegal",
        "SRB": "Serbia",
        "SYC": "Seychelles",
        "SLE": "Sierra Leona",
        "SGP": "Singapur",
        "LKA": "Sri Lanka",
        "ZAF": "Sudáfrica",
        "SDN": "Sudán",
        "SWE": "Suecia",
        "CHE": "Suiza",
        "TGO": "Togo",
        "TUN": "Túnez",
        "TUR": "Turquia",
        "UKR": "Ucrania",
        "URY": "Uruguay",
        "VEN": "Venezuela",
        "VNM": "Vietnam"

    }
    df["PartnerDesc"] = df["PartnerISO"].map(country_mapping).fillna(df["PartnerDesc"])
    #Extraemos los codigos ISO y nos quedamos solo con los paises cuyo codigo ISO esta en la lista
    iso_codes = list(country_mapping.keys())
    df = df[df["PartnerISO"].isin(iso_codes)]

    # Renombramos algunas columnas y cambiamos los kilos a toneladas
    df = df.rename(columns={"PartnerDesc": "Pais", "PartnerISO": "ISO", "NetWgt": "Toneladas"})
    df.reset_index(drop=True, inplace=True)
    df.loc[:, "Toneladas"] /= 1000

    # Deshacemos de los años 2023, como no coinciden con los años de produccion y no estan completos
    df.drop(df[df['RefYear'] == 2023].index, inplace=True)

    # Combinamos la columna RefYear con RefMonth para crear una unica columna Date y dropeamos las de Year y Month
    df["Date"] = df["RefYear"].astype(str) + '-' + df["RefMonth"].astype(str)
    df.drop(columns=["RefYear", "RefMonth"], inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])

    # Extraemos informacion de los paises de Europa, como es el mayor importador de naranjas de España, haremos el modelo basado en Europa
    europa = ["Alemania", "Andorra", "Austria", "Bélgica", "Bielorusia", "Bosnia-Herzegovina", "Bulgaria", "República Checa", "Chipre", "Croacia", 
    "Dinamarca", "Eslovaquia", "Eslovenia", "Estonia", "Finlandia", "Francia", "Gibraltar", "Reino Unido", "Grecia", "Países Bajos", "Hungría", "Italia", 
    "Irlanda", "Islandia", "Letonia", "Lituania", "Luxemburgo", "Macedonia", "Moldavia", "Malta", "Mayotte", "Montenegro", "Noruega", 
    "Polonia", "Portugal", "Rumania", "Rusia", "Serbia", "Suecia", "Suiza", "Ucrania"]
    df_europe = df[df["Pais"].isin(europa)]

    df_europe = df_europe.copy()
    df_europe.loc[:, "Year"] = df_europe["Date"].dt.year
    df_europe.loc[:, "Month"] = df_europe["Date"].dt.month
    df_europe_grouped = df_europe.groupby(["Year", "Month"]).agg({
    "Pais": "first", 
    "Toneladas": "sum"}).reset_index()
    #df_europe_grouped.to_csv("Export_Europe.csv", index=False)
    
    return df_europe_grouped

def download_file(df):

    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f"<a href='data:file/csv;base64,{b64}' download='Europe_data.csv'>Download CSV File</a>"

    return href

def loss_model():
    # Load CSV data
    df_loss = pd.read_csv("sources/loss_data.csv")
    
    # MSE 
    mse_loss = ((df_loss['loss'].iloc[-1] - df_loss['loss'].mean())**2).mean()
    mse_val_loss = ((df_loss['val_loss'].iloc[-1] - df_loss['val_loss'].mean())**2).mean()

    # Plotly
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_loss.index, y=df_loss['loss'], mode='lines', name='Loss', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df_loss.index, y=df_loss['val_loss'], mode='lines', name='Val_loss', line=dict(color='red')))

    fig.update_layout(
        title='Loss vs Val_loss',
        xaxis_title='Epochs',
        yaxis_title='Loss'
    )

    st.plotly_chart(fig)

#    # Invert scaled MSE values to original scale
#    scaler = MinMaxScaler()  # Initialize MinMaxScaler
#    scaler.fit([[mse_loss], [mse_val_loss]])  # Fit the scaler to the MSE values
#    mse_loss_original_scale = scaler.inverse_transform([[mse_loss]])[0][0]
#    mse_val_loss_original_scale = scaler.inverse_transform([[mse_val_loss]])[0][0]
#
#    # MSE
#    st.write(f"MSE from last value of loss: {mse_loss_original_scale}")
#    st.write(f"MSE from last value of val_loss: {mse_val_loss_original_scale}")

    return mse_loss, mse_val_loss





