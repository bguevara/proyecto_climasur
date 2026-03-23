# Prueba Técnica — Integración de Sistemas y Automatización

## Contexto

Climasur es una empresa de mantenimiento y climatización que opera en Andalucía, Ceuta y Melilla. Su sistema GMAO (MySQL) registra toda la actividad operativa.

En la carpeta `./muestras/` tienes exportaciones reales de 4 vistas de la base de datos, relacionadas entre sí por el campo `COD_INCIDENCIA`:

| Fichero | Filas | Contenido |
|---------|-------|-----------|
| `vista_climasur_intervenciones.csv` | 100 | Datos maestros de cada intervención (51 columnas): tipo, estado, cliente, provincia, fechas, técnico asignado, duración planificada, etc. |
| `vista_climasur_intervenciones_horas.csv` | 108 | Horas imputadas por los técnicos. Columnas: `COD_MANO_OBRA`, `COD_INCIDENCIA`, `USUARIO`, `FECHA_INICIO`, `FECHA_FIN`, `COSTE`, `VENTA`, entre otras. |
| `vista_climasur_intervenciones_materiales.csv` | 21 | Materiales usados en intervenciones. Columnas: `COD_INCIDENCIA`, `UNIDADES`, `PRECIO_COSTE`, `PRECIO_VENTA`, entre otras. |
| `vista_climasur_desplazamientos.csv` | 81 | Desplazamientos de técnicos. Columnas: `COD_DESPLAZAMIENTO`, `COD_INCIDENCIA`, `PRECIO_COSTE`, `PRECIO_VENTA`, entre otras. |

**Datos clave que encontrarás en las muestras:**

- La columna `ESTADO` de intervenciones contiene estos 8 valores: `Asignado` (30), `Albaranado` (21), `No facturar` (16), `Finalizado` (11), `Preasignada` (10), `Sin Asignar` (8), `Anulado` (3), `Pendiente` (1).
- La columna `TIPO` contiene: `Accion Correctiva`, `Mantenimiento Preventivo`, `Presupuesto`, `Obra`, `Visita Tecnica (No Facturable)`.
- La columna `PROVINCIA_SEDE` contiene: Málaga, Sevilla, Almería, Cádiz, Granada, Huelva, Córdoba, Melilla, Madrid.

---

## Ejercicio 1 — SQL (esquema + consulta)

Con la herramienta que prefieras (PostgreSQL, MySQL, SQLite...):

1. Crea el **esquema relacional** de las 4 tablas con tipos de datos correctos, claves primarias y claves foráneas sobre `COD_INCIDENCIA`. Puede asumirse que `COD_INCIDENCIA` identifica de forma única cada intervención en `vista_climasur_intervenciones.csv`. `COD_INCIDENCIA` actúa como identificador de negocio y debe conservarse tal como venga informado en los CSV. *Nota: no todas las tablas tienen un identificador único obvio en el CSV; se aceptan claves primarias técnicas autogeneradas (SERIAL, AUTOINCREMENT, etc.) siempre que justifiques la decisión.*

2. Escribe una consulta que calcule el **margen bruto por intervención**, definido como:
   - **Ventas** = `VENTA` de horas + (`UNIDADES` × `PRECIO_VENTA`) de materiales + `PRECIO_VENTA` de desplazamientos
   - **Costes** = `COSTE` de horas + (`UNIDADES` × `PRECIO_COSTE`) de materiales + `PRECIO_COSTE` de desplazamientos
   - **Margen bruto** = Ventas − Costes
   - Ordenado de mayor a menor margen.

Entrega: ficheros `.sql` con el DDL y la consulta.

---

## Ejercicio 2 — API de integración ligera (Node.js)

Desarrolla una API mínima (Express o Fastify) que cargue los 4 CSV de `./muestras/` en memoria y exponga estos 3 endpoints. No se espera conexión a base de datos ni capa de persistencia; el objetivo es evaluar tu capacidad de parsear datos, estructurar objetos, filtrar y validar.

| Método | Ruta | Qué devuelve |
|--------|------|--------------|
| `GET` | `/intervenciones` | Lista paginada de intervenciones. Acepta query params: `estado`, `provincia`, `page`, `limit`. Los filtros `estado` y `provincia` deben aplicarse por coincidencia exacta, ignorando mayúsculas/minúsculas. El formato de respuesta es libre, pero debe incluir como mínimo los registros paginados, la página actual, el límite y el total de resultados. |
| `GET` | `/intervenciones/:cod` | Detalle de una intervención (por `COD_INCIDENCIA`) junto con sus horas, materiales y desplazamientos asociados. |
| `GET` | `/kpis/resumen` | JSON con los campos descritos abajo. |

**Respuesta esperada de `/kpis/resumen`:**

