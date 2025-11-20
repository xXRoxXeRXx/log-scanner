# Root Cause Detection - Analyse & Verbesserungen

## 📊 Aktueller Stand (v1.0)

### ✅ Bereits implementierte Root Causes

#### **Client Log Patterns (Nextcloud Desktop Client)**
1. **FileIgnored (Symbolic Links)** - Symbolische Links nicht synchronisierbar
2. **HTTP 404** - Dateien auf Server nicht gefunden
3. **HTTP 403** - Zugriff verweigert
4. **Network/Connection** - Netzwerkprobleme, Timeouts
5. **InvalidFilename** - Ungültige Dateinamen (Sonderzeichen)
6. **SyncError** - Allgemeine Synchronisationsfehler

#### **Server Log Patterns (Nextcloud Server - Functional Categories)**
7. **Storage Problems (S3/ObjectStore)** - S3-Fehler, NoSuchUpload, 503 Errors
8. **File Sync (WebDAV)** - TypeErrors im HookConnector
9. **PHP Runtime** - Undefined Array Key, TypeErrors
10. **Database** - Connection Failures
11. **Authentication** - CSRF-Token-Fehler, Session-Probleme
12. **Security** - Attacks, Rate-Limits, Blocked IPs

#### **Generic Cross-Category Patterns**
13. **Storage Unavailable** - StorageNotAvailableException (CRITICAL)
14. **File Locking** - Lock/Unlock-Probleme
15. **Redis Connection** - RedisException, Read Errors
16. **WorkflowEngine Boot Failures** - Redis-bedingt
17. **WebDAV Redis Failures** - Sabre ServiceUnavailable

---

## 🎯 Verbesserungsvorschläge

### **1. Neue Pattern-Erkennung hinzufügen**

#### A) **App-spezifische Probleme**
- **Nextcloud Office/Collabora**: WOPI-Fehler, Document Server Timeouts
- **Nextcloud Talk**: Signaling-Server-Probleme, TURN/STUN-Fehler
- **Calendar/Contacts**: CalDAV/CardDAV-Synchronisationsfehler
- **External Storage**: Mount-Fehler, Credentials-Probleme
- **Text/Markdown**: File conflicts, Version-Probleme

**Implementierung:**
```javascript
// Apps category pattern (basierend auf app_name)
const appsCount = this.result.categories?.apps || 0;
const appsErrors = this.result.entries?.filter(e => e.category === 'apps');

// Group by app_name
const appErrorCounts = {};
appsErrors.forEach(e => {
    const app = e.app || 'unknown';
    appErrorCounts[app] = (appErrorCounts[app] || 0) + 1;
});

// Find apps with >50 errors
Object.entries(appErrorCounts).forEach(([app, count]) => {
    if (count > 50) {
        issues.push({
            type: `app_${app}`,
            severity: count > 200 ? 'high' : 'medium',
            icon: '📱',
            title: `App-Problem: ${app}`,
            description: `${count} Fehler in der App "${app}".`,
            count: count,
            percentage: ((count / totalErrors) * 100).toFixed(1),
            suggestion: `Prüfen Sie die App "${app}": 1) Update verfügbar? 2) Kompatibel mit Nextcloud-Version? 3) App-Logs checken, 4) Ggf. deaktivieren/neu installieren.`,
            filterCriteria: { category: 'apps', app: app }
        });
    }
});
```

#### B) **Background Jobs / Cron-Probleme**
- **Job-Failures**: Lange Laufzeiten, Timeouts
- **Memory Exhaustion**: PHP Memory Limit erreicht
- **Cron nicht konfiguriert**: System Cron vs Webcron

