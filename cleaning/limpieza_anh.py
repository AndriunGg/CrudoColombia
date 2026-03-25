# =============================================
# clean_data.py - Proceso completo de limpieza
# =============================================

import os
import pandas as pd
import calendar
import unicodedata
from pathlib import Path

# ===================== CONFIGURACIÓN =====================
# Rutas relativas (funciona tanto en local como en VS Code)
RAW_DATA_PATH = Path('../data')
PROCESSED_DATA_PATH = Path("../data_processed")
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DATA_PATH / "crudo_limpio.parquet"

# Meses en mayúsculas (como quedaron después del renombrado)
MES_COLS = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
            'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

# Valores sucios comunes en los archivos de la ANH
VALORES_SUCIOS = ["-", "--", "*", "ND", "N/D", "No reportado", "", " "]


def limpiar_tildes(texto):
    """Quita tildes pero mantiene la ñ"""
    if pd.isna(texto):
        return texto
    texto = str(texto)
    texto = texto.replace('ñ', '###NYE###').replace('Ñ', '###NYE_MAYUS###')
    
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    
    texto = texto.replace('###NYE###', 'ñ').replace('###NYE_MAYUS###', 'Ñ')
    return texto.strip().upper()


def dias_del_mes(año: int, mes_nombre: str) -> int:
    """Devuelve la cantidad de días de un mes (maneja años bisiestos)"""
    mes_num = MES_COLS.index(mes_nombre) + 1
    return calendar.monthrange(año, mes_num)[1]


print("🚀 Iniciando proceso de limpieza de datos de crudo...\n")

# ===================== 1. CARGAR ARCHIVOS =====================
archivos = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith((".xlsx", ".xls", ".csv"))]
archivos.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))

df_list = []
print(f"Se encontraron {len(archivos)} archivos:\n")

for archivo in archivos:
    ruta = RAW_DATA_PATH / archivo
    print(f"Cargando: {archivo} ...", end=" ")

    try:
        if archivo.endswith((".xlsx", ".xls")):
            df_temp = pd.read_excel(ruta, skiprows=10)
        else:
            df_temp = pd.read_csv(ruta, skiprows=10)

        # Normalizar columnas
        df_temp.columns = df_temp.columns.str.strip().str.lower()

        # Agregar columna año
        year = int(archivo.split('-')[-1].split('.')[0])
        df_temp["año"] = year

        df_list.append(df_temp)
        print("✓ OK")

    except Exception as e:
        print(f"✗ Error: {e}")

# ===================== 2. RENOMBRADO Y LIMPIEZA =====================
new_names = {
    'enero': 'ENERO', 'febrero': 'FEBRERO', 'marzo': 'MARZO', 'abril': 'ABRIL',
    'mayo': 'MAYO', 'junio': 'JUNIO', 'julio': 'JULIO', 'agosto': 'AGOSTO',
    'septiembre': 'SEPTIEMBRE', 'octubre': 'OCTUBRE', 'noviembre': 'NOVIEMBRE',
    'diciembre': 'DICIEMBRE',
    'departamento': 'DEPARTAMENTO', 'operadora': 'OPERADORA', 'campo': 'CAMPO',
    'contrato': 'CONTRATO', 'municipio': 'MUNICIPIO', 'año': 'AÑO'
}

for df in df_list:
    df.rename(columns=new_names, inplace=True)

# ===================== 3. LIMPIEZA DE VALORES SUCIOS Y MULTIPLICACIÓN =====================
for i, df in enumerate(df_list):
    año = df['AÑO'].iloc[0]
    print(f"\nProcesando año {año}...")

    meses_en_df = [col for col in MES_COLS if col in df.columns]

    # Reemplazar valores sucios
    df[meses_en_df] = df[meses_en_df].replace(VALORES_SUCIOS, pd.NA)

    # Multiplicar por días del mes
    for mes in meses_en_df:
        dias = dias_del_mes(año, mes)
        df[mes] = pd.to_numeric(df[mes], errors='coerce') * dias
        df[mes] = df[mes].round(0).astype('Int64')

    # Eliminar últimas 2 filas (totales)
    if len(df) > 2:
        df = df.iloc[:-2]

    df_list[i] = df
    print(f"   → {año} procesado correctamente ({len(meses_en_df)} meses)")

# ===================== 4. CONVERTIR A FORMATO LARGO =====================
print("\nConvirtiendo a formato largo...")

df_largo_list = []

for df in df_list:
    meses_en_df = [m for m in MES_COLS if m in df.columns]

    df_temp = pd.melt(
        df,
        id_vars=['DEPARTAMENTO', 'MUNICIPIO', 'OPERADORA', 'CONTRATO', 'CAMPO', 'AÑO'],
        value_vars=meses_en_df,
        var_name='MES',
        value_name='PRODUCCION'
    )

    df_largo_list.append(df_temp)

# ===================== 5. CREAR DATAFRAME FINAL =====================
print("Creando DataFrame final...")

df_total = pd.concat(df_largo_list, ignore_index=True)

# Limpieza final
df_total['PRODUCCION'] = pd.to_numeric(df_total['PRODUCCION'], errors='coerce')
df_total = df_total.dropna(subset=['PRODUCCION']).reset_index(drop=True)

# Aplicar limpieza de tildes (manteniendo ñ)
df_total['DEPARTAMENTO'] = df_total['DEPARTAMENTO'].apply(limpiar_tildes)
df_total['MUNICIPIO'] = df_total['MUNICIPIO'].apply(limpiar_tildes)
df_total['CAMPO'] = df_total['CAMPO'].apply(limpiar_tildes)
df_total['OPERADORA'] = df_total['OPERADORA'].apply(limpiar_tildes)

print(f"\n¡Proceso completado! DataFrame final: {df_total.shape[0]:,} filas × {df_total.shape[1]} columnas")

# ===================== 6. GUARDAR =====================
df_total.to_parquet('../data_processed/crudo_limpio.parquet', index=False)
print(f"Archivo guardado en: ../data_processed/crudo_limpio.parquet")