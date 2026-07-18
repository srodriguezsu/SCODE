# SCODE - Pipeline de Machine Learning

SCODE es un proyecto de machine learning diseñado para el procesamiento de datos, ingeniería de características (feature engineering) y entrenamiento de modelos. Este repositorio contiene los notebooks de Jupyter y los conjuntos de datos necesarios para ejecutar el pipeline.

---

## Estructura del Proyecto

```
SCODE/
├── Data/                             # Conjuntos de datos utilizados en el proyecto
│   ├── Datos_Test_Semestres_analisis.csv
│   └── group_data.pkl
├── Notebooks/                        # Notebooks de Jupyter que contienen el pipeline
│   ├── Procesamiento de datos.ipynb  # Preprocesamiento y exploración de datos
│   ├── Modeling.ipynb                 # Entrenamiento y validación de modelos
│   ├── Flujo por partes.ipynb         # Flujos de ejecución segmentados
│   └── decision_tree_scode.pkl       # Modelo de Árbol de Decisión entrenado y guardado
├── requirements.txt                  # Dependencias de Python
├── LICENSE                           # Licencia del proyecto
└── README.md                         # Este archivo
```

---

## Instrucciones de Configuración Local

Sigue estos pasos para configurar un entorno virtual y ejecutar el proyecto de forma local.

### 1. Prerrequisitos
Asegúrate de tener instalado **Python 3.8 o superior** en tu sistema. Puedes verificar tu versión ejecutando:
```bash
python3 --version
```

### 2. Crear el Entorno Virtual
Crea un entorno virtual llamado `.venv` en el directorio raíz del proyecto:

*   **Linux/macOS:**
    ```bash
    python3 -m venv .venv
    ```
*   **Windows:**
    ```cmd
    python -m venv .venv
    ```

### 3. Activar el Entorno Virtual
Activa el entorno virtual para aislar las dependencias:

*   **Linux/macOS:**
    ```bash
    source .venv/bin/activate
    ```
*   **Windows (Símbolo del sistema / CMD):**
    ```cmd
    .venv\Scripts\activate.bat
    ```
*   **Windows (PowerShell):**
    ```powershell
    .venv\Scripts\Activate.ps1
    ```

> [!NOTE]
> Una vez activado, el indicador (prompt) de tu terminal debería mostrar `(.venv)` al inicio.

### 4. Instalar Dependencias
Instala todas las librerías necesarias especificadas en `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Ejecución del Proyecto

Para ejecutar los notebooks con la configuración de entorno correcta, registra el kernel del entorno virtual y abre Jupyter:

### 1. Registrar el Kernel
Registra el kernel de tu entorno virtual en Jupyter para poder seleccionarlo dentro de los notebooks:
```bash
python -m ipykernel install --user --name=scode-venv --display-name "Python (SCODE)"
```

### 2. Iniciar Jupyter Notebook
Inicia la interfaz de Jupyter Notebook:
```bash
jupyter notebook
```

Esto abrirá automáticamente la interfaz de Jupyter en tu navegador web predeterminado.

### 3. Ejecutar los Notebooks
1. En la interfaz de Jupyter, navega al directorio `Notebooks/`.
2. Abre cualquiera de los archivos `.ipynb`.
3. En la esquina superior derecha del notebook, verifica el kernel. Si no está configurado como **Python (SCODE)**, ve a **Kernel** > **Change kernel** (Cambiar kernel) > **Python (SCODE)**.
4. Ejecuta las celdas de forma secuencial.

---

## Desactivación
Cuando hayas terminado de trabajar, puedes salir del entorno virtual ejecutando:
```bash
deactivate
```

---

## SCODE Recommendation API

Se ha agregado un servidor backend con **FastAPI** para exponer la lógica de recomendación de equipos como una API de alto rendimiento. Está diseñado para trabajar de forma asíncrona: recibe una petición con un ID de proyecto, consulta el API externo de datos, filtra los empleados según las habilidades necesarias, ejecuta el algoritmo de agrupamiento y predicción mediante un árbol de decisión, guarda los resultados creados y notifica al cliente frontend en tiempo real utilizando **WebSockets**.

### Estructura de Archivos del API
```
SCODE/
├── api/                              # Módulos del backend
│   ├── config.py                     # Carga de variables de entorno (.env)
│   ├── websocket_manager.py          # Administrador de conexiones WebSocket por tareas
│   ├── data_client.py                # Cliente HTTP asíncrono para consumir el API de datos
│   ├── recommender.py                # Lógica del modelo ML (Shannon, balance y predicción)
│   ├── tasks.py                      # Orquestador del flujo asíncrono en segundo plano
│   ├── main.py                       # Servidor de FastAPI y endpoints websocket/rest
│   └── test_recommender.py           # Script de validación local de la recomendación
├── run.py                            # Lanzador de la API (Uvicorn)
└── test_client.html                  # Dashboard web interactivo para pruebas de telemetría
```

### Iniciar la API

1. Asegúrate de tener activado el entorno virtual (`.venv`) y las dependencias instaladas.
2. Inicia el servidor de desarrollo local ejecutando:
   ```bash
   .venv/bin/python run.py
   ```
   El servidor se iniciará en `http://localhost:8000`.

