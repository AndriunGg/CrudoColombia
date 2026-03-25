import pandas as pd

# Cargar
df = pd.read_parquet('../data_processed/crudo_limpio.parquet')
print(f'Shape: {df.shape}')  # Esperado: ~49,928 filas, 8 cols[file:1]

print('\n--- Nulos finales (debe ser 0 todo) ---')
print(df.isna().sum())

print('\n--- Tipos (PRODUCCION Int64, AO int64) ---')
print(df.dtypes)

print('\n--- Stats PRODUCCION ---')
print(df['PRODUCCION'].describe())

print('\n--- Únicos clave (como Colab) ---')
print('Departamentos:', sorted(df['DEPARTAMENTO'].unique()))
print('Operadoras:', df['OPERADORA'].nunique())
print('Campos:', df['CAMPO'].nunique())
print('Contratos:', df['CONTRATO'].nunique())

print('\n--- VERIFICACIÓN TILDES (exacto como Colab) ---')
# 1. CAÑO LIMÓN en CAMPOS (sin tildes: CAO LIMON, pero Ñ preservada si existe)
print('Campos con "CAÑO" (esperado >0):', 
      df['CAMPO'].str.contains('CAÑO', case=False, na=False).sum())
print('Ejemplo campos CAO:', 
      df[df['CAMPO'].str.contains('CAO', case=False, na=False)]['CAMPO'].unique()[:3])

# 2. NARIÑO en DEPARTAMENTO (sin tildes: NARIÑO -> NARIÑO con Ñ preservada)
print('Depts con "NARIÑ" (esperado 0 si no hay NARIÑO, o >0):', 
      df['DEPARTAMENTO'].str.contains('NARIÑ', na=False).sum())
print('Depts únicos con NARI:', 
      df[df['DEPARTAMENTO'].str.contains('NARI', na=False)]['DEPARTAMENTO'].unique())

print('\n--- VERIFICACIÓN 2022 FEBRERO YATAY (Colab: 95955 barriles) ---')
valor_yatay = df[(df['CAMPO']=='YATAY') & (df['MES']=='FEBRERO') & (df['AÑO']==2022)]['PRODUCCION'].iloc[0]
print(f'YATAY-FEBRERO-2022: {valor_yatay} (esperado: 95955)')

print('\n--- TAIL FINAL (igual a Colab) ---')
print(df.tail())

print('\n--- ¡VALIDADO! ---' if df.isna().sum().sum() == 0 and valor_yatay == 95955 else '❌ Revisa logs')
