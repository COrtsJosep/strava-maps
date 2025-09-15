import glob
import pandas as pd
import geopandas as gpd
from pypalettes import load_cmap

cmap = load_cmap('kiss') # 5 categories

def generate_map() -> None:
    gdf = pd.concat(
        [
            gpd.read_file(filename, layer = 'tracks') 
            for filename
            in glob.glob('data/*.gpx')
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
            cmap = cmap,
            style_kwds = {'weight': 5},
        )
        .save('templates/map.html')
    )
