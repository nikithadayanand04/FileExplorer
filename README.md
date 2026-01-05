# CryptoFS++: AI-Governed, Blockchain-Audited Virtual File System

## 🎯 Project Overview

CryptoFS++ is a production-quality, research-grade intelligent file explorer that combines AI-powered content classification, autonomous encryption, blockchain-backed audit logging, and explainable AI decision-making in a zero-trust architecture.

## 🏗️ System Architecture

### Core Components

1. **Frontend (Next.js/React)**: Modern file explorer UI with zone visualization, drag & drop, and real-time AI insights
2. **Backend (FastAPI)**: Modular microservices architecture with typed schemas and async processing
3. **AI Intelligence Layer**: Multi-modal content analysis (text + images) with explainable classifications
4. **Autonomous Encryption Engine**: Policy-based encryption decisions with transparent key management
5. **Blockchain Audit Layer**: Immutable event logging for all file operations and access attempts
6. **Zero-Trust Access Control**: AI-enhanced behavioral analysis with dynamic permission enforcement

### File Zones

- 🟢 **Public Zone**: Low sensitivity, unencrypted files
- 🟡 **Monitored Zone**: Medium sensitivity, monitored access
- 🔴 **Crypto Vault**: High sensitivity, encrypted storage
- 🧊 **Cold Storage**: Critical files, maximum security

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `.env` files in backend and frontend directories with necessary configuration.

## 🧠 AI Classification Logic

### Text Analysis
- PII Detection: Aadhaar, PAN, SSN patterns
- Credential Detection: API keys, passwords, high-entropy strings
- Financial Data: Credit cards, bank account numbers
- Medical Terms: HIPAA-relevant content

### Image Analysis
- Face Detection: OpenCV/MediaPipe
- ID Card Recognition: Document structure analysis
- Sensitive Content: Screenshots with OTPs/QR codes

### Sensitivity Scoring (0-100)
- 0-30: LOW → Public Zone
- 31-60: MEDIUM → Monitored Zone
- 61-80: HIGH → Crypto Vault
- 81-100: CRITICAL → Cold Storage

## 🔐 Security Model

- **Encryption**: AES-256 per-file encryption with unique keys
- **Key Management**: Secure key derivation and storage (simulated for demo)
- **Access Control**: Role-based with behavioral anomaly detection
- **Audit Trail**: Blockchain-backed immutable logging

## ⛓️ Blockchain Integration

Uses a lightweight simulated blockchain ledger for audit events:
- File hash recording
- Encryption/decryption events
- Access attempts and results
- Permission changes
- Zone transitions

## 📊 Explainable AI

Every decision includes:
- Human-readable reasoning
- Detected entities and patterns
- Confidence scores
- Policy rule triggers

## 🧪 Advanced Features

- Live reclassification on file edits
- Semantic search ("Show files with credentials")
- Breach simulation mode
- User preference learning

## 📁 Project Structure

```
cryptofs-plusplus/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── api/
│   │   │   └── routes.py        # REST API endpoints
│   │   ├── services/            # Core business logic services
│   │   │   ├── file_ingestion.py
│   │   │   ├── content_analysis.py
│   │   │   ├── sensitivity_scoring.py
│   │   │   ├── encryption_service.py
│   │   │   ├── policy_engine.py
│   │   │   ├── blockchain_logger.py
│   │   │   └── access_control.py
│   │   ├── ai/                  # AI intelligence layer
│   │   │   ├── text_analyzer.py
│   │   │   ├── image_analyzer.py
│   │   │   └── explainability.py
│   │   └── models/              # Data models
│   │       ├── file.py
│   │       ├── user.py
│   │       └── audit.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app directory
│   │   ├── components/          # React components
│   │   │   ├── FileExplorer.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── FileDetails.tsx
│   │   │   ├── ZoneVisualization.tsx
│   │   │   └── BlockchainViewer.tsx
│   │   └── types/               # TypeScript types
│   └── package.json
└── README.md
```

## 🧠 AI Logic & Classification Details

### Text Analysis Pipeline

The text analyzer uses a hybrid approach combining regex patterns and ML-based classification:

1. **Pattern Matching**: Detects structured data patterns (Aadhaar, PAN, SSN, credit cards)
2. **Entity Detection**: Identifies credentials, API keys, passwords using pattern recognition
3. **Medical Term Detection**: Scans for healthcare-related terminology
4. **High-Entropy Detection**: Identifies random-looking credential strings

**Scoring Algorithm**:
- Each detected entity type has a weight (e.g., Aadhaar: 25, API key: 30)
- Scores are cumulative with diminishing returns for duplicate types
- Maximum score capped at 100

### Image Analysis Pipeline

1. **Face Detection**: Uses OpenCV Haar Cascades and MediaPipe for face recognition
2. **ID Card Detection**: Analyzes document structure using edge detection and contour analysis
3. **Screenshot Detection**: Identifies QR codes and OTP patterns through high-frequency edge analysis
4. **Text Region Detection**: Locates text content in images using morphological operations

**Scoring Algorithm**:
- Face detection: +30 points
- ID card detection: +40 points
- Sensitive screenshots: +35 points
- Text content: +15 points

### Combined Scoring

- Takes maximum of text and image scores
- Adds bonus (+10) if both modalities detect sensitive content
- Final score determines zone assignment and encryption policy

## 🔐 Security Model & Architecture

### Encryption Architecture

1. **Key Generation**: 
   - Per-file unique keys using PBKDF2-HMAC-SHA256
   - File-specific salt derived from file ID
   - 100,000 iterations for key derivation

2. **Encryption Process**:
   - AES-256-CBC encryption
   - Random IV per file (prepended to ciphertext)
   - PKCS7 padding for block alignment

