import os
import base64
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('app.log')  # File output
    ]
)
logger = logging.getLogger(__name__)

# Configuration - use local output directory in debug mode, /output in production
def get_output_dir():
    """Get the appropriate output directory based on environment"""
    if app.debug or os.environ.get('FLASK_ENV') == 'development':
        # In debug/development mode, use local output directory
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    else:
        # In production (Docker), use /output
        return '/output'

# Initialize OUTPUT_DIR - will be updated in main if needed
OUTPUT_DIR = '/output'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp'}
ALLOWED_EMAIL_EXTENSIONS = {'msg', 'eml'}
EMAIL_MIME_TYPES = {
    'message/rfc822',
    'application/vnd.ms-outlook',
    'application/octet-stream'  # Sometimes Outlook emails come as this
}

def ensure_output_dir():
    """Ensure the output directory exists"""
    output_dir = get_output_dir()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    else:
        logger.info(f"Output directory exists: {output_dir}")

def generate_filename(content_type, extension=None):
    """Generate a unique filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    if extension:
        return f"{timestamp}_{unique_id}.{extension}"
    elif content_type == 'text':
        return f"{timestamp}_{unique_id}.txt"
    elif content_type == 'email':
        return f"{timestamp}_{unique_id}.msg"
    else:
        return f"{timestamp}_{unique_id}.bin"

def is_valid_image_extension(filename):
    """Check if the file has a valid image extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def is_valid_email_extension(filename):
    """Check if the file has a valid email extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EMAIL_EXTENSIONS

def detect_email_content(data):
    """Detect if content appears to be an email"""
    if isinstance(data, bytes):
        try:
            data_str = data.decode('utf-8', errors='ignore')
        except:
            return False
    else:
        data_str = str(data)
    
    # Check for common email headers
    email_indicators = [
        'From:', 'To:', 'Subject:', 'Date:',
        'Return-Path:', 'Message-ID:', 'Content-Type:',
        'Received:', 'MIME-Version:'
    ]
    
    data_upper = data_str.upper()
    email_header_count = sum(1 for indicator in email_indicators if indicator.upper() in data_upper)
    
    # If we find multiple email headers, it's likely an email
    return email_header_count >= 3

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store', methods=['POST'])
def store_content():
    try:
        ensure_output_dir()
        output_dir = get_output_dir()
        
        data = request.get_json()
        content_type = data.get('type')
        content = data.get('content')
        
        logger.info(f"Received store request - Type: {content_type}, Content length: {len(content) if content else 0}")
        
        if not content:
            logger.warning("Store request failed: No content provided")
            return jsonify({'error': 'No content provided'}), 400
        
        if content_type == 'text':
            # Store text content
            filename = generate_filename('text')
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"Successfully stored text file: {filepath} ({file_size} bytes)")
                
            return jsonify({
                'success': True, 
                'filename': filename,
                'message': f'Text saved as {filename}'
            })
            
        elif content_type == 'image':
            # Handle base64 image data
            try:
                # Extract the image data and format
                header, data_base64 = content.split(',', 1)
                
                # Determine file extension from header
                if 'png' in header:
                    extension = 'png'
                elif 'jpeg' in header or 'jpg' in header:
                    extension = 'jpg'
                elif 'gif' in header:
                    extension = 'gif'
                elif 'webp' in header:
                    extension = 'webp'
                elif 'svg' in header:
                    extension = 'svg'
                else:
                    extension = 'png'  # default
                
                logger.info(f"Processing image - Format: {extension}, Data size: {len(data_base64)} chars")
                
                # Decode base64 data
                image_data = base64.b64decode(data_base64)
                
                filename = generate_filename('image', extension)
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                file_size = os.path.getsize(filepath)
                logger.info(f"Successfully stored image file: {filepath} ({file_size} bytes)")
                    
                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'message': f'Image saved as {filename}'
                })
                
            except Exception as e:
                logger.error(f"Failed to process image: {str(e)}")
                return jsonify({'error': f'Failed to process image: {str(e)}'}), 400
        
        elif content_type == 'email':
            # Handle email content (from Outlook drag & drop)
            try:
                # Check if it's base64 encoded binary data (like .msg files)
                if content.startswith('data:'):
                    # Handle base64 encoded email files
                    header, data_base64 = content.split(',', 1)
                    email_data = base64.b64decode(data_base64)
                    
                    # Determine extension based on content or header
                    if 'msg' in header.lower():
                        extension = 'msg'
                    elif 'eml' in header.lower():
                        extension = 'eml'
                    else:
                        # Try to detect based on content
                        if email_data.startswith(b'\xd0\xcf\x11\xe0'):  # OLE/MSG file signature
                            extension = 'msg'
                        else:
                            extension = 'eml'
                    
                    filename = generate_filename('email', extension)
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(email_data)
                        
                    file_size = os.path.getsize(filepath)
                    logger.info(f"Successfully stored email file: {filepath} ({file_size} bytes)")
                    
                    return jsonify({
                        'success': True,
                        'filename': filename,
                        'message': f'Email saved as {filename}'
                    })
                    
                else:
                    # Handle plain text email content
                    # Auto-detect if this looks like email content
                    if detect_email_content(content):
                        filename = generate_filename('email', 'eml')
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                        file_size = os.path.getsize(filepath)
                        logger.info(f"Successfully stored email text: {filepath} ({file_size} bytes)")
                        
                        return jsonify({
                            'success': True,
                            'filename': filename,
                            'message': f'Email saved as {filename}'
                        })
                    else:
                        # Treat as regular text if it doesn't look like an email
                        filename = generate_filename('text')
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                        file_size = os.path.getsize(filepath)
                        logger.info(f"Successfully stored text content: {filepath} ({file_size} bytes)")
                        
                        return jsonify({
                            'success': True,
                            'filename': filename,
                            'message': f'Text saved as {filename}'
                        })
                        
            except Exception as e:
                logger.error(f"Failed to process email: {str(e)}")
                return jsonify({'error': f'Failed to process email: {str(e)}'}), 400
        
        else:
            logger.warning(f"Store request failed: Invalid content type '{content_type}'")
            return jsonify({'error': 'Invalid content type'}), 400
            
    except Exception as e:
        logger.error(f"Server error during store operation: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    logger.info("Health check requested")
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    logger.info("Starting Docker Drop Flask application")
    ensure_output_dir()
    output_dir = get_output_dir()
    logger.info(f"Flask app starting on host=0.0.0.0, port=5000, debug=True")
    logger.info(f"Output directory configured at: {output_dir}")
    app.run(host='0.0.0.0', port=5000, debug=True)
