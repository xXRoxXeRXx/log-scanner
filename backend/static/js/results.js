// Store chart instance outside Alpine.js to avoid reactivity issues
        let chartInstance = null;

        function resultsApp() {
            return {
                loading: true,
                error: null,
                analysisId: null,
                result: null,
                historyList: null,
                selectedCategory: null,
                currentPage: 1,
                entriesPerPage: 100,
                selectedEntry: null, // Track which entry's details are expanded
                rootCause: { issues: [] }, // Root cause analysis data
                darkMode: false, // Dark mode state
                
                // Filter states
                filterDateFrom: '',
                filterDateTo: '',
                filterUsername: '',
                filterSearch: '',
                filtersApplied: false,
                
                // NEW: Enhanced filter states
                selectedCategories: [],  // Multi-category selection
                regexMode: false,        // Regex search toggle
                quickFilterActive: null, // Track active quick filter
                filtersApplied: false,
                
                // Computed property for available users
                get availableUsers() {
                    if (!this.result?.entries) return [];
                    
                    const users = new Set();
                    
                    this.result.entries.forEach(entry => {
                        // Method 1: Check if entry has a 'user' field (parsed from JSON logs)
                        if (entry.user && entry.user.trim() && entry.user !== '' && entry.user !== '--') {
                            users.add(entry.user.trim());
                        }
                        
                        // Method 2: Extract from raw_line if it's JSON
                        if (entry.raw_line) {
                            try {
                                const json = JSON.parse(entry.raw_line);
                                if (json.user && json.user.trim() && json.user !== '' && json.user !== '--') {
                                    users.add(json.user.trim());
                                }
                            } catch (e) {
                                // Not JSON, try pattern matching
                                const patterns = [
                                    /\/remote\.php\/dav\/files\/([a-zA-Z0-9_.-]+)/,
                                    /\/files\/([a-zA-Z0-9_.-]+)\//,
                                ];
                                
                                for (const pattern of patterns) {
                                    const match = entry.raw_line.match(pattern);
                                    if (match && match[1]) {
                                        users.add(match[1]);
                                        break;
                                    }
                                }
                            }
                        }
                    });
                    
                    const userArray = Array.from(users)
                        .filter(u => u.length >= 3 && u.length <= 50) // Reasonable username length
                        .sort();
                    
                    console.log('Extracted users:', userArray);
                    return userArray;
                },

                // Computed property for filtered entries
                get filteredEntries() {
                    if (!this.result?.entries) return [];
                    
                    let filtered = this.result.entries;
                    
                    // NEW: Multi-Category filter (takes precedence over single category)
                    if (this.selectedCategories.length > 0) {
                        filtered = filtered.filter(entry => 
                            this.selectedCategories.includes(entry.category)
                        );
                    }
                    // Category filter (legacy single category)
                    else if (this.selectedCategory) {
                        filtered = filtered.filter(entry => entry.category === this.selectedCategory);
                    }
                    
                    // NEW: Quick Filter - With Users
                    if (this.quickFilterActive === 'with_users') {
                        filtered = filtered.filter(entry => 
                            entry.user && entry.user.trim() && entry.user !== '--' && entry.user !== ''
                        );
                    }
                    
                    // Date filters (only if applied)
                    if (this.filtersApplied) {
                        if (this.filterDateFrom) {
                            const fromDate = new Date(this.filterDateFrom);
                            filtered = filtered.filter(entry => {
                                const entryDate = new Date(entry.time);
                                return entryDate >= fromDate;
                            });
                        }
                        
                        if (this.filterDateTo) {
                            const toDate = new Date(this.filterDateTo);
                            toDate.setHours(23, 59, 59, 999); // Include entire day
                            filtered = filtered.filter(entry => {
                                const entryDate = new Date(entry.time);
                                return entryDate <= toDate;
                            });
                        }
                        
                        // Username filter
                        if (this.filterUsername) {
                            const username = this.filterUsername.toLowerCase();
                            filtered = filtered.filter(entry => {
                                return entry.message?.toLowerCase().includes(username) ||
                                       entry.raw_line?.toLowerCase().includes(username);
                            });
                        }
                        
                        // NEW: Search filter with Regex support
                        if (this.filterSearch) {
                            if (this.regexMode) {
                                try {
                                    const regex = new RegExp(this.filterSearch, 'i');
                                    filtered = filtered.filter(entry => {
                                        return regex.test(entry.message || '') ||
                                               regex.test(entry.source_file || '') ||
                                               regex.test(entry.raw_line || '') ||
                                               regex.test(entry.error_code || '') ||
                                               regex.test(entry.category || '') ||
                                               regex.test(entry.type || '');
                                    });
                                } catch (e) {
                                    console.warn('Invalid regex pattern:', e);
                                    // Fall back to normal search if regex is invalid
                                    const search = this.filterSearch.toLowerCase();
                                    filtered = filtered.filter(entry => {
                                        return entry.message?.toLowerCase().includes(search) ||
                                               entry.source_file?.toLowerCase().includes(search) ||
                                               entry.raw_line?.toLowerCase().includes(search) ||
                                               entry.error_code?.toLowerCase().includes(search) ||
                                               entry.category?.toLowerCase().includes(search) ||
                                               entry.type?.toLowerCase().includes(search);
                                    });
                                }
                            } else {
                                // Normal text search
                                const search = this.filterSearch.toLowerCase();
                                filtered = filtered.filter(entry => {
                                    return entry.message?.toLowerCase().includes(search) ||
                                           entry.source_file?.toLowerCase().includes(search) ||
                                           entry.raw_line?.toLowerCase().includes(search) ||
                                           entry.error_code?.toLowerCase().includes(search) ||
                                           entry.category?.toLowerCase().includes(search) ||
                                           entry.type?.toLowerCase().includes(search);
                                });
                            }
                        }
                    }
                    
                    return filtered;
                },

                // Computed property for paginated entries
                get paginatedEntries() {
                    const start = (this.currentPage - 1) * this.entriesPerPage;
                    const end = start + this.entriesPerPage;
                    return this.filteredEntries.slice(start, end);
                },

                // Computed property for total pages
                get totalPages() {
                    return Math.ceil(this.filteredEntries.length / this.entriesPerPage);
                },

                nextPage() {
                    if (this.currentPage < this.totalPages) {
                        this.currentPage++;
                        this.scrollToTable();
                    }
                },

                previousPage() {
                    if (this.currentPage > 1) {
                        this.currentPage--;
                        this.scrollToTable();
                    }
                },

                goToPage(page) {
                    this.currentPage = page;
                    this.scrollToTable();
                },

                scrollToTable() {
                    document.querySelector('.entries-table')?.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                },
                
                // Filter methods
                applyFilters() {
                    this.filtersApplied = true;
                    this.currentPage = 1; // Reset to first page
                    console.log('Filters applied:', {
                        dateFrom: this.filterDateFrom,
                        dateTo: this.filterDateTo,
                        username: this.filterUsername,
                        search: this.filterSearch
                    });
                },
                
                resetAllFilters() {
                    this.filterDateFrom = '';
                    this.filterDateTo = '';
                    this.filterUsername = '';
                    this.filterSearch = '';
                    this.selectedCategory = null;
                    this.selectedCategories = [];  // NEW: Reset multi-category
                    this.regexMode = false;         // NEW: Reset regex mode
                    this.quickFilterActive = null;  // NEW: Reset quick filter
                    this.filtersApplied = false;
                    this.currentPage = 1;
                },
                
                hasActiveFilters() {
                    return this.filterDateFrom || this.filterDateTo || this.filterUsername || this.filterSearch || this.selectedCategory || this.selectedCategories.length > 0 || this.quickFilterActive || this.searchTerm;
                },
                
                // Clear all active filters
                clearAllFilters() {
                    console.log('🗑️ Clearing all filters');
                    this.resetAllFilters();
                    this.searchTerm = '';
                    this.applyFilters();
                },
                
                // NEW: Quick Filter Methods
                applyQuickFilter(filterType) {
                    console.log('🚀 Applying quick filter:', filterType);
                    
                    // Reset all filters first
                    this.resetAllFilters();
                    this.quickFilterActive = filterType;
                    
                    const now = new Date();
                    
                    switch(filterType) {
                        case 'errors':
                            this.filterSearch = 'error';
                            break;
                        
                        case 'warnings':
                            this.filterSearch = 'warning';
                            break;
                        
                        case 'last_hour':
                            const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
                            this.filterDateFrom = oneHourAgo.toISOString().split('T')[0];
                            this.filterDateTo = now.toISOString().split('T')[0];
                            break;
                        
                        case 'last_24h':
                            const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                            this.filterDateFrom = oneDayAgo.toISOString().split('T')[0];
                            this.filterDateTo = now.toISOString().split('T')[0];
                            break;
                        
                        case 'critical':
                            // Filter for critical severity
                            this.selectedCategories = ['storage', 'database', 'security'];
                            break;
                        
                        case 'with_users':
                            // Will be filtered in filteredEntries computed property
                            break;
                    }
                    
                    this.applyFilters();
                },
                
                // Download methods
                downloadJSON() {
                    if (!this.result) return;
                    
                    const data = JSON.stringify(this.result, null, 2);
                    const blob = new Blob([data], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `nextcloud-analysis-${this.analysisId || 'result'}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                },
                
                downloadCSV() {
                    if (!this.result?.entries) return;
                    
                    // CSV Header
                    const headers = ['Timestamp', 'Level', 'Category', 'Message', 'User', 'Error Code'];
                    
                    // Convert entries to CSV rows
                    const rows = this.result.entries.map(entry => {
                        return [
                            entry.timestamp || '',
                            entry.level || '',
                            entry.category || '',
                            this.escapeCsvValue(entry.message || ''),
                            entry.user || '--',
                            entry.error_code || ''
                        ];
                    });
                    
                    // Combine header and rows
                    const csvContent = [
                        headers.join(','),
                        ...rows.map(row => row.join(','))
                    ].join('\n');
                    
                    // Create download
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `nextcloud-analysis-${this.analysisId || 'result'}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                },
                
                escapeCsvValue(value) {
                    if (typeof value !== 'string') return value;
                    
                    // Escape quotes and wrap in quotes if contains comma, newline, or quote
                    if (value.includes(',') || value.includes('\n') || value.includes('"')) {
                        return '"' + value.replace(/"/g, '""') + '"';
                    }
                    return value;
                },
                
                getCategoryLabel(category) {
                    const labels = {
                        // Functional Categories (NEW)
                        'authentication': '🔐 Authentication & Access',
                        'file_sync': '📁 File Sync & WebDAV',
                        'storage': '☁️ Storage & S3',
                        'database': '🗄️ Database',
                        'security': '🔒 Security',
                        'apps': '📱 Apps',
                        'background_jobs': '⚙️ Background Jobs',
                        'php_runtime': '🐘 PHP Runtime',
                        'system': '⚡ System',
                        // Client Categories
                        'client_errors': 'Client Errors',
                        'client_events': 'Client Events'
                    };
                    return labels[category] || category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                },
                
                // Dark mode toggle
                toggleTheme() {
                    this.darkMode = !this.darkMode;
                    document.documentElement.setAttribute('data-theme', this.darkMode ? 'dark' : 'light');
                    localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
                    
                    // Recreate charts to apply new theme colors
                    this.$nextTick(() => {
                        this.createChart();
                        this.createTimelineChart();
                    });
                },

                async init() {
                    // Load theme from localStorage or system preference
                    const savedTheme = localStorage.getItem('theme');
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    this.darkMode = savedTheme === 'dark' || (!savedTheme && prefersDark);
                    document.documentElement.setAttribute('data-theme', this.darkMode ? 'dark' : 'light');
                    
                    // Check if we have an ID in URL
                    const params = new URLSearchParams(window.location.search);
                    this.analysisId = params.get('id');

                    if (this.analysisId) {
                        await this.loadResult(this.analysisId);
                    } else {
                        await this.loadHistory();
                    }
                },

                async loadResult(id) {
                    try {
                        const response = await fetch(`/api/results/${id}`);
                        
                        if (!response.ok) {
                            throw new Error('Analyse nicht gefunden');
                        }

                        this.result = await response.json();
                        
                        console.log('📊 Loaded result:', this.result);
                        console.log('📝 Entries count:', this.result?.entries?.length);
                        console.log('📝 First entry:', this.result?.entries?.[0]);
                        
                        // Perform root cause analysis
                        this.analyzeRootCause();
                        
                        // Wait for Alpine to render, then create charts with additional delay
                        this.$nextTick(() => {
                            setTimeout(() => {
                                this.createChart();
                                this.createTimelineChart();  // NEW: Create timeline chart
                            }, 100);
                        });

                    } catch (err) {
                        console.error('❌ Error loading result:', err);
                        this.error = err.message || 'Fehler beim Laden der Ergebnisse';
                    } finally {
                        this.loading = false;
                    }
                },

                async loadHistory() {
                    try {
                        const response = await fetch('/api/results');
                        
                        if (!response.ok) {
                            throw new Error('Fehler beim Laden der Historie');
                        }

                        const data = await response.json();
                        this.historyList = data.results;

                    } catch (err) {
                        this.error = err.message || 'Fehler beim Laden der Historie';
                    } finally {
                        this.loading = false;
                    }
                },

                createChart() {
                    try {
                        if (!this.result?.categories) {
                            return;
                        }

                        const ctx = document.getElementById('categoriesChart');
                        if (!ctx) {
                            return;
                        }

                        // Check if Chart is available
                        if (typeof Chart === 'undefined') {
                            console.error('Chart.js not available');
                            return;
                        }

                        const categories = this.result.categories;
                        
                        // Filter out categories with 0 entries
                        const filteredCategories = Object.entries(categories)
                            .filter(([key, value]) => value > 0);
                        
                        // If no categories have entries, don't show chart
                        if (filteredCategories.length === 0) {
                            console.log('No categories with entries to display');
                            return;
                        }
                        
                        const labels = filteredCategories.map(([key, value]) => key);
                        const data = filteredCategories.map(([key, value]) => value);

                        if (chartInstance) {
                            chartInstance.destroy();
                            chartInstance = null;
                        }

                    chartInstance = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Anzahl',
                                data: data,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)',
                                    'rgba(255, 206, 86, 0.7)',
                                    'rgba(75, 192, 192, 0.7)',
                                    'rgba(153, 102, 255, 0.7)',
                                    'rgba(255, 159, 64, 0.7)',
                                    'rgba(255, 99, 132, 0.7)',
                                    'rgba(54, 162, 235, 0.7)'
                                ],
                                borderColor: [
                                    'rgba(255, 99, 132, 1)',
                                    'rgba(54, 162, 235, 1)',
                                    'rgba(255, 206, 86, 1)',
                                    'rgba(75, 192, 192, 1)',
                                    'rgba(153, 102, 255, 1)',
                                    'rgba(255, 159, 64, 1)',
                                    'rgba(255, 99, 132, 1)',
                                    'rgba(54, 162, 235, 1)'
                                ],
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            animation: {
                                duration: 1000
                            },
                            onClick: (event, activeElements) => {
                                if (activeElements.length > 0) {
                                    const index = activeElements[0].index;
                                    const category = labels[index];
                                    this.selectedCategory = category;
                                    this.currentPage = 1; // Reset to first page when filtering
                                    // Scroll to table
                                    document.querySelector('.entries-table')?.scrollIntoView({ 
                                        behavior: 'smooth', 
                                        block: 'start' 
                                    });
                                }
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top',
                                    labels: {
                                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
                                    }
                                },
                                tooltip: {
                                    enabled: true,
                                    callbacks: {
                                        afterLabel: (context) => {
                                            return 'Klicken zum Filtern';
                                        }
                                    }
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        precision: 0,
                                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                                    },
                                    grid: {
                                        color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                                    }
                                },
                                x: {
                                    ticks: {
                                        autoSkip: false,
                                        maxRotation: 45,
                                        minRotation: 45,
                                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                                    },
                                    grid: {
                                        color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                                    }
                                }
                            }
                        }
                    });

                    // Force render
                    chartInstance.update();

                    } catch (error) {
                        console.error('Chart creation failed:', error);
                    }
                },

                // NEW: Timeline Chart
                createTimelineChart() {
                    try {
                        if (!this.result?.entries) {
                            console.log('No entries for timeline chart');
                            return;
                        }

                        const ctx = document.getElementById('timelineChart');
                        if (!ctx) {
                            console.warn('Timeline chart canvas not found');
                            return;
                        }

                        if (typeof Chart === 'undefined') {
                            console.error('Chart.js not available');
                            return;
                        }

                        // Group entries by hour
                        const timeGroups = {};
                        
                        this.result.entries.forEach(entry => {
                            if (!entry.time) return;
                            
                            try {
                                const date = new Date(entry.time);
                                if (isNaN(date.getTime())) return;
                                
                                // Group by hour
                                const hourKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:00`;
                                
                                if (!timeGroups[hourKey]) {
                                    timeGroups[hourKey] = {
                                        timestamp: date.setMinutes(0, 0, 0), // Round to hour
                                        count: 0
                                    };
                                }
                                timeGroups[hourKey].count++;
                            } catch (e) {
                                console.warn('Invalid date:', entry.time);
                            }
                        });

                        // Sort by timestamp
                        const sortedGroups = Object.entries(timeGroups)
                            .map(([label, data]) => ({ label, ...data }))
                            .sort((a, b) => a.timestamp - b.timestamp);

                        if (sortedGroups.length === 0) {
                            console.log('No valid timestamps for timeline');
                            return;
                        }

                        const labels = sortedGroups.map(g => g.label);
                        const data = sortedGroups.map(g => g.count);

                        // Destroy existing timeline chart if it exists
                        if (window.timelineChartInstance) {
                            window.timelineChartInstance.destroy();
                        }

                        window.timelineChartInstance = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Fehler pro Stunde',
                                    data: data,
                                    fill: true,
                                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                                    borderColor: 'rgba(102, 126, 234, 1)',
                                    borderWidth: 2,
                                    tension: 0.4,
                                    pointRadius: 4,
                                    pointHoverRadius: 6,
                                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                                    pointBorderColor: '#fff',
                                    pointBorderWidth: 2
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: {
                                    mode: 'index',
                                    intersect: false
                                },
                                onClick: (event, activeElements) => {
                                    if (activeElements.length > 0) {
                                        const index = activeElements[0].index;
                                        const timeLabel = labels[index];
                                        
                                        // Extract date for filtering
                                        const datePart = timeLabel.split(' ')[0];
                                        this.filterDateFrom = datePart;
                                        this.filterDateTo = datePart;
                                        this.applyFilters();
                                        
                                        // Scroll to entries
                                        this.$nextTick(() => {
                                            document.querySelector('.entries-table')?.scrollIntoView({ 
                                                behavior: 'smooth', 
                                                block: 'start' 
                                            });
                                        });
                                    }
                                },
                                plugins: {
                                    legend: {
                                        display: true,
                                        position: 'top',
                                        labels: {
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
                                        }
                                    },
                                    tooltip: {
                                        enabled: true,
                                        callbacks: {
                                            afterLabel: () => 'Klicken zum Filtern'
                                        }
                                    }
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: {
                                            precision: 0,
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                                        },
                                        title: {
                                            display: true,
                                            text: 'Anzahl Fehler',
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
                                        },
                                        grid: {
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                                        }
                                    },
                                    x: {
                                        ticks: {
                                            autoSkip: true,
                                            maxRotation: 45,
                                            minRotation: 45,
                                            maxTicksLimit: 24,
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                                        },
                                        grid: {
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                                        },
                                        title: {
                                            display: true,
                                            text: 'Zeitpunkt',
                                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
                                        }
                                    }
                                }
                            }
                        });

                        console.log('✅ Timeline chart created with', sortedGroups.length, 'data points');

                    } catch (error) {
                        console.error('Timeline chart creation failed:', error);
                    }
                },

                analyzeRootCause() {
                    console.log('🔍 Starting Root Cause Analysis...');
                    console.log('📊 Result entries:', this.result?.entries?.length);
                    
                    if (!this.result?.entries) {
                        console.log('❌ No entries found, aborting analysis');
                        return;
                    }
                    
                    const issues = [];
                    
                    // Analyze ALL entries (not just errors) since functional categories don't have "error" in name
                    const totalErrors = this.result.entries.length;
                    const totalEntries = this.result.total_entries || totalErrors;
                    
                    console.log('📊 Total entries to analyze:', totalErrors);
                    
                    if (totalErrors === 0) {
                        console.log('❌ Zero entries, aborting analysis');
                        return;
                    }
                    
                    // === DYNAMIC THRESHOLDS based on log size ===
                    // Small logs (< 100): Strict thresholds to avoid noise
                    // Large logs (> 10k): Relative thresholds (percentages)
                    const minThreshold = totalEntries < 100 ? 5 : Math.max(10, Math.floor(totalEntries * 0.001)); // 0.1%
                    const lowThreshold = Math.max(minThreshold, Math.floor(totalEntries * 0.01));  // 1%
                    const mediumThreshold = Math.floor(totalEntries * 0.02);  // 2%
                    const highThreshold = Math.floor(totalEntries * 0.05);    // 5%
                    const criticalThreshold = Math.floor(totalEntries * 0.10); // 10%
                    
                    console.log('📊 Dynamic Thresholds:', {
                        total: totalEntries,
                        min: minThreshold,
                        low: lowThreshold,
                        medium: mediumThreshold,
                        high: highThreshold,
                        critical: criticalThreshold
                    });
                    
                    // Helper function to determine severity based on count
                    const getSeverity = (count) => {
                        if (count >= criticalThreshold) return 'critical';
                        if (count >= highThreshold) return 'high';
                        if (count >= mediumThreshold) return 'medium';
                        return 'low';
                    };
                    
                    // Analyze error codes
                    const errorCodes = {};
                    const httpErrors = {};
                    const messagePatterns = {};
                    
                    // === USER IMPACT TRACKING ===
                    // Track unique users affected by each category and pattern
                    const userImpactByCategory = {};
                    const userImpactByPattern = {};
                    
                    this.result.entries.forEach(entry => {
                        // Analyze ALL entries (storage, file_sync, php_runtime, etc.)
                        
                        // Track users per category
                        if (entry.category && entry.user) {
                            if (!userImpactByCategory[entry.category]) {
                                userImpactByCategory[entry.category] = new Set();
                            }
                            userImpactByCategory[entry.category].add(entry.user);
                        }
                        
                        // Count error codes
                        if (entry.error_code && entry.error_code !== null && entry.error_code !== 'null') {
                            errorCodes[entry.error_code] = (errorCodes[entry.error_code] || 0) + 1;
                            
                            // Track users per error code
                            if (entry.user) {
                                if (!userImpactByPattern[entry.error_code]) {
                                    userImpactByPattern[entry.error_code] = new Set();
                                }
                                userImpactByPattern[entry.error_code].add(entry.user);
                            }
                        }
                        
                        // Extract HTTP status codes
                        const httpMatch = entry.message?.match(/HTTP.*?(\d{3})|status\s+(\d{3})/i);
                        if (httpMatch) {
                            const status = httpMatch[1] || httpMatch[2];
                            httpErrors[status] = (httpErrors[status] || 0) + 1;
                            
                            // Track users per HTTP error
                            if (entry.user) {
                                const key = `http_${status}`;
                                if (!userImpactByPattern[key]) {
                                    userImpactByPattern[key] = new Set();
                                }
                                userImpactByPattern[key].add(entry.user);
                            }
                        }
                        
                        // Pattern matching for common issues
                        const msg = entry.message?.toLowerCase() || '';
                        if (msg.includes('symbolic') || msg.includes('symlink')) {
                            messagePatterns['symlink'] = (messagePatterns['symlink'] || 0) + 1;
                            if (entry.user) {
                                if (!userImpactByPattern['symlink']) userImpactByPattern['symlink'] = new Set();
                                userImpactByPattern['symlink'].add(entry.user);
                            }
                        }
                        if (msg.includes('not found') || msg.includes('404')) {
                            messagePatterns['notfound'] = (messagePatterns['notfound'] || 0) + 1;
                            if (entry.user) {
                                if (!userImpactByPattern['notfound']) userImpactByPattern['notfound'] = new Set();
                                userImpactByPattern['notfound'].add(entry.user);
                            }
                        }
                        if (msg.includes('permission') || msg.includes('forbidden') || msg.includes('403')) {
                            messagePatterns['permission'] = (messagePatterns['permission'] || 0) + 1;
                            if (entry.user) {
                                if (!userImpactByPattern['permission']) userImpactByPattern['permission'] = new Set();
                                userImpactByPattern['permission'].add(entry.user);
                            }
                        }
                        if (msg.includes('network') || msg.includes('connection') || msg.includes('timeout')) {
                            messagePatterns['network'] = (messagePatterns['network'] || 0) + 1;
                            if (entry.user) {
                                if (!userImpactByPattern['network']) userImpactByPattern['network'] = new Set();
                                userImpactByPattern['network'].add(entry.user);
                            }
                        }
                        if (msg.includes('invalid') && msg.includes('filename')) {
                            messagePatterns['invalidname'] = (messagePatterns['invalidname'] || 0) + 1;
                            if (entry.user) {
                                if (!userImpactByPattern['invalidname']) userImpactByPattern['invalidname'] = new Set();
                                userImpactByPattern['invalidname'].add(entry.user);
                            }
                        }
                    });
                    
                    console.log('👥 User Impact Tracking:', {
                        categories: Object.keys(userImpactByCategory).length,
                        patterns: Object.keys(userImpactByPattern).length
                    });
                    
                    // Generate issues based on patterns
                    
                    // FileIgnored errors (symbolic links)
                    if (errorCodes['FileIgnored'] > 10) {
                        const percentage = ((errorCodes['FileIgnored'] / totalErrors) * 100).toFixed(1);
                        const affectedUsers = userImpactByPattern['FileIgnored']?.size || 0;
                        const userInfo = affectedUsers > 0 ? ` Betroffen: ${affectedUsers} User.` : '';
                        
                        issues.push({
                            type: 'fileignored',
                            severity: percentage > 30 ? 'high' : 'medium',
                            icon: '🔗',
                            title: 'Symbolische Links werden nicht synchronisiert',
                            description: `${errorCodes['FileIgnored']} Dateien/Ordner können nicht synchronisiert werden, da es sich um symbolische Verknüpfungen handelt.${userInfo}`,
                            count: errorCodes['FileIgnored'],
                            percentage: percentage,
                            affected_users: affectedUsers,
                            suggestion: 'Symbolische Links sind nicht synchronisierbar. Ersetzen Sie diese durch echte Ordner oder Kopien der Dateien, oder schließen Sie diese Pfade von der Synchronisation aus.',
                            filterCriteria: { error_code: 'FileIgnored' }
                        });
                    }
                    
                    // HTTP 404 errors
                    if (httpErrors['404'] > 10) {
                        const percentage = ((httpErrors['404'] / totalErrors) * 100).toFixed(1);
                        const affectedUsers = userImpactByPattern['http_404']?.size || 0;
                        const userInfo = affectedUsers > 0 ? ` Betroffen: ${affectedUsers} User.` : '';
                        
                        issues.push({
                            type: 'http404',
                            severity: percentage > 20 ? 'high' : 'medium',
                            icon: '🔍',
                            title: 'Dateien auf Server nicht gefunden (HTTP 404)',
                            description: `${httpErrors['404']} Anfragen schlugen fehl, weil Dateien auf dem Server nicht existieren.${userInfo}`,
                            count: httpErrors['404'],
                            percentage: percentage,
                            affected_users: affectedUsers,
                            suggestion: 'Dateien wurden möglicherweise auf dem Server gelöscht oder verschoben. Prüfen Sie den Server-Speicher oder synchronisieren Sie den Client neu.',
                            filterCriteria: { search: 'HTTP status 404' }
                        });
                    }
                    
                    // HTTP 403 Permission errors
                    if (httpErrors['403'] > 5) {
                        const percentage = ((httpErrors['403'] / totalErrors) * 100).toFixed(1);
                        issues.push({
                            type: 'http403',
                            severity: 'high',
                            icon: '🚫',
                            title: 'Zugriff verweigert (HTTP 403)',
                            description: `${httpErrors['403']} Anfragen wurden aufgrund fehlender Berechtigungen abgelehnt.`,
                            count: httpErrors['403'],
                            percentage: percentage,
                            suggestion: 'Überprüfen Sie die Benutzerberechtigungen auf dem Server. Möglicherweise fehlen Lese-/Schreibrechte für bestimmte Ordner.',
                            filterCriteria: { search: '403' }
                        });
                    }
                    
                    // Network/Connection errors
                    if (messagePatterns['network'] > 20) {
                        const percentage = ((messagePatterns['network'] / totalErrors) * 100).toFixed(1);
                        issues.push({
                            type: 'network',
                            severity: percentage > 40 ? 'critical' : 'high',
                            icon: '🌐',
                            title: 'Netzwerkverbindungsprobleme',
                            description: `${messagePatterns['network']} Fehler stehen im Zusammenhang mit Netzwerkproblemen oder Timeouts.`,
                            count: messagePatterns['network'],
                            percentage: percentage,
                            suggestion: 'Prüfen Sie die Internetverbindung, Firewall-Einstellungen und die Erreichbarkeit des Nextcloud-Servers. Möglicherweise ist der Server überlastet oder es gibt DNS-Probleme.',
                            filterCriteria: { search: 'network' }
                        });
                    }
                    
                    // Invalid filename errors
                    if (errorCodes['FileNameInvalidOnServer'] > 3 || messagePatterns['invalidname'] > 3) {
                        const count = (errorCodes['FileNameInvalidOnServer'] || 0) + (messagePatterns['invalidname'] || 0);
                        const percentage = ((count / totalErrors) * 100).toFixed(1);
                        issues.push({
                            type: 'invalidname',
                            severity: 'medium',
                            icon: '📝',
                            title: 'Ungültige Dateinamen',
                            description: `${count} Dateien haben Namen, die auf dem Server nicht erlaubt sind (z.B. Sonderzeichen, zu lang).`,
                            count: count,
                            percentage: percentage,
                            suggestion: 'Benennen Sie die betroffenen Dateien um. Vermeiden Sie Sonderzeichen wie :, *, ?, ", <, >, | und sehr lange Dateinamen.',
                            filterCriteria: { search: 'invalid' }
                        });
                    }
                    
                    // SyncError
                    if (errorCodes['SyncError'] > 3) {
                        const percentage = ((errorCodes['SyncError'] / totalErrors) * 100).toFixed(1);
                        issues.push({
                            type: 'syncerror',
                            severity: 'high',
                            icon: '⚠️',
                            title: 'Allgemeine Synchronisationsfehler',
                            description: `${errorCodes['SyncError']} allgemeine Synchronisationsfehler wurden erkannt.`,
                            count: errorCodes['SyncError'],
                            percentage: percentage,
                            suggestion: 'Diese Fehler können verschiedene Ursachen haben. Prüfen Sie die Detail-Logs und erwägen Sie einen Neustart des Clients oder eine Neusynchronisation.',
                            filterCriteria: { search: 'SyncError' }
                        });
                    }
                    
                    // === SERVER LOG ANALYSIS (FUNCTIONAL CATEGORIES) ===
                    
                    // Storage errors (S3, ObjectStore) - NEW FUNCTIONAL CATEGORY
                    const storageCount = this.result.categories?.storage || 0;
                    const storageCritical = this.result.entries?.filter(e => 
                        e.category === 'storage' && e.severity === 'critical'
                    ).length || 0;
                    
                    if (storageCount > 50 || storageCritical > 5) {
                        const percentage = ((storageCount / this.result.total_entries) * 100).toFixed(1);
                        const severity = storageCritical > 100 ? 'critical' : (storageCritical > 20 ? 'high' : 'medium');
                        const affectedUsers = userImpactByCategory['storage']?.size || 0;
                        const userInfo = affectedUsers > 0 ? ` | ${affectedUsers} User betroffen` : '';
                        
                        // Check for S3-specific errors
                        const s3_503 = this.result.entries?.filter(e => 
                            e.category === 'storage' && (e.error_code === '503' || e.message?.includes('503'))
                        ).length || 0;
                        
                        const noSuchUpload = this.result.entries?.filter(e => 
                            e.category === 'storage' && e.message?.includes('NoSuchUpload')
                        ).length || 0;
                        
                        let description = `${storageCount} Storage-Fehler (${storageCritical} kritisch)${userInfo}.`;
                        let suggestion = 'Prüfen Sie die S3/ObjectStore-Verbindung.';
                        
                        if (noSuchUpload > 10) {
                            description += ` ${noSuchUpload}x NoSuchUpload - unterbrochene Multi-Part-Uploads.`;
                            suggestion = 'KRITISCH: NoSuchUpload-Fehler bedeuten, dass Multi-Part-Uploads fehlgeschlagen sind. Prüfen Sie: 1) S3-Credentials, 2) Bucket-Existenz, 3) Upload-Timeout-Werte, 4) Netzwerkstabilität.';
                        } else if (s3_503 > 10) {
                            description += ` ${s3_503}x HTTP 503 - S3-Service überlastet.`;
                            suggestion = 'Der S3-Service ist nicht verfügbar. Prüfen Sie: 1) S3-Provider-Status, 2) Rate Limits, 3) Netzwerk-Verbindung, 4) Storage-Kapazität.';
                        }
                        
                        issues.push({
                            type: 'storage',
                            severity: severity,
                            icon: '☁️',
                            title: 'Storage-Probleme (S3/ObjectStore)',
                            description: description,
                            count: storageCount,
                            percentage: percentage,
                            affected_users: affectedUsers,
                            suggestion: suggestion,
                            filterCriteria: { category: 'storage' }
                        });
                    }
                    
                    // File Sync errors (WebDAV) - NEW FUNCTIONAL CATEGORY
                    const fileSyncCount = this.result.categories?.file_sync || 0;
                    if (fileSyncCount > 100) {
                        const percentage = ((fileSyncCount / this.result.total_entries) * 100).toFixed(1);
                        const severity = fileSyncCount > 500 ? 'high' : 'medium';
                        const affectedUsers = userImpactByCategory['file_sync']?.size || 0;
                        const userInfo = affectedUsers > 0 ? ` | ${affectedUsers} User betroffen` : '';
                        
                        // Check for TypeErrors in file sync
                        const typeErrors = this.result.entries?.filter(e => 
                            e.category === 'file_sync' && e.message?.includes('TypeError')
                        ).length || 0;
                        
                        let description = `${fileSyncCount} Fehler bei der Dateisynchronisierung (WebDAV)${userInfo}.`;
                        let suggestion = 'WebDAV-Fehler sind oft durch Backend-Probleme verursacht.';
                        
                        if (typeErrors > 50) {
                            description += ` ${typeErrors}x TypeError im HookConnector - Code-Problem!`;
                            suggestion = 'TypeErrors im HookConnector deuten auf einen Bug in Nextcloud oder einer App hin. Prüfen Sie: 1) Nextcloud-Version updaten, 2) Apps deaktivieren, 3) PHP-Version prüfen, 4) GitHub Issues checken.';
                        }
                        
                        issues.push({
                            type: 'file_sync',
                            severity: severity,
                            icon: '📁',
                            title: 'Dateisynchronisierungs-Probleme',
                            description: description,
                            count: fileSyncCount,
                            percentage: percentage,
                            affected_users: affectedUsers,
                            suggestion: suggestion,
                            filterCriteria: { category: 'file_sync' }
                        });
                    }
                    
                    // PHP Runtime errors - NEW FUNCTIONAL CATEGORY
                    const phpCount = this.result.categories?.php_runtime || 0;
                    if (phpCount > 20) {
                        const percentage = ((phpCount / this.result.total_entries) * 100).toFixed(1);
                        const severity = phpCount > 100 ? 'high' : 'medium';
                        const affectedUsers = userImpactByCategory['php_runtime']?.size || 0;
                        const userInfo = affectedUsers > 0 ? ` | ${affectedUsers} User betroffen` : '';
                        
                        // Check for specific PHP error types
                        const undefinedArrayKey = this.result.entries?.filter(e => 
                            e.category === 'php_runtime' && e.message?.includes('Undefined array key')
                        ).length || 0;
                        
                        const typeErrors = this.result.entries?.filter(e => 
                            e.category === 'php_runtime' && e.message?.includes('TypeError')
                        ).length || 0;
                        
                        let description = `${phpCount} PHP-Fehler wurden erkannt${userInfo}.`;
                        let suggestion = 'Prüfen Sie die PHP-Logs für Details.';
                        
                        if (undefinedArrayKey > 100) {
                            description += ` Hauptsächlich "Undefined array key"-Warnungen (${undefinedArrayKey}x) - meist harmlos.`;
                            suggestion = 'Viele "Undefined array key"-Fehler deuten auf fehlende Array-Checks im Code hin. Diese sind meist nicht kritisch, können aber mit Error-Grouping reduziert werden.';
                        } else if (typeErrors > 10) {
                            description += ` Viele TypeErrors (${typeErrors}x) - Code-Inkompatibilitäten!`;
                            suggestion = 'TypeErrors deuten auf Code-Inkompatibilitäten hin. Prüfen Sie: 1) Nextcloud-Version, 2) PHP-Version, 3) App-Updates, 4) Deaktivieren Sie problematische Apps.';
                        }
                        
                        issues.push({
                            type: 'php_runtime',
                            severity: severity,
                            icon: '🐘',
                            title: 'PHP Runtime-Fehler',
                            description: description,
                            count: phpCount,
                            percentage: percentage,
                            affected_users: affectedUsers,
                            suggestion: suggestion,
                            filterCriteria: { category: 'php_runtime' }
                        });
                    }
                    
                    // Database errors - NEW FUNCTIONAL CATEGORY
                    const databaseCount = this.result.categories?.database || 0;
                    if (databaseCount > 20) {
                        const percentage = ((databaseCount / this.result.total_entries) * 100).toFixed(1);
                        const severity = databaseCount > 100 ? 'critical' : (databaseCount > 50 ? 'high' : 'medium');
                        
                        // Check for connection failures
                        const connectionErrors = this.result.entries?.filter(e => 
                            e.category === 'database' && (e.message?.includes('Failed to connect') || e.message?.includes('connection'))
                        ).length || 0;
                        
                        let description = `${databaseCount} Datenbank-Fehler erkannt.`;
                        let suggestion = 'Prüfen Sie die Datenbank-Verbindung und Logs.';
                        
                        if (connectionErrors > 10) {
                            description += ` ${connectionErrors}x Connection-Fehler - DB nicht erreichbar!`;
                            suggestion = 'KRITISCH: Datenbank nicht erreichbar! Prüfen Sie: 1) MySQL/PostgreSQL läuft, 2) Credentials korrekt, 3) Netzwerk-Verbindung, 4) Max Connections nicht erreicht.';
                        }
                        
                        issues.push({
                            type: 'database',
                            severity: severity,
                            icon: '🗄️',
                            title: 'Datenbank-Probleme',
                            description: description,
                            count: databaseCount,
                            percentage: percentage,
                            suggestion: suggestion,
                            filterCriteria: { category: 'database' }
                        });
                    }
                    
                    // Authentication errors - NEW FUNCTIONAL CATEGORY
                    const authCount = this.result.categories?.authentication || 0;
                    if (authCount > 50) {
                        const percentage = ((authCount / this.result.total_entries) * 100).toFixed(1);
                        const severity = authCount > 200 ? 'high' : 'medium';
                        
                        // Check for CSRF or brute-force
                        const csrfErrors = this.result.entries?.filter(e => 
                            e.category === 'authentication' && e.message?.toLowerCase().includes('csrf')
                        ).length || 0;
                        
                        let description = `${authCount} Authentifizierungs-/Zugriffsfehler.`;
                        let suggestion = 'Prüfen Sie Login-Probleme und Berechtigungen.';
                        
                        if (csrfErrors > 20) {
                            description += ` ${csrfErrors}x CSRF-Token-Fehler - Session-Probleme!`;
                            suggestion = 'CSRF-Token-Fehler deuten auf Session-Probleme hin. Prüfen Sie: 1) Session-Storage (Redis/Memcached), 2) Cookie-Einstellungen, 3) Reverse-Proxy-Konfiguration.';
                        }
                        
                        issues.push({
                            type: 'authentication',
                            severity: severity,
                            icon: '🔐',
                            title: 'Authentifizierungs-Probleme',
                            description: description,
                            count: authCount,
                            percentage: percentage,
                            suggestion: suggestion,
                            filterCriteria: { category: 'authentication' }
                        });
                    }
                    
                    // Security issues - NEW FUNCTIONAL CATEGORY
                    const securityCount = this.result.categories?.security || 0;
                    if (securityCount > 5) {
                        const percentage = ((securityCount / this.result.total_entries) * 100).toFixed(1);
                        issues.push({
                            type: 'security',
                            severity: 'high',
                            icon: '🔒',
                            title: 'Sicherheits-Warnungen',
                            description: `${securityCount} sicherheitsrelevante Ereignisse erkannt (Attacks, Rate-Limits, Blocked IPs).`,
                            count: securityCount,
                            percentage: percentage,
                            suggestion: 'Prüfen Sie die Security-Logs und Fail2Ban. Eventuell laufender Angriff!',
                            filterCriteria: { category: 'security' }
                        });
                    }
                    
                    // Apps-specific problems - NEW FUNCTIONAL CATEGORY
                    const appsCount = this.result.categories?.apps || 0;
                    if (appsCount > 20) {
                        const appsErrors = this.result.entries?.filter(e => e.category === 'apps') || [];
                        
                        // Group by app_name
                        const appErrorCounts = {};
                        appsErrors.forEach(e => {
                            const app = e.app || 'unknown';
                            appErrorCounts[app] = (appErrorCounts[app] || 0) + 1;
                        });
                        
                        // Find apps with significant errors (>5% of app errors)
                        const minAppErrors = Math.max(20, appsCount * 0.05);
                        Object.entries(appErrorCounts)
                            .filter(([app, count]) => count > minAppErrors)
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, 5) // Top 5 problematic apps
                            .forEach(([app, count]) => {
                                const percentage = ((count / this.result.total_entries) * 100).toFixed(1);
                                const severity = count > 200 ? 'high' : count > 100 ? 'medium' : 'low';
                                
                                // Check for specific error patterns
                                const appErrors = appsErrors.filter(e => e.app === app);
                                const hasTypeError = appErrors.some(e => e.message?.includes('TypeError'));
                                const hasException = appErrors.some(e => e.exception_type);
                                
                                let description = `${count} Fehler in der App "${app}".`;
                                let suggestion = `Prüfen Sie die App "${app}": 1) Update verfügbar checken, 2) Kompatibilität mit Nextcloud-Version prüfen, 3) App-spezifische Logs analysieren.`;
                                
                                if (hasTypeError) {
                                    description += ' TypeErrors erkannt - Code-Inkompatibilität!';
                                    suggestion = `App "${app}" hat TypeErrors! 1) App auf neueste Version updaten, 2) Falls Problem bleibt: App deaktivieren, 3) GitHub Issue erstellen, 4) Alternative App suchen.`;
                                } else if (hasException) {
                                    description += ' Exceptions/Crashes erkannt.';
                                    suggestion = `App "${app}" crasht! 1) PHP-Version kompatibel? 2) Erforderliche PHP-Extensions installiert? 3) App-Logs checken: data/nextcloud.log, 4) App neu installieren.`;
                                }
                                
                                issues.push({
                                    type: `app_${app}`,
                                    severity: severity,
                                    icon: '📱',
                                    title: `App-Problem: ${app}`,
                                    description: description,
                                    count: count,
                                    percentage: percentage,
                                    suggestion: suggestion,
                                    filterCriteria: { category: 'apps', search: app }
                                });
                            });
                    }
                    
                    // Background Jobs problems - NEW FUNCTIONAL CATEGORY
                    const bgJobsCount = this.result.categories?.background_jobs || 0;
                    if (bgJobsCount > 10) {
                        const bgJobErrors = this.result.entries?.filter(e => e.category === 'background_jobs') || [];
                        
                        // Check for memory errors
                        const memoryErrors = bgJobErrors.filter(e => 
                            e.message?.toLowerCase().includes('memory') || 
                            e.message?.toLowerCase().includes('allowed memory size') ||
                            e.message?.toLowerCase().includes('out of memory')
                        ).length;
                        
                        // Check for timeout errors
                        const timeoutErrors = bgJobErrors.filter(e => 
                            e.message?.toLowerCase().includes('timeout') || 
                            e.message?.toLowerCase().includes('maximum execution time') ||
                            e.message?.toLowerCase().includes('max_execution_time')
                        ).length;
                        
                        const percentage = ((bgJobsCount / this.result.total_entries) * 100).toFixed(1);
                        let severity = 'medium';
                        let description = `${bgJobsCount} Fehler bei Background-Jobs (Cron).`;
                        let suggestion = 'Prüfen Sie Cron-Konfiguration: occ config:system:get cron';
                        
                        if (memoryErrors > 10) {
                            severity = memoryErrors > 50 ? 'high' : 'medium';
                            description += ` ${memoryErrors}x Memory-Limit erreicht!`;
                            suggestion = 'PHP memory_limit erhöhen: 1) In config.php: "memory_limit" => "1G", 2) In php.ini anpassen, 3) Apache/Nginx neu starten, 4) Große Background-Jobs optimieren.';
                        } else if (timeoutErrors > 10) {
                            severity = 'high';
                            description += ` ${timeoutErrors}x Execution-Timeout!`;
                            suggestion = 'max_execution_time erhöhen: 1) php.ini: max_execution_time = 3600, 2) Cron parallel laufen lassen (occ background:cron), 3) Schwere Jobs nachts laufen lassen.';
                        } else {
                            description += ' Verschiedene Job-Fehler.';
                            suggestion = 'Background-Jobs prüfen: 1) occ background:cron -v ausführen, 2) Nextcloud.log nach "cron" durchsuchen, 3) System-Cron aktiv? (crontab -u www-data -l)';
                        }
                        
                        issues.push({
                            type: 'background_jobs',
                            severity: severity,
                            icon: '⚙️',
                            title: 'Background-Job-Probleme',
                            description: description,
                            count: bgJobsCount,
                            percentage: percentage,
                            suggestion: suggestion,
                            filterCriteria: { category: 'background_jobs' }
                        });
                    }
                    
                    // System-level issues - NEW FUNCTIONAL CATEGORY
                    const systemCount = this.result.categories?.system || 0;
                    if (systemCount > 5) {
                        const systemErrors = this.result.entries?.filter(e => e.category === 'system') || [];
                        
                        // Check for disk space errors
                        const diskErrors = systemErrors.filter(e => 
                            e.message?.toLowerCase().includes('disk') || 
                            e.message?.toLowerCase().includes('no space') ||
                            e.message?.toLowerCase().includes('quota exceeded') ||
                            e.message?.toLowerCase().includes('filesystem full')
                        ).length;
                        
                        // Check for permission errors
                        const permErrors = systemErrors.filter(e => 
                            e.message?.toLowerCase().includes('permission denied') ||
                            e.message?.toLowerCase().includes('chmod') ||
                            e.message?.toLowerCase().includes('chown')
                        ).length;
                        
                        // Disk Full Critical Issue
                        if (diskErrors > 3) {
                            const percentage = ((diskErrors / this.result.total_entries) * 100).toFixed(1);
                            issues.push({
                                type: 'disk_full',
                                severity: 'critical',
                                icon: '💾',
                                title: 'Speicherplatz-Problem',
                                description: `${diskErrors} Fehler durch vollen Speicher oder Quota-Überschreitung. KRITISCH!`,
                                count: diskErrors,
                                percentage: percentage,
                                suggestion: 'SOFORT handeln: 1) df -h für Speicher-Status, 2) Trash leeren (occ trashbin:cleanup --all-users), 3) Versions bereinigen (occ versions:cleanup), 4) Große Dateien finden (find /data -size +1G), 5) Storage erweitern!',
                                filterCriteria: { search: 'disk' }
                            });
                        }
                        
                        // Permission Issues
                        if (permErrors > 5) {
                            const percentage = ((permErrors / this.result.total_entries) * 100).toFixed(1);
                            issues.push({
                                type: 'permissions',
                                severity: 'high',
                                icon: '🔐',
                                title: 'Dateisystem-Berechtigungen',
                                description: `${permErrors} Permission-Denied-Fehler. Nextcloud kann nicht auf Dateien/Ordner zugreifen!`,
                                count: permErrors,
                                percentage: percentage,
                                suggestion: 'Berechtigungen korrigieren: 1) chown -R www-data:www-data /var/www/nextcloud, 2) chmod -R 750 /var/www/nextcloud/data, 3) Bei Docker: Volume-Permissions prüfen, 4) SELinux/AppArmor checken.',
                                filterCriteria: { search: 'permission denied' }
                            });
                        }
                    }
                    
                    // === GENERIC ERROR PATTERNS (category-independent) ===
                    
                    // Check for storage unavailable exceptions
                    const storageUnavailable = this.result.entries?.filter(e => 
                        e.message?.includes('StorageNotAvailableException') ||
                        e.message?.includes('storage is not available') ||
                        e.message?.includes('Storage not available')
                    ).length || 0;
                    
                    if (storageUnavailable > 10) {
                        const percentage = ((storageUnavailable / this.result.total_entries) * 100).toFixed(1);
                        issues.push({
                            type: 'storage_unavailable',
                            severity: 'critical',
                            icon: '💥',
                            title: 'Storage nicht verfügbar',
                            description: `${storageUnavailable} "Storage Not Available"-Exceptions. Der Hauptspeicher ist nicht erreichbar!`,
                            count: storageUnavailable,
                            percentage: percentage,
                            suggestion: 'KRITISCH: Der Primary Storage ist offline oder nicht montiert. Prüfen Sie: 1) NFS/CIFS-Mounts, 2) S3-Credentials, 3) Netzwerk-Verbindung, 4) Storage-Server-Status.',
                            filterCriteria: { search: 'StorageNotAvailableException' }
                        });
                    }
                    
                    // Check for file locking issues
                    const lockErrors = this.result.entries?.filter(e => 
                        e.message?.toLowerCase().includes('lock') && 
                        (e.message?.toLowerCase().includes('failed') || e.message?.toLowerCase().includes('error'))
                    ).length || 0;
                    
                    if (lockErrors > 20) {
                        const percentage = ((lockErrors / this.result.total_entries) * 100).toFixed(1);
                        issues.push({
                            type: 'locking',
                            severity: 'medium',
                            icon: '🔒',
                            title: 'File-Locking-Probleme',
                            description: `${lockErrors} Fehler beim Sperren/Entsperren von Dateien. Dies kann zu Datenverlust führen!`,
                            count: lockErrors,
                            percentage: percentage,
                            suggestion: 'Locking-Probleme können durch: 1) Redis/Memcached-Probleme, 2) Datenbank-Locks, 3) Tote Lock-Einträge verursacht werden. Prüfen Sie das Locking-Backend und bereinigen Sie alte Locks.',
                            filterCriteria: { search: 'lock' }
                        });
                    }
                    
                    // Redis connection errors
                    const redisErrors = this.result.entries?.filter(e => 
                        e.message?.toLowerCase().includes('redisexception') || 
                        e.message?.toLowerCase().includes('read error on connection to') && e.message?.toLowerCase().includes('6379')
                    ).length || 0;
                    
                    if (redisErrors > 5) {
                        const percentage = ((redisErrors / this.result.total_entries) * 100).toFixed(1);
                        const severity = redisErrors > 100 ? 'critical' : redisErrors > 50 ? 'high' : 'medium';
                        issues.push({
                            type: 'redis_connection',
                            severity: severity,
                            icon: '🔴',
                            title: 'Redis Connection/Read Errors',
                            description: `${redisErrors} Redis-Verbindungsfehler erkannt. Redis-Cluster oder einzelne Nodes sind nicht erreichbar.`,
                            count: redisErrors,
                            percentage: percentage,
                            suggestion: 'Redis-Probleme beheben: 1) Prüfen Sie Redis-Cluster-Status (kubectl get pods -n redis-cluster), 2) Netzwerk-Verbindung zu Redis-Nodes testen, 3) Redis-Memory und Logs prüfen, 4) Timeout-Werte in NextCloud-Konfiguration erhöhen, 5) Bei Cluster: Failover und Node-Erreichbarkeit prüfen.',
                            filterCriteria: { search: 'RedisException' }
                        });
                    }
                    
                    // WorkflowEngine boot failures due to Redis
                    const workflowRedisErrors = this.result.entries?.filter(e => 
                        e.message?.toLowerCase().includes('could not boot workflowengine') && 
                        e.message?.toLowerCase().includes('redis')
                    ).length || 0;
                    
                    if (workflowRedisErrors > 5) {
                        const percentage = ((workflowRedisErrors / this.result.total_entries) * 100).toFixed(1);
                        const severity = workflowRedisErrors > 50 ? 'high' : 'medium';
                        issues.push({
                            type: 'workflow_redis',
                            severity: severity,
                            icon: '⚙️',
                            title: 'WorkflowEngine Boot Failures (Redis)',
                            description: `${workflowRedisErrors} WorkflowEngine-Start-Fehler durch Redis-Probleme. App kann nicht initialisiert werden.`,
                            count: workflowRedisErrors,
                            percentage: percentage,
                            suggestion: 'WorkflowEngine-Probleme: 1) Redis-Verfügbarkeit sicherstellen, 2) WorkflowEngine App deaktivieren/aktivieren, 3) Redis-Cache leeren (occ cache:clear), 4) Memcache-Konfiguration in config.php prüfen, 5) Alternativ: File-basiertes Caching verwenden.',
                            filterCriteria: { search: 'workflowengine' }
                        });
                    }
                    
                    // WebDAV failures due to Redis
                    const davRedisErrors = this.result.entries?.filter(e => 
                        e.message?.toLowerCase().includes('sabre') && 
                        e.message?.toLowerCase().includes('serviceunavailable') && 
                        e.message?.toLowerCase().includes('redis')
                    ).length || 0;
                    
                    if (davRedisErrors > 3) {
                        const percentage = ((davRedisErrors / this.result.total_entries) * 100).toFixed(1);
                        const severity = davRedisErrors > 20 ? 'high' : 'medium';
                        issues.push({
                            type: 'dav_redis',
                            severity: severity,
                            icon: '📂',
                            title: 'WebDAV Service Unavailable (Redis)',
                            description: `${davRedisErrors} WebDAV-Anfragen schlagen fehl durch Redis-Verbindungsprobleme. Sync-Clients betroffen!`,
                            count: davRedisErrors,
                            percentage: percentage,
                            suggestion: 'WebDAV-Redis-Probleme: 1) Redis-Cluster sofort prüfen (kritisch für Sync), 2) Betroffene Clients werden Fehler melden, 3) Temporär: Memcache in config.php deaktivieren, 4) Redis-Failover-Mechanismus überprüfen, 5) Load-Balancing zwischen Redis-Nodes optimieren.',
                            filterCriteria: { category: 'dav_errors' }
                        });
                    }
                    
                    // Sort by count (most frequent first)
                    issues.sort((a, b) => b.count - a.count);
                    
                    console.log('🔍 Root Cause Analysis Complete!');
                    console.log('📊 Total issues found:', issues.length);
                    console.log('📋 Issues:', issues);
                    
                    this.rootCause.issues = issues;
                    console.log('✅ Root cause issues set:', this.rootCause.issues.length);
                },

                filterByRootCause(issue) {
                    console.log('🔍 Filtering by root cause:', issue);
                    
                    // Clear all filters first
                    this.resetAllFilters();
                    
                    // Apply filter based on issue type
                    switch(issue.type) {
                        // Client errors (old types)
                        case 'fileignored':
                            this.filterSearch = 'FileIgnored';
                            break;
                        case 'network':
                            this.filterSearch = 'network';
                            break;
                        case 'invalidname':
                            this.filterSearch = 'invalid';
                            break;
                        case 'syncerror':
                            this.filterSearch = 'SyncError';
                            break;
                        
                        // Functional categories (NEW)
                        case 'storage':
                            this.selectedCategories = ['storage'];
                            break;
                        case 'file_sync':
                            this.selectedCategories = ['file_sync'];
                            break;
                        case 'php_runtime':
                            this.selectedCategories = ['php_runtime'];
                            break;
                        case 'database':
                            this.selectedCategories = ['database'];
                            break;
                        case 'authentication':
                            this.selectedCategories = ['authentication'];
                            break;
                        case 'security':
                            this.selectedCategories = ['security'];
                            break;
                        case 'background_jobs':
                            this.selectedCategories = ['background_jobs'];
                            break;
                        
                        // Specific system issues
                        case 'disk_full':
                            this.filterSearch = 'disk space';
                            break;
                        case 'permissions':
                            this.filterSearch = 'permission denied';
                            break;
                        case 'storage_unavailable':
                            this.filterSearch = 'StorageNotAvailableException';
                            break;
                        case 'locking':
                            this.filterSearch = 'lock';
                            break;
                        case 'redis_connection':
                            this.filterSearch = 'RedisException';
                            break;
                        case 'workflow_redis':
                            this.filterSearch = 'workflowengine';
                            break;
                        case 'dav_redis':
                            this.selectedCategories = ['file_sync'];
                            this.filterSearch = 'redis';
                            break;
                        
                        // Fallback: use filterCriteria if available
                        default:
                            if (issue.filterCriteria) {
                                if (issue.filterCriteria.category) {
                                    this.selectedCategories = [issue.filterCriteria.category];
                                }
                                if (issue.filterCriteria.search) {
                                    this.filterSearch = issue.filterCriteria.search;
                                }
                            }
                    }
                    
                    // CRITICAL: Actually apply the filters!
                    this.applyFilters();
                    
                    // Scroll to entries table
                    this.$nextTick(() => {
                        const entriesTable = document.querySelector('.entries-container');
                        if (entriesTable) {
                            entriesTable.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    });
                },

                exportJSON() {
                    const dataStr = JSON.stringify(this.result, null, 2);
                    const dataBlob = new Blob([dataStr], { type: 'application/json' });
                    const url = URL.createObjectURL(dataBlob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `analysis_${this.analysisId}.json`;
                    link.click();
                    URL.revokeObjectURL(url);
                },

                async deleteAnalysis() {
                    if (!confirm('Möchten Sie diese Analyse wirklich löschen?')) {
                        return;
                    }

                    try {
                        const response = await fetch(`/api/results/${this.analysisId}`, {
                            method: 'DELETE'
                        });

                        if (!response.ok) {
                            throw new Error('Löschen fehlgeschlagen');
                        }

                        alert('Analyse gelöscht');
                        window.location.href = '/results.html';

                    } catch (err) {
                        alert(err.message || 'Fehler beim Löschen');
                    }
                }
            }
        }