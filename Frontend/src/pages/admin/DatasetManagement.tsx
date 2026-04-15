import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, Trash2, Eye, Loader2, X } from 'lucide-react';
import { GlassCard } from '@/components/common/GlassCard';
import { adminAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface Dataset {
  id: number;
  name: string;
  file_path: string;
  file_size_mb?: number;
  row_count?: number;
  uploaded_at: string;
  status?: string;
}

interface DatasetRow {
  [key: string]: any;
}

const DatasetManagement: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [viewingDatasetId, setViewingDatasetId] = useState<number | null>(null);
  const [viewingDatasetName, setViewingDatasetName] = useState<string>('');
  const [datasetData, setDatasetData] = useState<DatasetRow[]>([]);
  const [datasetDataLoading, setDatasetDataLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Load datasets on component mount
  useEffect(() => {
    loadDatasets();
  }, []);

  // Load datasets from backend
  const loadDatasets = async () => {
    setLoading(true);
    try {
      const data = await adminAPI.getDatasets();
      setDatasets(data.datasets || []);
    } catch (error) {
      console.error('Failed to load datasets:', error);
      toast({
        title: 'Error',
        description: 'Failed to load datasets',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Load dataset data from backend
  const loadDatasetData = async (datasetId: number, datasetName: string) => {
    setDatasetDataLoading(true);
    try {
      const data = await adminAPI.getDatasetRows(datasetId, 500);
      setDatasetData(data.rows || []);
      setViewingDatasetId(datasetId);
      setViewingDatasetName(datasetName);
    } catch (error) {
      console.error('Failed to load dataset data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dataset data',
        variant: 'destructive',
      });
    } finally {
      setDatasetDataLoading(false);
    }
  };

  // Handle file selection and upload
  const handleFileUpload = async (file: File) => {
    // Validate file type
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const fileExt = file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !['csv', 'xls', 'xlsx'].includes(fileExt || '')) {
      toast({
        title: 'Invalid File Type',
        description: 'Please upload a CSV or Excel file',
        variant: 'destructive',
      });
      return;
    }

    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
      toast({
        title: 'File Too Large',
        description: 'Maximum file size is 50MB',
        variant: 'destructive',
      });
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      // Simulate progress (increment every 100ms during upload)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) return prev; // Stop at 90% until actual completion
          return prev + Math.random() * 30;
        });
      }, 100);

      const result = await adminAPI.uploadDataset(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      // Add new dataset to the list
      const newDataset: Dataset = {
        id: result.id || Date.now(),
        name: result.name,
        file_path: result.file_path,
        file_size_mb: result.file_size_mb,
        row_count: result.row_count,
        uploaded_at: result.uploaded_at,
        status: result.status || 'processed',
      };

      setDatasets([newDataset, ...datasets]);

      toast({
        title: 'Upload Successful',
        description: `${result.name} uploaded with ${result.row_count} rows`,
      });

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Reset progress after delay
      setTimeout(() => setUploadProgress(0), 1000);
    } catch (error: any) {
      console.error('Upload failed:', error);
      toast({
        title: 'Upload Failed',
        description: error.response?.data?.detail || 'Failed to upload file',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  // Handle file browser button click
  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dataset Management</h1>
        <p className="text-muted-foreground text-sm mt-1">Upload, preview, and manage climate datasets</p>
      </div>

      {/* Upload Zone */}
      <GlassCard hover={false}>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${dragActive ? 'border-primary bg-primary/5' : 'border-border/30'}`}
        >
          {uploading ? (
            <>
              <Loader2 className="w-10 h-10 text-primary mx-auto mb-3 animate-spin" />
              <p className="text-foreground font-medium">Uploading...</p>
              <div className="mt-4 w-full bg-border/20 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary h-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-muted-foreground text-xs mt-2">{Math.round(uploadProgress)}%</p>
            </>
          ) : (
            <>
              <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
              <p className="text-foreground font-medium">Drag & drop CSV or Excel files here</p>
              <p className="text-muted-foreground text-sm mt-1">or click to browse (max 50MB)</p>
              <button
                onClick={handleBrowseClick}
                disabled={uploading}
                className="mt-4 px-6 py-2 bg-primary/20 text-primary border border-primary/30 rounded-lg text-sm font-medium hover:bg-primary/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Browse Files
              </button>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileInputChange}
                accept=".csv,.xlsx,.xls"
                className="hidden"
                disabled={uploading}
              />
            </>
          )}
        </div>
      </GlassCard>

      {/* Datasets Table */}
      <GlassCard hover={false} className="p-0 overflow-hidden">
        <div className="p-5 border-b border-border/10 flex justify-between items-center">
          <h3 className="text-foreground font-semibold">
            Uploaded Datasets {loading && <Loader2 className="inline w-4 h-4 ml-2 animate-spin" />}
          </h3>
          {datasets.length > 0 && (
            <span className="text-muted-foreground text-sm">{datasets.length} dataset{datasets.length !== 1 ? 's' : ''}</span>
          )}
        </div>
        <div className="overflow-x-auto">
          {datasets.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              {loading ? 'Loading datasets...' : 'No datasets uploaded yet'}
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/10 text-muted-foreground text-xs uppercase tracking-wider">
                  <th className="text-left p-4">Name</th>
                  <th className="text-left p-4">Size</th>
                  <th className="text-left p-4">Rows</th>
                  <th className="text-left p-4">Uploaded</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map(d => (
                  <tr key={d.id} className="border-b border-border/5 hover:bg-muted/20 transition-colors">
                    <td className="p-4 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary" />
                      <span className="text-foreground">{d.name}</span>
                    </td>
                    <td className="p-4 text-muted-foreground">
                      {d.file_size_mb ? `${d.file_size_mb.toFixed(2)} MB` : 'N/A'}
                    </td>
                    <td className="p-4 text-muted-foreground">
                      {d.row_count ? d.row_count.toLocaleString() : 'N/A'}
                    </td>
                    <td className="p-4 text-muted-foreground">
                      {new Date(d.uploaded_at).toLocaleDateString()}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${d.status === 'processed' ? 'bg-accent/20 text-accent' : 'bg-warning/20 text-warning'}`}>
                        {d.status || 'processed'}
                      </span>
                    </td>
                    <td className="p-4 flex gap-2">
                      <button
                        onClick={() => loadDatasetData(d.id, d.name)}
                        className="p-1.5 rounded hover:bg-muted/50 transition-colors"
                        title="View dataset"
                      >
                        <Eye className="w-3.5 h-3.5 text-muted-foreground" />
                      </button>
                      <button
                        className="p-1.5 rounded hover:bg-destructive/20 transition-colors"
                        title="Delete dataset"
                      >
                        <Trash2 className="w-3.5 h-3.5 text-destructive" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </GlassCard>

      {/* Dataset Viewer Modal */}
      {viewingDatasetId && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setViewingDatasetId(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-background rounded-lg w-full max-w-6xl max-h-[80vh] flex flex-col shadow-2xl border border-border"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-6 border-b border-border/10 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-foreground">{viewingDatasetName}</h2>
                <p className="text-sm text-muted-foreground mt-1">Dataset ID: {viewingDatasetId}</p>
              </div>
              <button
                onClick={() => setViewingDatasetId(null)}
                className="p-2 hover:bg-muted rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>

            {/* Data Table */}
            <div className="flex-1 overflow-auto p-6">
              {datasetDataLoading ? (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading data...</span>
                </div>
              ) : datasetData.length === 0 ? (
                <div className="text-center text-muted-foreground">No data available</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="border-b border-border/20 bg-muted/20">
                        {datasetData[0] && Object.keys(datasetData[0]).map(key => (
                          <th key={key} className="p-3 text-left font-semibold text-foreground text-xs uppercase">
                            {key}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {datasetData.map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-b border-border/10 hover:bg-muted/10">
                          {Object.values(row).map((value, colIndex) => (
                            <td key={colIndex} className="p-3 text-muted-foreground max-w-xs truncate">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-border/10 text-xs text-muted-foreground">
              Showing {datasetData.length} rows (limit: 500)
            </div>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default DatasetManagement;
