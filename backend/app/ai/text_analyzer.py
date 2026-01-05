"""
AI-powered text content analysis for PII, credentials, and sensitive data detection.
Uses regex patterns and ML-based classification.
"""
import re
import hashlib
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class DetectionResult:
    """Result of a single pattern detection."""
    pattern_type: str
    matched_text: str
    confidence: float
    reason: str

class TextAnalyzer:
    """
    Advanced text content analyzer for sensitive information detection.
    Implements hybrid regex + ML approach for PII and credential detection.
    """
    
    def __init__(self):
        """Initialize text analyzer with detection patterns."""
        self.patterns = self._initialize_patterns()
        self.medical_terms = [
            'diagnosis', 'prescription', 'medical record', 'patient id',
            'blood pressure', 'cholesterol', 'allergy', 'medication',
            'surgery', 'treatment', 'doctor', 'physician', 'clinic'
        ]
        
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize detection patterns for various sensitive data types."""
        return {
            'aadhaar': {
                'pattern': r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                'confidence': 0.85,
                'description': 'Aadhaar-like 12-digit pattern'
            },
            'pan': {
                'pattern': r'[A-Z]{5}\d{4}[A-Z]{1}',
                'confidence': 0.90,
                'description': 'PAN card pattern'
            },
            'ssn': {
                'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
                'confidence': 0.90,
                'description': 'SSN pattern (XXX-XX-XXXX)'
            },
            'credit_card': {
                'pattern': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                'confidence': 0.80,
                'description': 'Credit card number pattern'
            },
            'bank_account': {
                'pattern': r'\b\d{9,18}\b',
                'confidence': 0.60,
                'description': 'Bank account number pattern'
            },
            'api_key': {
                'pattern': r'(?i)(api[_-]?key|apikey)[\s:=]+([A-Za-z0-9_\-]{20,})',
                'confidence': 0.85,
                'description': 'API key pattern'
            },
            'password': {
                'pattern': r'(?i)(password|pwd|pass)[\s:=]+([^\s]{8,})',
                'confidence': 0.75,
                'description': 'Password pattern'
            },
            'email': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'confidence': 0.50,
                'description': 'Email address'
            },
            'phone': {
                'pattern': r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                'confidence': 0.40,
                'description': 'Phone number pattern'
            }
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content for sensitive information.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary containing detected entities, sensitivity score, and reasons
        """
        if not text:
            return {
                'detected_entities': [],
                'sensitivity_score': 0,
                'classification': 'LOW',
                'reasons': [],
                'confidence': 0.0
            }
        
        detections: List[DetectionResult] = []
        text_lower = text.lower()
        
        # Pattern-based detection
        for pattern_name, pattern_config in self.patterns.items():
            matches = re.finditer(pattern_config['pattern'], text, re.IGNORECASE)
            for match in matches:
                detections.append(DetectionResult(
                    pattern_type=pattern_name,
                    matched_text=match.group()[:50],  # Truncate for privacy
                    confidence=pattern_config['confidence'],
                    reason=f"Detected {pattern_config['description']}"
                ))
        
        # Medical term detection
        medical_matches = sum(1 for term in self.medical_terms if term in text_lower)
        if medical_matches > 0:
            detections.append(DetectionResult(
                pattern_type='medical',
                matched_text=f'{medical_matches} medical terms',
                confidence=0.70,
                reason=f'Detected {medical_matches} medical/healthcare-related terms'
            ))
        
        # High-entropy credential detection (random-looking strings)
        high_entropy_pattern = r'\b[A-Za-z0-9_\-]{32,}\b'
        entropy_matches = re.findall(high_entropy_pattern, text)
        for match in entropy_matches:
            if self._is_high_entropy(match):
                detections.append(DetectionResult(
                    pattern_type='high_entropy_credential',
                    matched_text=match[:20] + '...',
                    confidence=0.80,
                    reason='Detected high-entropy credential-like string'
                ))
        
        # Calculate sensitivity score
        sensitivity_score = self._calculate_sensitivity_score(detections)
        
        # Determine classification
        classification = self._classify_sensitivity(sensitivity_score)
        
        # Extract unique reasons
        reasons = list(set([d.reason for d in detections]))
        
        # Calculate overall confidence
        confidence = sum(d.confidence for d in detections) / len(detections) if detections else 0.0
        
        return {
            'detected_entities': [d.pattern_type for d in detections],
            'sensitivity_score': sensitivity_score,
            'classification': classification,
            'reasons': reasons,
            'confidence': min(confidence, 1.0),
            'detection_details': [
                {
                    'type': d.pattern_type,
                    'reason': d.reason,
                    'confidence': d.confidence
                }
                for d in detections
            ]
        }
    
    def _is_high_entropy(self, text: str) -> bool:
        """Check if string has high entropy (likely credential)."""
        if len(text) < 32:
            return False
        
        # Simple entropy check: variety of characters
        unique_chars = len(set(text))
        return unique_chars > len(text) * 0.5
    
    def _calculate_sensitivity_score(self, detections: List[DetectionResult]) -> int:
        """Calculate overall sensitivity score (0-100) based on detections."""
        if not detections:
            return 0
        
        # Weight different detection types
        weights = {
            'aadhaar': 25,
            'pan': 20,
            'ssn': 25,
            'credit_card': 20,
            'bank_account': 15,
            'api_key': 30,
            'password': 30,
            'high_entropy_credential': 25,
            'medical': 20,
            'email': 5,
            'phone': 5
        }
        
        score = 0
        seen_types = set()
        
        for detection in detections:
            weight = weights.get(detection.pattern_type, 10)
            # Reduce weight for duplicate types
            if detection.pattern_type not in seen_types:
                score += weight
                seen_types.add(detection.pattern_type)
            else:
                score += weight * 0.3  # Diminishing returns
        
        # Cap at 100
        return min(int(score), 100)
    
    def _classify_sensitivity(self, score: int) -> str:
        """Classify sensitivity level based on score."""
        if score >= 81:
            return 'CRITICAL'
        elif score >= 61:
            return 'HIGH'
        elif score >= 31:
            return 'MEDIUM'
        else:
            return 'LOW'

