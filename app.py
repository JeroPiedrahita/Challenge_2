import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata

# ==================================================
# Configuración general
# ==================================================
st.set_page_config(
    page_title="EDA Operacional",
    layout="wide"
)

# ==================================================
# Funciones auxiliares
# ==================================================
def norm(x):
    if pd.isna(x):
        return x
    x = str(x).strip().lower()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def nps_grupo(x):
    if pd.isna(x): return np.nan
    if x >= 9: return "Promotor"
    if x >= 7: return "Pasivo"
    return "Detractor"

# ==================================================
# Sidebar – Carga de archivos
# ==================================================
st.sidebar.title("Carga de datos crudos")

inv_file = st.sidebar.file_uploader(
    "Inventario (CSV)",
    type="csv"
)

tx_file = st.sidebar.file_uploader(
    "Transacciones (CSV)",
    type="csv"
)

fb_file = st.sidebar.file_uploader(
    "Feedback Clientes (CSV)",
    type="csv"
)

# ==================================================
# Botón de limpieza
# ==================================================
if st.sidebar.button("🧹 Ejecutar limpieza"):

    if not all([inv_file, tx_file, fb_file]):
        st.sidebar.error("Debes cargar los tres archivos.")
    else:
        # -------------------------------
        # Cargar como strings
        # -------------------------------
        df_inv = pd.read_csv(inv_file, dtype=str)
        df_tx  = pd.read_csv(tx_file, dtype=str)
        df_fb  = pd.read_csv(fb_file, dtype=str)

        # -------------------------------
        # LIMPIEZA INVENTARIO
        # -------------------------------
        df_inv["SKU_ID"] = df_inv["SKU_ID"].str.strip().str.upper()
        df_inv["Categoria"] = df_inv["Categoria"].apply(norm)
        df_inv["Bodega_Origen"] = df_inv["Bodega_Origen"].apply(norm)

        df_inv["Stock_Actual"] = pd.to_numeric(df_inv["Stock_Actual"], errors="coerce")
        df_inv["Costo_Unitario_USD"] = pd.to_numeric(df_inv["Costo_Unitario_USD"], errors="coerce")
        df_inv["Lead_Time_Dias"] = pd.to_numeric(df_inv["Lead_Time_Dias"], errors="coerce")
        df_inv["Ultima_Revision"] = pd.to_datetime(df_inv["Ultima_Revision"], errors="coerce")

        df_inv["Costo_Unitario_USD"] = df_inv["Costo_Unitario_USD"].replace(0, np.nan)
        df_inv["Lead_Time_Dias"] = df_inv["Lead_Time_Dias"].replace(0, np.nan)
        df_inv["Categoria"] = df_inv["Categoria"].replace("???", np.nan)

        df_inv["stock_negativo"] = df_inv["Stock_Actual"] < 0

        med_cat = df_inv.groupby("Categoria")["Costo_Unitario_USD"].transform("median")
        med_global = df_inv["Costo_Unitario_USD"].median()

        df_inv["Costo_Unitario_Limpio"] = (
            df_inv["Costo_Unitario_USD"]
            .fillna(med_cat)
            .fillna(med_global)
        )

        med_bod = df_inv.groupby("Bodega_Origen")["Lead_Time_Dias"].transform("median")
        med_lead_global = df_inv["Lead_Time_Dias"].median()

        df_inv["Lead_Time_Limpio"] = (
            df_inv["Lead_Time_Dias"]
            .fillna(med_bod)
            .fillna(med_lead_global)
        )

        df_inv = (
            df_inv
            .sort_values("Ultima_Revision")
            .drop_duplicates(subset="SKU_ID", keep="last")
        )

        # -------------------------------
        # LIMPIEZA TRANSACCIONES
        # -------------------------------
        df_tx["SKU_ID"] = df_tx["SKU_ID"].str.strip().str.upper()
        df_tx["Ciudad_Destino"] = df_tx["Ciudad_Destino"].apply(norm)

        df_tx["Fecha_Venta"] = pd.to_datetime(df_tx["Fecha_Venta"], errors="coerce")
        df_tx["Cantidad_Vendida"] = pd.to_numeric(df_tx["Cantidad_Vendida"], errors="coerce")
        df_tx["Precio_Venta_Final"] = pd.to_numeric(df_tx["Precio_Venta_Final"], errors="coerce")
        df_tx["Costo_Envio"] = pd.to_numeric(df_tx["Costo_Envio"], errors="coerce")
        df_tx["Tiempo_Entrega_Real"] = pd.to_numeric(df_tx["Tiempo_Entrega_Real"], errors="coerce")

        df_tx["Tiempo_Entrega_Limpio"] = df_tx["Tiempo_Entrega_Real"].clip(0, 180)

        ciudades = {
            "med": "Medellín",
            "medellin": "Medellín",
            "bog": "Bogotá",
            "bogota": "Bogotá"
        }

        df_tx["Ciudad_Destino_Limpia"] = (
            df_tx["Ciudad_Destino"]
            .map(ciudades)
            .fillna(df_tx["Ciudad_Destino"].str.title())
        )

        # -------------------------------
        # LIMPIEZA FEEDBACK
        # -------------------------------
        df_fb = df_fb.drop_duplicates()

        df_fb["Edad_Cliente"] = pd.to_numeric(df_fb["Edad_Cliente"], errors="coerce")
        df_fb.loc[
            (df_fb["Edad_Cliente"] < 0) | (df_fb["Edad_Cliente"] > 100),
            "Edad_Cliente"
        ] = np.nan

        df_fb["Rating_Producto"] = pd.to_numeric(df_fb["Rating_Producto"], errors="coerce")
        df_fb.loc[
            (df_fb["Rating_Producto"] < 1) | (df_fb["Rating_Producto"] > 5),
            "Rating_Producto"
        ] = np.nan

        df_fb["Rating_Producto"] = df_fb["Rating_Producto"].fillna(
            df_fb["Rating_Producto"].median()
        )

        map_si_no = {
            "si": "Sí", "sí": "Sí", "yes": "Sí", "1": "Sí",
            "no": "No", "0": "No"
        }

        df_fb["Ticket_Soporte_Abierto"] = (
            df_fb["Ticket_Soporte_Abierto"]
            .astype(str).str.lower().str.strip()
            .map(map_si_no)
        )

        df_fb["Recomienda_Marca"] = (
            df_fb["Recomienda_Marca"]
            .astype(str).str.lower().str.strip()
            .map(map_si_no)
        )

        df_fb["Satisfaccion_NPS"] = pd.to_numeric(df_fb["Satisfaccion_NPS"], errors="coerce")
        df_fb["Comentario_Texto"] = df_fb["Comentario_Texto"].replace("---", np.nan)
        df_fb["NPS_Grupo"] = df_fb["Satisfaccion_NPS"].apply(nps_grupo)

        # -------------------------------
        # Guardar en sesión
        # -------------------------------
        st.session_state["df_inv"] = df_inv
        st.session_state["df_tx"] = df_tx
        st.session_state["df_fb"] = df_fb

        st.sidebar.success("Limpieza ejecutada correctamente ✅")

# ==================================================
# EDA (solo si hay datos limpios)
# ==================================================
if "df_inv" in st.session_state:

    df_inv = st.session_state["df_inv"]
    df_tx  = st.session_state["df_tx"]
    df_fb  = st.session_state["df_fb"]

    st.sidebar.title("EDA – Navegación")

    seccion = st.sidebar.radio(
        "Selecciona el módulo:",
        ["Inventario", "Transacciones", "Feedback Clientes"]
    )

    # (Aquí iría exactamente tu EDA tal como ya lo tienes,
    # no lo repito para no duplicar, pero funciona igual)
else:
    st.info("👈 Carga los archivos y ejecuta la limpieza para comenzar.")
