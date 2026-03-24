# Proyecto de Prueba Técnica - Full Stack / Data Engineer

Este repositorio contiene la resolución de una prueba técnica integral, que abarca desde el modelado de datos en SQL hasta la creación de procesos ETL, una API REST y un Dashboard interactivo para la toma de decisiones.

https://github.com/bguevara

---

## 📁 Estructura del Proyecto

```text
borisGuevara/
├── muestras/               # Datos proporcionados (no modificar)
│   ├── vista_climasur_intervenciones.csv
│   ├── vista_climasur_intervenciones_horas.csv
│   ├── vista_climasur_intervenciones_materiales.csv
│   └── vista_climasur_desplazamientos.csv
├── ejercicio_1_sql/        # Modelado y consultas de base de datos
│   ├── loadTables.py       # Script de python para cargar datos en las tablas de mysql (**adicional**)
│   ├── schema.sql          # DDL: tablas, tipos, PKs, FKs
│   └── margen_bruto.sql    # Consulta de margen bruto
├── ejercicio_2_api/        # API REST funcional
│   ├── package.json
│   └── server.js           # (Punto de entrada con Express)
├── ejercicio_3_etl/        # Proceso de extracción y transformación
│   ├── sync.py             # Script elaborado en python
│   ├── output/             # Ficheros generados por el script
│   └── sync.log            # Log de ejecución
└── ejercicio_4_propuesta/  # Análisis de negocio y visualización
    ├── propuesta.md        # Análisis y propuesta de valor
    └── dashboard.py        # Panel con visualización por provincia de márgenes (**adicional**)


    🛠️ Lenguajes y Librerías Utilizadas
Python (Data & Automation)
Librerías principales: pandas, numpy, sqlAlchemy, pymysql

Visualización: streamlit, plotly.express

Core: os, json, logging, datetime

Node.js (API REST)
Framework: express

Validación: zod

Parsing: csv-parser, fs (FileSystem)

Base de Datos
Motor: MySQL

📋 Requisitos Previos
Antes de comenzar, asegúrate de tener instalado:

Python: v3.9 o superior

Node.js: v18.x o superior

MySQL: v8.0 o superior

Instalación de dependencias de Python:

Bash
pip install pandas numpy sqlalchemy pymysql streamlit plotly
🚀 Guía de Ejecución por Carpetas
1. ejercicio_1_sql
Incluye un script adicional para cargar los datos desde los CSV a cada tabla en la base de datos MySQL para testear la consulta de margen_bruto.sql.

🎥 Video explicativo: Ver en YouTube

Ejecutar carga:

Bash
python3 loadTables.py
2. ejercicio_2_api
API construida con Express para la gestión de datos.

🎥 Video explicativo: Ver en YouTube

Ejecución:

Bash
npm install
npm start
Acceso local: http://localhost:3000

3. ejercicio_3_etl
Proceso automatizado de sincronización y limpieza de datos.

🎥 Video explicativo: Ver en YouTube

Ejecución:

Bash
python3 sync.py
4. ejercicio_4_propuesta
Contiene el análisis estratégico y un dashboard interactivo para visualizar los márgenes de ganancia por provincia.

🎥 Video explicativo: Ver en YouTube

Ejecutar dashboard:

Bash
streamlit run dashboard.py --server.port 8501