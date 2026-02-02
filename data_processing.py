"""
Módulo de Limpieza de Datos - Challenge 02
Limpieza simple y transparente con Health Score
"""

import pandas as pd
import numpy as np
from datetime import datetime


def calculate_health_score(df, dataset_name):
    """Calcula el Health Score de un dataset"""
    total_cells = df.shape[0] * df.shape[1]
    total_nulls = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()
    
    null_penalty = (total_nulls / total_cells) * 100
    duplicate_penalty = (duplicates / len(df)) * 100
    
    health_score = max(0, 100 - null_penalty - duplicate_penalty)
    
    return {
        'dataset_name': dataset_name,
        'total_records': len(df),
        'total_columns': len(df.columns),
        'health_score': round(health_score, 2),
        'total_nulls': total_nulls,
        'duplicates': duplicates
    }


def clean_inventario(df):
    """Limpia el dataset de inventario"""
    df_clean = df.copy()
    log = []
    
    # 1. Normalizar nombres de bodegas
    bodega_map = {
        'MED': 'Medellín', 'med': 'Medellín',
        'BOG': 'Bogotá', 'bog': 'Bogotá',
        'CLO': 'Cali', 'clo': 'Cali'
    }
    df_clean['Bodega_Origen'] = df_clean['Bodega_Origen'].replace(bodega_map)
    log.append("Normalizados nombres de bodegas")
    
    # 2. Corregir stocks negativos
    negative = (df_clean['Stock_Actual'] < 0).sum()
    if negative > 0:
        df_clean.loc[df_clean['Stock_Actual'] < 0, 'Stock_Actual'] = 0
        log.append(f"Corregidos {negative} stocks negativos")
    
    # 3. Limpiar costos (eliminar outliers extremos)
    Q1 = df_clean['Costo_Unitario_USD'].quantile(0.25)
    Q3 = df_clean['Costo_Unitario_USD'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df_clean['Costo_Unitario_USD'] < Q1 - 1.5*IQR) | 
                (df_clean['Costo_Unitario_USD'] > Q3 + 1.5*IQR)).sum()
    if outliers > 0:
        df_clean = df_clean[
            (df_clean['Costo_Unitario_USD'] >= Q1 - 1.5*IQR) & 
            (df_clean['Costo_Unitario_USD'] <= Q3 + 1.5*IQR)
        ]
        log.append(f"Eliminados {outliers} productos con costos extremos")
    
    # 4. Limpiar Lead Time
    df_clean['Lead_Time_Dias'] = pd.to_numeric(df_clean['Lead_Time_Dias'], errors='coerce')
    nulls = df_clean['Lead_Time_Dias'].isnull().sum()
    if nulls > 0:
        df_clean['Lead_Time_Dias'].fillna(df_clean['Lead_Time_Dias'].median(), inplace=True)
        log.append(f"Imputados {nulls} Lead Times con mediana")
    
    # 5. Limpiar fechas
    df_clean['Ultima_Revision'] = pd.to_datetime(df_clean['Ultima_Revision'], errors='coerce')
    today = pd.Timestamp.now()
    future = (df_clean['Ultima_Revision'] > today).sum()
    if future > 0:
        df_clean.loc[df_clean['Ultima_Revision'] > today, 'Ultima_Revision'] = today
        log.append(f"Corregidas {future} fechas futuras")
    
    # 6. Eliminar duplicados
    dups = df_clean.duplicated(subset=['SKU_ID']).sum()
    if dups > 0:
        df_clean = df_clean.drop_duplicates(subset=['SKU_ID'])
        log.append(f"Eliminados {dups} SKUs duplicados")
    
    return df_clean, log

def clean_transacciones(df):
    """Limpia el dataset de transacciones"""
    df_clean = df.copy()
    log = []

    # 1. Limpiar fechas
    df_clean['Fecha_Venta'] = pd.to_datetime(df_clean['Fecha_Venta'], errors='coerce')
    nulls = df_clean['Fecha_Venta'].isnull().sum()
    if nulls > 0:
        df_clean = df_clean[df_clean['Fecha_Venta'].notna()]
        log.append(f"Eliminadas {nulls} transacciones sin fecha")

    # Eliminar fechas futuras
    today = pd.Timestamp.now()
    future = (df_clean['Fecha_Venta'] > today).sum()
    if future > 0:
        df_clean = df_clean[df_clean['Fecha_Venta'] <= today]
        log.append(f"Eliminadas {future} transacciones con fecha futura")

    # 2. Normalizar ciudades
    city_map = {
        'MED': 'Medellín', 'med': 'Medellín', 'Medellin': 'Medellín',
        'BOG': 'Bogotá', 'bog': 'Bogotá', 'Bogota': 'Bogotá'
    }
    df_clean['Ciudad_Destino'] = df_clean['Ciudad_Destino'].replace(city_map)
    log.append("Normalizados nombres de ciudades")

    # 3. Limpiar tiempo de entrega (columna real)
    col_tiempo = 'Tiempo_Entrega_Real'

    df_clean[col_tiempo] = pd.to_numeric(df_clean[col_tiempo], errors='coerce')

    outliers = (df_clean[col_tiempo] > 90).sum()
    if outliers > 0:
        mediana = df_clean[col_tiempo].median()
        df_clean.loc[df_clean[col_tiempo] > 90, col_tiempo] = mediana
        log.append(
            f"Corregidos {outliers} tiempos de entrega > 90 días "
            f"(mediana = {round(mediana, 2)})"
        )

    # 4. Eliminar cantidades y precios inválidos
    invalid = (
        (df_clean['Cantidad_Vendida'] <= 0) |
        (df_clean['Precio_Venta_Final'] <= 0)
    ).sum()

    if invalid > 0:
        df_clean = df_clean[
            (df_clean['Cantidad_Vendida'] > 0) &
            (df_clean['Precio_Venta_Final'] > 0)
        ]
        log.append(
            f"Eliminadas {invalid} transacciones con cantidades o precios inválidos"
        )

    # 5. Eliminar duplicados
    dups = df_clean.duplicated(subset=['Transaccion_ID']).sum()
    if dups > 0:
        df_clean = df_clean.drop_duplicates(subset=['Transaccion_ID'])
        log.append(f"Eliminados {dups} IDs de transacción duplicados")

    return df_clean, log


