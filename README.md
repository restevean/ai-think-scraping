# AI THINK Scrapping

Web scraper para recopilar opiniones, mensajes y conversaciones de múltiples plataformas sobre desarrollo de software.

## Requisitos

- Python 3.12+
- UV para gestión de entornos y dependencias

## Instalación

```bash
# Clonar el repositorio
git clone <repo>
cd ai-think-scrapping

# Crear entorno virtual con UV
uv venv

# Activar entorno
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows

# Instalar dependencias
uv pip install -e .

# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"
```

## Ejecución de test# AI THINK Scrapping

Web scraper para recopilar opiniones, mensajes y conversaciones de múltiples plataformas sobre desarrollo de software.

## Requisitos

- Python 3.12+
- UV para gestión de entornos y dependencias

## Instalación

```bash
# Clonar el repositorio
git clone <repo>
cd ai-think-scrapping

# Crear entorno virtual con UV
uv venv

# Activar entorno
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows

# Instalar dependencias
uv pip install -e .

# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"
```

## Ejecución de tests

```bash
pytest
```

## Estructura del proyecto

```
ai-think-scrapping/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   └── (módulos del proyecto)
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── data/
    └── (salida en JSON)
```

## Características

- [ ] Scraping de Google búsquedas
- [ ] Scraping de Bing
- [ ] Scraping de Reddit
- [ ] Scraping de Stack Overflow
- [ ] Scraping de Medium/Dev.to
- [ ] Scraping de X/Twitter
- [ ] Exportación a JSON
- [ ] Rate limiting y reintentos
- [ ] Logging detallado

## Licencia

MIT
```bash
pytest
```

## Estructura del proyecto

```
ai-think-scrapping/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   └── (módulos del proyecto)
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── data/
    └── (salida en JSON)
```

## Características

- [ ] Scraping de Google búsquedas
- [ ] Scraping de Bing
- [ ] Scraping de Reddit
- [ ] Scraping de Stack Overflow
- [ ] Scraping de Medium/Dev.to
- [ ] Scraping de X/Twitter
- [ ] Exportación a JSON
- [ ] Rate limiting y reintentos
- [ ] Logging detallado

## Licencia

MIT