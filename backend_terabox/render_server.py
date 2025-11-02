import os
import requests
import re
import uuid
import time
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extract_terabox_simple(terabox_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.terabox.com/'
        }
        
        response = requests.get(terabox_url, headers=headers, timeout=15)
        
        patterns = [
            r'"dlink"\s*:\s*"([^"]+)"',
            r'"play_url"\s*:\s*"([^"]+)"', 
            r'"downloadUrl"\s*:\s*"([^"]+)"',
            r'https?://[^"\']+\.mp4[^"\']*'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                download_url = match.group(1) if match.lastindex else match.group(0)
                download_url = download_url.replace('\\u0026', '&')
                
                title_match = re.search(r'<title>(.*?)</title>', response.text)
                title = title_match.group(1).replace(' - TeraBox', '') if title_match else 'TeraBox Video'
                
                return {
                    'success': True,
                    'title': title,
                    'directLink': download_url
                }
        
        return {'success': False, 'message': 'No video link found'}
        
    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}

@app.route('/')
def home():
    return jsonify({'status': 'online', 'service': 'TeraBox Downloader'})

@app.route('/api/test')
def test():
    return jsonify({'status': 'working', 'message': 'Python API is running!'})

@app.route('/api/get-info', methods=['POST'])
def get_info():
    try:
        data = request.get_json()
        terabox_url = data.get('teraboxUrl', '').strip()
        
        if not terabox_url:
            return jsonify({'success': False, 'message': 'URL is required'})
        
        if not ('terabox.com' in terabox_url or '1024tera.com' in terabox_url):
            return jsonify({'success': False, 'message': 'Invalid TeraBox URL'})
        
        time.sleep(2)
        result = extract_terabox_simple(terabox_url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)