# Explicación Detallada del Comando ThinkScraper

## Nivel 1: Estructura General

ThinkScraper es una **herramienta CLI (Command Line Interface)** que funciona con la estructura:

```bash
thinkscraper [COMANDO] [ARGUMENTOS] [OPCIONES]
```

Tiene **7 comandos principales**.

---

## Nivel 2: Comandos Disponibles

### 1️⃣ `list-platforms` (El más simple)

```bash
thinkscraper list-platforms
```

**Qué hace:** Muestra las plataformas que ThinkScraper soporta.

**Salida:**
```
📋 Supported Platforms:
  • devto
  • medium
  • reddit
  • stackoverflow
```

---

### 2️⃣ `scrape-url` (Una URL, simple)

```bash
thinkscraper scrape-url "https://reddit.com/r/Python"
```

**Qué hace:** Scrappea una única URL detectando automáticamente su plataforma.

**Con opción output:**
```bash
thinkscraper scrape-url "https://reddit.com/r/Python" --output resultado.json
```

**Salida:**
```
🔍 Scraping: https://reddit.com/r/Python
✅ Success! Extracted 15 messages
📁 Results saved to: resultado.json
```

---

### 3️⃣ `scrape-urls` (Múltiples URLs desde archivo)

Primero creas un archivo de texto:

```bash
cat > urls.txt << EOF
https://reddit.com/r/Python
https://stackoverflow.com/questions/123
https://medium.com/@author/article
EOF
```

Luego lo scrapeas:

```bash
thinkscraper scrape-urls urls.txt --output resultados.json
```

**Qué hace:**
- Lee TODAS las URLs del archivo `urls.txt` (una por línea)
- Scrappea cada una detectando su plataforma automáticamente
- Guarda resultados combinados en `resultados.json`
- Genera un resumen estadístico

**Salida:**
```
🔍 Scraping 3 URLs from urls.txt
✅ Completed: 3/3 successful
   Total messages extracted: 120
   Success rate: 100.0%
📁 Results saved to: resultados.json
```

**Opción importante:**
```bash
thinkscraper scrape-urls urls.txt --output resultados.json --skip-errors
```

La opción `--skip-errors` hace que continúe aunque algunas URLs fallen. Sin ella, si una URL falla, se detiene TODO.

---

### 4️⃣ `scrape-platform` (Múltiples URLs de UNA plataforma)

```bash
thinkscraper scrape-platform reddit \
  https://reddit.com/r/Python \
  https://reddit.com/r/JavaScript \
  https://reddit.com/golang
```

**Qué hace:**
- Scrappea múltiples URLs de la MISMA plataforma
- Es más eficiente que `scrape-urls` porque **no necesita detectar plataforma para cada URL**
- Usa el mismo scraper para todas (más rápido)

**Ventaja de rendimiento:**
```
scrape-urls     → Detecta plataforma 3 veces (lento)
scrape-platform → Usa el mismo scraper 3 veces (rápido)
```

---

### 5️⃣ `show-summary` (Ver resumen de resultados)

```bash
thinkscraper show-summary resultados.json
```

**Qué hace:** Muestra un resumen de los datos extraídos sin abrir el archivo JSON.

**Salida:**
```
📊 Scraping Summary:

  Total URLs:        5
  Successful:        4
  Failed:            1
  Total Messages:    245
  Success Rate:      80.0%
```

---

### 6️⃣ `export-results` (Convertir JSON a otro formato)

```bash
thinkscraper export-results resultados.json reporte.csv --format csv
```

**Qué hace:** Convierte los resultados JSON a CSV (o mantiene JSON).

**Formatos disponibles:**
- `--format json` → Mantiene formato JSON
- `--format csv` → Convierte a CSV

**CSV resultante:**
```csv
url,success,messages_count,error
https://reddit.com/r/Python,True,15,
https://stackoverflow.com/q/123,True,8,
https://invalid.com,False,0,No scraper supports URL
```

---

## Nivel 3: Estructura del JSON de Salida

Cuando haces scraping y usas `--output`, obtienes algo como:

