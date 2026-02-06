import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import { Layers } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Research Intelligence Platform',
  description: 'Intelligent document search and analysis platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <Providers>
          <div className="min-h-screen flex flex-col bg-[hsl(var(--bg-page))]">
            {/* Corporate Glass Header */}
            <header className="glass-header">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <div className="flex items-center justify-between">
                  {/* Brand Logo */}
                  <div className="flex items-center gap-3">
                    <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2 rounded-lg shadow-lg shadow-blue-500/20">
                      <Layers className="text-white w-6 h-6" />
                    </div>
                    <div>
                      <h1 className="text-xl font-bold tracking-tight text-slate-900 leading-none">
                        Research Intelligence
                      </h1>
                      <p className="text-xs text-slate-500 font-medium tracking-wide">ENTERPRISE PLATFORM</p>
                    </div>
                  </div>
                  
                  {/* Modern Navigation */}
                  <nav className="hidden md:flex items-center gap-8">
                    <a href="/" className="text-slate-600 hover:text-blue-600 font-medium text-sm transition-colors py-2 border-b-2 border-transparent hover:border-blue-600">
                      Dashboard
                    </a>
                    <a href="/upload" className="text-slate-600 hover:text-blue-600 font-medium text-sm transition-colors py-2 border-b-2 border-transparent hover:border-blue-600">
                      Upload
                    </a>
                    <a href="/documents" className="text-slate-600 hover:text-blue-600 font-medium text-sm transition-colors py-2 border-b-2 border-transparent hover:border-blue-600">
                      Repository
                    </a>
                  </nav>
                  
                  {/* User Profile Placeholder */}
                  <div className="flex items-center gap-3 pl-6 border-l border-slate-200">
                    <div className="text-right hidden sm:block">
                      <p className="text-sm font-semibold text-slate-900">Dr. Alex Morgan</p>
                      <p className="text-xs text-slate-500">Lead Researcher</p>
                    </div>
                    <div className="h-10 w-10 rounded-full bg-slate-200 border-2 border-white shadow-sm overflow-hidden">
                      <img 
                        src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex" 
                        alt="User"
                        className="h-full w-full object-cover"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </header>
            
            <main className="flex-1">
              {children}
            </main>
            
            <footer className="bg-white border-t border-slate-200 mt-auto">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                  <p className="text-sm text-slate-500 font-medium">
                    © 2026 Research Intelligence Platform. Enterprise Edition.
                  </p>
                  <div className="flex gap-6 text-sm text-slate-400">
                    <a href="#" className="hover:text-slate-600 transition-colors">Privacy Policy</a>
                    <a href="#" className="hover:text-slate-600 transition-colors">Terms of Service</a>
                    <a href="#" className="hover:text-slate-600 transition-colors">Support</a>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  )
}
