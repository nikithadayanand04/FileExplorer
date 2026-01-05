# CryptoFS++ Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites Check
```bash
python3 --version  # Should be 3.9+
node --version     # Should be 18+
npm --version      # Should be 8+
```

### Step 1: Backend (Terminal 1)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at `http://localhost:8000`

### Step 2: Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at `http://localhost:3000`

### Step 3: Test the System

1. **Open Browser**: Navigate to `http://localhost:3000`

2. **Upload Test File**: Create `test.txt` with content:
   ```
   Aadhaar: 1234 5678 9012
   PAN: ABCDE1234F
   API_KEY=sk_live_51HqJ8K2mN3pQ4rS5tU6vW7xY8zA9bC0dE1fG2hI3jK4lM5nO6pQ7rS8tU9vW0xY1zA2bC3dE4fG5h
   ```

3. **Observe Results**:
   - File should be classified as HIGH/CRITICAL
   - Assigned to Crypto Vault or Cold Storage
   - Automatically encrypted
   - See AI explanations

4. **Explore Features**:
   - Click file to see detailed explanations
   - Check "Zones" tab for zone visualization
   - View "Blockchain Audit" for event history

## 🧪 Test Scenarios

### Scenario 1: PII Detection
Upload a file containing:
- Aadhaar numbers (12 digits)
- PAN numbers
- SSN patterns

**Expected**: High sensitivity score, encryption, Crypto Vault zone

### Scenario 2: Credential Detection
Upload a file containing:
- API keys (long random strings)
- Passwords
- High-entropy strings

**Expected**: High sensitivity, encryption, restricted access

### Scenario 3: Image Analysis
Upload an image containing:
- Human faces
- ID card structure
- Text content

**Expected**: Face detection, ID card recognition, sensitivity scoring

### Scenario 4: Low Sensitivity
Upload a regular document with no sensitive data

**Expected**: Low score, Public Zone, no encryption

## 📊 Understanding the UI

### File Explorer Tab
- List of all uploaded files
- Zone indicators (🟢🟡🔴🧊)
- Sensitivity scores
- Encryption status
- Click file for details

### Zones Tab
- Visual representation of file zones
- File counts per zone
- Zone statistics

### Blockchain Audit Tab
- Immutable event log
- Block structure visualization
- Event details
- Chain integrity verification

## 🔍 Key Features to Demo

1. **AI Classification**: Upload files and see automatic classification
2. **Explainable AI**: Click "Why is this encrypted?" to see reasoning
3. **Autonomous Encryption**: Files encrypted automatically based on policy
4. **Blockchain Audit**: View immutable audit trail
5. **Zero-Trust Access**: Access control with behavioral analysis
6. **Zone Visualization**: See files organized by sensitivity

## 🐛 Troubleshooting

**Backend won't start**:
- Check Python version: `python3 --version`
- Verify dependencies: `pip list`
- Check port 8000 is available

**Frontend won't start**:
- Check Node version: `node --version`
- Clear cache: `rm -rf node_modules .next && npm install`
- Check port 3000 is available

**API connection errors**:
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`

**File upload fails**:
- Check file size (max 100MB)
- Verify backend uploads directory exists
- Check backend logs for errors

## 📝 Next Steps

1. Explore the codebase structure
2. Read the comprehensive README.md
3. Experiment with different file types
4. Review blockchain events
5. Test access control policies

## 🎓 For Research/Demo

- Document your findings
- Capture screenshots of classifications
- Record blockchain audit trails
- Explain AI decision-making process
- Demonstrate zero-trust access control

Happy exploring! 🚀

