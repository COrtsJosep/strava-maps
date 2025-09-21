from pathlib import Path
from mapping import generate_map
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
src_path = Path(__file__).parent
data_path = src_path.parent / 'data'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/upload', methods = ['POST'])
def upload():
    if request.method == 'POST':
        # Get the list of files from webpage
        files = request.files.getlist('file')

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(data_path / file.filename)
            
        generate_map()
        
        # delete them after having created the map
        for file in data_path.glob('data/*.gpx'):
            file.unlink()
            
        return jsonify({'status': 'success', 'redirect': '/map'})
        
@app.route('/map')
def show_map():
    return render_template('map.html')
