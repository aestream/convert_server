from flask import Flask, request, send_file, render_template_string
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_FORMATS = ['csv', 'aedat4', 'es', 'raw'] #, 'mp4']

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        .upload-form {
            border: 2px dashed #ccc;
            padding: 20px;
            text-align: center;
        }
        .form-group {
            margin: 15px 0;
        }
        select, input[type="file"] {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            width: 300px;
        }
        .submit-btn {
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .submit-btn:hover {
            background-color: #45a049;
        }
    </style>
    <!-- Matomo -->
    <script>
    var _paq = window._paq = window._paq || [];
    /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
    _paq.push(['trackPageView']);
    _paq.push(['enableLinkTracking']);
    (function() {
        var u="//matomo.jepedersen.dk/";
        _paq.push(['setTrackerUrl', u+'matomo.php']);
        _paq.push(['setSiteId', '1']);
        var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
        g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
    })();
    </script>
    <!-- End Matomo Code -->
</head>
<body>
    <div class="upload-form">
        <h2>Address-event data File Converter</h2>
        <p>Supported formats: {{ formats|join(', ') }}</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <input type="file" name="file" required>
            </div>
            <div class="form-group">
                <select name="output_format" required>
                    <option value="">Select output format</option>
                    {% for format in formats %}
                    <option value="{{ format }}">{{ format.upper() }}</option>
                    {% endfor %}
                </select>
            </div>
            <input type="submit" value="Convert File" class="submit-btn">
        </form>
    </div>
    <div id="donation-reminder" style="display: none;">
        
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, formats=ALLOWED_FORMATS)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    output_format = request.form.get('output_format')
    
    if file.filename == '':
        return 'No file selected', 400
        
    if not output_format or output_format not in ALLOWED_FORMATS:
        return 'Invalid output format', 400

    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        input_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(input_path)
        
        # Create output filename with the selected format
        output_filename = f'converted_{os.path.splitext(secure_filename(file.filename))[0]}.{output_format}'
        output_path = os.path.join(temp_dir, output_filename)
        
        try:
            # Run faery conversion with output format
            subprocess.run(['faery', 'input', 'file', input_path, 'output', 'file', output_path], check=True)
            
            # Send file back with JavaScript trigger for donation reminder
            response = send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename
            )
            response.headers['Content-Type'] = 'application/octet-stream'
            
            return response
        except subprocess.CalledProcessError as e:
            return f'Error converting file: {str(e)}', 500
        except Exception as e:
            return f'Unexpected error: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')