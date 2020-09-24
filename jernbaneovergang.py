from copy import deepcopy 
import pdb 
import sqlite3 

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

    jb = nvdbapiv3.nvdbFagdata( 100)
    jb.filter( { 'overlapp' : '900'})
    dfjb  = pd.DataFrame( jb.to_records(   )) 

    bk = nvdbapiv3.nvdbFagdata( 900)
    bk.filter( { 'overlapp' : '100'})
    dfbk = pd.DataFrame( bk.to_records( ) )
    dfkb = dfbk[['objekttype', 'nvdbId', 'Bruksklasse', 'Bruksklasse vinter',  
                'Maks vogntoglengde', 'Maks totalvekt', 'Merknad',  
                'veglenkesekvensid', 'startposisjon', 'sluttposisjon']].copy( )

    dfkb.rename( columns={  'objekttype' : 'BKobjekttype', 'nvdbId' : 'bkNvdbId', 
                            'veglenkesekvensid' : 'bk_vid', 'startposisjon' : 'bkstart', 
                            'sluttposisjon' : 'bkslutt'  }, inplace=True)


# Lager virituell database, slik at vi kan gjøre SQL-spørringer
    conn = sqlite3.connect( ':memory:')
    temp2010.to_sql( 'v2010', conn, index=False )
    temp2009.to_sql( 'v2009', conn, index=False )

    # Finner overlapp mellom ERF-veger per 31.12.2009 og K-veger per 1.1.2010
    # Overlapp = samme plassering på samme veglenkesekvens
    qry = """
            select  * from v2009
                    INNER JOIN v2010 ON 
                    v2009.d2009_veglenkesekvensid = v2010.veglenkesekvensid and
                    v2009.d2009_startposisjon     < v2010.sluttposisjon and 
                    v2009.d2009_sluttposisjon     > v2010.startposisjon
            """


    # mindf = pd.DataFrame( data )
    # filnavn = 'dump577_v2.gpkg'
    # mindf['geometry'] = mindf['geometri'].apply( wkt.loads )
    # minGdf = gpd.GeoDataFrame( mindf, geometry='geometry', crs=25833 )
    # # må droppe kolonne vegsegmenter hvis du har vegsegmenter=False 
    # minGdf.drop( 'vegsegmenter', 1)
    # minGdf.to_file( filnavn, layer='vf577', driver="GPKG")  