Con las muestras suministradas, se espera un resultado equivalente a:

```json
{
  "total_intervenciones": 100,
  "total_cerradas": 51,
  "total_pendientes": 49,
  "coste_total": <suma de costes de horas + materiales + desplazamientos>,
  "venta_total": <suma de ventas de horas + materiales + desplazamientos>
}
```

Para calcular `total_cerradas` y `total_pendientes`, clasifica el campo `ESTADO` así:

| Clasificación | Estados (valores exactos del CSV) |
|---------------|-----------------------------------|
| **Cerrada** | `Finalizado`, `Albaranado`, `No facturar`, `Anulado` |
| **Pendiente** | `Asignado`, `Preasignada`, `Sin Asignar`, `Pendiente` |

Para `coste_total` y `venta_total`, suma las mismas columnas que en la consulta de margen bruto del Ejercicio 1 (columnas `COSTE`/`VENTA` de horas, `UNIDADES × PRECIO_COSTE`/`UNIDADES × PRECIO_VENTA` de materiales, y `PRECIO_COSTE`/`PRECIO_VENTA` de desplazamientos).

**Requisitos:**
- Manejo de errores HTTP: `400` para parámetros inválidos, `404` para intervención no encontrada.
- Validación de parámetros de entrada. Se valorará el uso de una librería de validación de esquemas (Zod, Joi o similar) frente a validaciones manuales dispersas.
- Que arranque con `npm install && npm start`.

---

## Ejercicio 3 — Script ETL (Node.js o Python)

Escribe un script que lea los 4 CSV de `./muestras/`, los transforme y genere una tabla analítica unificada:

1. **Extrae** los datos de los 4 ficheros CSV de `./muestras/`.

2. **Transforma** aplicando estas reglas:
   - Clasifica la columna `ESTADO` en una nueva columna `Estado_Clasificacion`:
     - `"Cerrada"` → para `Finalizado`, `Albaranado`, `No facturar`, `Anulado`
     - `"Pendiente"` → para `Asignado`, `Preasignada`, `Sin Asignar`, `Pendiente`
   - Convierte `DURACION_PLANIFICADA` (formato `"HH:MM"`) a horas decimales en una nueva columna `DuracionPlanificada_h` (ej: `"02:00"` → `2.0`, `"01:30"` → `1.5`). Si el valor viene vacío o mal formado, trátalo como `0`.
   - Calcula las horas reales trabajadas por intervención a partir de `FECHA_FIN - FECHA_INICIO` de la tabla de horas (columna `HorasImputadas_h`). Suma todas las filas de cada intervención; no es necesario detectar ni corregir posibles solapes temporales entre técnicos. Las fechas vienen en formato ISO 8601 (`YYYY-MM-DDTHH:MM:SS`) **sin indicador de zona horaria**; si alguna fila no puede parsearse correctamente, ignórala en el cálculo agregado y regístralo en el log. Se valorará documentar qué zona horaria se asume (ej. `Europe/Madrid`) y por qué.
   - Agrega por `COD_INCIDENCIA` desde las otras 3 tablas: `HorasImputadas_h`, `ImporteCoste` (materiales), `ImporteVenta` (materiales), `CosteDesplaz` y `VentaDesplaz` (desplazamientos).

3. **Carga** el resultado en un fichero `output/interv_analitica_YYYYMMDD_HHmmss.json` (o `.csv`). La tabla final debe tener las mismas 100 filas que intervenciones. Las columnas agregadas sin datos asociados deben representarse como `null` en JSON o campo vacío en CSV (no usar `NaN` ni valores centinela).

4. **Registra** en `sync.log` cada ejecución con: timestamp, filas procesadas, filas con horas imputadas, filas sin horas, y errores o incidencias de parseo. Los errores de parseo (fechas mal formadas, campos vacíos, etc.) deben registrarse como warnings no fatales; el script debe continuar procesando el resto de filas.

Ejecución con un solo comando: `node sync.js` o `python sync.py`.

---

## Ejercicio 4 — Propuesta de valor (creatividad y visión técnica)

Explora los datos de las 4 tablas de muestra y entrega un documento (`propuesta.md`) donde:

1. **Identifica al menos 2 problemas u oportunidades** que hayas detectado en los datos (calidad, incoherencias, patrones, información que falta, métricas que se podrían calcular, etc.). Explica por qué son relevantes para la operativa de una empresa de mantenimiento.

2. **Propón una funcionalidad, automatización o herramienta concreta** que podrías construir con estos datos para aportar valor real al negocio. Algunas ideas orientativas (valora proponer la tuya):
   - Un sistema de alertas automáticas.
   - Un panel de control con KPIs específicos.
   - Una optimización de asignación de técnicos.
   - Un proceso de detección de anomalías.
   - Una integración con un servicio externo.

