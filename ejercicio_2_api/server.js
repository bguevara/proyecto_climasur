import express from 'express';
import fs from 'fs';
import csv from 'csv-parser';
import { z } from 'zod';

const app = express();
const PORT = 3000;

// Almacenamiento en memoria
const db = {
    intervenciones: [],
    horas: [],
    materiales: [],
    desplazamientos: []
};

// Función auxiliar para cargar CSV
const loadCSV = (path) => {
    return new Promise((resolve) => {
        const results = [];
        fs.createReadStream(path)
            .pipe(csv())
            .on('data', (data) => results.push(data))
            .on('end', () => resolve(results));
    });
};

// Carga inicial de datos
async function init() {
    db.intervenciones = await loadCSV('../muestras/vista_climasur_intervenciones.csv');
    db.horas = await loadCSV('../muestras/vista_climasur_intervenciones_horas.csv');
    db.materiales = await loadCSV('../muestras/vista_climasur_intervenciones_materiales.csv');
    db.desplazamientos = await loadCSV('../muestras/vista_climasur_desplazamientos.csv');
    console.log('✅ CSVs cargados en memoria');
}

// --- ENDPOINTS ---

// 1. GET /intervenciones (Lista paginada)
const QuerySchema = z.object({
    estado: z.string().optional(),
    provincia: z.string().optional(),
    page: z.coerce.number().int().positive().default(1),
    limit: z.coerce.number().int().positive().default(10)
});

app.get('/intervenciones', (req, res) => {
    const validated = QuerySchema.safeParse(req.query);
    if (!validated.success) return res.status(400).json(validated.error);

    const { estado, provincia, page, limit } = validated.data;

    let filtered = db.intervenciones;

    if (estado) {
        filtered = filtered.filter(i => i.ESTADO?.toLowerCase() === estado.toLowerCase());
    }
    if (provincia) {
        filtered = filtered.filter(i => i.PROVINCIA_SEDE?.toLowerCase() === provincia.toLowerCase());
    }

    const total = filtered.length;
    const start = (page - 1) * limit;
    const paginated = filtered.slice(start, start + limit);

    res.json({
        data: paginated,
        pagination: { total, page, limit, total_pages: Math.ceil(total / limit) }
    });
});

// 2. GET /intervenciones/:cod (Detalle)
app.get('/intervenciones/:cod', (req, res) => {
    const cod = req.params.cod;
    const inter = db.intervenciones.find(i => i.COD_INCIDENCIA === cod);

    if (!inter) return res.status(404).json({ error: 'Intervención no encontrada' });

    res.json({
        ...inter,
        horas: db.horas.filter(h => h.COD_INCIDENCIA === cod),
        materiales: db.materiales.filter(m => m.COD_INCIDENCIA === cod),
        desplazamientos: db.desplazamientos.filter(d => d.COD_INCIDENCIA === cod)
    });
});

// 3. GET /kpis/resumen
app.get('/kpis/resumen', (req, res) => {
    const cerrados = ['Finalizado', 'Albaranado', 'No facturar', 'Anulado'];
    const pendientes = ['Asignado', 'Preasignada', 'Sin Asignar', 'Pendiente'];

    const stats = {
        total_intervenciones: db.intervenciones.length,
        total_cerradas: db.intervenciones.filter(i => cerrados.includes(i.ESTADO)).length,
        total_pendientes: db.intervenciones.filter(i => pendientes.includes(i.ESTADO)).length,
        coste_total: 0,
        venta_total: 0
    };

    // Cálculos de costes y ventas (Conversión a Float para evitar errores de string)
    db.horas.forEach(h => {
        stats.coste_total += parseFloat(h.COSTE || 0);
        stats.venta_total += parseFloat(h.VENTA || 0);
    });

    db.materiales.forEach(m => {
        const cant = parseFloat(m.UNIDADES || 0);
        stats.coste_total += cant * parseFloat(m.PRECIO_COSTE || 0);
        stats.venta_total += cant * parseFloat(m.PRECIO_VENTA || 0);
    });

    db.desplazamientos.forEach(d => {
        stats.coste_total += parseFloat(d.PRECIO_COSTE || 0);
        stats.venta_total += parseFloat(d.PRECIO_VENTA || 0);
    });

    res.json(stats);
});

init().then(() => {
    app.listen(PORT, () => console.log(`🚀 API lista en http://localhost:${PORT}`));
});