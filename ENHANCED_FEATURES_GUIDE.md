# 📊 Enhanced Analysis Features (v1.1.0)

## 🎯 Overview

Die Enhanced Analysis Features erweitern den Nextcloud Log Analyzer um leistungsstarke Filter-, Visualisierungs- und Analysefunktionen.

---

## ✨ Neue Features

### 1. 🎛️ **Multi-Category Filter**

**Mehrere Kategorien gleichzeitig filtern**

- ✅ Checkbox-Grid mit allen Kategorien
- ✅ Mehrfachauswahl möglich
- ✅ Live-Update beim An/Abwählen
- ✅ Visuelles Feedback (blaue Border)
- ✅ Counter zeigt Anzahl pro Kategorie

**Verwendung:**
1. Scrolle zur "Multi-Category Filter" Section
2. Wähle gewünschte Kategorien via Checkboxen
3. Filter wird automatisch angewendet

---

### 2. ⚡ **Quick Filters**

**Vordefinierte Filter für schnellen Zugriff**

- 🔴 **Nur Errors** - Zeigt nur Error-Einträge
- 🟡 **Nur Warnings** - Zeigt nur Warnings
- ⏰ **Letzte Stunde** - Fehler der letzten 60 Minuten
- 📅 **Letzte 24h** - Fehler des letzten Tages
- 💥 **Kritisch** - Nur kritische Kategorien (Storage, Database, Security)
- 👥 **Mit User-Info** - Nur Einträge mit User-Informationen

**Design:**
- Purple/Blue Gradient Background
- One-Click-Anwendung
- Kombinierbar mit anderen Filtern

---

### 3. 🔍 **Regex-Suche**

**Erweiterte Suchfunktion mit Regular Expressions**

**Features:**
- Toggle-Switch zwischen Normal- und Regex-Modus
- Orange Border im Regex-Modus
- Monospace-Font für Regex
- Error-Handling (Fallback auf normale Suche)
- Beispiele unterhalb des Suchfelds

**Beispiele:**
```regex
error.*redis          # Findet "error" gefolgt von "redis"
(404|403|500)         # Findet HTTP-Statuscodes
user\d+               # Findet user1, user2, etc.
(TypeError|ValueError) # Findet PHP-Fehlertypen
```

---

### 4. ⏱️ **Timeline Chart**

**Fehler-Verteilung über Zeit visualisieren**

**Features:**
- Line Chart mit Fehlern pro Stunde
- Automatisches Gruppieren nach Stunden
- Gradient Fill in IONOS-Farben
- Interaktiv: Click auf Datenpunkt filtert nach diesem Zeitraum
- Hover zeigt Details
- Smooth Scrolling zur Entry-Table

**Technisch:**
- Chart.js Line Chart
- Zeitachse gruppiert nach Stunden
- Click-Handler für Filter-Integration

---

### 5. 🔥 **Heatmap-Visualisierung**

**Fehler-Muster erkennen: Stunden × Wochentage**

**Features:**
- 7×24 Matrix (Wochentage × Stunden)
- Farbcodierung nach Fehleranzahl
- Gradient: Grau (keine) → Blau (wenig) → Gelb (mittel) → Rot (viel)
- Grouped Bar Chart
- Tooltip zeigt Tag, Uhrzeit und Anzahl

**Use Cases:**
- Erkennen von Zeit-Mustern
- Peak-Hours identifizieren
- Wochenend-Probleme vs. Werktags
- Cron-Job-Probleme erkennen

---

### 6. 🗂️ **Filter Breadcrumb Navigation**

**Visuelles Dashboard der aktiven Filter**

**Features:**
- Purple Gradient Design
- Zeigt alle aktiven Filter als Badges
- One-Click-Removal: X auf Badge klicken
- "Alle löschen" Button
- Kategorien zeigen Anzahl
- Kombiniert mit Regex/Quick Filter Status

**Filter-Badges:**
- ⚡ Quick Filter
- 📂 Categories (mit Anzahl)
- 📅 Datum-Range
- 👤 Username
- 🔍 Suche (mit Regex-Indicator)

---

