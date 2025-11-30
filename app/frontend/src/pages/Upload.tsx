import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Upload as UploadIcon,
    FileText,
    CheckCircle,
    AlertCircle,
    X,
    Download,
    Eye,
    Database
} from 'lucide-react';
import { api } from '../lib/api';
import clsx from 'clsx';

interface UploadResult {
    rows_imported: number;
    rejected_rows: number;
    items_created: number;
    transactions_created: number;
    errors: string[];
}

export function Upload() {
    const navigate = useNavigate();
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<UploadResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
                setFile(droppedFile);
                setError(null);
            } else {
                setError('Please upload a CSV file');
            }
        }
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
                setFile(selectedFile);
                setError(null);
            } else {
                setError('Please upload a CSV file');
            }
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/api/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const resetUpload = () => {
        setFile(null);
        setResult(null);
        setError(null);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 py-6 px-4">
            {/* Header */}
            <header className="text-center space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                    <Database size={14} />
                    Data Upload
                </div>
                <h1 className="text-3xl font-bold text-text-primary">Upload Transaction Data</h1>
                <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                    Import your transaction data to unlock AI-powered insights and bundle recommendations.
                </p>
            </header>

            {/* Upload Area */}
            {!result ? (
                <div className="space-y-6">
                    <div
                        className={clsx(
                            'relative border-2 border-dashed rounded-2xl p-12 text-center transition-all',
                            dragActive
                                ? 'border-primary bg-primary/5'
                                : file
                                    ? 'border-success bg-success/5'
                                    : 'border-border hover:border-primary/50 hover:bg-primary/5'
                        )}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileSelect}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />

                        <div className="space-y-4">
                            {file ? (
                                <>
                                    <CheckCircle size={48} className="mx-auto text-success" />
                                    <div>
                                        <p className="text-lg font-medium text-text-primary">{file.name}</p>
                                        <p className="text-sm text-text-secondary">
                                            {(file.size / 1024 / 1024).toFixed(2)} MB • Ready to upload
                                        </p>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <UploadIcon size={48} className="mx-auto text-text-muted" />
                                    <div>
                                        <p className="text-lg font-medium text-text-primary">
                                            Drop your CSV file here
                                        </p>
                                        <p className="text-sm text-text-secondary">
                                            or click to browse • Supports transaction data with items, prices, and timestamps
                                        </p>
                                    </div>
                                </>
                            )}

                            {error && (
                                <div className="flex items-center justify-center gap-2 text-danger">
                                    <AlertCircle size={16} />
                                    <span className="text-sm">{error}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Upload Button */}
                    <div className="flex justify-center">
                        <button
                            onClick={handleUpload}
                            disabled={!file || uploading}
                            className={clsx(
                                'px-8 py-3 rounded-xl font-medium transition-all flex items-center gap-2',
                                file && !uploading
                                    ? 'bg-primary text-white hover:bg-primary-dark shadow-md hover:shadow-lg'
                                    : 'bg-surface border border-border text-text-muted cursor-not-allowed'
                            )}
                        >
                            {uploading ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <UploadIcon size={16} />
                                    Upload Data
                                </>
                            )}
                        </button>
                    </div>
                </div>
            ) : (
                /* Results */
                <div className="space-y-6">
                    <div className="bg-surface border border-border rounded-2xl p-8">
                        <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <CheckCircle size={24} className="text-success" />
                                <h2 className="text-xl font-semibold text-text-primary">Upload Complete</h2>
                            </div>
                            <button
                                onClick={resetUpload}
                                className="p-2 rounded-lg hover:bg-surface-elevated transition-colors"
                            >
                                <X size={16} className="text-text-muted" />
                            </button>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-primary">{result.rows_imported.toLocaleString()}</div>
                                <div className="text-sm text-text-muted">Rows Imported</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-success">{result.transactions_created.toLocaleString()}</div>
                                <div className="text-sm text-text-muted">Transactions</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-accent">{result.items_created.toLocaleString()}</div>
                                <div className="text-sm text-text-muted">Items Created</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-danger">{result.rejected_rows.toLocaleString()}</div>
                                <div className="text-sm text-text-muted">Rejected Rows</div>
                            </div>
                        </div>

                        {result.errors.length > 0 && (
                            <div className="bg-danger/5 border border-danger/20 rounded-xl p-4">
                                <h3 className="font-medium text-danger mb-2">Errors Encountered:</h3>
                                <ul className="text-sm text-danger space-y-1">
                                    {result.errors.map((error, idx) => (
                                        <li key={idx}>• {error}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Next Steps */}
                    <div className="bg-surface border border-border rounded-2xl p-8 text-center">
                        <h3 className="text-lg font-semibold text-text-primary mb-2">What's Next?</h3>
                        <p className="text-text-secondary mb-6">
                            Your data is now being processed. Check out the recommendations and validation tools.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button
                                onClick={() => navigate('/recommendations')}
                                className="px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary-dark transition-colors flex items-center justify-center gap-2"
                            >
                                <Eye size={16} />
                                View Recommendations
                            </button>
                            <button
                                onClick={() => navigate('/validation')}
                                className="px-6 py-3 bg-surface border border-border text-text-primary rounded-xl font-medium hover:bg-surface-elevated transition-colors flex items-center justify-center gap-2"
                            >
                                <FileText size={16} />
                                Validate Data
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Sample Data Info */}
            <div className="bg-surface border border-border rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Expected CSV Format</h3>
                <div className="bg-surface-elevated rounded-lg p-4 font-mono text-sm text-text-secondary mb-4">
                    transaction_id,customer_id,timestamp,store_id,item_id,item_name,quantity,price,discount_flag<br/>
                    TXN001,CUST001,2024-01-01 10:30:00,STORE001,ITEM001,Milk,1,50.00,0<br/>
                    TXN001,CUST001,2024-01-01 10:30:00,STORE001,ITEM002,Bread,1,30.00,0
                </div>
                <div className="flex items-center gap-2 text-sm text-text-muted">
                    <Download size={14} />
                    <span>Download sample data to see the expected format</span>
                </div>
            </div>
        </div>
    );
}