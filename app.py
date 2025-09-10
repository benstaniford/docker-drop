import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configuration
OUTPUT_DIR = '/output'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp'}

def ensure_output_dir():
    """Ensure the output directory exists"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_filename(content_type, extension=None):
    """Generate a unique filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    if extension:
        return f"{timestamp}_{unique_id}.{extension}"
    elif content_type == 'text':
        return f"{timestamp}_{unique_id}.txt"
    else:
        return f"{timestamp}_{unique_id}.bin"

def is_valid_image_extension(filename):
    """Check if the file has a valid image extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store', methods=['POST'])
def store_content():
    try:
        ensure_output_dir()
        
        data = request.get_json()
        content_type = data.get('type')
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        if content_type == 'text':
            # Store text content
            filename = generate_filename('text')
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
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
                
                # Decode base64 data
                image_data = base64.b64decode(data_base64)
                
                filename = generate_filename('image', extension)
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                    
                return jsonify({
                    'success': True, 
                    'filename': filename,
                    'message': f'Image saved as {filename}'
                })
                
            except Exception as e:
                return jsonify({'error': f'Failed to process image: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'Invalid content type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    ensure_output_dir()
    app.run(host='0.0.0.0', port=5000, debug=True)
