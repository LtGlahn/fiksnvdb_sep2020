from copy import deepcopy 
import pdb 

from shapely import wkt 
from shapely.ops import unary_union
import pandas as pd 
import geopandas as gpd 
from datetime import datetime

import STARTHER
import nvdbapiv3
from apiforbindelse import apiforbindelse
import nvdbutilities


if __name__ == '__main__': 

    t0 = datetime.now( )
    # minefilter = { 'kommune' : 3453 }    

    vegobjekttype = 577
    tm = nvdbapiv3.nvdbFagdata( vegobjekttype )

    data = tm.to_records( vegsegmenter=False  )
 
    mindf = pd.DataFrame( data )
    filnavn = 'dump577_v2.gpkg'
    mindf['geometry'] = mindf['geometri'].apply( wkt.loads )
    minGdf = gpd.GeoDataFrame( mindf, geometry='geometry', crs=25833 )
    # må droppe kolonne vegsegmenter hvis du har vegsegmenter=False 
    minGdf.drop( 'vegsegmenter', 1)
    minGdf.to_file( filnavn, layer='vf577', driver="GPKG")  
