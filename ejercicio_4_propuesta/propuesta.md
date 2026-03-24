# Propuesta de Valor: Sistema de Control de Rentabilidad y Eficiencia SAT
**Candidato:** Boris Roberto Guevara Galíndez
## https://github.com/bguevara/proyecto_climasur.git


## 1. Identificación de Problemas y Oportunidades

Tras analizar los datos de `intervenciones`, `materiales` y `desplazamientos`, se han detectado fugas de valor crítico:

### A. Fuga de Ingresos en Desplazamientos
En `vista_climasur_desplazamientos.csv`, se observa que un **38% de los registros tienen PRECIO_VENTA = 0.0**, a pesar de generar un `PRECIO_COSTE` de entre 19€ y 25€. 
* **Impacto:** Impacto: En la muestra actual, técnicos como Daniel Castaño (Málaga) o Pedro Iglesias (Jaén) presentan múltiples registros con coste pero sin venta. Para una empresa de mantenimiento con cientos de servicios mensuales, esto supone una erosión silenciosa del margen neto de miles de euros al año.
* **Relevancia:** El desplazamiento es un recurso directo (combustible, tiempo, desgaste). Si no se factura o no se vincula a un contrato de mantenimiento que lo cubra, la operativa pierde sostenibilidad.

### La oportunidad: 

Implementando una validación automática en la API o el Dashboard (como la que diseñamos), puedes recuperar ese margen de forma inmediata. Si ClimaSur realiza 500 intervenciones al mes, recuperar 20€ de desplazamiento en el 40% de ellas equivale a 4.000€ mensuales de beneficio directo que hoy se están perdiendo.

### B. Materiales sin Referencia (Coste Cero)
Se han detectado múltiples registros en `vista_climasur_intervenciones_materiales.csv` con `COD_PIEZA: 0` y descripciones como *"líquido desatascador"* o *"filtros"*, donde los precios de coste y venta son **0.0**.
* **Impacto:** Esto indica que el técnico está utilizando materiales en el cliente que no están inventariados o no se están valorando. Si el material tiene coste cero en el sistema, el margen calculado es irreal.
* **Relevancia:** Impide el control de stock y el cálculo del Margen Bruto Real por intervención. Sin datos de coste precisos, la empresa no puede saber qué tipos de averías o qué clientes son realmente rentables.

### La oportunidad:

 Crear un Inventario Predictivo. Si los datos muestran que en la zona de Málaga las incidencias de "Acción Correctiva" consumen recurrentemente gas R-410A, la empresa puede realizar compras por volumen (bajando el PRECIO_COSTE) y asegurar que el técnico lleve el material en la furgoneta, evitando un segundo viaje.

### C.  Rediseño de la estructura de la base de datos.  
La estructura de las tablas presentadas obedece a la carga de los archivos csv, pero no estan normalizadas, los datos se repiten y no tienen relación con tablas maestro, ejemplo en la tabla de intervenciones, deberia estar relacionada con otras tablas, lo que implica crearlas, entre estas tablas pueden ser: tabla sintomas (cod_sintoma, sintoma),  departamentos (cod_departamento, departamento), estado (cod_estado, estado),
cliente (cod_cliente, cliente, direccion, cif), agente (cod_agente, nombre_agente), sede (cod_sede, sede, direccion, localidad), tecnico (cod?tecnico, nombre) .  Igualmente con las demás tablas asociadas a cada archivo.csv se debe implentar un rediseño


### D. Gestión de Desempeño por Sedes (Benchmarking)
    El Dashboard que creamos reveló que la rentabilidad no es uniforme entre Málaga, Sevilla, Almería o Jaén.

    ### La oportunidad: 
    Identificar por qué una sede es más eficiente que otra. ¿Es porque en Almería se agrupan mejor las rutas? ¿O porque en Sevilla se factura mejor la mano de obra? Esta visibilidad permite aplicar las "mejores prácticas" de la sede más rentable a las demás.

### E. Evolución de Mantenimiento Correctivo a Preventivo
    Los datos muestran una alta carga de "Acción Correctiva" (reparaciones de averías).

    ### La oportunidad: 

    Utilizar el historial de intervenciones para vender Contratos de Mantenimiento Preventivo a los clientes con más averías (como Moda Sur o Gestiona Facility). Es más rentable para ClimaSur planificar una visita que atender una emergencia un domingo con costes de horas extra.

### F. Profesionalización Tecnológica 
    Desde el punto de vista técnico, se tiene la oportunidad de dotar a la empresa de una Arquitectura de Datos Moderna:

    ETL Automatizado: Menos errores humanos al procesar partes de trabajo.

    API con Validación Zod: Datos limpios desde el origen (el técnico no puede cerrar un parte si faltan datos críticos).

    Dashboard Interactivo: Democratización del dato para que los gerentes no dependan de pedir informes en Excel.

---

## 2. Solución: "Sistema de Rentabilidad SAT"

Propongo una herramienta de **Análisis de datos **. Este sistema extrae, transforma e integra la información desde los archivos csv. o json, igualmente establece controles sobre el manejo de la infrormación .

### Funcionalidades:
1. **Bloqueo de Cierre por Margen Negativo:** Si la suma de ventas es menor a los costes (Horas + Mat + Desp), el sistema impide el cierre y envía una alerta al jefe de zona (ej. SAT Málaga).

1. **Dashboard por cliente y provincia:** El usuario puede observar facilmente, márgenes de ganancias y tomar medidas correctivas.

3. **Validación de Facturación de Kilometraje:** Si una incidencia tiene horas pero el desplazamiento está a 0€, el sistema solicita una justificación obligatoria.

---

## 3. Implementación Técnica

### Arquitectura
* **Backend:** Node.js (Express) para la lógica de validación 
* **Análisis:** Python (Pandas) para la generación de reportes de anomalías. Se incorporó un dashboard que muestra márgenes de ganancia. Ver README.MD
* **Alertas:** Integración vía **n8n** para notificar desviaciones de margen por Telegram o WhatsApp.

### Pasos:
1. **Normalización SQL:** Forzar precios mínimos en el maestro de desplazamientos.
2. **Endpoint de Validación:** Creado el endpoint `POST /intervenciones/:cod/validar` que calcule el balance real antes de permitir el cambio a estado "Finalizado". Ejecutar API con: npm start  
#http://localhost:3000
3. **Dashboard:** Crear un dashboard para el análisis de los márgenes de ganancia.
     Ejecutar con: streamlit run dashboard.py --server.port 8501
4. Igualmente si se desea un control pleno de todos los procesos, se puede implementar un sistema completo (backend-frontend) con Symfony (php), Django(python) o simplemnte una api con Express  