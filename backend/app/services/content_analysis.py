"""
Content analysis service for CryptoFS++.
Orchestrates AI analysis of file content (text and images).
"""
from typing import Dict, Any
import mimetypes

from app.ai.text_analyzer import TextAnalyzer
from app.ai.image_analyzer import ImageAnalyzer
from app.models.file import FileContentAnalysis, SensitivityLevel

class ContentAnalysisService:
    """
    Service for analyzing file content using AI.
    Coordinates text and image analysis.
    """
    
    def __init__(self):
        """Initialize content analysis service."""
        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
    
    async def analyze_file(
        self,
        file_content: bytes,
        mime_type: str,
        file_id: str
    ) -> FileContentAnalysis:
        """
        Analyze file content for sensitive information.
        
        Args:
            file_content: Raw file bytes
            mime_type: MIME type of the file
            file_id: UUID of the file
            
        Returns:
            FileContentAnalysis object with results
        """
        text_results = {}
        image_results = {}
        all_detected_entities = []
        all_reasons = []
        
        # Determine file type and analyze accordingly
        if mime_type.startswith('text/') or mime_type in [
            'application/json',
            'application/xml',
            'application/pdf'  # Simplified: treat PDF as text
        ]:
            # Text analysis
            try:
                text_content = file_content.decode('utf-8', errors='ignore')
                text_results = self.text_analyzer.analyze(text_content)
                all_detected_entities.extend(text_results.get('detected_entities', []))
                all_reasons.extend(text_results.get('reasons', []))
            except Exception as e:
                text_results = {'error': str(e)}
        
        elif mime_type.startswith('image/'):
            # Image analysis
            try:
                image_results = self.image_analyzer.analyze(file_content, mime_type)
                all_detected_entities.extend(image_results.get('detected_entities', []))
                all_reasons.extend(image_results.get('reasons', []))
            except Exception as e:
                image_results = {'error': str(e)}
        
        # Combine results and calculate overall sensitivity
        sensitivity_score = self._combine_sensitivity_scores(text_results, image_results)
        classification = self._classify_sensitivity(sensitivity_score)
        
        # Calculate overall confidence
        text_confidence = text_results.get('confidence', 0.0)
        image_confidence = image_results.get('confidence', 0.0)
        overall_confidence = max(text_confidence, image_confidence)
        
        return FileContentAnalysis(
            file_id=file_id,
            text_analysis=text_results,
            image_analysis=image_results,
            detected_entities=list(set(all_detected_entities)),  # Remove duplicates
            sensitivity_score=sensitivity_score,
            classification=classification,
            reasons=all_reasons,
            confidence=overall_confidence
        )
    
    def _combine_sensitivity_scores(
        self,
        text_results: Dict[str, Any],
        image_results: Dict[str, Any]
    ) -> int:
        """Combine sensitivity scores from text and image analysis."""
        text_score = text_results.get('sensitivity_score', 0)
        image_score = image_results.get('sensitivity_score', 0)
        
        # Take maximum (most sensitive detection wins)
        combined_score = max(text_score, image_score)
        
        # If both detected something, add bonus
        if text_score > 0 and image_score > 0:
            combined_score = min(combined_score + 10, 100)
        
        return combined_score
    
    def _classify_sensitivity(self, score: int) -> SensitivityLevel:
        """Classify sensitivity level based on score."""
        if score >= 81:
            return SensitivityLevel.CRITICAL
        elif score >= 61:
            return SensitivityLevel.HIGH
        elif score >= 31:
            return SensitivityLevel.MEDIUM
        else:
            return SensitivityLevel.LOW

