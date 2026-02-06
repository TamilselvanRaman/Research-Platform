'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentApi } from '@/lib/api'
import Link from 'next/link'
import { FileText, Trash2, Download, Clock, CheckCircle, XCircle, Loader, Filter, Plus } from 'lucide-react'
import type { Document } from '@/lib/types'

export default function DocumentsPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const queryClient = useQueryClient()
  
  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', statusFilter],
    queryFn: () => documentApi.list({ limit: 100, status: statusFilter || undefined }),
    refetchInterval: 5000, // Refresh every 5 seconds for processing updates
  })
  
  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
  
  const handleDelete = (id: number, filename: string) => {
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
      deleteMutation.mutate(id)
    }
  }
  
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
  
  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown'
    const kb = bytes / 1024
    const mb = kb / 1024
    if (mb >= 1) return `${mb.toFixed(2)} MB`
    return `${kb.toFixed(2)} KB`
  }
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
        year: 'numeric', 
        month: 'short', 
        day: 'numeric'
    })
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
            Document Repository
          </h2>
          <p className="text-slate-600 mt-1">
            Manage and analyze your uploaded research materials
          </p>
        </div>
        
        <a href="/upload" className="btn btn-primary flex items-center gap-2 shadow-lg shadow-blue-600/20">
          <Plus className="w-4 h-4" />
          <span>Upload Document</span>
        </a>
      </div>
      
      {/* Controls */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-8 shadow-sm flex items-center gap-4">
        <div className="flex items-center gap-2 text-slate-500">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Filters:</span>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input border-slate-200 text-sm py-1.5 w-auto"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
        
        {documents && (
            <div className="ml-auto text-sm text-slate-500 font-medium">
                {documents.length} Documents
            </div>
        )}
      </div>
      
      {/* Documents List */}
      {isLoading && (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-200">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-500 font-medium">Loading repository...</p>
        </div>
      )}
      
      {documents && documents.length === 0 && (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
          <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-slate-300" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-1">No documents found</h3>
          <p className="text-slate-500 mb-6 max-w-sm mx-auto">Upload your first document to start analyzing semantic data.</p>
          <a href="/upload" className="btn btn-secondary">
            Upload Your First Document
          </a>
        </div>
      )}
      
      {documents && documents.length > 0 && (
        <div className="grid grid-cols-1 gap-4">
          {documents.map((doc: Document) => (
            <div key={doc.id} className="card hover:border-blue-300 transition-colors p-5 group flex flex-col md:flex-row gap-6 items-start md:items-center">
              
              {/* Icon & Main Info */}
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
                    <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div className="min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                        <Link href={`/documents/${doc.id}`} className="hover:underline focus:outline-none focus:underline">
                            <h3 className="font-semibold text-lg text-slate-900 truncate pr-2">
                                {doc.title || doc.original_filename}
                            </h3>
                        </Link>
                        {getStatusBadge(doc.status)}
                    </div>
                    
                    <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-500">
                        <span className="flex items-center gap-1.5">
                            <span className="font-medium text-slate-700">Size:</span> {formatFileSize(doc.file_size)}
                        </span>
                        <span className="flex items-center gap-1.5">
                            <span className="font-medium text-slate-700">Uploaded:</span> {formatDate(doc.created_at)}
                        </span>
                        {doc.page_count && (
                             <span className="flex items-center gap-1.5">
                                <span className="font-medium text-slate-700">Pages:</span> {doc.page_count}
                             </span>
                        )}
                        {doc.company && (
                             <span className="hidden sm:inline-block px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-xs font-medium uppercase tracking-wide">
                                {doc.company}
                             </span>
                        )}
                    </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3 w-full md:w-auto border-t md:border-t-0 pt-4 md:pt-0 mt-2 md:mt-0 justify-end">
                <Link 
                    href={`/documents/${doc.id}`}
                    className="btn btn-secondary py-2 px-4 text-xs"
                >
                    View Details
                </Link>
                <button
                    onClick={() => handleDelete(doc.id, doc.original_filename)}
                    disabled={deleteMutation.isPending}
                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete Document"
                >
                    <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
