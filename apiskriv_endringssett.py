from datetime import datetime
import glob 

import geopandas as gpd 
import pandas as pd 
from shapely.geometry import Point

import STARTHER
import skrivnvdb
import apiforbindelse 
import nvdbutilities

emptyGeom = Point()

forb = apiforbindelse.apiforbindelse()
forb.login( miljo='prodskriv' )

url = 'https://www.vegvesen.no/nvdb/apiskriv/rest/v3/endringssett?antall=100&start=1&sorterP%C3%A5=TID&sorterStigende=false&status=UTF%C3%98RT_OG_ETTERBEHANDLET&brukernavnEllerKlient=vegfunksjon_'

data = forb.les( url ).json()

# for endr in data['endringssett']: 
#     starturl = [ x['src'] for x in endr['status']['ressurser'] if x['rel'] == 'start' ]
#     print( starturl[0])

endr = data['endringssett'][0]

utvidetdata = []

for endr in data['endringssett']: 
    
    nyedata = { 'id' : endr['id'] }
    nyedata.update( endr['status'])
    
    tmp = endr['status']['klient'].split( '_')
    nyedata['orginal577id'] = tmp[1]
    nyedata['kommune'] = tmp[2]

    r = forb.les( 'https://www.vegvesen.no/nvdb/apiskriv/rest/v3/endringssett/' +  endr['id']  )
    dd = r.json()
    vo = [ x['nvdbId'] for x in  dd['status']['resultat']['vegobjekter'] ]
    if len( vo ) > 1: 
        print( "flere vegobjekt", endr['klient'])

    nyedata['nyNvdbId'] = vo[0]
    nyedata['geometry'] = emptyGeom
    nyedata.pop( 'ressurser', None )
    nyedata.pop( 'etterbehandling', None )

    utvidetdata.append( nyedata )

myGdf = gpd.GeoDataFrame( utvidetdata, geometry='geometry', crs=25833 )

