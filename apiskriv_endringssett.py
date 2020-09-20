from datetime import datetime
import glob 

import geopandas as gpd 
import pandas as pd 


import STARTHER
import skrivnvdb
import apiforbindelse 
import nvdbutilities

forb = apiforbindelse.apiforbindelse()
forb.login( miljo='prodskriv' )


url = 'https://www.vegvesen.no/nvdb/apiskriv/rest/v3/endringssett?antall=600&start=1&sorterPå=TID&sorterStigende=false&brukernavnEllerKlient=fiks577_'

data = forb.les( url ).json()

for endr in data['endringssett']: 
    starturl = [ x['src'] for x in endr['status']['ressurser'] if x['rel'] == 'start' ]
    print( starturl[0])