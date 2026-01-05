'use client'

import { FileMetadata } from '@/types'
import { FileText, Lock, Shield } from 'lucide-react'

interface ZoneVisualizationProps {
  files: FileMetadata[]
}

export default function ZoneVisualization({ files }: ZoneVisualizationProps) {
  const zones = [
    {
      id: 'public',
      name: '🟢 Public Zone',
      description: 'Low sensitivity, unencrypted files',
      threshold: '0-30',
      color: 'bg-green-50 border-green-300',
      files: files.filter(f => f.zone === 'public')
    },
    {
      id: 'monitored',
      name: '🟡 Monitored Zone',
      description: 'Medium sensitivity, monitored access',
      threshold: '31-60',
      color: 'bg-yellow-50 border-yellow-300',
      files: files.filter(f => f.zone === 'monitored')
    },
    {
      id: 'crypto_vault',
      name: '🔴 Crypto Vault',
      description: 'High sensitivity, encrypted storage',
      threshold: '61-80',
      color: 'bg-red-50 border-red-300',
      files: files.filter(f => f.zone === 'crypto_vault')
    },
    {
      id: 'cold_storage',
      name: '🧊 Cold Storage',
      description: 'Critical files, maximum security',
      threshold: '81-100',
      color: 'bg-blue-50 border-blue-300',
      files: files.filter(f => f.zone === 'cold_storage')
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">File Zones</h2>
        <p className="text-gray-600">
          Files are automatically organized into zones based on their sensitivity scores
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {zones.map((zone) => (
          <div
            key={zone.id}
            className={`${zone.color} border-2 rounded-lg p-6`}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {zone.name}
                </h3>
                <p className="text-sm text-gray-600 mb-2">{zone.description}</p>
                <p className="text-xs text-gray-500">Sensitivity: {zone.threshold}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">
                  {zone.files.length}
                </div>
                <div className="text-xs text-gray-600">files</div>
              </div>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {zone.files.length === 0 ? (
                <div className="text-center py-4 text-gray-500 text-sm">
                  No files in this zone
                </div>
              ) : (
                zone.files.map((file) => (
                  <div
                    key={file.file_id}
                    className="bg-white rounded p-3 border border-gray-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.filename}
                        </p>
                        <div className="mt-1 flex items-center space-x-2 text-xs">
                          <span className="text-gray-500">
                            Score: {file.sensitivity_score}
                          </span>
                          {file.encryption_status === 'encrypted' && (
                            <span className="flex items-center text-red-600">
                              <Lock className="h-3 w-3 mr-1" />
                              Encrypted
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Statistics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Zone Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {zones.map((zone) => (
            <div key={zone.id} className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {zone.files.length}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {zone.name.split(' ').slice(1).join(' ')}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {files.length > 0
                  ? `${((zone.files.length / files.length) * 100).toFixed(1)}%`
                  : '0%'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