**Implementierung:**
```javascript
const bgJobsCount = this.result.categories?.background_jobs || 0;
if (bgJobsCount > 20) {
    const memoryErrors = this.result.entries?.filter(e => 
        e.category === 'background_jobs' && 
        (e.message?.includes('memory') || e.message?.includes('Memory'))
    ).length || 0;
    
    const timeoutErrors = this.result.entries?.filter(e => 
        e.category === 'background_jobs' && 
        (e.message?.includes('timeout') || e.message?.includes('maximum execution'))
    ).length || 0;
    
    let description = `${bgJobsCount} Fehler bei Background-Jobs.`;
    let suggestion = 'Prüfen Sie Cron-Konfiguration.';
    
    if (memoryErrors > 10) {
        description += ` ${memoryErrors}x Memory-Probleme!`;
        suggestion = 'PHP memory_limit erhöhen (config.php oder php.ini). Empfohlen: 512M oder höher für große Instanzen.';
    } else if (timeoutErrors > 10) {
        description += ` ${timeoutErrors}x Timeouts!`;
        suggestion = 'max_execution_time erhöhen oder Jobs in kleinere Tasks aufteilen.';
    }
    
    issues.push({
        type: 'background_jobs',
        severity: memoryErrors > 50 ? 'high' : 'medium',
        icon: '⚙️',
        title: 'Background-Job-Probleme',
        description: description,
        count: bgJobsCount,
        percentage: ((bgJobsCount / totalErrors) * 100).toFixed(1),
        suggestion: suggestion,
        filterCriteria: { category: 'background_jobs' }
    });
}
```

#### C) **System-Level Issues**
- **Disk Full**: Speicher voll, Upload-Fehler
- **Permission Denied**: Filesystem-Berechtigungen
- **SSL/TLS**: Certificate-Probleme
- **PHP Version**: Deprecated-Warnings

**Implementierung:**
```javascript
const systemCount = this.result.categories?.system || 0;
if (systemCount > 10) {
    // Disk space errors
    const diskErrors = this.result.entries?.filter(e => 
        e.category === 'system' && 
        (e.message?.toLowerCase().includes('disk') || 
         e.message?.toLowerCase().includes('no space') ||
         e.message?.toLowerCase().includes('quota'))
    ).length || 0;
    
    // Permission errors
    const permErrors = this.result.entries?.filter(e => 
        e.category === 'system' && 
        e.message?.toLowerCase().includes('permission denied')
    ).length || 0;
    
    if (diskErrors > 5) {
        issues.push({
            type: 'disk_full',
            severity: 'critical',
            icon: '💾',
            title: 'Speicherplatz-Problem',
            description: `${diskErrors} Fehler durch vollen Speicher oder Quota-Überschreitung.`,
            count: diskErrors,
            percentage: ((diskErrors / totalErrors) * 100).toFixed(1),
            suggestion: 'KRITISCH: Speicher voll! 1) Alte Dateien löschen, 2) Trash leeren, 3) Versions bereinigen, 4) Speicher erweitern.',
            filterCriteria: { search: 'disk' }
        });
    }
    
    if (permErrors > 10) {
        issues.push({
            type: 'permissions',
            severity: 'high',
            icon: '🔐',
            title: 'Dateisystem-Berechtigungen',
            description: `${permErrors} Permission-Denied-Fehler. Nextcloud kann nicht auf Dateien zugreifen.`,
            count: permErrors,
            percentage: ((permErrors / totalErrors) * 100).toFixed(1),
            suggestion: 'Berechtigungen korrigieren: chown -R www-data:www-data /var/www/nextcloud/data',
            filterCriteria: { search: 'permission denied' }
        });
    }
}
```

---

### **2. Pattern-Priorisierung & Grouping**

#### Problem: Zu viele kleine Issues
**Aktuell:** Jedes Pattern mit >10/20 Einträgen wird erkannt → viele irrelevante Issues

**Lösung: Dynamische Schwellwerte**
```javascript
// Calculate dynamic thresholds based on log size
const totalEntries = this.result.entries.length;
const minThreshold = Math.max(10, totalEntries * 0.01); // Min 1% oder 10 Entries
const criticalThreshold = totalEntries * 0.05; // 5% = Critical
const highThreshold = totalEntries * 0.02; // 2% = High

// Example: Only show issues above threshold
if (phpCount > minThreshold) {
    const percentage = ((phpCount / totalEntries) * 100).toFixed(1);
    const severity = phpCount > criticalThreshold ? 'critical' : 
                     phpCount > highThreshold ? 'high' : 'medium';
    // ... rest of code
}
```

#### Problem: Redundante Root Causes
**Beispiel:** Redis Connection + WorkflowEngine Boot + WebDAV Redis = alle durch Redis verursacht

