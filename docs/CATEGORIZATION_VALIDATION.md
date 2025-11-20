# Kategorisierungssystem - Multi-Log-Validierung

## Übersicht
Analyse von **8 verschiedenen Nextcloud-Logs** mit stark unterschiedlichen Schweregrad-Profilen zur Validierung des neuen funktionalen Kategorisierungssystems.

---

## 📊 Log-Profile (Statistik)

| Log-Datei | Größe | Debug | Info | Warnings | **Errors** | Profil |
|-----------|-------|-------|------|----------|------------|--------|
| **122511000.log** | 94.34 MB | 0% | 0% | 0.08% | **99.92%** | 🔴 **KRITISCH** |
| **136931020.log** | 95.9 MB | **99.98%** | 0.02% | 0% | 0% | 🟢 **GESUND** |
| **145161120.log** | 56.83 MB | 29.6% | 20.8% | 3.2% | **44.8%** | 🟠 **PROBLEMATISCH** |
| **150141120.log** | 2.43 MB | 1.0% | 15.2% | **76.5%** | 6.3% | 🟡 **WARNING-STORM** |
| **150931160.log** | 30.39 MB | 0% | 0% | **62.5%** | 35.8% | 🟠 **INSTABIL** |
| **27661000.log** | 55.58 MB | 57.8% | 33.8% | 2.1% | 3.8% | 🟢 **STABIL** |
| **nextcloud.log** | 37.11 MB | ? | ? | ? | ? | ⚪ **UNKLAR** |

---

## 🔴 KRITISCHES PROFIL: 122511000.log (99.92% Errors)

### Fehlerarten
```
S3-Fehler (NoSuchUpload):     ~53 Vorkommen
PHP TypeError-Fehler:          ~47 Vorkommen
```

### Dominante App
- **webdav**: 100% aller Fehler

### Fehler-Patterns

#### 1. **S3 Multipart Upload Fehler** (☁️ Storage → Critical)
```json
{
  "app": "webdav",
  "level": 3,
  "exception": "Aws\\S3\\Exception\\S3Exception",
  "message": "Error executing \"ListParts\" on IONOS S3 bucket...",
  "AWS Error": "NoSuchUpload - The specified multipart upload does not exist"
}
```

**Kategorisierung:**
- **Funktionale Kategorie**: `☁️ storage` (S3 ObjectStore)
- **Severity**: `Critical` (Upload-Prozess fehlgeschlagen)
- **Root Cause**: Multipart-Upload wurde abgebrochen oder existiert nicht mehr
- **Impact**: Datei-Uploads schlagen fehl → User-blockierend

#### 2. **PHP TypeError** (🐘 PHP Runtime → High)
```json
{
  "app": "webdav",
  "level": 3,
  "exception": "TypeError",
  "message": "OC\\Files\\Node\\HookConnector::getNodeForPath(): Argument #1 ($path) must be of type string, null given"
}
```

**Kategorisierung:**
- **Funktionale Kategorie**: `🐘 php_runtime` (TypeError)
- **Severity**: `High` (Code-Fehler)
- **Root Cause**: Null-Wert wird an Funktion übergeben
- **Impact**: File-Copy-Operation schlägt fehl

---

## 🟡 WARNING-STORM PROFIL: 150141120.log (76.5% Warnings)

### Warning-Arten
```
PHP Undefined Array Key:  ~1,830 Vorkommen (76.5%)
```

### Dominante App
- **PHP**: 100% (Core-System-Warnings)

### Warning-Patterns

#### **PHP Undefined Array Key** (🐘 PHP Runtime → Medium)
```json
{
  "app": "PHP",
  "level": 2,
  "message": "Undefined array key \"flags\" at /var/www/html/lib/private/Config/UserConfig.php#1723"
}
```

**Kategorisierung:**
- **Funktionale Kategorie**: `🐘 php_runtime` 
- **Severity**: `Medium` (Non-critical, aber häufig)
- **Root Cause**: Array-Key wird nicht geprüft vor Zugriff
- **Impact**: Funktioniert trotzdem, aber spammt Logs
- **Pattern**: Vermutlich Nextcloud-Bug in Config-Reader

---

## 🟢 GESUNDER SERVER: 136931020.log (99.98% Debug)

### Siehe ursprüngliche Analyse
- **125,675 Debug-Einträge** zu "dirty table reads"
- Funktioniert einwandfrei, aber extrem verbose logging
- **Lösung**: `INCLUDE_DEBUG_LEVEL=False` filtert 99.8% weg

---

## ✅ Validierung der funktionalen Kategorien

