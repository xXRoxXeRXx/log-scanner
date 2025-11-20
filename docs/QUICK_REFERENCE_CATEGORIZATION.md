# 🎯 Categorization Quick Reference

**Status:** ✅ Validiert mit 8 Log-Profilen (Debug-Heavy, Error-Heavy, Warning-Heavy)

---

## 📋 9 Funktionale Kategorien

| Icon | Name | Beschreibung | Severity | Beispiele |
|------|------|--------------|----------|-----------|
| 🔐 | **Authentication & Access** | Login, Sessions, Tokens | High | NotLoggedInException, 401 |
| 📁 | **File Synchronization** | WebDAV, Sync-Konflikte | High | Sabre\DAV, PROPFIND |
| ☁️ | **Storage & Object Store** | S3, Backend-Fehler | **Critical** | NoSuchUpload, 503 |
| 🗄️ | **Database** | Performance, SQL | Medium | dirty table reads |
| 🔒 | **Security & CSRF** | Sicherheit, Cookies | High | CSRF validation |
| 📱 | **Apps & Extensions** | App-spezifisch | Medium | Deck, Text, Calendar |
| ⚙️ | **Background Jobs** | Cron, Tasks | Low | Starting job |
| 🐘 | **PHP Runtime** | PHP-Fehler | High | TypeError, Fatal |
| ⚡ | **System & Core** | System-Meldungen | Low | Activity, Core |

---

## 🔍 Erkennungslogik (Priorität)

```python
# 1. Authentication
if '401' or 'NotLoggedInException' → authentication

# 2. Storage (WICHTIG: WebDAV → S3 Routing!)
if 's3exception' or 'NoSuchUpload' → storage
if webdav + ('s3' or 'bucket') → storage  # WebDAV mit S3-Backend!

# 3. File Sync
if 'webdav' or 'Sabre\\DAV' → file_sync

# 4. Database
if 'dirty table reads' or 'sql' → database

# 5. Security
if 'csrf' or 'xss' → security

# 6. PHP Runtime
if 'TypeError' or 'undefined array key' → php_runtime

# 7. Background Jobs
if 'cron' → background_jobs

# 8. Apps
if app in ['deck', 'text', ...] → apps

# 9. Default
→ system
```

---

## 📊 Severity-Mapping

```python
Level 3 (Error) →
  - 'NoSuchUpload', '503' → CRITICAL 🔴
  - 'TypeError' → HIGH 🔴
  - Other → HIGH 🔴

Level 2 (Warning) →
  - 'undefined array key' → MEDIUM 🟡
  - 'csrf', 'xss' → HIGH 🔴
  - Other → MEDIUM 🟡

Level 1 (Info) → LOW 🔵
Level 0 (Debug) → LOW 🔵
```

---

## 🔄 Error-Grouping (für Error-Heavy Logs)

**Wann aktivieren:**
- Log hat >50% Errors oder Warnings
- Viele identische Fehler (z.B. 53× S3 NoSuchUpload)

**Wie:**
```python
GROUP_REPEATED_ERRORS = True  # In config

# Im Code:
entries = group_similar_errors(entries)
# 53 einzelne S3-Fehler → [53×] S3 NoSuchUpload
```

---

## 📈 Erwartete Resultate nach Log-Typ

### 🟢 Debug-Heavy Log (99% Debug)
```
Vorher: 125,675 Einträge
Nachher: 1,251 Einträge (99.0% Reduktion)
Filter: INCLUDE_DEBUG_LEVEL=False
```

### 🔴 Error-Heavy Log (99% Errors)
```
Vorher: 100 Einträge (53 S3, 47 TypeError)
Nachher: 2 Einträge
  - [53×] ☁️ Storage: S3 NoSuchUpload (Critical)
  - [47×] 🐘 PHP Runtime: TypeError (High)
Grouping: Aktiviert
```

### 🟡 Warning-Heavy Log (76% Warnings)
```
Vorher: 1,830 Einträge (alle "Undefined array key")
Nachher: 1 Eintrag
  - [1,830×] 🐘 PHP Runtime: Undefined array key (Medium)
Grouping: Aktiviert
```

---

## 🚀 Implementierungs-Checkliste

### Backend (server_parser.py)
- [ ] `_get_functional_category()` implementieren
- [ ] `_get_severity()` mit erweiterten Checks
- [ ] `group_similar_errors()` für Error-Grouping
- [ ] WebDAV → S3 Routing hinzufügen
- [ ] Tests mit allen 8 Log-Profilen

### Config
- [ ] `FUNCTIONAL_CATEGORIES` dict
- [ ] `GROUP_REPEATED_ERRORS` option
- [ ] `INCLUDE_DEBUG_LEVEL` option

### Frontend (results.html)
- [ ] Category Cards mit Icons
- [ ] Severity Badges (🔴 Critical, 🔴 High, 🟡 Medium, 🔵 Low)
- [ ] Grouped Error Display mit [count×]
- [ ] "Show all occurrences" Button

### Testing
- [ ] 🟢 Debug-Heavy: 136931020.log (99.98% Debug)
- [ ] 🔴 Error-Heavy: 122511000.log (99.92% Errors)
- [ ] 🟡 Warning-Heavy: 150141120.log (76.5% Warnings)
- [ ] 🟠 Mixed: 145161120.log (44.8% Errors)

---

## 🔗 Siehe auch

- **`CATEGORIZATION_REDESIGN.md`** - Vollständige Design-Spezifikation
- **`MULTI_LOG_FINDINGS.md`** - Executive Summary der Multi-Log-Analyse
- **`CATEGORIZATION_VALIDATION.md`** - Detaillierte Validierung mit allen 8 Logs
