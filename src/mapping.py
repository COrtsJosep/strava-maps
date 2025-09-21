import shapely
import pandas as pd
import geopy.distance
import geopandas as gpd
from pathlib import Path

src_path = Path(__file__).parent
data_path = src_path.parent / 'data'

def euclidean_distance(
    p0: shapely.Point, 
    p1: shapely.Point, 
    vertical_distance: float
) -> float:
    ''' Calculates the distance between two points.
    
    Parameters
    ----------
    p0 : shapely.Point
        Origin of the segment.
    p1 : shapely.Point
        End of the segment.
    vertical_distance : float
        Vertical distance between p0 and p1, in meters.

    Returns
    -------
    float
        the Euclidean distance between p0 and p1, in kilometers.
    '''
    vertical_distance = vertical_distance / 1000 # conversion to kilometers
    horizontal_distance = geopy.distance.geodesic(
        (p0.y, p0.x), 
        (p1.y, p1.x)
    ).km
    
    return (horizontal_distance ** 2 + vertical_distance ** 2) ** 0.5

def calculate_statistics(filepath: Path) -> pd.DataFrame:
    ''' Calculates some statistics about a Strava activity.
        
    Parameters
    ----------
    filepath : pathlib.Path
        Path of the gpx file of the Strava activity.
        
    Returns
    -------
    pandas.DataFrame
        The dataframe has one row and four columns: the activity date as str,
        the activity distance in kilometers as float, and the altitude won and
        lost in meters as float.
    '''
    gdf = gpd.read_file(
        filepath, 
        layer = 'track_points', 
        columns = ['ele', 'time', 'geometry']
    )
    
    total_euclidean_distance = 0
    altitude_won = 0
    altitude_lost = 0
    for i in range(1, gdf.shape[0]):
        # iterate segment by segment on the curve
        p0 = gdf.loc[i - 1, 'geometry']
        p1 = gdf.loc[i, 'geometry']
        
        segment_vertical_distance = (gdf.loc[i, 'ele'] - gdf.loc[i - 1, 'ele'])
        segment_euclidean_distance = euclidean_distance(p0, p1, segment_vertical_distance)
        
        if segment_euclidean_distance > 1: 
            # segments of more than one kilometer between signal and signal
            # ignore them: unreliable measuring for a long time
            continue
        
        total_euclidean_distance += segment_euclidean_distance
        if segment_vertical_distance > 0:
            altitude_won += segment_vertical_distance
        else:
            altitude_lost += -segment_vertical_distance
            
    data = {
        'Activity date': [gdf.loc[0, 'time'].strftime('%Y-%m-%d')],
        'Distance (float)': [total_euclidean_distance],
        'Altitude won (float)': [altitude_won],
        'Altitude lost (float)': [altitude_lost],
    }
            
    return pd.DataFrame(data = data)

def generate_map() -> None:
    ''' Generates a map of the activity tracks stored in data/ as gtx files. 
    Writes the output as a html file in src/templates/.
    
    Returns:
    -------
    None
    '''
    gdf = pd.concat(
        [
            pd.concat(
                [
                    gpd.read_file(
                        filename, 
                        layer = 'tracks',
                        columns = ['name', 'type', 'geometry']
                    ),
                    calculate_statistics(filename)
                ],
                axis = 1
            )
            for filename
            in data_path.glob('*.gpx')
        ]
    )

    gdf.loc[:, 'Activity type'] = gdf.loc[:, 'type'].map(lambda x: x.title())
    gdf.loc[:, 'Distance'] = gdf.loc[:, 'Distance (float)'].apply(lambda d: str(round(d, 2)) + ' km')
    gdf.loc[:, 'Altitude won'] = gdf.loc[:, 'Altitude won (float)'].apply(lambda d: str(round(d)) + ' m')
    gdf.loc[:, 'Altitude lost'] = gdf.loc[:, 'Altitude lost (float)'].apply(lambda d: str(round(d)) + ' m')
        
    cols = [
        'Activity name', 
        'Activity type', 
        'Activity date', 
        'Distance', 
        'Altitude won', 
        'Altitude lost', 
        'geometry'
    ]
        
    (
        gdf
        .rename(columns = {'name': 'Activity name'})
        .loc[:, cols]
        .reset_index(drop = True)
        .explore(
            tiles = 'CartoDB dark_matter', 
            column = 'Activity type', 
            cmap = ['cyan', 'magenta', 'yellow', 'green'],
            style_kwds = {'weight': 2.5},
        )
        .save(src_path / 'templates' / 'map.html')
    )
