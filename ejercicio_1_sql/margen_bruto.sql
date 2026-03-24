WITH TotalesHoras AS (
    SELECT COD_INCIDENCIA, SUM(COSTE) as total_coste_h, SUM(VENTA) as total_venta_h
    FROM intervenciones_horas GROUP BY COD_INCIDENCIA
),
TotalesMateriales AS (
    SELECT COD_INCIDENCIA, 
           SUM(UNIDADES * PRECIO_COSTE) as total_coste_m, 
           SUM(UNIDADES * PRECIO_VENTA) as total_venta_m
    FROM intervenciones_materiales GROUP BY COD_INCIDENCIA
),
TotalesDesplaz AS (
    SELECT COD_INCIDENCIA, SUM(PRECIO_COSTE) as total_coste_d, SUM(PRECIO_VENTA) as total_venta_d
    FROM desplazamientos GROUP BY COD_INCIDENCIA
)
SELECT 
    i.COD_INCIDENCIA,
    i.CLIENTE,
    (COALESCE(h.total_venta_h, 0) + COALESCE(m.total_venta_m, 0) + COALESCE(d.total_venta_d, 0)) AS Ventas,
    (COALESCE(h.total_coste_h, 0) + COALESCE(m.total_coste_m, 0) + COALESCE(d.total_coste_d, 0)) AS Costes,
    ((COALESCE(h.total_venta_h, 0) + COALESCE(m.total_venta_m, 0) + COALESCE(d.total_venta_d, 0)) - 
     (COALESCE(h.total_coste_h, 0) + COALESCE(m.total_coste_m, 0) + COALESCE(d.total_coste_d, 0))) AS Margen_Bruto
FROM intervenciones i
LEFT JOIN TotalesHoras h ON i.COD_INCIDENCIA = h.COD_INCIDENCIA
LEFT JOIN TotalesMateriales m ON i.COD_INCIDENCIA = m.COD_INCIDENCIA
LEFT JOIN TotalesDesplaz d ON i.COD_INCIDENCIA = d.COD_INCIDENCIA
ORDER BY Margen_Bruto DESC;