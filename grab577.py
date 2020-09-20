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
    forb = apiforbindelse()
    # tm.filter( minefilter)
    tm.respons['inkluder'] = 'egenskaper'

    data = [ ]
    vf = tm.nesteForekomst()
    while vf: 

        # data = [ ]

        egenskaper = nvdbutilities.registreringsegenskaper( vf['egenskaper'])

        tmp = [ x for x in vf['egenskaper'] if x['navn'] == 'Liste av lokasjonsattributt' ]
        count = 0 
        for linje in tmp[0]['innhold']:
            rad = { 'nvdbId' : vf['id'],
                    'egenskaper' : egenskaper,
                    'objekttype' : vegobjekttype,
                    'veglenkesekvensid' : linje['veglenkesekvensid'], 
                    'startposisjon' : linje['startposisjon'], 
                    'sluttposisjon' : linje['sluttposisjon']
                      }
            # Legg på info fra vegnettet
            url = '/vegnett/veglenkesekvenser/segmentert/' + str( linje['veglenkesekvensid'] )
            r = forb.les( url  )
            if r.ok: 
                veger = r.json()
                veg = veger[0]
                rad['kortform'] = veg['kortform']
                rad['geometri'] = veg['geometri']['wkt']
                rad['lengde']   = veg['lengde']
                rad['fylke']   = veg['fylke']
                rad['kommune']   = veg['kommune']
                rad['mykey']     = str( vf['id'] ) + '_' + str( veg['kommune'])
                data.append( rad )

            else: 
                print( 'Fant ingen veg for', r.url )

            count += 1
            if count % 1000 == 0: 
                print( 'iterasjon', count, 'av', len(tmp[0]['innhold'] ),  'for objekt', vf['id'])

                
        # # vf = False   
        # if len( data ) > 0: 

        # else: 
        #     print( "fant ingen gyldige veger for objekt", vf['id'])

        tidsbruk = datetime.now( ) - t0 
        print( "tidsbruk:", tidsbruk.total_seconds( ), "sekunder")

        vf = tm.nesteForekomst()


    mindf = pd.DataFrame( data )
    filnavn = 'fiks577_v2.gpkg'
    mindf['geometry'] = mindf['geometri'].apply( wkt.loads )
    minGdf = gpd.GeoDataFrame( mindf, geometry='geometry', crs=25833 )
    minGdf.to_file( filnavn, layer='vf577', driver="GPKG")  
