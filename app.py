"""
Enhanced Medical Report Simplifier API
- Advanced text extraction from multiple file types
- Improved medical term recognition and explanation
- Enhanced status indicators with risk levels
- Detailed actionable recommendations
- Better error handling and logging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import re
import logging
import json
from datetime import datetime
import PyPDF2
from PIL import Image
import pytesseract
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class EnhancedMedicalReportSimplifier:
    def __init__(self):
        self.medical_terms = {
            # Blood Tests - Complete Blood Count
            'hemoglobin': {'term': 'Hemoglobin', 'description': 'Protein in red blood cells that carries oxygen throughout your body'},
            'wbc': {'term': 'White Blood Cells', 'description': 'Cells that fight infection and diseases'},
            'rbc': {'term': 'Red Blood Cells', 'description': 'Cells that carry oxygen from your lungs to the rest of your body'},
            'platelets': {'term': 'Platelets', 'description': 'Tiny blood cells that help your body form clots to stop bleeding'},
            'hematocrit': {'term': 'Hematocrit', 'description': 'Percentage of red blood cells in your blood'},
            'mcv': {'term': 'Mean Corpuscular Volume', 'description': 'Average size of your red blood cells'},
            
            # Metabolic Panel
            'glucose': {'term': 'Blood Sugar', 'description': 'Amount of sugar in your blood'},
            'creatinine': {'term': 'Creatinine', 'description': 'Waste product from muscle activity, filtered by kidneys'},
            'bun': {'term': 'Blood Urea Nitrogen', 'description': 'Measure of kidney function and protein metabolism'},
            'sodium': {'term': 'Sodium', 'description': 'Electrolyte that helps control fluid balance and nerve function'},
            'potassium': {'term': 'Potassium', 'description': 'Electrolyte important for heart and muscle function'},
            'chloride': {'term': 'Chloride', 'description': 'Electrolyte that helps maintain fluid balance'},
            'calcium': {'term': 'Calcium', 'description': 'Mineral essential for bones, teeth, and nerve function'},
            'egfr': {'term': 'Estimated Glomerular Filtration Rate', 'description': 'Measure of how well your kidneys are filtering waste'},
            
            # Liver Function
            'alt': {'term': 'ALT (Liver Enzyme)', 'description': 'Enzyme that indicates liver health and potential damage'},
            'ast': {'term': 'AST (Liver Enzyme)', 'description': 'Enzyme found in liver, heart, and muscles'},
            'alkaline phosphatase': {'term': 'Alkaline Phosphatase', 'description': 'Enzyme related to liver and bone health'},
            'bilirubin': {'term': 'Bilirubin', 'description': 'Substance produced when red blood cells break down'},
            'albumin': {'term': 'Albumin', 'description': 'Protein made by your liver that keeps fluid in your bloodstream'},
            
            # Cardiac/Lipid Panel
            'cholesterol': {'term': 'Total Cholesterol', 'description': 'Total amount of cholesterol in your blood'},
            'ldl': {'term': 'LDL (Bad Cholesterol)', 'description': 'Cholesterol that can build up in arteries'},
            'hdl': {'term': 'HDL (Good Cholesterol)', 'description': 'Cholesterol that helps remove bad cholesterol'},
            'triglycerides': {'term': 'Triglycerides', 'description': 'Type of fat stored in fat cells for energy'},
            
            # Thyroid Function
            'tsh': {'term': 'TSH (Thyroid Stimulating Hormone)', 'description': 'Hormone that controls thyroid function'},
            't4': {'term': 'Thyroxine (T4)', 'description': 'Main hormone produced by thyroid gland'},
            't3': {'term': 'Triiodothyronine (T3)', 'description': 'Active thyroid hormone'},
            
            # Other Important Tests
            'hba1c': {'term': 'HbA1c (Average Blood Sugar)', 'description': 'Average blood sugar level over past 3 months'},
            'vitamin d': {'term': 'Vitamin D', 'description': 'Vitamin important for bone health and immunity'},
            'iron': {'term': 'Iron', 'description': 'Mineral needed for red blood cell production'},
            'ferritin': {'term': 'Ferritin', 'description': 'Protein that stores iron in your body'},
            'psa': {'term': 'PSA (Prostate Specific Antigen)', 'description': 'Protein produced by prostate cells'},
            'inr': {'term': 'INR (Blood Clotting)', 'description': 'Measure of how long it takes blood to clot'},
        }
        
        self.normal_ranges = {
            'hemoglobin': {'male': (13.8, 17.2), 'female': (12.1, 15.1), 'units': 'g/dL'},
            'wbc': {'range': (4.5, 11.0), 'units': 'x10^9/L'},
            'rbc': {'male': (4.5, 5.9), 'female': (4.1, 5.1), 'units': 'x10^12/L'},
            'platelets': {'range': (150, 450), 'units': 'x10^9/L'},
            'glucose': {'range': (70, 100), 'units': 'mg/dL'},
            'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1), 'units': 'mg/dL'},
            'sodium': {'range': (135, 145), 'units': 'mmol/L'},
            'potassium': {'range': (3.5, 5.1), 'units': 'mmol/L'},
            'ldl': {'range': (0, 100), 'units': 'mg/dL'},
            'hdl': {'range': (40, 60), 'units': 'mg/dL'},
            'hba1c': {'range': (4.0, 5.6), 'units': '%'},
        }

    def extract_text_from_file(self, file_path, file_type):
        """Extract text from various file types with enhanced processing"""
        try:
            if file_type == 'text/plain':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    return file.read()
            
            elif file_type == 'application/pdf':
                return self._extract_text_from_pdf(file_path)
            
            elif file_type.startswith('image/'):
                return self._extract_text_from_image(file_path)
            
            else:
                return f"File type {file_type} detected. Please provide text content directly for best results."
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_type}: {e}")
            return ""

    def _extract_text_from_pdf(self, file_path):
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return "PDF content extraction failed. Please upload as text file."

    def _extract_text_from_image(self, file_path):
        """Extract text from image files using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return "Image text extraction failed. Please ensure image is clear and well-lit."

    def preprocess_text(self, text):
        """Enhanced text preprocessing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        corrections = {
            'rn': 'm',
            'l': '1',
            'O': '0',
            'o': '0',
            '|': '1'
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
            
        return text.strip()

    def detect_report_type(self, text):
        """Enhanced report type detection"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['hba1c', 'glucose', 'diabetes', 'glycemic']):
            return "diabetes"
        elif any(term in text_lower for term in ['cholesterol', 'ldl', 'hdl', 'triglycerides', 'lipid']):
            return "cardiac"
        elif any(term in text_lower for term in ['cbc', 'complete blood count', 'wbc', 'rbc', 'hemoglobin']):
            return "blood_work"
        elif any(term in text_lower for term in ['tsh', 't4', 't3', 'thyroid']):
            return "thyroid"
        elif any(term in text_lower for term in ['alt', 'ast', 'bilirubin', 'liver']):
            return "liver"
        elif any(term in text_lower for term in ['creatinine', 'bun', 'egfr', 'kidney']):
            return "kidney"
        else:
            return "general"

    def _extract_test_results(self, text):
        """Enhanced test result extraction with multiple pattern matching"""
        results = []
        
        # Multiple patterns to catch different report formats
        patterns = [
            # Pattern: Test Name: Value Units (Range)
            r'([A-Za-z\s]+)\s*[:=]\s*([\d.]+)\s*([a-zA-Z/%]*)\s*[\([]?\s*([\d.-]+\s*[-–]\s*[\d.-]+)\s*[\)\]]?',
            # Pattern: Test Name Value/Units (Range)
            r'([A-Za-z\s]+)\s+([\d.]+)\s*\/?\s*([a-zA-Z/%]*)\s*[\([]?\s*([\d.-]+\s*[-–]\s*[\d.-]+)\s*[\)\]]?',
            # Pattern with different bracket styles
            r'([A-Za-z\s]+)\s+([\d.]+)\s*([^\(\)\[\]]*?)\s*[\(\[\{]([^\)\]\}]+)[\)\]\}]',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 3:
                    test_name = match.group(1).strip()
                    value = match.group(2).strip()
                    units = match.group(3).strip() if match.group(3) else ''
                    normal_range = match.group(4).strip() if len(match.groups()) >= 4 else ''
                    
                    # Clean up units and ranges
                    units = re.sub(r'[^\w/%]', '', units)
                    normal_range = re.sub(r'[^\d.-–]', ' ', normal_range)
                    
                    results.append({
                        'test_name': test_name,
                        'value': value,
                        'units': units,
                        'normal_range': normal_range
                    })
        
        return results

    def _determine_status(self, test_name, value_str, normal_range=""):
        """Enhanced status determination with risk levels"""
        try:
            value_num = float(value_str)
            test_lower = test_name.lower()
            
            # Try to extract range from provided normal_range
            range_parts = re.findall(r'[\d.]+', normal_range)
            
            # If no range provided, use default ranges
            if len(range_parts) >= 2:
                low, high = map(float, range_parts[:2])
            elif test_lower in self.normal_ranges:
                range_info = self.normal_ranges[test_lower]
                if 'range' in range_info:
                    low, high = range_info['range']
                else:
                    # Use male range as default if gender not specified
                    low, high = range_info['male']
            else:
                return "Review Needed", "Please consult your healthcare provider for interpretation"
            
            # Calculate how far from normal
            if low <= value_num <= high:
                return "Normal", f"Within normal range ({low}-{high})"
            
            elif value_num < low:
                deviation = (low - value_num) / low * 100
                if deviation > 30:
                    return "Critically Low", f"Significantly below normal range ({low}-{high}) - Seek immediate medical attention"
                elif deviation > 15:
                    return "Low", f"Below normal range ({low}-{high}) - Discuss with your doctor"
                else:
                    return "Slightly Low", f"Just below normal range ({low}-{high}) - Monitor and discuss if symptomatic"
            
            else:  # value_num > high
                deviation = (value_num - high) / high * 100
                if deviation > 50:
                    return "Critically High", f"Significantly above normal range ({low}-{high}) - Seek immediate medical attention"
                elif deviation > 25:
                    return "High", f"Above normal range ({low}-{high}) - Discuss with your doctor"
                else:
                    return "Slightly High", f"Just above normal range ({low}-{high}) - Monitor and discuss if symptomatic"
                    
        except (ValueError, TypeError):
            return "Review Needed", "Unable to interpret value - consult your healthcare provider"

    def simplify_medical_report(self, text):
        """Enhanced simplification with better formatting and explanations"""
        report_type = self.detect_report_type(text)
        test_results = self._extract_test_results(text)
        
        sections = []
        
        # Header
        sections.append("MEDICAL REPORT SIMPLIFICATION")
        sections.append("=" * 50)
        sections.append(f"Report Type: {report_type.upper().replace('_', ' ')}")
        sections.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        sections.append("")
        
        if not test_results:
            sections.append("No structured test results found in the report.")
            sections.append("Please ensure your report contains values with normal ranges.")
            return "\n".join(sections)
        
        # Group by test categories
        categorized_tests = self._categorize_tests(test_results)
        
        for category, tests in categorized_tests.items():
            if tests:
                sections.append(f"{category.upper()}")
                sections.append("-" * 30)
                
                for test in tests:
                    test_name = test['test_name']
                    value = test['value']
                    units = test['units']
                    normal_range = test['normal_range']
                    
                    # Get medical term explanation
                    term_info = self.medical_terms.get(test_name.lower(), {})
                    display_name = term_info.get('term', test_name)
                    description = term_info.get('description', 'Medical measurement')
                    
                    # Determine status
                    status, explanation = self._determine_status(test_name, value, normal_range)
                    
                    # Add emoji based on status
                    emoji = self._get_status_emoji(status)
                    
                    sections.append(f"{emoji} {display_name}: {value} {units}")
                    sections.append(f"   Status: {status}")
                    sections.append(f"   What it means: {description}")
                    sections.append(f"   Note: {explanation}")
                    sections.append("")
        
        return "\n".join(sections)

    def _categorize_tests(self, test_results):
        """Categorize tests into logical groups"""
        categories = {
            'Blood Count': [],
            'Metabolic Panel': [],
            'Liver Function': [],
            'Kidney Function': [],
            'Lipids (Cholesterol)': [],
            'Thyroid Function': [],
            'Other Tests': []
        }
        
        blood_terms = ['hemoglobin', 'wbc', 'rbc', 'platelets', 'hematocrit']
        metabolic_terms = ['glucose', 'sodium', 'potassium', 'chloride', 'calcium']
        liver_terms = ['alt', 'ast', 'bilirubin', 'alkaline phosphatase', 'albumin']
        kidney_terms = ['creatinine', 'bun', 'egfr']
        lipid_terms = ['cholesterol', 'ldl', 'hdl', 'triglycerides']
        thyroid_terms = ['tsh', 't4', 't3']
        
        for test in test_results:
            test_lower = test['test_name'].lower()
            categorized = False
            
            for term_list, category in [
                (blood_terms, 'Blood Count'),
                (metabolic_terms, 'Metabolic Panel'),
                (liver_terms, 'Liver Function'),
                (kidney_terms, 'Kidney Function'),
                (lipid_terms, 'Lipids (Cholesterol)'),
                (thyroid_terms, 'Thyroid Function')
            ]:
                if any(term in test_lower for term in term_list):
                    categories[category].append(test)
                    categorized = True
                    break
            
            if not categorized:
                categories['Other Tests'].append(test)
        
        return categories

    def _get_status_emoji(self, status):
        """Get appropriate emoji for status"""
        emoji_map = {
            'Normal': '✅',
            'Slightly Low': '⚠️',
            'Slightly High': '⚠️',
            'Low': '🔻',
            'High': '🔺',
            'Critically Low': '🚨',
            'Critically High': '🚨',
            'Review Needed': '❓'
        }
        return emoji_map.get(status, '📋')

    def generate_recommendations(self, simplified_text, report_type="general"):
        """Enhanced recommendations based on findings"""
        recommendations = []
        
        recommendations.append("HEALTH RECOMMENDATIONS")
        recommendations.append("=" * 30)
        recommendations.append("")
        
        # General recommendations
        recommendations.append("General Advice:")
        recommendations.append("• Share these results with your healthcare provider")
        recommendations.append("• Discuss any symptoms or concerns with your doctor")
        recommendations.append("• Follow up as recommended by your healthcare team")
        recommendations.append("• Maintain regular health check-ups")
        recommendations.append("")
        
        # Specific recommendations based on findings
        if "Critically" in simplified_text:
            recommendations.append("🚨 URGENT RECOMMENDATIONS:")
            recommendations.append("• Seek immediate medical attention if you have symptoms")
            recommendations.append("• Contact your healthcare provider today")
            recommendations.append("• Do not ignore these critical results")
            recommendations.append("")
        
        if any(status in simplified_text for status in ["High", "Low"]):
            recommendations.append("Important Next Steps:")
            recommendations.append("• Schedule a follow-up appointment with your doctor")
            recommendations.append("• Discuss potential causes and treatment options")
            recommendations.append("• Consider lifestyle modifications if appropriate")
            recommendations.append("")
        
        # Type-specific recommendations
        if report_type == "diabetes" or "glucose" in simplified_text.lower():
            recommendations.append("Blood Sugar Management:")
            recommendations.append("• Monitor blood glucose levels regularly")
            recommendations.append("• Follow a balanced diet with controlled carbohydrates")
            recommendations.append("• Engage in regular physical activity")
            recommendations.append("• Maintain a healthy weight")
            recommendations.append("")
        
        if report_type == "cardiac" or any(term in simplified_text.lower() for term in ['cholesterol', 'ldl']):
            recommendations.append("Heart Health:")
            recommendations.append("• Follow a heart-healthy diet (Mediterranean style)")
            recommendations.append("• Exercise regularly (30 minutes most days)")
            recommendations.append("• Manage stress through relaxation techniques")
            recommendations.append("• Avoid smoking and limit alcohol")
            recommendations.append("")
        
        if "kidney" in report_type or any(term in simplified_text.lower() for term in ['creatinine', 'egfr']):
            recommendations.append("Kidney Health:")
            recommendations.append("• Stay well-hydrated with water")
            recommendations.append("• Monitor blood pressure regularly")
            recommendations.append("• Limit salt intake")
            recommendations.append("• Review medications with your doctor")
            recommendations.append("")
        
        recommendations.append("")
        recommendations.append("Important Disclaimer:")
        recommendations.append("• This analysis is for informational purposes only")
        recommendations.append("• Always consult qualified healthcare providers for medical advice")
        recommendations.append("• Do not make treatment decisions based solely on this information")
        
        return "\n".join(recommendations)

    def process_report(self, file_path, file_type, text_content=None):
        """Enhanced main processing method"""
        try:
            logger.info(f"Processing report: {file_path if file_path else 'text input'}")
            
            start_time = datetime.now()
            
            if text_content:
                raw_text = text_content
            else:
                raw_text = self.extract_text_from_file(file_path, file_type)
            
            if not raw_text.strip():
                return {
                    'error': 'No readable text content found. Please provide a file with text or text content directly.',
                    'status': 'error'
                }
            
            cleaned_text = self.preprocess_text(raw_text)
            report_type = self.detect_report_type(cleaned_text)
            simplified_text = self.simplify_medical_report(cleaned_text)
            recommendations = self.generate_recommendations(simplified_text, report_type)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Count tests found
            test_results = self._extract_test_results(cleaned_text)
            
            return {
                'original_text': cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text,
                'simplified_text': simplified_text,
                'recommendations': recommendations,
                'report_type': report_type,
                'summary': {
                    'tests_found': len(test_results),
                    'report_type': report_type,
                    'processing_time_seconds': round(processing_time, 2),
                    'character_count': len(cleaned_text)
                },
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing report: {e}")
            return {
                'error': f'Error processing report: {str(e)}',
                'status': 'error'
            }


# Initialize the enhanced simplifier
simplifier = EnhancedMedicalReportSimplifier()


@app.route('/')
def home():
    return jsonify({
        'message': 'Enhanced Medical Report Simplification API',
        'status': 'running',
        'version': '2.0',
        'features': [
            'Multi-format file support (TXT, PDF, Images)',
            'Enhanced medical term recognition',
            'Risk-level status indicators',
            'Categorized test results',
            'Personalized recommendations'
        ],
        'endpoints': {
            '/api/simplify': 'POST - Upload medical report for simplification',
            '/api/simplify-text': 'POST - Simplify medical text directly',
            '/api/health': 'GET - API health check'
        }
    })


@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced Medical Report Simplifier',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })


@app.route('/api/simplify', methods=['POST'])
def simplify_report():
    """Enhanced API endpoint for medical report simplification"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Enhanced file type support
        allowed_types = {
            'text/plain': '.txt',
            'application/pdf': '.pdf',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png'
        }
        
        if file.content_type not in allowed_types:
            return jsonify({
                'error': f'File type {file.content_type} not supported. Supported types: {list(allowed_types.keys())}'
            }), 400
        
        # Create temporary file with proper extension
        file_extension = allowed_types[file.content_type]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            result = simplifier.process_report(temp_path, file.content_type)
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        finally:
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")
                
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/simplify-text', methods=['POST'])
def simplify_text():
    """Enhanced text simplification endpoint"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        if len(text) > 20000:
            return jsonify({'error': 'Text too long. Maximum 20000 characters.'}), 400
        
        result = simplifier.process_report(None, 'text/plain', text_content=text)
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Text simplification error: {e}")
        return jsonify({
            'error': f'Error processing text: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("🚀 Starting Enhanced Medical Report Simplification API...")
    print("📊 Features:")
    print("   • Multi-format file support (TXT, PDF, Images)")
    print("   • Enhanced medical term recognition")
    print("   • Risk-level status indicators")
    print("   • Categorized test results")
    print("   • Personalized health recommendations")
    print("\n🌐 Available endpoints:")
    print("  GET  /                       - API information")
    print("  GET  /api/health             - Health check")
    print("  POST /api/simplify           - Upload medical report file")
    print("  POST /api/simplify-text      - Simplify medical text directly")
    print("\n💊 Server running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)