```json
{
  "results": [
    {
      "success": true,
      "url": "https://reddit.com/r/Python",
      "messages_count": 15,
      "error": null,
      "timestamp": "2024-11-04T10:30:00"
    },
    {
      "success": false,
      "url": "https://invalid.com",
      "messages_count": 0,
      "error": "No scraper supports URL",
      "timestamp": "2024-11-04T10:31:00"
    }
  ],
  "summary": {
    "total_urls": 2,
    "successful": 1,
    "failed": 1,
    "total_messages": 15,
    "success_rate": 50.0
  }
}
```

---

## Nivel 4: Flujo Completo (Cómo usarlos juntos)

**Paso 1:** Crear archivo con URLs
```bash
cat > mis_urls.txt << EOF
https://reddit.com/r/Python
https://stackoverflow.com/questions/12345
https://medium.com/@author/article
EOF
```

**Paso 2:** Scrapear todas
```bash
thinkscraper scrape-urls mis_urls.txt --output resultados.json
```

**Paso 3:** Ver resumen
```bash
thinkscraper show-summary resultados.json
```

**Paso 4:** Exportar a CSV para análisis
```bash
thinkscraper export-results resultados.json reporte.csv --format csv
```

**Resultado final:** `reporte.csv` listo para abrir en Excel.

---

## Nivel 5: Opciones Disponibles por Comando

### `thinkscraper scrape-url`
- `--output, -o` → Archivo de salida (JSON)
- `--help` → Mostrar ayuda

### `thinkscraper scrape-urls`
- `--output, -o` → Archivo de salida (JSON) [REQUERIDO]
- `--skip-errors` → Continuar si hay errores
- `--help` → Mostrar ayuda

### `thinkscraper scrape-platform`
- `--output, -o` → Archivo de salida (JSON)
- `--help` → Mostrar ayuda

### `thinkscraper export-results`
- `--format` → Formato de salida (json, csv) [default: json]
- `--help` → Mostrar ayuda

---

## Resumen Visual de Todos los Comandos

| Comando | Para qué | Entrada | Salida |
|---------|----------|---------|--------|
| `list-platforms` | Ver plataformas soportadas | Ninguna | Terminal |
| `scrape-url` | Scrapear 1 URL | URL en terminal | JSON (opcional) |
| `scrape-urls` | Scrapear N URLs | Archivo .txt | JSON con resumen |
| `scrape-platform` | Scrapear N URLs misma plataforma | Plataforma + URLs | JSON con resumen |
| `show-summary` | Ver resumen de resultados | JSON previo | Terminal |
| `export-results` | Convertir formato JSON a CSV | JSON previo | CSV o JSON |

---

## Casos de Uso Comunes

### Caso 1: Scraping simple de una URL de Reddit
```bash
thinkscraper scrape-url https://reddit.com/r/Python
```

### Caso 2: Scraping de múltiples URLs con reporte
```bash
thinkscraper scrape-urls urls.txt --output results.json
thinkscraper show-summary results.json
thinkscraper export-results results.json report.csv --format csv
```

### Caso 3: Scraping por plataforma
```bash
thinkscraper scrape-platform stackoverflow \
  https://stackoverflow.com/q/1 \
  https://stackoverflow.com/q/2 \
  https://stackoverflow.com/q/3 \
  --output so_results.json
```

### Caso 4: Workflow completo
```bash
cat > urls.txt << EOF
https://reddit.com/r/python
https://stackoverflow.com/q/123
https://medium.com/@user/story
EOF

thinkscraper scrape-urls urls.txt --output results.json
thinkscraper show-summary results.json
thinkscraper export-results results.json export.csv --format csv
```

---

## Solución de Problemas

### Error: "command not found: thinkscraper"
**Solución:** Ejecuta:
```bash
uv pip install -e .
```

### Error: "No scraper supports URL"
**Solución:** Verifica que la URL sea de una plataforma soportada. Usa `list-platforms` para ver las disponibles.

### Una URL falla y se detiene todo
**Solución:** Usa la opción `--skip-errors`:
```bash
thinkscraper scrape-urls urls.txt --output resultados.json --skip-errors
```