import pandas as pd
from sqlalchemy import create_engine, text
import os
import logging

# este script se encarga de cargar los datos desde los archivos CSV a las tablas de MariaDB, asegurando que solo se inserten registros nuevos para evitar duplicados. Además, se implementa un sistema de logging para registrar el proceso de sincronización, incluyendo cualquier error que pueda ocurrir. La
# esto con la finalidad de probar el query de margen bruto

# Configuración de Logs
logging.basicConfig(
    filename='sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DB_CONFIG = {
    'user': 'bguevara',
    'pass': '16557544',
    'host': 'localhost',
    'port': '3306',
    'db': 'bd_proyecto'
}

def get_engine():
    url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['pass']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db']}"
    # autocommit=True ayuda a que los cambios se reflejen inmediatamente en MariaDB
    return create_engine(url, isolation_level="READ COMMITTED")

def run_sync():
    engine = get_engine()
    base_path = "../muestras/"
    
    # Mapeo de archivos, tablas y sus Claves Primarias para validación
    tablas_mapeo = [
        {
            'archivo': 'vista_climasur_intervenciones.csv', 
            'tabla': 'intervenciones', 
            'pk': 'cod_incidencia'
        },
        {
            'archivo': 'vista_climasur_desplazamientos.csv', 
            'tabla': 'desplazamientos', 
            'pk': 'cod_desplazamiento'
        },
        {
            'archivo': 'vista_climasur_intervenciones_horas.csv', 
            'tabla': 'intervenciones_horas', 
            'pk': 'cod_mano_obra'
        },
        {
            'archivo': 'vista_climasur_intervenciones_materiales.csv', 
            'tabla': 'intervenciones_materiales', 
            'pk': 'cod_pieza' # O el campo identificador que prefieras
        }
    ]

    logging.info("--- Iniciando Sincronización con Validación ---")

    try:
        with engine.connect() as connection:
            # Desactivar temporalmente FK para evitar bloqueos durante la carga masiva
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            for item in tablas_mapeo:
                file_path = os.path.join(base_path, item['archivo'])
                
                if not os.path.exists(file_path):
                    logging.warning(f"Archivo no encontrado: {file_path}")
                    continue

                # 1. Extracción y Transformación
                df = pd.read_csv(file_path)
                df.columns = [c.lower() for c in df.columns]
                
                # 2. Validación: Filtrar registros que ya existen en la BD
                try:
                    existentes = pd.read_sql(f"SELECT {item['pk']} FROM {item['tabla']}", connection)
                    # Solo nos quedamos con los que NO están en la base de datos
                    df_nuevo = df[~df[item['pk']].isin(existentes[item['pk']])]
                except:
                    # Si la tabla está vacía o hay error, cargamos todo
                    df_nuevo = df

                # 3. Carga
                if not df_nuevo.empty:
                    # Usamos method='multi' para mayor eficiencia en MySQL
                    df_nuevo.to_sql(
                        item['tabla'], 
                        con=connection, 
                        if_exists='append', 
                        index=False, 
                        chunksize=500
                    )
                    logging.info(f"Tabla {item['tabla']}: Se insertaron {len(df_nuevo)} registros nuevos.")
                else:
                    logging.info(f"Tabla {item['tabla']}: No hay registros nuevos para cargar.")

            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            # Forzamos un COMMIT final
            connection.execute(text("COMMIT;"))
            
        print("Proceso completado. Revisa sync.log para el detalle de la carga.")

    except Exception as e:
        logging.error(f"Error crítico: {e}")
        print(f"Error detectado: {e}")

if __name__ == "__main__":
    run_sync()