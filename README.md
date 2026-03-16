# FutureTech – Análisis de Centros de Datos

Script de visualización y análisis energético de centros de datos. Se conecta a una base de datos MySQL, extrae datos de consumo energético, costes operativos e indicadores de sostenibilidad, y genera automáticamente tres figuras con gráficos listos para informes.

---

## Requisitos

- Python 3.8 o superior

### Dependencias

| Librería | Versión recomendada | Uso |
|---|---|---|
| `pymysql` | ≥ 1.0 | Conexión a MySQL |
| `pandas` | ≥ 1.5 | Manipulación y análisis de datos |
| `matplotlib` | ≥ 3.6 | Generación de gráficos |

```bash
pip install pymysql pandas matplotlib
```

---

## Estructura de la base de datos

El script espera las siguientes tablas:

| Tabla | Columnas relevantes |
|---|---|
| `Centro_Datos` | `id_centro`, `nombre` |
| `Sector` | `id_sector`, `id_centro`, `nombre` |
| `Consumo_Energetico` | `id_sector`, `fecha`, `kwh_consumidos`, `fuente_energia` |
| `Costes_Operativos` | `id_sector`, `fecha`, `coste_energia`, `coste_mantenimiento`, `coste_personal`, `coste_total` |
| `Indicadores_Sostenibilidad` | `id_centro`, `anio`, `huella_carbono`, `porcentaje_renovable`, `indice_social`, `puntuacion_global` |

---

## Uso

```bash
python analisis_futuretech.py
```

El script realiza automáticamente los siguientes pasos:

1. Conecta a la base de datos y carga todas las tablas.
2. Limpia y prepara los datos (conversión de fechas, extracción del año, merge de tablas).
3. Imprime estadísticas descriptivas en la consola.
4. Genera y guarda tres archivos de imagen con los gráficos.
5. Muestra los gráficos en pantalla.

---

## Archivos generados

| Archivo | Contenido |
|---|---|
| `consumo_energetico.png` | kWh por año (barras), kWh por centro (barras horizontales), distribución por fuente de energía (tarta) |
| `costes_operativos.png` | Coste total por año (barras), desglose medio de costes (tarta), coste total por centro (barras horizontales) |
| `sostenibilidad.png` | Huella de carbono media por año (línea), % energía renovable por centro (barras), puntuación global por centro y año (líneas) |

---

## Descripción de los análisis

### 1. Consumo Energético

Analiza el total de kilovatios-hora consumidos, desglosando la evolución temporal por año, la comparativa entre centros y la distribución según la fuente de energía utilizada.

### 2. Costes Operativos

Muestra la evolución del coste total por año, el reparto proporcional entre energía, mantenimiento y personal, y el coste acumulado por centro de datos.

### 3. Indicadores de Sostenibilidad

Presenta la tendencia de la huella de carbono media a lo largo de los años, el porcentaje de energía renovable de cada centro en el último año disponible, y la evolución de la puntuación global de sostenibilidad por centro.

---

## Notas adicionales

- Los valores numéricos en consola se formatean con separador de miles (punto) y decimales (coma), siguiendo la convención española.
- Los ejes de los gráficos usan formato de número sin notación científica.
- Si algún registro tiene una fecha inválida o nula, se descarta automáticamente antes del análisis.
