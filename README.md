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
