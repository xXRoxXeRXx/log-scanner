function uploadApp() {
            return {
                files: [],
                dragover: false,
                dragFileCount: 0, // Track number of files being dragged
                loading: false,
                uploadStatus: null, // 'uploading' or 'analyzing'
                uploadProgress: 0, // 0-100
                error: null,
                success: null,
                analysisId: null,
                darkMode: false,
                xhr: null, // Store XMLHttpRequest for cancellation

                init() {
                    // Load dark mode preference from localStorage
                    const savedTheme = localStorage.getItem('theme');
                    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                        this.darkMode = true;
                        document.documentElement.setAttribute('data-theme', 'dark');
                    }
                },

                toggleTheme() {
                    this.darkMode = !this.darkMode;
                    if (this.darkMode) {
                        document.documentElement.setAttribute('data-theme', 'dark');
                        localStorage.setItem('theme', 'dark');
                    } else {
                        document.documentElement.removeAttribute('data-theme');
                        localStorage.setItem('theme', 'light');
                    }
                },

                handleFiles(event) {
                    const newFiles = Array.from(event.target.files);
                    this.addFiles(newFiles);
                },

                handleDrop(event) {
                    this.dragover = false;
                    this.dragFileCount = 0;
                    const newFiles = Array.from(event.dataTransfer.files);
                    this.addFiles(newFiles);
                },
                
                handleDragOver(event) {
                    event.preventDefault();
                    this.dragover = true;
                    // Try to get file count from drag event
                    if (event.dataTransfer.items) {
                        this.dragFileCount = event.dataTransfer.items.length;
                    }
                },
                
                handleDragLeave() {
                    this.dragover = false;
                    this.dragFileCount = 0;
                },

                addFiles(newFiles) {
                    // Filter valid files - allow any file with .log in name, plus .txt, .gz, .zip
                    const validFiles = newFiles.filter(file => {
                        const nameLower = file.name.toLowerCase();
                        return nameLower.includes('.log') || 
                               nameLower.endsWith('.txt') || 
                               nameLower.endsWith('.gz') || 
                               nameLower.endsWith('.zip');
                    });

                    if (validFiles.length < newFiles.length) {
                        this.error = 'Einige Dateien wurden übersprungen (nur .log*, .txt, .gz, .zip erlaubt)';
                        setTimeout(() => this.error = null, 3000);
                    }

                    // Check file size (2GB limit)
                    const oversized = validFiles.filter(f => f.size > 2 * 1024 * 1024 * 1024);
                    if (oversized.length > 0) {
                        this.error = 'Einige Dateien sind zu groß (max 2GB)';
                        return;
                    }

                    this.files.push(...validFiles);
                },

                removeFile(index) {
                    this.files.splice(index, 1);
                },

                formatFileSize(bytes) {
                    if (bytes < 1024) return bytes + ' B';
                    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
                    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
                },

                async analyze() {
                    this.loading = true;
                    this.uploadStatus = 'uploading';
                    this.uploadProgress = 0;
                    this.error = null;
                    this.success = null;

                    try {
                        const formData = new FormData();
                        this.files.forEach(file => {
                            formData.append('files', file);
                        });

                        // Use XMLHttpRequest for progress tracking
                        const result = await this.uploadWithProgress(formData);
                        
                        this.analysisId = result.analysis_id;
                        this.success = `✅ Analyse erfolgreich! ${result.file_count} Datei(en) analysiert.`;
                        this.files = [];

                    } catch (err) {
                        if (err.message === 'UPLOAD_CANCELLED') {
                            this.error = 'Upload wurde abgebrochen';
                        } else {
                            this.error = err.message || 'Ein Fehler ist aufgetreten';
                        }
                    } finally {
                        this.loading = false;
                        this.uploadStatus = null;
                        this.uploadProgress = 0;
                        this.xhr = null;
                    }
                },

                cancelUpload() {
                    if (this.xhr) {
                        this.xhr.abort();
                        this.xhr = null;
                    }
                },

                uploadWithProgress(formData) {
                    return new Promise((resolve, reject) => {
                        const xhr = new XMLHttpRequest();
                        this.xhr = xhr; // Store for cancellation

                        // Upload progress event
                        xhr.upload.addEventListener('progress', (e) => {
                            if (e.lengthComputable) {
                                this.uploadProgress = Math.round((e.loaded / e.total) * 100);
                            }
                        });

                        // Upload complete, switch to analyzing
                        xhr.upload.addEventListener('load', () => {
                            this.uploadProgress = 100;
                            this.uploadStatus = 'analyzing';
                        });

                        // Request complete (response received)
                        xhr.addEventListener('load', () => {
                            if (xhr.status === 200) {
                                try {
                                    const result = JSON.parse(xhr.responseText);
                                    resolve(result);
                                } catch (e) {
                                    reject(new Error('Ungültige Server-Antwort'));
                                }
                            } else {
                                try {
                                    const errorData = JSON.parse(xhr.responseText);
                                    reject(new Error(errorData.detail || 'Upload fehlgeschlagen'));
                                } catch (e) {
                                    reject(new Error(`Upload fehlgeschlagen (Status: ${xhr.status})`));
                                }
                            }
                        });

                        // Network error
                        xhr.addEventListener('error', () => {
                            reject(new Error('Netzwerkfehler beim Upload'));
                        });

                        // Upload aborted
                        xhr.addEventListener('abort', () => {
                            reject(new Error('UPLOAD_CANCELLED'));
                        });

                        // Timeout
                        xhr.addEventListener('timeout', () => {
                            reject(new Error('Upload-Timeout - Datei zu groß oder Netzwerk zu langsam. Bitte versuche eine kleinere Datei.'));
                        });

                        // Send request
                        xhr.open('POST', '/api/upload');
                        xhr.timeout = 600000; // 10 minutes timeout (600 seconds)
                        xhr.send(formData);
                    });
                }
            }
        }