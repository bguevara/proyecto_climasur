## https://github.com/bguevara
## Estructura final del proyecto

```
borisGuevara/                    # Usa tu nombre real (ej. juan-garcia/)
├── README.md                       # Instrucciones de instalación y ejecución
├── muestras/                       # Datos proporcionados (no modificar)
│   ├── vista_climasur_intervenciones.csv
│   ├── vista_climasur_intervenciones_horas.csv
│   ├── vista_climasur_intervenciones_materiales.csv
│   └── vista_climasur_desplazamientos.csv
├── ejercicio_1_sql/
    |── loadTables.py               # script de python para cargar datos en la tablas de mysql (**adicional**) 
│   ├── schema.sql                  # DDL: tablas, tipos, PKs, FKs
│   └── margen_bruto.sql            # Consulta de margen bruto
├── ejercicio_2_api/
│   ├── package.json
│   ├── server.js                   # (o src/ con estructura libre)
│   └── ...
├── ejercicio_3_etl/
│   ├── sync.py                     # elaborado en python
│   ├── output/                     # Ficheros generados por el script
│   └── sync.log                    # Log de ejecución
└── ejercicio_4_propuesta/
    └── propuesta.md                # Análisis y propuesta de valor
    └── dashboard.py                # panel con visualizacion por provincia de margenes de ganancia (***adicional**)
```

## Lenguajes y librerias utilizadas
#Python
pandas

numpy

os

json

logging

datetime

streamlit

plotly.express

sqlAlchemy

#Node.js
express

fs (FileSystem)

csv-parser

zod (validación de esquemas)

## Base de datos
  Mysql

## Carpetas

 ## ejercicio_1.sql  

    # script adicional para cargar los datos desde los csv a cada tabla en la base de datos mysql. Esto para testear el sql margen_bruto
    python3 loadTables.py  
  
 ## ejercicio_2_api

    # ejecutar api express
     npm start

    #  http://localhost:3000

 ## ejercicio_3_etl

     # ejecutar etl

     python3 sync.py

## ejercicio_4_propuesta
    
    # ejecutar dashboard interactivo
     streamlit run dashboard.py --server.port 8501



