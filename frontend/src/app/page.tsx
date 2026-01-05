'use client'

import { useState, useEffect } from 'react'
import FileExplorer from '@/components/FileExplorer'
import ZoneVisualization from '@/components/ZoneVisualization'
import BlockchainViewer from '@/components/BlockchainViewer'
import FileUpload from '@/components/FileUpload'
import { FileMetadata } from '@/types'

export default function Home() {
  const [files, setFiles] = useState<FileMetadata[]>([])
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null)
  const [activeTab, setActiveTab] = useState<'explorer' | 'zones' | 'blockchain'>('explorer')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchFiles()
  }, [])

  const fetchFiles = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/files`, {
        headers: {
          'X-User-ID': 'demo_user'
        }
      })
      const data = await response.json()
      setFiles(data)
    } catch (error) {
      console.error('Error fetching files:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUploaded = () => {
    fetchFiles()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">CryptoFS++</h1>
              <p className="text-sm text-gray-500">AI-Governed, Blockchain-Audited File System</p>
            </div>
            <div className="flex items-center space-x-4">
              <FileUpload onUploaded={handleFileUploaded} />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('explorer')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'explorer'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              File Explorer
            </button>
            <button
              onClick={() => setActiveTab('zones')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'zones'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Zones
            </button>
            <button
              onClick={() => setActiveTab('blockchain')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'blockchain'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Blockchain Audit
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        ) : (
          <>
            {activeTab === 'explorer' && (
              <FileExplorer
                files={files}
                selectedFile={selectedFile}
                onSelectFile={setSelectedFile}
                onRefresh={fetchFiles}
              />
            )}
            {activeTab === 'zones' && <ZoneVisualization files={files} />}
            {activeTab === 'blockchain' && <BlockchainViewer />}
          </>
        )}
      </main>
    </div>
  )
}