3. **Describe cómo lo implementarías**: tecnologías, datos necesarios, arquitectura a alto nivel y pasos a seguir. No es necesario escribir código, pero el planteamiento debe ser técnicamente viable.

**Se valorará:**
- Que las propuestas demuestren que realmente exploraste y entendiste los datos. No te limites a decir "falta un KPI"; cuantifica el impacto con cifras concretas sacadas de las muestras (ej. porcentajes, costes acumulados, distribución por cliente o zona).
- Que el enfoque aporte valor al negocio, no solo sea un ejercicio técnico. Queremos ver que entiendes qué le duele a una empresa de mantenimiento, no solo que sabes escribir código.
- Claridad en la explicación y viabilidad de la solución.

No buscamos un documento extenso, sino una propuesta concreta, viable y bien razonada a partir de los datos.

---

## Estructura esperada del proyecto

```
nombre-apellido/                    # Usa tu nombre real (ej. juan-garcia/)
├── README.md                       # Instrucciones de instalación y ejecución
├── muestras/                       # Datos proporcionados (no modificar)
│   ├── vista_climasur_intervenciones.csv
│   ├── vista_climasur_intervenciones_horas.csv
│   ├── vista_climasur_intervenciones_materiales.csv
│   └── vista_climasur_desplazamientos.csv
├── ejercicio_1_sql/
│   ├── schema.sql                  # DDL: tablas, tipos, PKs, FKs
│   └── margen_bruto.sql            # Consulta de margen bruto
├── ejercicio_2_api/
│   ├── package.json
│   ├── server.js                   # (o src/ con estructura libre)
│   └── ...
├── ejercicio_3_etl/
│   ├── sync.js  (o sync.py)
│   ├── output/                     # Ficheros generados por el script
│   └── sync.log                    # Log de ejecución
└── ejercicio_4_propuesta/
    └── propuesta.md                # Análisis y propuesta de valor
```

**Notas sobre la organización:**
- Cada carpeta de ejercicio debe ser **autocontenida**: con su propio `package.json` si requiere dependencias, o ejecutable directamente.
- No subas `node_modules/` al repositorio (usa `.gitignore`).
- Si usas variables de entorno, incluye un `.env.example` con los nombres de las variables (sin valores reales).
- Se recomienda que los commits reflejen un progreso lógico del trabajo, aunque no se considerará un requisito eliminatorio.

---

## Entrega

- Repositorio Git (GitHub/GitLab) con la carpeta raíz nombrada como `nombre-apellido/`. Puede ser público o privado; si es privado, añade como colaborador al usuario que te indiquemos.
- Incluye en el `README.md` el **enlace a tu perfil de GitHub/GitLab** con tus repositorios y proyectos personales.
- **Tiempo orientativo: 6–10 horas.** Preferimos una entrega bien hecha en ese rango que una entrega apresurada en menos tiempo. Si necesitas priorizar, céntrate en que los ejercicios 1–3 funcionen correctamente antes de pulir el ejercicio 4 o la documentación.
- La prueba es individual.

## Qué se evalúa

| Área | Peso |
|------|------|
| Ejercicios 1–3: código funcional, limpio y bien estructurado | 60 % |
| Ejercicio 4: calidad del análisis, creatividad y viabilidad de la propuesta | 25 % |
| Organización del repositorio, commits y documentación | 15 % |

**Criterio general:** se valorará más una solución simple, correcta y bien explicada que una incompleta pero sobrearquitecturada. No se espera arquitectura hexagonal ni separación avanzada por capas; prioriza legibilidad, robustez básica y correcta resolución del problema. Preferimos código que funcione y se entienda a un README musculado con un backend de cartón.

**Sobre los commits:** un historial progresivo y con mensajes descriptivos es una buena señal, pero no es un requisito eliminatorio. Unos pocos commits claros valen más que veinte de "fix typo final v3".

**Aclaraciones técnicas:**
- **Lenguaje:** JavaScript y TypeScript son igualmente válidos. Se valorará positivamente el uso de TypeScript.
- **Librerías:** se permite el uso de librerías habituales para parseo de CSV, validación y utilidades, siempre que la solución mantenga un nivel de complejidad razonable.
- **Tests:** no se exigen tests unitarios ni de integración; si decides incluirlos, se tendrán en cuenta como extra.
- **Tipos de datos en SQL:** se esperan tipos razonables (`NUMERIC`/`DECIMAL` para importes, `TIMESTAMP` para fechas, `TEXT` cuando no se conozca la longitud máxima). No se penalizará la elección concreta siempre que sea coherente.
- **Datos inconsistentes:** campos vacíos, nulos o mal formados deben tratarse de forma defensiva (valores por defecto, ignorar el registro, etc.), no provocar un error fatal.