def clean_feedback(df):
    """Limpia el dataset de feedback"""
    df_clean = df.copy()
    log = []
    
    # 1. Eliminar duplicados
    dups_total = df_clean.duplicated().sum()
    df_clean = df_clean.drop_duplicates()
    dups_id = df_clean.duplicated(subset=['Feedback_ID']).sum()
    df_clean = df_clean.drop_duplicates(subset=['Feedback_ID'])
    total_removed = dups_total + dups_id
    if total_removed > 0:
        log.append(f"Eliminados {total_removed} registros duplicados")
    
    # 2. Normalizar NPS (si está en escala 0-10, convertir a -100/100)
    if df_clean['Satisfaccion_NPS'].max() <= 10:
        df_clean['Satisfaccion_NPS'] = df_clean['Satisfaccion_NPS'].apply(
            lambda x: -100 + (x/10)*200 if pd.notna(x) else x
        )
        log.append("Normalizada escala NPS a -100/+100")
    
    # 3. Validar ratings (1-5)
    invalid = ((df_clean['Rating_Producto'] < 1) | (df_clean['Rating_Producto'] > 5) |
               (df_clean['Rating_Logistica'] < 1) | (df_clean['Rating_Logistica'] > 5)).sum()
    if invalid > 0:
        df_clean = df_clean[
            (df_clean['Rating_Producto'] >= 1) & (df_clean['Rating_Producto'] <= 5) &
            (df_clean['Rating_Logistica'] >= 1) & (df_clean['Rating_Logistica'] <= 5)
        ]
        log.append(f"Eliminados {invalid} registros con ratings inválidos")
    
    # 4. Normalizar Ticket_Soporte a Sí/No
    ticket_map = {
        'si': 'Sí', 'SI': 'Sí', 'Si': 'Sí', 'sí': 'Sí',
        'no': 'No', 'NO': 'No', '1': 'Sí', '0': 'No'
    }
    df_clean['Ticket_Soporte'] = df_clean['Ticket_Soporte'].astype(str).map(
        lambda x: ticket_map.get(x, x)
    )
    
    return df_clean, log


def merge_datasets(inventario, transacciones, feedback):
    """Integra los tres datasets en uno solo"""
    
    # Merge transacciones + inventario (LEFT JOIN para identificar SKUs fantasma)
    df_merged = transacciones.merge(
        inventario,
        on='SKU_ID',
        how='left',
        indicator=True
    )
    
    # Marcar ventas fantasma
    df_merged['SKU_Fantasma'] = df_merged['_merge'] == 'left_only'
    phantom_count = df_merged['SKU_Fantasma'].sum()
    phantom_revenue = df_merged[df_merged['SKU_Fantasma']]['Precio_Venta_Final'].sum()
    
    df_merged = df_merged.drop('_merge', axis=1)
    
    # Merge con feedback
    df_final = df_merged.merge(
        feedback,
        on='Transaccion_ID',
        how='left'
    )
    
    # Crear variables derivadas
    df_final['Margen_USD'] = (
        df_final['Precio_Venta_Final'] - 
        (df_final['Costo_Unitario_USD'] * df_final['Cantidad_Vendida']) - 
        df_final['Costo_Envio']
    )
    
    df_final['Margen_Pct'] = (df_final['Margen_USD'] / df_final['Precio_Venta_Final'] * 100)
    
    df_final['Dias_Sin_Revision'] = (pd.Timestamp.now() - df_final['Ultima_Revision']).dt.days
    
    df_final['Ticket_Binary'] = (df_final['Ticket_Soporte'] == 'Sí').astype(int)
    
    metrics = {
        'total_records': len(df_final),
        'phantom_sales': phantom_count,
        'phantom_revenue': phantom_revenue
    }
    
    return df_final, metrics