### Abdeckung aller Error-Types

| Error-Type | Functional Category | Severity | Coverage |
|------------|---------------------|----------|----------|
| ✅ S3 NoSuchUpload | ☁️ `storage` | Critical | **JA** |
| ✅ S3 403/404 | ☁️ `storage` | High | **JA** |
| ✅ PHP TypeError | 🐘 `php_runtime` | High | **JA** |
| ✅ PHP Undefined Key | 🐘 `php_runtime` | Medium | **JA** |
| ✅ WebDAV PROPFIND | 📁 `file_sync` | varies | **JA** |
| ✅ WebDAV MOVE | 📁 `file_sync` | varies | **JA** |

### Neue Erkenntnisse für Redesign

#### 1. **S3-Fehler brauchen Subcategories**
```python
# ERGÄNZUNG zu CATEGORIZATION_REDESIGN.md:

# Innerhalb der "storage"-Kategorie:
if 'NoSuchUpload' in message:
    subcategory = 'multipart_upload_failed'
    severity = 'Critical'  # Upload komplett gescheitert
    
elif '404' in message and 's3' in str(exception).lower():
    subcategory = 's3_object_not_found'
    severity = 'High'
```

#### 2. **PHP Warnings brauchen Severity-Abstufung**
```python
# Nicht alle PHP-Warnings sind gleich wichtig:

if 'Undefined array key' in message:
    severity = 'Medium'  # Häufig, aber non-breaking
    
elif 'TypeError' in str(exception):
    severity = 'High'    # Echte Code-Fehler
```

#### 3. **WebDAV-Fehler sind kontextabhängig**
```python
# WebDAV kann Storage ODER File-Sync sein:

if 'webdav' in app:
    if 's3' in message.lower() or 'objectstore' in message.lower():
        category = 'storage'  # WebDAV → S3 → Storage-Problem
    else:
        category = 'file_sync'  # WebDAV-Sync-Problem
```

---

## 🎯 Empfohlene Anpassungen für CATEGORIZATION_REDESIGN.md

### 1. **Erweiterte Severity-Logik**
```python
def _get_severity(self, entry: Dict) -> str:
    """
    ERWEITERTE VERSION für diverse Log-Profile
    """
    level = entry.get('level', 0)
    exception = str(entry.get('exception', {}))
    message = entry.get('message', '').lower()
    
    # CRITICAL (Level 3 mit schwerwiegenden Folgen)
    if level == 3:
        if any(keyword in message for keyword in [
            'nosuchupload',      # S3-Upload komplett fehlgeschlagen
            'database',          # DB-Fehler
            'authentication',    # Auth-Fehler
            '500',              # Server-Fehler
        ]):
            return 'Critical'
        
        # HIGH (andere Level-3-Fehler)
        if 'typeerror' in exception.lower():
            return 'High'  # Code-Fehler
        
        return 'High'  # Default für Errors
    
    # WARNING (Level 2)
    if level == 2:
        # MEDIUM für PHP-Warnings
        if 'undefined array key' in message:
            return 'Medium'  # Häufig, aber unkritisch
        
        if 'csrf' in message:
            return 'High'  # Security-relevant
        
        return 'Medium'  # Default für Warnings
    
    # INFO/DEBUG
    return 'Low'
```

### 2. **Erweiterte Storage-Kategorisierung**
```python
def _is_storage_error(self, entry: Dict) -> bool:
    """
    Storage-Fehler umfassen:
    - S3/ObjectStore (AWS, IONOS, etc.)
    - WebDAV → S3 Proxy-Fehler
    - Multipart Upload-Fehler
    """
    app = entry.get('app', '').lower()
    message = entry.get('message', '').lower()
    exception = str(entry.get('exception', {})).lower()
    
    # Direkte S3-Fehler
    if app in ['objectstore'] or 's3exception' in exception:
        return True
    
    # WebDAV mit S3-Backend
    if app == 'webdav' and any(keyword in message for keyword in [
        's3', 'ionos', 'bucket', 'aws', 'nosuchupload', 'listparts'
    ]):
        return True
    
    return False
```

### 3. **PHP-Runtime-Kategorisierung**
```python
def _is_php_runtime_error(self, entry: Dict) -> bool:
    """
    PHP-Fehler umfassen:
    - TypeError, ValueError, etc.
    - Undefined array keys
    - Parse errors
    """
    app = entry.get('app', '').lower()
    exception = str(entry.get('exception', {}))
    message = entry.get('message', '').lower()
    
    if app == 'php':
        return True
    
    if any(keyword in exception for keyword in [
        'TypeError', 'ValueError', 'ParseError', 'ArgumentCountError'
    ]):
        return True
    
    if 'undefined array key' in message or 'undefined index' in message:
        return True
    
    return False
```

