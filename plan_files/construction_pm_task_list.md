# Construction PM MVP - Lista de tareas

## Checklist de ejecucion

- [x] Confirmar alcance final del MVP (rapido, hibrido, convivencia con hospitality).
- [x] Definir KPIs obligatorios de la primera version (6-8 maximo).
- [x] Definir los 2-3 graficos iniciales del modulo.
- [x] Preparar en data.py el bloque minimo de datos de construccion.
- [x] Crear funciones derivadas en data.py para calcular KPIs agregados.
- [x] Crear modules/construction_pm.py con funcion render().
- [x] Implementar filtro por proyecto dentro del nuevo modulo.
- [x] Renderizar bloque ejecutivo de KPIs usando kpi_card.
- [x] Renderizar graficos de avance y presupuesto usando Plotly.
- [x] Agregar tabla operativa de riesgos priorizados.
- [x] Integrar modulo en app.py (import + opcion sidebar + router).
- [x] Redefinir Planned vs Actual con logica a fecha de corte (hoy).
- [x] Incorporar SPI y CPI para semaforo cuantitativo.
- [x] Incorporar Delay Days y EAC Variance para exposicion de margen.
- [x] Implementar Gantt dinamico por proyecto (Baseline vs Forecast/Actual).
- [x] Agregar linea Today en Gantt para lectura inmediata de atraso.
- [ ] Probar navegacion completa entre todas las secciones.
- [ ] Validar coherencia de cifras entre KPIs, graficos y tabla.
- [x] Revisar errores de import/lint en archivos modificados.
- [ ] Ajustar textos y labels para claridad del demo en presentacion.

## Que hacer primero (orden critico)

1. Confirmar KPIs y graficos obligatorios.
2. Estructurar datos minimos en data.py.
3. Construir render() base en modules/construction_pm.py.
4. Integrar en app.py.
5. Cerrar con pruebas y ajustes visuales.