**Lösung: Hierarchische Root Cause**
```javascript
// Step 1: Detect root issue (Redis)
const redisErrors = [...]; // total redis errors
if (redisErrors > threshold) {
    issues.push({
        type: 'redis_root',
        severity: 'critical',
        icon: '🔴',
        title: 'Redis-Infrastruktur-Problem (ROOT CAUSE)',
        description: `${redisErrors} Redis-Fehler erkannt.`,
        affected_services: ['WorkflowEngine', 'WebDAV', 'Locking', 'Sessions'],
        // ...
    });
}

// Step 2: Only show child issues if root not present
if (!issues.find(i => i.type === 'redis_root')) {
    // Show specific WorkflowEngine, WebDAV issues
}
```

---

### **3. Zeitbasierte Pattern-Erkennung**

#### Erkennung von Ereignis-Clustern
**Use Case:** Plötzlicher Anstieg von Fehlern in kurzer Zeit

**Implementierung:**
```javascript
// Group errors by time windows (10min intervals)
const timeWindows = {};
this.result.entries.forEach(entry => {
    if (!entry.timestamp) return;
    
    const date = new Date(entry.timestamp);
    const windowKey = Math.floor(date.getTime() / (10 * 60 * 1000)); // 10min windows
    
    if (!timeWindows[windowKey]) {
        timeWindows[windowKey] = { count: 0, timestamp: date };
    }
    timeWindows[windowKey].count++;
});

// Find spikes (>3x average)
const avgPerWindow = totalEntries / Object.keys(timeWindows).length;
const spikes = Object.entries(timeWindows).filter(([key, data]) => 
    data.count > avgPerWindow * 3
);

if (spikes.length > 0) {
    const biggestSpike = spikes.sort((a, b) => b[1].count - a[1].count)[0];
    const spikeTime = biggestSpike[1].timestamp.toLocaleString('de-DE');
    
    issues.push({
        type: 'error_spike',
        severity: 'high',
        icon: '📈',
        title: 'Fehler-Spike erkannt',
        description: `Plötzlicher Anstieg von ${biggestSpike[1].count} Fehlern um ${spikeTime}.`,
        count: biggestSpike[1].count,
        percentage: ((biggestSpike[1].count / totalEntries) * 100).toFixed(1),
        suggestion: 'Prüfen Sie Server-Events zu diesem Zeitpunkt: Deployment, Restart, Traffic-Spike?',
        filterCriteria: { timestamp: spikeTime }
    });
}
```

---

### **4. User-Impact-Score**

#### Welche Issues betreffen die meisten User?
**Aktuell:** Nur Anzahl der Errors, nicht Anzahl betroffener User

**Lösung:**
```javascript
// Count unique users per issue type
const userImpact = {};

this.result.entries.forEach(entry => {
    const issueType = determineIssueType(entry); // helper function
    if (!userImpact[issueType]) {
        userImpact[issueType] = new Set();
    }
    if (entry.user) {
        userImpact[issueType].add(entry.user);
    }
});

// Add userImpact to issues
issues.forEach(issue => {
    const affectedUsers = userImpact[issue.type]?.size || 0;
    issue.affected_users = affectedUsers;
    issue.description += ` Betroffen: ${affectedUsers} User.`;
    
    // Increase severity if many users affected
    if (affectedUsers > 50 && issue.severity === 'medium') {
        issue.severity = 'high';
    }
});
```

---

### **5. Actionable Suggestions verbessern**

#### Aktuell: Generische Tipps
**Beispiel:** "Prüfen Sie die Datenbank-Verbindung"

#### Verbesserung: Konkrete Commands
```javascript
suggestion: `
<strong>Sofort-Maßnahmen:</strong>
1. Prüfen: <code>systemctl status mysql</code>
2. Connection Test: <code>mysql -u nextcloud -p</code>
3. Nextcloud Logs: <code>tail -f /var/www/nextcloud/data/nextcloud.log</code>
4. Max Connections: <code>SHOW VARIABLES LIKE 'max_connections';</code>

<strong>Langfristig:</strong>
- Max Connections erhöhen (my.cnf)
- Connection Pooling aktivieren
- Read-Replicas für Load-Balancing
`.trim()
```

