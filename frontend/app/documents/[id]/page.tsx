'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { documentApi } from '@/lib/api';
import Link from 'next/link';
import { FileText, Download, Trash2, ArrowLeft, Calendar, HardDrive, FileType, Layers, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';

interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  chunk_count?: number;
}

export default function DocumentViewPage() {
  const params = useParams();
  const router = useRouter();
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const documentId = params.id as string;

  useEffect(() => {
    async function fetchDocument() {
      try {
        setLoading(true);
        const data = await documentApi.get(parseInt(documentId));
        setDocument(data);
        setError(null);
      } catch (err: any) {
        console.error('Failed to fetch document:', err);
        setError(err.response?.data?.detail || 'Failed to load document');
      } finally {
        setLoading(false);
      }
    }

    if (documentId) {
      fetchDocument();
    }
  }, [documentId]);

  const handleDownload = async () => {
    if (!document) return;
    
    try {
      setDownloading(true);
      const response = await documentApi.getDownloadUrl(document.id);
      
      // If we get a URL, open it
      if (response.url) {
        window.open(response.url, '_blank');
      } else {
        // Direct download for demo mode
        const link = window.document.createElement('a');
        link.href = `http://localhost:8000/api/documents/${document.id}/download`;
        link.download = document.original_filename;
        window.document.body.appendChild(link);
        link.click();
        window.document.body.removeChild(link);
      }
    } catch (err: any) {
      console.error('Download failed:', err);
      // Fallback: direct download link
      const link = window.document.createElement('a');
      link.href = `http://localhost:8000/api/documents/${document.id}/download`;
      link.download = document.original_filename;
      window.document.body.appendChild(link);
      link.click();
      window.document.body.removeChild(link);
    } finally {
      setDownloading(false);
    }
  };

  const handleDelete = async () => {
    if (!document || !confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await documentApi.delete(document.id);
      router.push('/documents');
    } catch (err: any) {
      console.error('Delete failed:', err);
      alert('Failed to delete document');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="badge badge-yellow flex items-center gap-1.5">
            <Clock className="w-3 h-3" /> Pending
          </span>
        )
      case 'processing':
        return (
          <span className="badge badge-blue flex items-center gap-1.5">
            <Loader className="w-3 h-3 animate-spin" /> Processing
          </span>
        )
      case 'completed':
        return (
          <span className="badge badge-green flex items-center gap-1.5">
            <CheckCircle className="w-3 h-3" /> Completed
          </span>
        )
      case 'failed':
        return (
          <span className="badge badge-red flex items-center gap-1.5">
            <XCircle className="w-3 h-3" /> Failed
          </span>
        )
      default:
        return <span className="badge badge-gray">{status}</span>
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="animate-pulse space-y-8">
          <div className="h-8 bg-slate-200 rounded w-1/3"></div>
          <div className="bg-white rounded-xl h-64 border border-slate-200"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
          <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-red-900 text-xl font-semibold mb-2">Failed to Load Document</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <Link 
            href="/documents" 
            className="btn btn-secondary inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Repository
          </Link>
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-center">
        <p className="text-slate-500">Document not found</p>
        <Link href="/documents" className="text-blue-600 hover:underline mt-4 inline-block">
          ← Back to Documents
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <Link 
          href="/documents" 
          className="text-slate-500 hover:text-blue-600 text-sm font-medium mb-4 inline-flex items-center gap-1 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Repository
        </Link>
        
        <div className="flex items-start justify-between gap-4">
            <div>
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight break-all">
                {document.original_filename}
                </h1>
                <div className="flex items-center gap-3 mt-3">
                    <span className="text-sm text-slate-500 font-mono bg-slate-100 px-2 py-0.5 rounded">ID: {document.id}</span>
                    {getStatusBadge(document.status)}
                </div>
            </div>
            
             <div className="hidden sm:block">
                <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center">
                    <FileText className="w-8 h-8 text-blue-600" />
                </div>
             </div>
        </div>
      </div>

      {/* Document Details Card */}
      <div className="card mb-8 overflow-hidden">
        <div className="border-b border-slate-100 bg-slate-50/50 px-6 py-4">
            <h2 className="text-base font-semibold text-slate-900">Metadata Analysis</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-8 gap-x-12 p-6">
          <div className="space-y-6">
             <div>
                <dt className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-1">
                    <HardDrive className="w-4 h-4" /> File Size
                </dt>
                <dd className="text-slate-900 font-medium">{formatFileSize(document.file_size)}</dd>
             </div>
             
             <div>
                <dt className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-1">
                    <FileType className="w-4 h-4" /> MIME Type
                </dt>
                <dd className="text-slate-900 font-mono text-sm bg-slate-100 inline-block px-2 py-0.5 rounded">{document.mime_type}</dd>
             </div>
             
             <div>
                <dt className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-1">
                    <Layers className="w-4 h-4" /> Chunks Processed
                </dt>
                <dd className="text-slate-900 font-medium">{document.chunk_count || 0}</dd>
             </div>
          </div>
          
          <div className="space-y-6">
            <div>
                <dt className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-1">
                    <Calendar className="w-4 h-4" /> Created At
                </dt>
                <dd className="text-slate-900">{formatDate(document.created_at)}</dd>
             </div>
             
             <div>
                <dt className="flex items-center gap-2 text-sm font-medium text-slate-500 mb-1">
                    <Clock className="w-4 h-4" /> Last Updated
                </dt>
                <dd className="text-slate-900">{formatDate(document.updated_at)}</dd>
             </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-slate-200">
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="btn btn-primary flex-1 sm:flex-none flex items-center justify-center gap-2"
        >
          {downloading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Downloading...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Download Document
            </>
          )}
        </button>
        
        <button
          onClick={handleDelete}
          className="btn btn-danger flex-1 sm:flex-none flex items-center justify-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          Delete Document
        </button>
      </div>

      {/* Demo Mode Notice */}
      <div className="mt-12 bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
        <Clock className="w-5 h-5 text-amber-600 mt-0.5" />
        <div>
            <h4 className="text-sm font-semibold text-amber-900">Demo Environment</h4>
            <p className="text-sm text-amber-700 mt-1">
            Files uploaded in this session are stored in temporary memory. 
            Restarting the application server will clear all uploaded documents.
            </p>
        </div>
      </div>
    </div>
  );
}
