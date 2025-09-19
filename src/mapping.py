import pandas as pd
import geopandas as gpd
from pathlib import Path
from pypalettes import load_cmap

src_path = Path(__file__).parent
data_path = src_path.parent / 'data'

cmap = load_cmap('kiss') # 5 categories

def generate_map() -> None:
    gdf = pd.concat(
        [
            gpd.read_file(filename, layer = 'tracks') 
            for filename
            in data_path.glob('*.gpx')
        ]
    )

    (
        gdf
        .rename(columns = {'type': 'Type', 'name': 'Name'})
        .loc[:, ['Name', 'Type', 'geometry']]
        .assign(Type = lambda gdf: gdf.loc[:, 'Type'].map(lambda x: x.title()))
        .explore(
            tiles = 'CartoDB dark_matter', 
            column = 'Type', 
            #cmap = cmap,
            cmap = ['cyan', 'magenta', 'yellow', 'green'],
            style_kwds = {'weight': 2.5},
        )
        .save(src_path / 'templates' / 'map.html')
    )
