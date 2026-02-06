'use client'

import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { documentApi } from '@/lib/api'
import { Upload, FileText, CheckCircle, XCircle, Loader } from 'lucide-react'

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<Array<{
    name: string;
    status: 'uploading' | 'success' | 'error';
    message?: string;
    id?: number;
  }>>([])
  
  const uploadMutation = useMutation({
    mutationFn: (file: File) => documentApi.upload(file),
    onSuccess: (data, file) => {
      setUploadedFiles(prev => prev.map(f =>
        f.name === file.name
          ? { name: f.name, status: 'success', message: data.message, id: data.document_id }
          : f
      ))
    },
    onError: (error: any, file) => {
      setUploadedFiles(prev => prev.map(f =>
        f.name === file.name
          ? { name: f.name, status: 'error', message: error.message }
          : f
      ))
    },
  })
  
  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return
    
    Array.from(files).forEach(file => {
      // Check if PDF
      if (file.type !== 'application/pdf') {
        setUploadedFiles(prev => [
          ...prev,
          { name: file.name, status: 'error', message: 'Only PDF files are supported' }
        ])
        return
      }
      
      // Add to uploading list
      setUploadedFiles(prev => [
        ...prev,
        { name: file.name, status: 'uploading' }
      ])
      
      // Upload
      uploadMutation.mutate(file)
    })
  }, [uploadMutation])
  
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'drag over') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    handleFiles(e.dataTransfer.files)
  }, [handleFiles])
  
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }, [handleFiles])
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Documents
        </h2>
        <p className="text-gray-600">
          Upload PDF documents to process and make them searchable
        </p>
      </div>
      
      {/* Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-12 text-center transition-colors
          ${dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input
          type="file"
          id="file-upload"
          multiple
          accept=".pdf,application/pdf"
          onChange={handleChange}
          className="hidden"
        />
        
        <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        
        <label
          htmlFor="file-upload"
          className="cursor-pointer"
        >
          <span className="text-lg font-medium text-gray-900">
            Click to upload
          </span>
          {' or drag and drop'}
        </label>
        
        <p className="text-sm text-gray-500 mt-2">
          PDF files only, up to 100MB each
        </p>
      </div>
      
      {/* Upload Progress */}
      {uploadedFiles.length > 0 && (
        <div className="mt-8">
          <h3 className="font-semibold text-lg text-gray-900 mb-4">
            Upload Status
          </h3>
          
          <div className="space-y-3">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="card flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <FileText className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <span className="font-medium text-gray-900 truncate">
                    {file.name}
                  </span>
                </div>
                
                <div className="flex items-center gap-2 ml-4">
                  {file.status === 'uploading' && (
                    <>
                      <Loader className="w-5 h-5 text-primary-600 animate-spin" />
                      <span className="text-sm text-gray-600">Uploading...</span>
                    </>
                  )}
                  
                  {file.status === 'success' && (
                    <>
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="text-sm text-green-600">Uploaded</span>
                      {file.id && (
                        <a
                          href={`/documents/${file.id}`}
                          className="text-sm text-primary-600 hover:text-primary-700 ml-2"
                        >
                          View →
                        </a>
                      )}
                    </>
                  )}
                  
                  {file.status === 'error' && (
                    <>
                      <XCircle className="w-5 h-5 text-red-600" />
                      <span className="text-sm text-red-600">
                        {file.message || 'Upload failed'}
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          <button
            onClick={() => setUploadedFiles([])}
            className="mt-4 text-sm text-gray-600 hover:text-gray-900"
          >
            Clear completed
          </button>
        </div>
      )}
    </div>
  )
}
