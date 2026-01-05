export interface FileMetadata {
  file_id: string
  filename: string
  file_size: number
  mime_type: string
  uploaded_at: string
  zone: 'public' | 'monitored' | 'crypto_vault' | 'cold_storage'
  sensitivity_score: number
  sensitivity_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  encryption_status: 'unencrypted' | 'encrypted' | 'pending'
  detected_entities: string[]
  classification_reasons?: string[]
  ai_confidence?: number
}

export interface FileExplanation {
  classification: {
    summary: string
    full_explanation: string
    detected_entities: string[]
    reasons: string[]
    confidence: number
    sensitivity_score: number
    classification: string
    recommended_zone: string
  }
  encryption: {
    encrypted: boolean
    summary: string
    full_explanation: string
    policy_rule: string
    reasons: string[]
    sensitivity_score: number
  }
  zone: {
    zone: string
    zone_display: string
    summary: string
    full_explanation: string
    sensitivity_score: number
    reasons: string[]
  }
}

export interface BlockchainEvent {
  event_id: string
  event_type: string
  file_id?: string
  user_id?: string
  action: string
  result: string
  timestamp: string
  metadata?: Record<string, any>
  block_hash?: string
  block_index?: number
}

export interface BlockchainBlock {
  index: number
  timestamp: string
  events: BlockchainEvent[]
  hash: string
  previous_hash: string
}

