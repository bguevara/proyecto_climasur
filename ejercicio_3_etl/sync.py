import pandas as pd
import numpy as np
import os
import json
import logging
from datetime import datetime

# 0. Configuración de Logging
logging.basicConfig(
    filename='sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_duration_to_hours(duration_str):
    """Convierte HH:MM a horas decimales."""
    try:
        if pd.isna(duration_str) or not duration_str:
            return 0.0
        h, m = map(int, str(duration_str).split(':'))
        return h + (m / 60.0)
    except:
        return 0.0

def sync():
    start_time = datetime.now()
    path_muestras = '../muestras/'
    output_dir = './output/'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # 1. EXTRAER (Extract)
        df_intv = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_intervenciones.csv'))
        df_horas = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_intervenciones_horas.csv'))
        df_mats = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_intervenciones_materiales.csv'))
        df_desp = pd.read_csv(os.path.join(path_muestras, 'vista_climasur_desplazamientos.csv'))

        # 2. TRANSFORMAR (Transform)
        
        # A. Clasificación de Estado
        cerrados = ["Finalizado", "Albaranado", "No facturar", "Anulado"]
        df_intv['Estado_Clasificacion'] = df_intv['ESTADO'].apply(
            lambda x: 'Cerrada' if x in cerrados else 'Pendiente'
        )

        # B. Duración Planificada a Decimal
        df_intv['DuracionPlanificada_h'] = df_intv['DURACION_PLANIFICADA'].apply(parse_duration_to_hours)

        # C. Cálculo de Horas Reales (Agregación)
        # Nota: Se asume zona horaria Europe/Madrid por ser el contexto operativo de la empresa.
        def calculate_diff(row):
            try:
                inicio = pd.to_datetime(row['FECHA_INICIO'])
                fin = pd.to_datetime(row['FECHA_FIN'])
                diff = (fin - inicio).total_seconds() / 3600
                return diff if diff >= 0 else 0
            except Exception as e:
                logging.warning(f"Error parseando fechas en intervención {row['COD_INCIDENCIA']}: {e}")
                return np.nan

        df_horas['horas_calc'] = df_horas.apply(calculate_diff, axis=1)
        # Agregamos por intervención ignorando NaNs (filas que fallaron el parseo)
        horas_agg = df_horas.groupby('COD_INCIDENCIA')['horas_calc'].sum().reset_index()
        horas_agg.columns = ['COD_INCIDENCIA', 'HorasImputadas_h']

        # D. Agregación de Materiales
        df_mats['coste_total'] = df_mats['UNIDADES'] * df_mats['PRECIO_COSTE']
        df_mats['venta_total'] = df_mats['UNIDADES'] * df_mats['PRECIO_VENTA']
        mats_agg = df_mats.groupby('COD_INCIDENCIA').agg({
            'coste_total': 'sum',
            'venta_total': 'sum'
        }).reset_index()
        mats_agg.columns = ['COD_INCIDENCIA', 'ImporteCoste', 'ImporteVenta']

        # E. Agregación de Desplazamientos
        desp_agg = df_desp.groupby('COD_INCIDENCIA').agg({
            'PRECIO_COSTE': 'sum',
            'PRECIO_VENTA': 'sum'
        }).reset_index()
        desp_agg.columns = ['COD_INCIDENCIA', 'CosteDesplaz', 'VentaDesplaz']

        # F. Merge Final (LEFT JOIN para mantener las 100 intervenciones)
        df_final = df_intv.merge(horas_agg, on='COD_INCIDENCIA', how='left')
        df_final = df_final.merge(mats_agg, on='COD_INCIDENCIA', how='left')
        df_final = df_final.merge(desp_agg, on='COD_INCIDENCIA', how='left')

        # 3. CARGAR (Load)
        timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'interv_analitica_{timestamp_str}.json')
        
        # Convertimos a diccionario y manejamos NaNs como None (null en JSON)
        result_json = df_final.replace({np.nan: None}).to_dict(orient='records')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_json, f, ensure_ascii=False, indent=4)

        # 4. Registro en Log
        filas_procesadas = len(df_final)
        filas_con_horas = df_final['HorasImputadas_h'].notna().sum()
        filas_sin_horas = df_final['HorasImputadas_h'].isna().sum()
        
        logging.info(f"EJECUCIÓN EXITOSA | Filas procesadas: {filas_procesadas} | "
                     f"Con horas: {filas_con_horas} | Sin horas: {filas_sin_horas}")

    except Exception as e:
        logging.error(f"ERROR FATAL en el proceso ETL: {str(e)}")

if __name__ == "__main__":
    sync()