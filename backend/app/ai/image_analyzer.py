"""
AI-powered image content analysis using OpenCV and MediaPipe.
Detects faces, ID cards, sensitive content, and screenshots.
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import base64

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: MediaPipe not available. Face detection will use OpenCV only.")

class ImageAnalyzer:
    """
    Advanced image content analyzer for sensitive information detection.
    Uses computer vision to detect faces, ID cards, and sensitive content.
    """
    
    def __init__(self):
        """Initialize image analyzer with detection models."""
        self.face_cascade = None
        self._initialize_models()
        
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5
            )
        else:
            self.face_detection = None
    
    def _initialize_models(self):
        """Initialize OpenCV cascade classifiers."""
        try:
            # Try to load face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"Warning: Could not load face cascade: {e}")
            self.face_cascade = None
    
    def analyze(self, image_data: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Analyze image content for sensitive information.
        
        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image
            
        Returns:
            Dictionary containing detected entities, sensitivity score, and reasons
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    'detected_entities': [],
                    'sensitivity_score': 0,
                    'classification': 'LOW',
                    'reasons': [],
                    'confidence': 0.0
                }
            
            detections = []
            reasons = []
            
            # Face detection
            face_count = self._detect_faces(image)
            if face_count > 0:
                detections.append('face')
                reasons.append(f'Detected {face_count} human face(s) in image')
            
            # ID card detection
            is_id_card = self._detect_id_card(image)
            if is_id_card:
                detections.append('id_card')
                reasons.append('Detected ID card or document structure')
            
            # Screenshot/OTP detection
            has_otp_qr = self._detect_sensitive_screenshots(image)
            if has_otp_qr:
                detections.append('sensitive_screenshot')
                reasons.append('Detected screenshot with potential OTP or QR code')
            
            # Text detection (OCR-like, simplified)
            has_text = self._detect_text_regions(image)
            if has_text:
                detections.append('text_content')
                reasons.append('Detected text content in image')
            
            # Calculate sensitivity score
            sensitivity_score = self._calculate_sensitivity_score(detections)
            classification = self._classify_sensitivity(sensitivity_score)
            
            # Calculate confidence based on detection quality
            confidence = min(0.7 + (len(detections) * 0.1), 0.95) if detections else 0.0
            
            return {
                'detected_entities': detections,
                'sensitivity_score': sensitivity_score,
                'classification': classification,
                'reasons': reasons,
                'confidence': confidence,
                'face_count': face_count,
                'is_id_card': is_id_card,
                'has_text': has_text
            }
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {
                'detected_entities': [],
                'sensitivity_score': 0,
                'classification': 'LOW',
                'reasons': [f'Analysis error: {str(e)}'],
                'confidence': 0.0
            }
    
    def _detect_faces(self, image: np.ndarray) -> int:
        """Detect faces in image using OpenCV and/or MediaPipe."""
        face_count = 0
        
        # Try MediaPipe first (more accurate)
        if self.face_detection is not None:
            try:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(rgb_image)
                if results.detections:
                    face_count = len(results.detections)
            except Exception as e:
                print(f"MediaPipe face detection error: {e}")
        
        # Fallback to OpenCV
        if face_count == 0 and self.face_cascade is not None:
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                face_count = len(faces)
            except Exception as e:
                print(f"OpenCV face detection error: {e}")
        
        return face_count
    
    def _detect_id_card(self, image: np.ndarray) -> bool:
        """
        Detect ID card or document structure.
        Uses edge detection and contour analysis.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Look for rectangular contours (potential ID cards)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > image.shape[0] * image.shape[1] * 0.1:  # At least 10% of image
                    peri = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                    if len(approx) == 4:  # Rectangle
                        return True
        except Exception as e:
            print(f"ID card detection error: {e}")
        
        return False
    
    def _detect_sensitive_screenshots(self, image: np.ndarray) -> bool:
        """
        Detect screenshots with OTPs or QR codes.
        Simplified detection based on image characteristics.
        """
        try:
            # Check for QR code-like patterns (simplified)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for high contrast regions (potential QR codes or OTPs)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Count small square-like regions (potential QR code modules)
            square_count = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 10 < area < 1000:  # Small square regions
                    peri = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
                    if len(approx) == 4:
                        square_count += 1
            
            # If many small squares, might be QR code
            if square_count > 50:
                return True
            
            # Check for text-like regions (potential OTPs)
            # Simplified: look for high-frequency edges
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (image.shape[0] * image.shape[1])
            if edge_density > 0.15:  # High edge density suggests text
                return True
                
        except Exception as e:
            print(f"Screenshot detection error: {e}")
        
        return False
    
    def _detect_text_regions(self, image: np.ndarray) -> bool:
        """Detect if image contains text regions."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Look for horizontal lines (common in text)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            detected_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            
            # Count horizontal line regions
            contours, _ = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            text_region_count = len([c for c in contours if cv2.contourArea(c) > 100])
            
            return text_region_count > 5
        except Exception as e:
            print(f"Text detection error: {e}")
            return False
    
    def _calculate_sensitivity_score(self, detections: List[str]) -> int:
        """Calculate sensitivity score based on image detections."""
        if not detections:
            return 0
        
        weights = {
            'face': 30,
            'id_card': 40,
            'sensitive_screenshot': 35,
            'text_content': 15
        }
        
        score = sum(weights.get(detection, 10) for detection in detections)
        return min(score, 100)
    
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

