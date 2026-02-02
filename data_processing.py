import pandas as pd
import numpy as np
import unicodedata

def norm(x):
    if pd.isna(x):
        return x
    x = str(x).strip().lower()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

# ---------------- Inventario ----------------
def clean_inventario(df_raw):
    df = df_raw.copy()

    df["SKU_ID"] = df["SKU_ID"].str.strip().str.upper()
    df["Categoria"] = df["Categoria"].apply(norm)
    df["Bodega_Origen"] = df["Bodega_Origen"].apply(norm)

    for c in ["Stock_Actual","Costo_Unitario_USD","Lead_Time_Dias","Punto_Reorden"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["Ultima_Revision"] = pd.to_datetime(df["Ultima_Revision"], errors="coerce")
    df["stock_negativo"] = df["Stock_Actual"] < 0

    df["Costo_Unitario_USD"] = df["Costo_Unitario_USD"].replace(0, np.nan)
    df["Costo_Unitario_Limpio"] = (
        df["Costo_Unitario_USD"]
        .fillna(df.groupby("Categoria")["Costo_Unitario_USD"].transform("median"))
        .fillna(df["Costo_Unitario_USD"].median())
    )

    df["Lead_Time_Limpio"] = (
        df["Lead_Time_Dias"]
        .replace(0, np.nan)
        .fillna(df.groupby("Bodega_Origen")["Lead_Time_Dias"].transform("median"))
        .fillna(df["Lead_Time_Dias"].median())
    )

    return df.sort_values("Ultima_Revision").drop_duplicates("SKU_ID", keep="last")

# ---------------- Transacciones ----------------
def clean_transacciones(df_raw):
    df = df_raw.copy()

    df["SKU_ID"] = df["SKU_ID"].str.strip().str.upper()
    df["Ciudad_Destino"] = df["Ciudad_Destino"].apply(norm)

    for c in ["Cantidad_Vendida","Precio_Venta_Final","Costo_Envio","Tiempo_Entrega_Real"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["Fecha_Venta"] = pd.to_datetime(df["Fecha_Venta"], errors="coerce")
    df["Tiempo_Entrega_Limpio"] = df["Tiempo_Entrega_Real"].clip(0,180)

    ciudades = {
        "med":"Medellín","medellin":"Medellín",
        "bog":"Bogotá","bogota":"Bogotá"
    }
    df["Ciudad_Destino_Limpia"] = df["Ciudad_Destino"].map(ciudades).fillna(df["Ciudad_Destino"].str.title())

    return df

# ---------------- Feedback ----------------
def clean_feedback(df_raw):
    df = df_raw.drop_duplicates().copy()

    df["Edad_Cliente"] = pd.to_numeric(df["Edad_Cliente"], errors="coerce")
    df.loc[(df["Edad_Cliente"] < 0) | (df["Edad_Cliente"] > 100), "Edad_Cliente"] = np.nan

    for c in ["Rating_Producto","Rating_Logistica"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[(df[c] < 1) | (df[c] > 5), c] = np.nan
        df[c] = df[c].fillna(df[c].median())

    map_sn = {"si":"Sí","sí":"Sí","yes":"Sí","1":"Sí","no":"No","0":"No"}
    df["Ticket_Soporte_Abierto"] = df["Ticket_Soporte_Abierto"].str.lower().str.strip().map(map_sn)
    df["Recomienda_Marca"] = df["Recomienda_Marca"].str.lower().str.strip().map(map_sn)

    df["Satisfaccion_NPS"] = pd.to_numeric(df["Satisfaccion_NPS"], errors="coerce")
    df["Comentario_Texto"] = df["Comentario_Texto"].replace("---", np.nan)

    return df