### 7. 📸 **Chart Export (PNG)**

**Charts als Bilder exportieren**

**Features:**
- Exportiert alle 3 Charts als PNG
- Automatische Dateinamen: `chart_{name}_{analysisId}.png`
- Canvas.toDataURL() für PNG-Generation
- Downloads:
  - `chart_categories_{id}.png`
  - `chart_timeline_{id}.png`
  - `chart_heatmap_{id}.png`

**Verwendung:**
1. Klick auf "📸 Charts Export" Button
2. 3 PNG-Dateien werden heruntergeladen
3. Verwendbar für Reports/Dokumentation

---

### 8. 📊 **CSV Export**

**Analyseergebnisse als CSV exportieren**

**Features:**
- Alle Log-Einträge als CSV
- Spalten: Timestamp, Level, Category, Message, User, Error Code
- CSV-Escaping für Kommas/Quotes
- Automatischer Filename: `nextcloud-analysis_{id}.csv`

**Use Cases:**
- Excel-Analyse
- Datenbank-Import
- Weitere Verarbeitung
- Archivierung

---

## 🎯 App-spezifische Root Causes

**Automatische Erkennung problematischer Apps**

**Detection:**
- Gruppierung nach `app_name`
- Schwellwerte: Mindestens 5% der App-Fehler
- Top 5 problematische Apps werden angezeigt
- TypeError/Exception-Erkennung

**Informationen pro App:**
- Fehleranzahl
- Prozentsatz
- Severity (Critical/High/Medium/Low)
- Spezifische Error-Patterns
- Lösungsvorschläge

**Erkannte Apps:**
- Nextcloud Office/Collabora
- Nextcloud Talk
- Calendar/Contacts
- External Storage
- Text/Markdown
- Alle installierten Apps

---

## 🛠️ Background Jobs & Performance

**Erkennung von Cron/Performance-Problemen**

**Erkannte Probleme:**
- **Memory Exhaustion** - PHP memory_limit erreicht
- **Timeouts** - max_execution_time überschritten
- **Disk Full** - Speicherplatz voll
- **Permissions** - Dateisystem-Berechtigungen
- **Slow Queries** - Datenbank-Performance

**Lösungsvorschläge:**
- Memory-Limit erhöhen
- Execution-Time anpassen
- Speicher bereinigen
- Berechtigungen korrigieren
- Query-Optimierung

---

## 🚀 Performance

**Optimierungen:**
- Lazy Chart Rendering (100ms Delay)
- Efficient Data Structures (Sets für User-Tracking)
- Regex-Fallback bei Invalid Patterns
- Canvas-based Chart Export
- Client-side Filtering

**Bundle Size:**
- HTML: ~90 KB
- No external dependencies (Alpine.js + Chart.js from CDN)
- Fast initial load

---

## 📱 Browser-Kompatibilität

**Getestet:**
- ✅ Chrome 120+
- ✅ Firefox 120+
- ✅ Safari 17+
- ✅ Edge 120+

**Voraussetzungen:**
- JavaScript enabled
- Canvas-Support
- ES6-Support

---

## 🔜 Roadmap

**Geplante Features:**
- [ ] PDF-Report Generation
- [ ] Email-Benachrichtigungen
- [ ] Saved Filters
- [ ] Comparison Mode (2 Analysen vergleichen)
- [ ] AI-basierte Anomalie-Erkennung
- [ ] Multi-Language Support
- [ ] Prometheus Metrics Export

---

## 📚 Weitere Dokumentation

- [SECURITY.md](SECURITY.md) - Security Features
- [ROOT_CAUSE_ANALYSIS.md](ROOT_CAUSE_ANALYSIS.md) - Root Cause Patterns
- [README-DESKTOP.md](README-DESKTOP.md) - Desktop Version
- [docs/DOCKER.md](docs/DOCKER.md) - Docker Deployment

---

## 🤝 Contribution

Contributions sind willkommen! Bitte erstelle einen Pull Request mit:
- Feature-Branch von `desktop`
- Tests für neue Features
- Dokumentation
- Screenshots

---

## 📄 License

MIT License - siehe [LICENSE](LICENSE)
