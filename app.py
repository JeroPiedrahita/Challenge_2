import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata

st.set_page_config(page_title="EDA Operacional – TechLog", layout="wide")

# --------------------------------------------------
# Utilidades
# --------------------------------------------------
def norm(x):
    if pd.isna(x):
        return x
    x = x.strip().lower()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def auditoria_calidad(df):
    audit = pd.DataFrame({
        "Porcentaje_Nulos (%)": df.isna().mean() * 100,
        "Valores_Unicos": df.nunique()
    })
    duplicados = df.duplicated().sum()

    outliers = {}
    for col in df.select_dtypes(include="number").columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers[col] = int(((df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)).sum())

    audit["Outliers"] = audit.index.map(outliers).fillna(0)

    health_score = max(
        0,
        100
        - audit["Porcentaje_Nulos (%)"].mean()
        - (duplicados / len(df) * 100)
        - (sum(outliers.values()) / len(df) * 100)
    )

    return audit, duplicados, health_score

# --------------------------------------------------
# Carga de archivos crudos
# --------------------------------------------------
st.sidebar.title("Carga de Datos")

inv_file = st.sidebar.file_uploader("Inventario (CSV)", type="csv")
tx_file  = st.sidebar.file_uploader("Transacciones (CSV)", type="csv")
fb_file  = st.sidebar.file_uploader("Feedback (CSV)", type="csv")

if not (inv_file and tx_file and fb_file):
    st.warning("Carga los tres archivos para continuar.")
    st.stop()

df_inv_raw = pd.read_csv(inv_file, dtype=str)
df_tx_raw  = pd.read_csv(tx_file, dtype=str)
df_fb_raw  = pd.read_csv(fb_file, dtype=str)

# --------------------------------------------------
# Auditoría ANTES
# --------------------------------------------------
st.title("🔍 Fase 1 – Auditoría de Calidad y Transparencia")

st.subheader("Inventario – Antes")
audit_inv_raw, dup_inv_raw, hs_inv_raw = auditoria_calidad(df_inv_raw)
st.metric("Health Score", f"{hs_inv_raw:.1f}")
st.write("Duplicados:", dup_inv_raw)
st.dataframe(audit_inv_raw)

st.subheader("Transacciones – Antes")
audit_tx_raw, dup_tx_raw, hs_tx_raw = auditoria_calidad(df_tx_raw)
st.metric("Health Score", f"{hs_tx_raw:.1f}")
st.write("Duplicados:", dup_tx_raw)
st.dataframe(audit_tx_raw)

st.subheader("Feedback – Antes")
audit_fb_raw, dup_fb_raw, hs_fb_raw = auditoria_calidad(df_fb_raw)
st.metric("Health Score", f"{hs_fb_raw:.1f}")
st.write("Duplicados:", dup_fb_raw)
st.dataframe(audit_fb_raw)

# --------------------------------------------------
# Limpieza (idéntica a la que tú definiste)
# --------------------------------------------------
df_inv = df_inv_raw.copy()
df_tx  = df_tx_raw.copy()
df_fb  = df_fb_raw.copy()

df_inv["SKU_ID"] = df_inv["SKU_ID"].str.strip().str.upper()
df_inv["Categoria"] = df_inv["Categoria"].apply(norm)
df_inv["Bodega_Origen"] = df_inv["Bodega_Origen"].apply(norm)

df_inv["Stock_Actual"] = pd.to_numeric(df_inv["Stock_Actual"], errors="coerce")
df_inv["Costo_Unitario_USD"] = pd.to_numeric(df_inv["Costo_Unitario_USD"], errors="coerce")
df_inv["Lead_Time_Dias"] = pd.to_numeric(df_inv["Lead_Time_Dias"], errors="coerce")

df_inv["stock_negativo"] = df_inv["Stock_Actual"] < 0

df_tx["SKU_ID"] = df_tx["SKU_ID"].str.strip().str.upper()
df_tx["Cantidad_Vendida"] = pd.to_numeric(df_tx["Cantidad_Vendida"], errors="coerce")
df_tx["Precio_Venta_Final"] = pd.to_numeric(df_tx["Precio_Venta_Final"], errors="coerce")
df_tx["Tiempo_Entrega_Real"] = pd.to_numeric(df_tx["Tiempo_Entrega_Real"], errors="coerce")
df_tx["Tiempo_Entrega_Limpio"] = df_tx["Tiempo_Entrega_Real"].clip(0, 180)

df_fb["Edad_Cliente"] = pd.to_numeric(df_fb["Edad_Cliente"], errors="coerce")
df_fb.loc[(df_fb["Edad_Cliente"] < 0) | (df_fb["Edad_Cliente"] > 100), "Edad_Cliente"] = np.nan

df_fb["Rating_Producto"] = pd.to_numeric(df_fb["Rating_Producto"], errors="coerce")
df_fb.loc[(df_fb["Rating_Producto"] < 1) | (df_fb["Rating_Producto"] > 5), "Rating_Producto"] = np.nan
df_fb["Rating_Producto"] = df_fb["Rating_Producto"].fillna(df_fb["Rating_Producto"].median())

# --------------------------------------------------
# Auditoría DESPUÉS
# --------------------------------------------------
st.title("✅ Auditoría Posterior a la Limpieza")

st.subheader("Inventario – Después")
audit_inv, dup_inv, hs_inv = auditoria_calidad(df_inv)
st.metric("Health Score", f"{hs_inv:.1f}")
st.write("Duplicados eliminados:", dup_inv_raw - dup_inv)
st.dataframe(audit_inv)

st.subheader("Transacciones – Después")
audit_tx, dup_tx, hs_tx = auditoria_calidad(df_tx)
st.metric("Health Score", f"{hs_tx:.1f}")
st.write("Duplicados eliminados:", dup_tx_raw - dup_tx)
st.dataframe(audit_tx)

st.subheader("Feedback – Después")
audit_fb, dup_fb, hs_fb = auditoria_calidad(df_fb)
st.metric("Health Score", f"{hs_fb:.1f}")
st.write("Duplicados eliminados:", dup_fb_raw - dup_fb)
st.dataframe(audit_fb)
