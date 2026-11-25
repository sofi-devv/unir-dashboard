# UNIR · Dashboard de Competencias en Analítica (PRELIMINAR)

Tablero interactivo en Streamlit para comparar las competencias demandadas en ofertas laborales frente a los planes de estudio de UNIR, junto con el detalle de evidencias por oferta/programa y los resultados de la encuesta a profesionales de datos.

> **Aviso importante:** Todas las cifras corresponden a la **relectura preliminar del 30 de octubre de 2026** (51 avisos completos y 29 planes de estudio; encuesta procesada el 14 de octubre de 2026) y están sujetas a validación oficial con el clasificador y el juez. **No compartir ni publicar sin autorización expresa.**

## Estructura del proyecto

```text
unir_streamlit/
├── app.py                  # Aplicación principal de Streamlit
├── requirements.txt        # Dependencias de Python
├── README.md               # Esta guía
├── .streamlit/
│   └── config.toml         # Tema visual (primario #1F4E79, fondo blanco)
├── assets/
│   └── unir_logo.png       # Logotipo de UNIR
└── data/
    ├── tab_comparacion.csv # Tabla agregada por variable × fuente × medida
    ├── tab_detalle.csv     # Evidencias y citas por unidad × variable
    ├── tab_encuesta.csv    # Resultados de la encuesta (P01–P11)
    └── tab_notas.csv       # Notas metodológicas y pendientes
```

## Cómo ejecutarlo en local

1. Asegúrate de tener Python 3.10 o superior.
2. Desde esta carpeta (`unir_streamlit/`), crea e inicia un entorno virtual (opcional pero recomendado) e instala las dependencias:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Inicia la aplicación:

   ```bash
   streamlit run app.py
   ```

4. Abre en tu navegador la dirección local que aparece en la terminal (por defecto `http://localhost:8501`).

## Cómo desplegarlo en Streamlit Community Cloud (cuando autorices compartirlo)

1. Crea un repositorio **privado** (recomendado mientras siga en revisión) en GitHub y sube el contenido completo de la carpeta `unir_streamlit/` (incluyendo `data/`, `assets/` y `.streamlit/config.toml`).
2. Ingresa a [share.streamlit.io](https://share.streamlit.io/) con tu cuenta de GitHub.
3. Haz clic en **New app**, selecciona el repositorio, la rama principal (`main`) y establece como archivo principal `app.py`.
4. Haz clic en **Deploy!**. Una vez publicado, puedes gestionar en **Settings → Sharing** quién tiene permiso para ver la aplicación antes de abrir el enlace a terceros.
