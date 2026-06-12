# CNH Aftermarket Intelligence - Dashboard & Installer

Este directorio contiene el código fuente y las herramientas necesarias para instalar y ejecutar el **CNH Aftermarket Intelligence Dashboard**, una aplicación interactiva construida con Python (Dash y Plotly) para el análisis de flotas, horas de servicio y retención de clientes.

## 📋 Requisitos Previos

1. **Python**: Es imprescindible tener instalado [Python 3.8 o superior](https://www.python.org/downloads/).
   - **IMPORTANTE**: Durante la instalación de Python, asegúrate de marcar la casilla **"Add Python to PATH"** para que el instalador pueda detectarlo automáticamente.
2. **Sistema Operativo**: Windows (los scripts de instalación y lanzamiento están optimizados para entornos Windows a través de archivos `.bat` y `.lnk`).

---

## 🚀 Instrucciones de Instalación y Uso

### 1. Instalación
Para preparar el entorno y las dependencias, simplemente ejecuta el instalador principal:
- Haz doble clic en el archivo **`CNH_Dashboard_Instalador.bat`**.

**¿Qué hace el instalador?**
1. Verifica que Python esté instalado en tu sistema.
2. Crea un entorno virtual (`.venv`) aislado para no afectar otras instalaciones en tu computadora.
3. Actualiza el gestor de paquetes (`pip`).
4. Genera un script de lanzamiento (`Iniciar_Dashboard.bat`) dentro de la carpeta `codigo`.
5. Crea un acceso directo llamado **`CNH Dashboard.lnk`** junto al instalador.
6. Abre automáticamente el **Launcher** (interfaz gráfica) por primera vez.

### 2. Uso del Launcher
El Launcher (interfaz gráfica) facilita la ejecución del sistema sin necesidad de usar la línea de comandos. 

- **Verificación e Instalación de Librerías**: Al abrirse, comprobará si están instaladas todas las librerías necesarias (como `dash`, `pandas`, `plotly`, `openpyxl`, etc.). Si faltan, te mostrará un botón para **"Instalar librerías"**. Haz clic y espera a que termine.
- **Lanzar Dashboard**: Una vez que las librerías estén listas, haz clic en **"Lanzar Dashboard"**. Esto iniciará el servidor de la aplicación y, tras unos segundos, abrirá automáticamente tu navegador web por defecto mostrando el dashboard interactivo en `http://127.0.0.1:8050`.
- **Detener Dashboard**: Desde el mismo launcher puedes detener el servidor de forma segura.
- **Desinstalar**: Si necesitas limpiar el entorno, el launcher también provee una opción para desinstalar las dependencias de analítica de datos.

### 3. Siguientes Ejecuciones
Para volver a usar el dashboard en el futuro, no es necesario ejecutar el instalador principal nuevamente. Simplemente usa el acceso directo **`CNH Dashboard.lnk`** que se creó durante la instalación.

---

## 📁 Estructura del Código y Funciones

El corazón del proyecto se encuentra dentro del directorio `codigo`. A continuación, se detallan los componentes principales:

### `CNH_Dashboard_Instalador.bat` (Raíz)
- **Función**: Automatiza la configuración del entorno para Windows. Facilita que un usuario sin conocimientos técnicos pueda inicializar el proyecto con un par de clics, creando el entorno virtual y los accesos directos necesarios.

### `codigo/launcher.py`
- **Función**: Es una interfaz gráfica ligera construida con `tkinter`. 
- **Qué hace**: Evalúa qué librerías requiere el sistema y cuáles están disponibles. Ejecuta instalaciones de `pip` en segundo plano con una barra de progreso. Lanza un subproceso (`subprocess`) para levantar la aplicación principal (`app.py`) y abre el navegador web.

### `codigo/cnh_pipeline.py`
- **Función**: El cerebro de datos del sistema (Data Pipeline).
- **Qué hace**: 
  - Se encarga de la extracción, limpieza, y transformación (ETL) de los datos en bruto de los archivos Excel (`PopulationView`, `Horas`, `Mantenimientos`, `Reporte unidades día anterior`).
  - Normaliza columnas, imputa valores faltantes y unifica toda la información en un DataFrame central (`df_master`).
  - Calcula métricas, KPIs globales (como tasas de cumplimiento, unidades fuera de la red) e ingeniaría de características (Feature Engineering).
  - Admite carga de datos desde el disco duro o desde buffers en memoria (cuando el usuario sube archivos directamente en el dashboard).

### `codigo/app.py`
- **Función**: La aplicación web frontal (Frontend / Backend de presentación).
- **Qué hace**:
  - Utiliza el marco **Dash** y componentes de **Bootstrap** para renderizar la interfaz web con opciones de modo oscuro (Dark Theme) y modo claro (Light Theme).
  - Presenta las métricas a través de visualizaciones interactivas creadas con **Plotly**: 
    - Tarjetas de KPIs (unidades, alarmas, cumplimiento).
    - Gráficos de embudo de retención.
    - Mapas interactivos (con latitud/longitud de las unidades).
    - Mapas de calor (Heatmaps) de abandono por zonas y meses.
    - Coordenadas paralelas y clustering de riesgo para el análisis de flotas.
  - Interactúa directamente con el pipeline (`cnh_pipeline.py`) para consumir los datos limpios.

---

## 📊 Flujo de Trabajo (Resumen)
1. **Ejecución**: El usuario abre el acceso directo.
2. **Validación**: `launcher.py` asegura que las dependencias existan e inicia el servidor.
3. **Carga y Procesamiento**: `cnh_pipeline.py` procesa los Excels de datos.
4. **Visualización**: `app.py` renderiza la web interactiva, permitiendo al usuario explorar insights clave del Aftermarket de CNH de forma local y segura.
