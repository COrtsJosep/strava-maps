from pathlib import Path
from mapping import generate_map
from flask import Flask, render_template, request

app = Flask(__name__)

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
            file.save(f'data/{file.filename}')
            
        generate_map()
        
        for file in Path('data/').glob('data/*.gpx'):
            file.unlink()
            
        return render_template('map.html')
