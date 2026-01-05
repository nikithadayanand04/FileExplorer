'use client'

import { useState, useEffect } from 'react'
import { FileMetadata, FileExplanation } from '@/types'
import { X, Lock, Shield, Info, AlertCircle } from 'lucide-react'

interface FileDetailsProps {
  file: FileMetadata
  onClose: () => void
}

export default function FileDetails({ file, onClose }: FileDetailsProps) {
  const [explanations, setExplanations] = useState<FileExplanation | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchExplanations()
  }, [file.file_id])

  const fetchExplanations = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/files/${file.file_id}/explain`,
        {
          headers: {
            'X-User-ID': 'demo_user'
          }
        }
      )
      const data = await response.json()
      setExplanations(data.explanations)
    } catch (error) {
      console.error('Error fetching explanations:', error)
    } finally {
      setLoading(false)
    }
  }

  const getZoneDisplay = (zone: string) => {
    const zones: Record<string, string> = {
      public: '🟢 Public Zone',
      monitored: '🟡 Monitored Zone',
      crypto_vault: '🔴 Crypto Vault',
      cold_storage: '🧊 Cold Storage'
    }
    return zones[zone] || zone
  }

  return (
    <div className="bg-white rounded-lg shadow-lg h-fit sticky top-4">
      <div className="p-4 border-b flex items-center justify-between">
        <h3 className="text-lg font-semibold">File Details</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="p-4 space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto">
        {/* Basic Info */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2">File Information</h4>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-500">Name:</span>{' '}
              <span className="font-medium">{file.filename}</span>
            </div>
            <div>
              <span className="text-gray-500">Size:</span>{' '}
              <span className="font-medium">
                {(file.file_size / 1024).toFixed(2)} KB
              </span>
            </div>
            <div>
              <span className="text-gray-500">Type:</span>{' '}
              <span className="font-medium">{file.mime_type}</span>
            </div>
            <div>
              <span className="text-gray-500">Zone:</span>{' '}
              <span className="font-medium">{getZoneDisplay(file.zone)}</span>
            </div>
          </div>
        </div>

        {/* Sensitivity Score */}
        <div className="border-t pt-4">
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <Shield className="h-4 w-4 mr-2" />
            Sensitivity Analysis
          </h4>
          <div className="space-y-2">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600">Score</span>
                <span className="text-sm font-semibold">{file.sensitivity_score}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    file.sensitivity_score >= 81
                      ? 'bg-red-600'
                      : file.sensitivity_score >= 61
                      ? 'bg-orange-600'
                      : file.sensitivity_score >= 31
                      ? 'bg-yellow-600'
                      : 'bg-green-600'
                  }`}
                  style={{ width: `${file.sensitivity_score}%` }}
                />
              </div>
            </div>
            <div>
              <span className="text-sm text-gray-600">Level:</span>{' '}
              <span className="text-sm font-medium">{file.sensitivity_level}</span>
            </div>
            {file.ai_confidence && (
              <div>
                <span className="text-sm text-gray-600">AI Confidence:</span>{' '}
                <span className="text-sm font-medium">
                  {(file.ai_confidence * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Encryption Status */}
        <div className="border-t pt-4">
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <Lock className="h-4 w-4 mr-2" />
            Encryption Status
          </h4>
          <div className="flex items-center space-x-2">
            {file.encryption_status === 'encrypted' ? (
              <>
                <Lock className="h-4 w-4 text-red-600" />
                <span className="text-sm text-red-600 font-medium">Encrypted</span>
              </>
            ) : (
              <>
                <Lock className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">Unencrypted</span>
              </>
            )}
          </div>
        </div>

        {/* Detected Entities */}
        {file.detected_entities.length > 0 && (
          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-2">Detected Entities</h4>
            <div className="flex flex-wrap gap-2">
              {file.detected_entities.map((entity, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded"
                >
                  {entity}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* AI Explanations */}
        {loading ? (
          <div className="border-t pt-4">
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          </div>
        ) : explanations ? (
          <div className="border-t pt-4 space-y-4">
            <h4 className="font-medium text-gray-900 mb-2 flex items-center">
              <Info className="h-4 w-4 mr-2" />
              AI Explanations
            </h4>

            {/* Classification Explanation */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <h5 className="font-medium text-sm text-blue-900 mb-2">
                Why was this file classified as {explanations.classification.classification}?
              </h5>
              <p className="text-sm text-blue-800 whitespace-pre-line">
                {explanations.classification.full_explanation}
              </p>
            </div>

            {/* Encryption Explanation */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              <h5 className="font-medium text-sm text-purple-900 mb-2">
                Why is this file {file.encryption_status === 'encrypted' ? 'encrypted' : 'not encrypted'}?
              </h5>
              <p className="text-sm text-purple-800 whitespace-pre-line">
                {explanations.encryption.full_explanation}
              </p>
            </div>

            {/* Zone Explanation */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <h5 className="font-medium text-sm text-green-900 mb-2">
                Why was this file assigned to {explanations.zone.zone_display}?
              </h5>
              <p className="text-sm text-green-800 whitespace-pre-line">
                {explanations.zone.full_explanation}
              </p>
            </div>
          </div>
        ) : (
          <div className="border-t pt-4">
            <div className="flex items-center text-sm text-gray-500">
              <AlertCircle className="h-4 w-4 mr-2" />
              Unable to load explanations
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