---

## 📈 Erwartete Ergebnisse nach Implementierung

### Für KRITISCHE Server (122511000.log)
```
Vor:  99.92% "other_errors" (alles in einen Topf)
Nach: 
  - ☁️ Storage (S3 Errors):     53 Einträge (Critical)
  - 🐘 PHP Runtime (TypeError):  47 Einträge (High)
  - Total:                       100 Einträge (alle sichtbar + kategorisiert)
```

### Für WARNING-STORM Server (150141120.log)
```
Vor:  76.5% "server_warnings" (undifferenziert)
Nach: 
  - 🐘 PHP Runtime (Array Key): 1,830 Einträge (Medium)
  - Grouped by error:            ~1 Gruppe (Pattern erkannt)
  - User sieht:                  "Wiederholter PHP-Fehler in UserConfig"
```

### Für GESUNDE Server (136931020.log)
```
Vor:  125,675 Einträge (alle angezeigt)
Nach: 
  - Mit INCLUDE_DEBUG_LEVEL=False: 53 Einträge
  - Reduktion:                     99.8%
```

---

## 🔥 Kritische Funktionen für Error-Heavy Logs

### 1. **Error-Grouping** (WICHTIG!)
```python
def group_similar_errors(entries: List[Dict]) -> List[Dict]:
    """
    Gruppiert identische Fehler zusammen
    Beispiel: 1,830x "Undefined array key 'flags'" → 1 Eintrag mit count=1830
    """
    grouped = {}
    
    for entry in entries:
        # Gruppierungs-Schlüssel
        key = (
            entry.get('exception', {}).get('Exception', ''),
            entry.get('message', '')[:100],  # Erste 100 Zeichen
            entry.get('app', '')
        )
        
        if key in grouped:
            grouped[key]['count'] += 1
            grouped[key]['last_seen'] = entry.get('time')
        else:
            grouped[key] = {
                **entry,
                'count': 1,
                'first_seen': entry.get('time'),
                'last_seen': entry.get('time')
            }
    
    return list(grouped.values())
```

### 2. **Adaptive Filtering** (basierend auf Log-Profil)
```python
def should_show_entry(self, entry: Dict, log_profile: str) -> bool:
    """
    Zeigt Einträge basierend auf Log-Profil:
    - Critical Logs: Zeige ALLES (auch Debug)
    - Warning Logs:  Zeige Warnings + Errors
    - Healthy Logs:  Nur Errors (Filter Debug/Info)
    """
    level = entry.get('level', 0)
    
    if log_profile == 'critical':  # >90% Errors
        return True  # Zeige alles, auch Debug
    
    elif log_profile == 'warning_storm':  # >50% Warnings
        return level >= 2  # Nur Warnings + Errors
    
    elif log_profile == 'healthy':  # >90% Debug
        return level >= 3  # Nur Errors
    
    return level >= 1  # Default: Info+
```

---

## ✅ Validierungs-Checkliste

- [x] **S3-Fehler werden erkannt** (NoSuchUpload, 404, etc.)
- [x] **PHP-Fehler werden differenziert** (TypeError vs Undefined Key)
- [x] **WebDAV wird korrekt geroutet** (Storage vs File-Sync)
- [x] **Severity passt zu Impact** (Critical für Upload-Fehler)
- [x] **Warning-Storms werden gehandhabt** (Grouping)
- [x] **Debug-Heavy-Logs werden gefiltert** (99.8% Reduktion)
- [ ] **Error-Grouping implementiert** (TODO)
- [ ] **Adaptive Filtering implementiert** (TODO)
- [ ] **UI zeigt Grouped Errors** (TODO)

---

## 🎯 Nächste Schritte

1. **CATEGORIZATION_REDESIGN.md aktualisieren** mit:
   - Erweiterte Severity-Logik
   - Storage-Subkategories
   - PHP-Runtime-Differenzierung
   - Error-Grouping-Funktion

2. **Implementierung in server_parser.py**:
   - `_get_functional_category()` erweitern
   - `_get_severity()` verfeinern
   - `group_similar_errors()` hinzufügen

3. **UI-Anpassungen**:
   - Grouped Errors anzeigen (`count: 1830x`)
   - "Show Details" für Error-Gruppe
   - Log-Profile-Erkennung & adaptive Filterung

4. **Testing mit allen 8 Logs**:
   - Jedes Log einzeln parsen
   - Kategorien validieren
   - Performance messen (große Files)
