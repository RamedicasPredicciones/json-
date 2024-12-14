import streamlit as st
import pandas as pd
import json
import requests
from msal import ConfidentialClientApplication

# Configuración de autenticación para Power BI
TENANT_ID = "tu-tenant-id"
CLIENT_ID = "tu-client-id"
CLIENT_SECRET = "tu-client-secret"
POWER_BI_GROUP_ID = "tu-grupo-id"  # ID del espacio de trabajo de Power BI
DATASET_NAME = "MiDataset"

def authenticate_with_powerbi():
    """
    Autenticarse con Power BI usando MSAL.
    """
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    token_response = app.acquire_token_for_client(scopes=["https://analysis.windows.net/powerbi/api/.default"])
    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        st.error("Error autenticando con Power BI.")
        return None

def upload_to_powerbi(df, access_token):
    """
    Subir datos a Power BI como un dataset en un espacio de trabajo.
    """
    # Crear un payload con los datos del DataFrame
    payload = {
        "name": DATASET_NAME,
        "tables": [
            {
                "name": "Table1",
                "columns": [{"name": col, "dataType": "string"} for col in df.columns],
                "rows": df.to_dict(orient="records"),
            }
        ],
    }

    # Endpoint para crear o actualizar un dataset
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{POWER_BI_GROUP_ID}/datasets"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        st.success("¡Datos subidos con éxito a Power BI!")
    else:
        st.error(f"Error subiendo datos: {response.text}")

# Configuración de la página
st.set_page_config(page_title="Convertidor JSON a Power BI", layout="wide")

# Título
st.title("Convertidor de JSON a Power BI con Integración REST API")

# Subida de archivo JSON
uploaded_file = st.file_uploader("Sube tu archivo JSON aquí:", type=["json"])

if uploaded_file is not None:
    st.success("¡Archivo subido con éxito!")
    st.write("Procesando archivo...")
    
    # Procesar el archivo JSON
    try:
        data = json.load(uploaded_file)
        if isinstance(data, dict):
            df = pd.json_normalize(data)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            st.error("El formato JSON no es válido para la conversión a tabla.")
            df = None
    except Exception as e:
        st.error(f"Error procesando el archivo JSON: {e}")
        df = None

    if df is not None:
        st.write("Vista previa de los datos procesados:")
        st.dataframe(df.head(10))  # Mostrar las primeras 10 filas
        
        # Opción para subir a Power BI
        if st.button("Subir a Power BI"):
            st.write("Autenticando con Power BI...")
            access_token = authenticate_with_powerbi()
            if access_token:
                st.write("Subiendo datos a Power BI...")
                upload_to_powerbi(df, access_token)

# Footer
st.markdown("---")
st.caption("Desarrollado con ❤️ usando Streamlit y Power BI REST API.")
