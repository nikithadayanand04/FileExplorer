# Sample Test Files

These files are provided for testing CryptoFS++ classification and encryption features.

## Files

1. **test_pii.txt** - Contains PII (Aadhaar, PAN, credit card, bank details)
   - Expected: HIGH/CRITICAL sensitivity, Crypto Vault/Cold Storage, Encrypted

2. **test_credentials.txt** - Contains API keys, passwords, tokens
   - Expected: HIGH sensitivity, Crypto Vault, Encrypted

3. **test_medical.txt** - Contains medical/healthcare information
   - Expected: MEDIUM/HIGH sensitivity, Monitored/Crypto Vault

4. **test_normal.txt** - Regular document with no sensitive content
   - Expected: LOW sensitivity, Public Zone, Unencrypted

## Usage

Upload these files through the CryptoFS++ web interface to test:
- AI classification accuracy
- Sensitivity scoring
- Zone assignment
- Encryption policies
- Explainable AI explanations

## Expected Results

Each file should demonstrate different classification behaviors:
- PII files → High scores, encryption, restricted zones
- Credential files → High scores, encryption, Crypto Vault
- Medical files → Medium-High scores, monitored/encrypted
- Normal files → Low scores, public zone, no encryption

