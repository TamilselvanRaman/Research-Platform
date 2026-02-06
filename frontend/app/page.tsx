'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchApi } from '@/lib/api'
import { Search, FileText, ArrowRight, Sparkles } from 'lucide-react'
import type { SearchResult } from '@/lib/types'

export default function HomePage() {
  const [query, setQuery] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCompany, setSelectedCompany] = useState('')
  const [selectedType, setSelectedType] = useState('')
  
  // Get filter options
  const { data: filters } = useQuery({
    queryKey: ['filters'],
    queryFn: () => searchApi.getFilters(),
  })
  
  // Search query
  const { data: searchResults, isLoading, error } = useQuery({
    queryKey: ['search', searchQuery, selectedCompany, selectedType],
    queryFn: () => searchApi.search({
      query: searchQuery,
      company: selectedCompany || undefined,
      document_type: selectedType || undefined,
      limit: 20,
    }),
    enabled: searchQuery.length > 0,
  })
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      setSearchQuery(query.trim())
    }
  }
  
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 mb-6">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <span className="text-sm font-medium text-blue-800">New: Hybrid Semantic Search</span>
        </div>
        <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">
          Unlock the Power of <br className="hidden md:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
            Intelligent Research
          </span>
        </h2>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto text-balance">
          Instantly analyze thousands of documents using our enterprise-grade AI engine. 
          Retrieve precise insights with semantic understanding.
        </p>
      </div>
      
      {/* Search Interface */}
      <div className="max-w-3xl mx-auto mb-16">
        <form onSubmit={handleSearch} className="relative mb-8 group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for financial reports, analysis, or specific entities..."
            className="block w-full pl-12 pr-32 py-4 text-lg bg-white border border-slate-200 rounded-2xl shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all duration-300"
          />
          <div className="absolute inset-y-0 right-2 flex items-center">
            <button 
              type="submit" 
              className="px-6 py-2 bg-slate-900 text-white font-medium rounded-xl hover:bg-blue-600 transition-colors shadow-lg shadow-slate-900/10"
            >
              Search
            </button>
          </div>
        </form>
        
        {/* Filters */}
        {filters && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200/60">
            <div>
              <label className="label text-xs uppercase tracking-wider text-slate-500 font-semibold mb-2 ml-1">
                Company Entity
              </label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="input border-slate-200 bg-white shadow-sm py-2 text-sm"
              >
                <option value="">All Companies</option>
                {filters.companies.map((company: string) => (
                  <option key={company} value={company}>
                    {company}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="label text-xs uppercase tracking-wider text-slate-500 font-semibold mb-2 ml-1">
                Document Type
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="input border-slate-200 bg-white shadow-sm py-2 text-sm"
              >
                <option value="">All Types</option>
                {filters.document_types.map((type: string) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>
      
      {/* Results Section */}
      {searchQuery && (
        <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between mb-6 pb-2 border-b border-slate-200">
            <h3 className="text-lg font-semibold text-slate-900">Search Results</h3>
            {searchResults && (
              <span className="text-sm text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
                {searchResults.total} matches found ({searchResults.took_ms}ms)
              </span>
            )}
          </div>
          
          {isLoading && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="card h-40 animate-pulse bg-slate-50"></div>
              ))}
            </div>
          )}
          
          {error && (
            <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
              <p className="font-medium">Search failed</p>
              <p className="text-sm opacity-90">{error.message}</p>
            </div>
          )}
          
          {searchResults && (
            <div className="space-y-4">
              {searchResults.results.map((result: SearchResult) => (
                <div key={result.chunk_id} className="card group hover:border-blue-200 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-1 h-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="badge badge-blue">
                          {(result.score * 100).toFixed(0)}% relevant
                        </span>
                        {result.company && (
                          <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                            {result.company}
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-lg text-slate-900 group-hover:text-blue-600 transition-colors">
                        {result.document_title}
                      </h3>
                    </div>
                  </div>
                  
                  <div className="prose prose-sm prose-slate max-w-none mb-4 bg-slate-50 p-4 rounded-lg border border-slate-100 text-slate-600">
                    {result.highlighted_text ? (
                      <span dangerouslySetInnerHTML={{ __html: result.highlighted_text }} />
                    ) : (
                      result.text.substring(0, 300) + (result.text.length > 300 ? '...' : '')
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between mt-4 pl-1">
                    <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
                      {result.page_number && (
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3" /> Page {result.page_number}
                        </span>
                      )}
                      <span>ID: {result.chunk_id}</span>
                    </div>
                    
                    <a
                      href={`/documents/${result.document_id}`}
                      className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      View Analysis <ArrowRight className="w-4 h-4 ml-1" />
                    </a>
                  </div>
                </div>
              ))}
              
              {searchResults.results.length === 0 && (
                <div className="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
                  <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Search className="w-6 h-6 text-slate-400" />
                  </div>
                  <h3 className="text-slate-900 font-medium mb-1">No matches found</h3>
                  <p className="text-slate-500 text-sm">Try adjusting your search terms or filters</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Empty State / Initial View */}
      {!searchQuery && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mt-16 text-center">
            <div className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">Upload PDFs</h3>
                <p className="text-sm text-slate-500">Securely ingest financial reports and research papers.</p>
            </div>
            <div className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm">
                <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="w-5 h-5 text-indigo-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">AI Processing</h3>
                <p className="text-sm text-slate-500">Automated extraction, semantic indexing, and tagging.</p>
            </div>
            <div className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm">
                <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Search className="w-5 h-5 text-emerald-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">Instant Answers</h3>
                <p className="text-sm text-slate-500">Retrieve precise information with hybrid search.</p>
            </div>
        </div>
      )}
    </div>
  )
}