---

### **6. Root Cause Confidence Score**

#### Problem: Falsche Positives
**Beispiel:** "Undefined array key" sind oft harmlos, werden aber als "high severity" erkannt

**Lösung: Confidence Score**
```javascript
issues.push({
    type: 'php_runtime',
    severity: 'medium',
    confidence: 0.6, // 60% sicher, dass es ein echtes Problem ist
    icon: '🐘',
    title: 'PHP Runtime-Fehler (niedrige Konfidenz)',
    description: `Viele "Undefined array key"-Warnungen - meist harmlos.`,
    // ...
});

// Sort by confidence * count
issues.sort((a, b) => {
    const scoreA = (a.confidence || 1.0) * a.count;
    const scoreB = (b.confidence || 1.0) * b.count;
    return scoreB - scoreA;
});
```

---

## 🏆 Priorität für nächste Implementation

### **MUST HAVE (Sofort)**
1. ✅ **App-spezifische Probleme** (häufig, leicht zu fixen)
2. ✅ **Background Jobs** (Performance-kritisch)
3. ✅ **Disk Full Detection** (kritisch für Betrieb)

### **SHOULD HAVE (Bald)**
4. **Dynamische Schwellwerte** (weniger Noise)
5. **User-Impact-Score** (bessere Priorisierung)
6. **Hierarchische Root Causes** (Redis → Child Issues)

### **NICE TO HAVE (Später)**
7. **Zeitbasierte Spikes** (advanced analytics)
8. **Confidence Scores** (ML-ähnlich)
9. **Actionable Commands** (Copy-Paste-Ready)

---

## 📦 Test-Logs benötigt

Für bessere Pattern-Erkennung brauchen wir:

1. **App-Error Log** - Collabora/Office-Fehler
2. **Cron-Job Log** - Background-Job-Probleme mit Memory/Timeout
3. **External Storage Log** - SMB/NFS-Mount-Fehler
4. **Disk Full Log** - Quota/Speicher-Probleme
5. **Permission Error Log** - Chown/Chmod-Probleme
6. **Multi-User Log** - Verschiedene User betroffen (für User-Impact)

---

## 🎨 UI-Verbesserungen

### A) Root Cause Severity Visual
```html
<!-- Add visual indicator for severity -->
<div class="root-cause-card">
    <div class="severity-badge" :class="'severity-' + issue.severity">
        {{ issue.severity.toUpperCase() }}
    </div>
    <!-- rest of card -->
</div>
```

### B) Expandable Details
```html
<!-- Collapsible suggestion section -->
<div class="root-cause-suggestion" x-data="{ expanded: false }">
    <div @click="expanded = !expanded" style="cursor: pointer;">
        <strong>💡 Lösung</strong> <span x-text="expanded ? '▼' : '▶'"></span>
    </div>
    <div x-show="expanded" x-transition>
        <p x-text="issue.suggestion"></p>
        <pre x-show="issue.commands" x-text="issue.commands"></pre>
    </div>
</div>
```

### C) "Fix Applied" Tracking
```html
<!-- Checkbox to mark issues as resolved -->
<div class="root-cause-actions">
    <label>
        <input type="checkbox" @change="markAsFixed(issue.type)">
        Als behoben markieren
    </label>
</div>
```

---

## 📊 Analytics / Metrics

### Track Root Cause Trends über Zeit
```javascript
// Save to localStorage for historical comparison
const analysisHistory = {
    timestamp: new Date().toISOString(),
    total_entries: this.result.total_entries,
    issues: issues.map(i => ({ type: i.type, count: i.count, severity: i.severity }))
};

localStorage.setItem(`analysis_${this.analysisId}`, JSON.stringify(analysisHistory));
```

---

## 🚀 Nächste Schritte

**Jetzt implementieren:**
1. App-spezifische Probleme (15min)
2. Background Jobs Detection (10min)
3. Disk Full Detection (5min)

**Diskutieren:**
- Welche Test-Logs hast du verfügbar?
- Welche Issues siehst du am häufigsten in Produktion?
- Soll ich dynamische Schwellwerte implementieren?

