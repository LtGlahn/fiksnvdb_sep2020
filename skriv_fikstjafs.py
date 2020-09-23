from datetime import datetime
import glob 

import geopandas as gpd 
import pandas as pd 


import STARTHER
import skrivnvdb
import apiforbindelse 
import nvdbutilities


skrivtil = skrivnvdb.endringssett( )
skrivtil.forbindelse.login( miljo='prodskriv' )

nvdbfilterid = [ 1007739029, 1007739322 ]

fil = 'fiks899.gpkg' # 'fiks577_alle.gpkg'

mingdf = gpd.read_file( fil )
alleid = list( mingdf['nvdbId'].unique() ) 

count = 0 
alleendringssett = []
filtrertendringssett = [ ]
filtrertendringssett_v2 = [ ]

for nvdbId in alleid: 

    subset = mingdf[ mingdf['nvdbId'] == nvdbId ]

    if len( subset['kommune'].unique() ) > 1: 

        gruppe = subset.groupby( ['mykey']).agg('count').sort_values( 'nvdbId', ascending=False )
        gruppe.reset_index( inplace=True)

        for index, row in gruppe.iterrows(): 
            if index == 0: 
                print( 'Lar', row['mykey'], 'ligge med', row['nvdbId'], 'stedfestinger' )

                if nvdbId in nvdbfilterid:  

                    subset2 = mingdf[ mingdf['mykey'] == row['mykey']]
                    endringssett = nvdbutilities.d577_subset2endringssett( subset2 )
                    skrivtil.data = endringssett
                    skrivtil.forbindelse.klientinfo( 'bk889_' + row['mykey'] )
                    skrivtil.registrer()
                    skrivtil.startskriving()
                    
                    ###  alleendringssett.append( endringssett)

                    if nvdbId in nvdbfilterid:  
                        filtrertendringssett_v2.append( endringssett )                

            else:
                print( '\tskriver', row['mykey'], 'med',   row['nvdbId'], 'stedfestinger' )
                count += 1 
                subset2 = mingdf[ mingdf['mykey'] == row['mykey']]
                endringssett = nvdbutilities.d577_subset2endringssett( subset2 )
                skrivtil.data = endringssett
                skrivtil.forbindelse.klientinfo( 'bk889_' + row['mykey'] )
                # skrivtil.registrer()
                # skrivtil.startskriving()
                alleendringssett.append( endringssett)

                if nvdbId in nvdbfilterid:  
                    filtrertendringssett.append( endringssett )
                    
                    # skrivtil.registrer()
                    # skrivtil.startskriving()
            

print( count, "endringssett")
# for endr in endringID: 
#     r = forb.les( url + endr )
#     data = r.json( )
#     nyendring = skrivnvdb.endringssett_mal( operasjon='delvisOppdater')
#     for obj in data['delvisOppdater']['vegobjekter']: 
#         obj['gyldighetsperiode']['startdato'] = datetime.now().strftime("%Y-%m-%d")
#         nyendring['delvisOppdater']['vegobjekter'].append( obj )

#     skrivtil.data= nyendring 
#     skrivtil.registrer( dryrun=False)
#     skrivtil.startskriving()
