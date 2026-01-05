'use client'

import { useState } from 'react'
import { FileMetadata, FileExplanation } from '@/types'
import { FileText, Lock, Unlock, Shield, Info, Download } from 'lucide-react'
import FileDetails from './FileDetails'

interface FileExplorerProps {
  files: FileMetadata[]
  selectedFile: FileMetadata | null
  onSelectFile: (file: FileMetadata | null) => void
  onRefresh: () => void
}

export default function FileExplorer({
  files,
  selectedFile,
  onSelectFile,
  onRefresh
}: FileExplorerProps) {
  const [showDetails, setShowDetails] = useState(false)

  const getZoneColor = (zone: string) => {
    switch (zone) {
      case 'public':
        return 'bg-green-100 border-green-300 text-green-800'
      case 'monitored':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      case 'crypto_vault':
        return 'bg-red-100 border-red-300 text-red-800'
      case 'cold_storage':
        return 'bg-blue-100 border-blue-300 text-blue-800'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  const getZoneIcon = (zone: string) => {
    switch (zone) {
      case 'public':
        return '🟢'
      case 'monitored':
        return '🟡'
      case 'crypto_vault':
        return '🔴'
      case 'cold_storage':
        return '🧊'
      default:
        return '📁'
    }
  }

  const getSensitivityColor = (score: number) => {
    if (score >= 81) return 'text-red-600 font-bold'
    if (score >= 61) return 'text-orange-600 font-semibold'
    if (score >= 31) return 'text-yellow-600'
    return 'text-green-600'
  }

  const handleFileClick = async (file: FileMetadata) => {
    onSelectFile(file)
    setShowDetails(true)
  }

  const handleDownload = async (file: FileMetadata) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/files/${file.file_id}/download`,
        {
          headers: {
            'X-User-ID': 'demo_user'
          }
        }
      )

      if (!response.ok) {
        throw new Error('Download failed')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Download error:', error)
      alert('Failed to download file')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* File List */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Files ({files.length})</h2>
          </div>
          <div className="divide-y">
            {files.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p>No files uploaded yet</p>
                <p className="text-sm mt-2">Upload files to see them here</p>
              </div>
            ) : (
              files.map((file) => (
                <div
                  key={file.file_id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                    selectedFile?.file_id === file.file_id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleFileClick(file)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <FileText className="h-5 w-5 text-gray-400 mt-1" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {file.filename}
                        </p>
                        <div className="mt-2 flex flex-wrap items-center gap-2">
                          <span
                            className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getZoneColor(
                              file.zone
                            )}`}
                          >
                            {getZoneIcon(file.zone)} {file.zone.replace('_', ' ')}
                          </span>
                          <span
                            className={`text-xs font-medium ${getSensitivityColor(
                              file.sensitivity_score
                            )}`}
                          >
                            Sensitivity: {file.sensitivity_score}/100
                          </span>
                          {file.encryption_status === 'encrypted' ? (
                            <span className="inline-flex items-center text-xs text-red-600">
                              <Lock className="h-3 w-3 mr-1" />
                              Encrypted
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-xs text-gray-500">
                              <Unlock className="h-3 w-3 mr-1" />
                              Unencrypted
                            </span>
                          )}
                        </div>
                        {file.detected_entities.length > 0 && (
                          <p className="mt-1 text-xs text-gray-500">
                            Detected: {file.detected_entities.slice(0, 3).join(', ')}
                            {file.detected_entities.length > 3 && '...'}
                          </p>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDownload(file)
                      }}
                      className="ml-4 p-2 text-gray-400 hover:text-blue-600"
                      title="Download"
                    >
                      <Download className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* File Details Sidebar */}
      {showDetails && selectedFile && (
        <FileDetails
          file={selectedFile}
          onClose={() => {
            setShowDetails(false)
            onSelectFile(null)
          }}
        />
      )}
    </div>
  )
}

