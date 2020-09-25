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


if __name__ == '__main__': 

    jb = nvdbapiv3.nvdbFagdata( 100)
    jb.filter( { 'overlapp' : '900'})
    dfjb  = pd.DataFrame( jb.to_records(   )) 

    bk = nvdbapiv3.nvdbFagdata( 900)
    bk.filter( { 'overlapp' : '100'})
    dfbk = pd.DataFrame( bk.to_records( ) )
    dfbk_2 = dfbk[['objekttype', 'nvdbId', 'Bruksklasse', 'Bruksklasse vinter',  
                'Maks vogntoglengde', 'Maks totalvekt', 'Merknad',  
                'veglenkesekvensid', 'startposisjon', 'sluttposisjon']].copy( )

    # Døper om så vi unngår navnekollisjon mellom data om bruksklasse og jernbaneoverganger
    dfbk_2.rename( columns={  'objekttype' : 'BKobjekttype', 'nvdbId' : 'bkNvdbId', 
                            'veglenkesekvensid' : 'bk_vid', 'startposisjon' : 'bkstart', 
                            'sluttposisjon' : 'bkslutt'  }, inplace=True)


    # Lager virituell database, slik at vi kan gjøre SQL-spørringer
    conn = sqlite3.connect( ':memory:')
    dfjb.to_sql( 'jb', conn, index=False )
    dfbk_2.to_sql( 'bk', conn, index=False )

    # Finner overlapp mellom jernbaneoverganger (punkt på veglenkesekvens)
    # og bruksklasse (strekning på veglenkesekvens). 
    qry = """
            select  * from jb
                    LEFT JOIN bk ON 
                    jb.veglenkesekvensid     = bk.bk_vid   and
                    jb.relativPosisjon       > bk.bkstart  and 
                    jb.relativPosisjon       < bk.bkslutt
        """

    joined = pd.read_sql_query( qry, conn)

    # Hvilke egenskaper og rekkefølge vi ønsker i utskrift / presentasjon
    # Merk også at vi ikke har noen jb-kryssinger med egenskapene "Geometri, punkt" eller "Tillegsinformasjon"  
    # Se datatakatlogen for beskrivelse https://datakatalogen.vegdata.no/100-Jernbanekryssing
    utskriftkolonner = [ 'objekttype', 'nvdbId', 'versjon', 'startdato', 'Type',
                        'fylke', 'kommune', 'vegkategori', 'vref',
                        'Bruksklasse', 'Bruksklasse vinter','Maks vogntoglengde','Maks totalvekt','Merknad',
                        'BKobjekttype', 'bkNvdbId', 
                        'typeVeg','trafikantgruppe', 
                        'veglenkesekvensid', 'relativPosisjon', 'adskilte_lop', 'geometri'
                      ]

    # Fjerner jernbanekryssinger med Type = 'Veg over', 'Veg under'
    # Se datatakatlogen for beskrivelse https://datakatalogen.vegdata.no/100-Jernbanekryssing
    joined.fillna('', inplace=True) # Tomme verdier (NaN) => tom tekst ('')
    presentasjon = joined[ ~joined['Type'].str.contains( 'Veg') ][utskriftkolonner]

    # Lagrer resultater 
    filnavn = 'jernbanekryssinger' + datetime.now().strftime('%Y-%m-%d')
    presentasjon.to_excel( filnavn + '.xlsx' )

    jbGdf = presentasjon.copy()
    jbGdf['geometry'] = jbGdf['geometri'].apply( wkt.loads )
    jbGdf.drop( columns='geometri', inplace=True)
    jbGdf = gpd.GeoDataFrame( jbGdf, geometry='geometry', crs=25833)
    jbGdf.to_file( filnavn + '.gpkg', layer='jernbanekryssing', driver="GPKG")  
