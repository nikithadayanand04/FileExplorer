'use client'

import { useState, useEffect } from 'react'
import { BlockchainBlock, BlockchainEvent } from '@/types'
import { Link, Clock, FileText, User, Shield } from 'lucide-react'
import { format } from 'date-fns'

export default function BlockchainViewer() {
  const [blocks, setBlocks] = useState<BlockchainBlock[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [selectedBlock, setSelectedBlock] = useState<BlockchainBlock | null>(null)

  useEffect(() => {
    fetchBlockchain()
    fetchStats()
  }, [])

  const fetchBlockchain = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/blockchain/chain`
      )
      const data = await response.json()
      setBlocks(data.blocks || [])
    } catch (error) {
      console.error('Error fetching blockchain:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/blockchain/stats`
      )
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'FILE_UPLOAD':
        return <FileText className="h-4 w-4" />
      case 'ACCESS':
        return <Shield className="h-4 w-4" />
      case 'ENCRYPTION':
        return <Shield className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getEventColor = (result: string) => {
    switch (result) {
      case 'ALLOWED':
      case 'SUCCESS':
        return 'text-green-600 bg-green-50'
      case 'DENIED':
      case 'FAILED':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Blockchain Audit Trail</h2>
        <p className="text-gray-600">
          Immutable record of all file operations and access attempts
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-2xl font-bold text-gray-900">{stats.total_blocks}</div>
            <div className="text-sm text-gray-600 mt-1">Total Blocks</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-2xl font-bold text-gray-900">{stats.total_events}</div>
            <div className="text-sm text-gray-600 mt-1">Total Events</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-2xl font-bold text-gray-900">{stats.pending_events}</div>
            <div className="text-sm text-gray-600 mt-1">Pending Events</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className={`text-sm font-medium ${stats.chain_valid ? 'text-green-600' : 'text-red-600'}`}>
              {stats.chain_valid ? '✓ Valid' : '✗ Invalid'}
            </div>
            <div className="text-sm text-gray-600 mt-1">Chain Integrity</div>
          </div>
        </div>
      )}

      {/* Blockchain Blocks */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Blockchain Blocks</h3>
        </div>
        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading blockchain...</p>
          </div>
        ) : blocks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Link className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p>No blocks yet</p>
            <p className="text-sm mt-2">Upload files to see blockchain events</p>
          </div>
        ) : (
          <div className="divide-y">
            {blocks.map((block, idx) => (
              <div
                key={block.index}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  selectedBlock?.index === block.index ? 'bg-blue-50' : ''
                }`}
                onClick={() => setSelectedBlock(block)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="mt-1">
                      {idx === 0 ? (
                        <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-green-600">G</span>
                        </div>
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-xs font-bold text-blue-600">{block.index}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="font-medium text-gray-900">
                          {idx === 0 ? 'Genesis Block' : `Block #${block.index}`}
                        </h4>
                        <span className="text-xs text-gray-500">
                          {format(new Date(block.timestamp), 'MMM d, yyyy HH:mm:ss')}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>{block.events.length} event(s)</span>
                        <span className="font-mono text-xs">
                          Hash: {block.hash.substring(0, 16)}...
                        </span>
                      </div>
                      {block.events.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {block.events.slice(0, 3).map((event, eventIdx) => (
                            <div
                              key={eventIdx}
                              className="flex items-center space-x-2 text-xs"
                            >
                              {getEventIcon(event.event_type)}
                              <span className="text-gray-700">{event.action}</span>
                              <span
                                className={`px-2 py-0.5 rounded ${getEventColor(
                                  event.result
                                )}`}
                              >
                                {event.result}
                              </span>
                            </div>
                          ))}
                          {block.events.length > 3 && (
                            <div className="text-xs text-gray-500">
                              +{block.events.length - 3} more events
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Block Details Modal */}
      {selectedBlock && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                {selectedBlock.index === 0 ? 'Genesis Block' : `Block #${selectedBlock.index}`}
              </h3>
              <button
                onClick={() => setSelectedBlock(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Block Information</h4>
                <div className="space-y-1 text-sm">
                  <div>
                    <span className="text-gray-500">Index:</span>{' '}
                    <span className="font-mono">{selectedBlock.index}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Timestamp:</span>{' '}
                    <span>{format(new Date(selectedBlock.timestamp), 'PPpp')}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Hash:</span>{' '}
                    <span className="font-mono text-xs break-all">{selectedBlock.hash}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Previous Hash:</span>{' '}
                    <span className="font-mono text-xs break-all">
                      {selectedBlock.previous_hash}
                    </span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">
                  Events ({selectedBlock.events.length})
                </h4>
                <div className="space-y-2">
                  {selectedBlock.events.map((event, idx) => (
                    <div
                      key={idx}
                      className="border rounded-lg p-3 bg-gray-50"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getEventIcon(event.event_type)}
                          <span className="font-medium text-sm">{event.event_type}</span>
                        </div>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${getEventColor(
                            event.result
                          )}`}
                        >
                          {event.result}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 space-y-1">
                        <div>
                          <span className="font-medium">Action:</span> {event.action}
                        </div>
                        {event.file_id && (
                          <div>
                            <span className="font-medium">File ID:</span>{' '}
                            <span className="font-mono">{event.file_id.substring(0, 8)}...</span>
                          </div>
                        )}
                        {event.user_id && (
                          <div>
                            <span className="font-medium">User:</span> {event.user_id}
                          </div>
                        )}
                        {event.metadata && Object.keys(event.metadata).length > 0 && (
                          <div>
                            <span className="font-medium">Metadata:</span>{' '}
                            <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-x-auto">
                              {JSON.stringify(event.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