---

## Uso de la API

### 1. Iniciar recomendación (`POST /projects/{project_id}/recommend`)

Registra e inicia un cálculo de recomendación de equipos para un proyecto determinado.

- **URL:** `http://localhost:8000/projects/{project_id}/recommend`
- **Método:** `POST`
- **Headers Requeridos:**
  - `Authorization: Bearer <JWT>` (El JWT es obligatorio ya que se reenvía al API de datos externo)
- **Ejemplo de Respuesta (200 OK):**
  ```json
  {
    "status": "processing",
    "message": "Team recommendation request received. Connect to WebSocket /ws/{task_id} to track progress.",
    "task_id": "4b684a0d-df89-4b36-a36c-9c3fbfb5ad21"
  }
  ```

### 2. Monitorear progreso (`WebSocket /ws/{task_id}`)

Los clientes (por ejemplo, el navegador web) se conectan a este WebSocket utilizando el `task_id` obtenido en el paso anterior para recibir telemetría paso a paso.

- **URL:** `ws://localhost:8000/ws/{task_id}`
- **Mensajes de Progreso (JSON):**
  A medida que avanza el procesamiento, el servidor notifica los cambios de estado:
  ```json
  {
    "status": "running_model",
    "message": "Step 4/5: Running machine learning model predictions..."
  }
  ```
- **Mensaje Final Exitoso:**
  Una vez finalizada la recomendación, los equipos se guardarán mediante `POST /teams/` en el backend externo y se transmitirá un reporte completo de los mismos antes de cerrar la conexión:
  ```json
  {
    "status": "completed",
    "message": "Team recommendation finished successfully.",
    "teams": [
      {
        "project_id": 1,
        "predicted_cohesion_index": 0.87298,
        "id": 142,
        "tenant_id": "default_tenant",
        "created_at": "2026-07-18T21:54:47.956Z",
        "members": []
      }
    ]
  }
  ```

---

## Cliente de Pruebas Interactivo

Se incluye un panel web interactivo [test_client.html](file:///home/sebas/UNAL/seminario-2/mvp/SCODE/test_client.html) para validar localmente el comportamiento completo del flujo:
1. Abre [test_client.html](file:///home/sebas/UNAL/seminario-2/mvp/SCODE/test_client.html) directamente en tu navegador.
2. Introduce las credenciales (URL del servidor, WebSocket, ID del proyecto y token JWT).
3. Haz clic en **Run Team Recommendation** para presenciar el ciclo de telemetría y ver los equipos resultantes en tarjetas interactivas de diseño moderno.

---