3. **Key Management**:
   - Keys derived deterministically (no storage needed)
   - Master secret stored in environment variables
   - Key IDs stored in metadata for tracking

### Access Control Model

**Zero-Trust Principles**:
- No implicit trust based on authentication alone
- Every access request evaluated independently
- Behavioral anomaly detection
- Dynamic permission adjustment

**Role-Based Access Control (RBAC)**:
- **Admin**: Full access to all files
- **User**: Read/Write access to LOW-MEDIUM files
- **Viewer**: Read-only access to LOW-MEDIUM files
- **Guest**: No access (for demo purposes)

**Behavioral Analysis**:
- Access frequency monitoring
- Failed attempt tracking
- IP address consistency checks
- Unusual time access detection
- Rapid file switching detection

### Blockchain Audit Architecture

**Block Structure**:
- Index: Sequential block number
- Timestamp: Block creation time
- Events: Array of audit events
- Previous Hash: Link to previous block
- Hash: SHA-256 hash of block contents

**Event Types**:
- `FILE_UPLOAD`: File ingestion events
- `ENCRYPTION`: Encryption/decryption operations
- `ACCESS`: Access attempts (READ, WRITE, DELETE, MOVE)
- `ZONE_TRANSITION`: File zone changes
- `PERMISSION_CHANGE`: Access control modifications

**Integrity Verification**:
- Chain validation checks previous hash links
- Block hash verification ensures immutability
- Event ordering preserved through block structure

## 🎯 Policy Engine

### Encryption Policies

1. **Sensitivity Threshold**: Files with score > 70 automatically encrypted
2. **Always Encrypt Entities**: Face, ID card, API keys, passwords, PII patterns
3. **Classification-Based**: CRITICAL and HIGH classifications trigger encryption

### Zone Assignment Policies

- **Public Zone** (0-30): Unencrypted, accessible to all roles
- **Monitored Zone** (31-60): Unencrypted but access logged
- **Crypto Vault** (61-80): Encrypted, restricted access
- **Cold Storage** (81-100): Encrypted, admin-only access

### Access Control Policies

- Role-based permissions matrix
- Sensitivity-based restrictions
- Behavioral flag evaluation
- Automatic blocking on suspicious patterns

## 🚀 Demo Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Step 1: Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file (optional, defaults provided)
cp .env.example .env

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### Step 2: Frontend Setup

```bash
cd frontend
npm install

# Create .env.local file (optional)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 3: Testing the System

1. **Upload Test Files**:
   - Upload a text file containing "1234 5678 9012" (Aadhaar pattern)
   - Upload an image with faces
   - Upload a file with API keys

2. **Observe Classifications**:
   - Check sensitivity scores
   - View detected entities
   - See zone assignments

3. **Review Explanations**:
   - Click on any file to see AI explanations
   - Understand why encryption was applied
   - View zone assignment rationale

4. **Explore Blockchain**:
   - Navigate to Blockchain Audit tab
   - View all events and blocks
   - Verify chain integrity

### Sample Test Files

**test_pii.txt**:
```
Name: John Doe
Aadhaar: 1234 5678 9012
PAN: ABCDE1234F
Email: john@example.com
```

**test_credentials.txt**:
```
API_KEY=sk_live_51HqJ8K2mN3pQ4rS5tU6vW7xY8zA9bC0dE1fG2hI3jK4lM5nO6pQ7rS8tU9vW0xY1zA2bC3dE4fG5h
Password: MySecureP@ssw0rd123
```

## 📊 API Endpoints

### File Operations
- `POST /api/v1/files/upload` - Upload and analyze file
- `GET /api/v1/files` - List all files
- `GET /api/v1/files/{file_id}` - Get file metadata
- `GET /api/v1/files/{file_id}/download` - Download file (decrypts if needed)
- `GET /api/v1/files/{file_id}/explain` - Get AI explanations

### Blockchain
- `GET /api/v1/blockchain/chain` - Get entire blockchain
- `GET /api/v1/blockchain/file/{file_id}` - Get file audit trail
- `GET /api/v1/blockchain/stats` - Get blockchain statistics

### Zones
- `GET /api/v1/zones` - Get zone information

## 🔬 Research & Academic Use

### Key Features for Research

1. **Explainable AI**: Every decision includes human-readable explanations
2. **Modular Architecture**: Clean separation of concerns for extensibility
3. **Blockchain Integration**: Immutable audit trail for trust verification
4. **Zero-Trust Model**: Advanced access control with behavioral analysis
5. **Multi-Modal AI**: Text and image analysis pipelines

### Potential Extensions

- Integration with real blockchain networks (Ethereum, Hyperledger)
- Advanced ML models for classification
- Real-time file monitoring and reclassification
- Distributed file storage
- Multi-user collaboration features
- Advanced semantic search

### Citation

If using this system for research, please cite:
```
CryptoFS++: AI-Governed, Blockchain-Audited Virtual File System
A production-quality intelligent file explorer with explainable AI
```

## 🐛 Troubleshooting

### Backend Issues

- **Import Errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
- **Port Already in Use**: Change port in `uvicorn` command
- **MediaPipe Not Available**: Face detection will fallback to OpenCV only

### Frontend Issues

- **API Connection Errors**: Verify backend is running on port 8000
- **Build Errors**: Clear `.next` directory and rebuild
- **Type Errors**: Ensure TypeScript dependencies are installed

## 📝 License

Research/Educational Use

## 🤝 Contributing

This is a research project. Contributions welcome for:
- Enhanced AI models
- Additional file type support
- UI/UX improvements
- Security enhancements
- Documentation improvements

