# PetroAnalytics Colombia

**Dashboard Interactivo de Producción de Crudo en Colombia (2013–2022)**

Análisis completo, visualizaciones interactivas y predicciones basadas en datos oficiales de la **Agencia Nacional de Hidrocarburos (ANH)**.

---

## Características Principales

- Análisis por año, departamento, operadora y campo
- Mapa de calor (Choropleth) interactivo de Colombia
- Predicciones de producción nacional y declinación de campos usando Prophet
- Identificación de los campos con mayor tasa de declinación
- Filtros dinámicos y opción de descarga de datos
- Diseño moderno, responsive y profesional

---

## Tecnologías Utilizadas

- **Streamlit** – Framework para el dashboard
- **Pandas + PyArrow** – Procesamiento y almacenamiento eficiente
- **Plotly** – Visualizaciones interactivas
- **Prophet** – Modelos de predicción de series de tiempo
- **Parquet** – Formato optimizado de datos

---

## Estructura del Proyecto

```plaintext
crudo-colombia-dashboard/
├── data/                          # Archivos originales (.xlsx) de la ANH
├── cleaning/
│   └── clean_data.py              # Script completo de limpieza y transformación
├── dashboard/
│   └── app.py                     # Aplicación principal de Streamlit
├── data_processed/
│   └── crudo_limpio.parquet       # Datos limpios y optimizados
├── notebooks/                     # Notebooks de Colab (proceso exploratorio)
├── requirements.txt               # Librerias requeridas 
├── README.md
└── .gitignore
```
---
## Proceso de Limpieza Realizado

Se realizó un **ETL completo y robusto** para garantizar la calidad, consistencia y utilidad de los datos. Las principales etapas de limpieza fueron las siguientes:

### 1. Carga y Estandarización Inicial
- Carga de archivos Excel anuales (En `data/` )
- Eliminación de las primeras 10 filas de metadatos (`skiprows=10`)
- Normalización de nombres de columnas (`strip` + `lower`)
- Agregación de la columna `AÑO` como entero

### 2. Renombrado y Estandarización
- Conversión de nombres de columnas a mayúsculas consistentes  
  (`ENERO`, `FEBRERO`, `MARZO`, ..., `DEPARTAMENTO`, `CAMPO`, `CONTRATO`, etc.)

### 3. Limpieza de Valores Sucios
- Reemplazo de valores no numéricos comunes: `"-"`, `"*"`, `"ND"`, `"N/D"`, espacios en blanco, etc.
- Conversión a tipo numérico con `pd.to_numeric(errors='coerce')`
- Relleno de valores faltantes con 0 (cuando correspondía)

### 4. Conversión a Producción Mensual Real
- Multiplicación de la producción diaria promedio por el número real de días de cada mes
- Manejo correcto de años bisiestos (febrero con 29 días cuando aplica)
- Redondeo a entero usando el tipo `Int64` (que soporta valores NaN)

### 5. Eliminación de Filas de Totales
- Eliminación de las últimas 2 filas de cada archivo (filas de totales y resúmenes)

### 6. Limpieza de Texto (Tildes y Normalización)
- Eliminación de tildes manteniendo la letra **ñ**  
  (Ejemplo:`BOGOTÁ` → `BOGOTA`)
- Conversión a mayúsculas consistentes
- Eliminación de espacios innecesarios al inicio y final

### 7. Transformación a Formato Largo
- Conversión del formato ancho (una columna por mes) a formato largo (una fila por mes y valor)
- Creación de las columnas `MES` y `PRODUCCION`

---

## Cómo ejecutarlo localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/crudo-colombia-dashboard.git
cd crudo-colombia-dashboard

# 2. Crear y activar entorno virtual (recomendado)
python -m venv entorno
entorno\Scripts\activate        # En Windows
# source entorno/bin/activate   # En Linux / Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el dashboard
streamlit run dashboard/app.py
```
