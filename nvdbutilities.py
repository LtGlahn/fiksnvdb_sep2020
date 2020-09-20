from copy import deepcopy 
import pdb 
from datetime import datetime
import json 

from shapely import wkt 
from shapely.ops import unary_union
import pandas as pd 
import geopandas as gpd 

import STARTHER
import nvdbapiv3
import skrivnvdb


def utvidbbox( bbox, buffer):
    """
    Utvider en boundingbox

    ARGUMENTS
        bbox : tuple med de eksisterende (xmin, ymin, xmax, ymax) boundingBox-verdier

        buffer: Int eller float, antall koordinat-enheter (meter) som boksen skal utvides med

    KEYWORDS: 
        None

    RETURNS
        bbox : tuple med utvidede (xmin, ymin, xmax, ymax) boundingBox-verdier
    
    """

    return (  bbox[0] - buffer, bbox[1] - buffer, bbox[2] + buffer,  bbox[3] + buffer) 


def joinbbox( bboxA, bboxB): 
    """
    Slår sammen to boundinbboxer til en større bbox som overlapper begge to

    ARGUMENTS
        bboxA : None eller tuple med de eksisterende (xmin, ymin, xmax, ymax) boundingBox-verdier

        bboxB:  tuple med nye (xmin, ymin, xmax, ymax) boundingBox-verdier

    KEYWORDS: 
        None

    RETURNS
        tuple med (xmin, ymin, xmax, ymax) boundingBox-verdier
    """


    if not bboxA: 
        bbox = bboxB
    else: 
        bbox = (  min( bboxA[0], bboxB[0] ), 
                  min( bboxA[1], bboxB[1] ), 
                  max( bboxA[2], bboxB[2] ), 
                  max( bboxA[3], bboxB[3] )
                ) 


    return bbox 

def finntrafikantgruppe( seg): 
    """
    Finner trafikantgruppe for vegsegment tilknyttet vegobjekt (rått fra NVDB api V3)
    """

    trafikantgruppe = 'U'
    if 'kryssystem' in seg['vegsystemreferanse'].keys(): 
        trafikantgruppe = seg['vegsystemreferanse']['kryssystem']['trafikantgruppe']
    elif 'sideanlegg' in seg['vegsystemreferanse'].keys(): 
        trafikantgruppe = seg['vegsystemreferanse']['sideanlegg']['trafikantgruppe']
    elif 'strekning' in seg['vegsystemreferanse'].keys(): 
        trafikantgruppe = seg['vegsystemreferanse']['strekning']['trafikantgruppe']
    else: 
        print( 'MANGLER vegreferansedetaljer', seg['vegsystemreferanse']['kortform'])


    return trafikantgruppe

def registreringsegenskaper( egenskaper ): 
    """
    Konvererer liste med egenskapverdier (rått fra NVDB api V3) til dictionary med ID : verdi 
    hvor ID = typeId til denne egenskapen ihtt datakatalogen 
    """

    data = { }
    for eg in egenskaper: 

        if 'verdi' in eg.keys():
            data[ eg['id'] ] = eg['verdi']

    return data 

def ignorerliste( ):
    """
    Liste med objektid som av ulike årsaker IKKE skal prosesseres 
    """

    # ignorer = [ 835347602   ]
    ignorer = [  779620154,  1007822938  ]
    return ignorer 

def liste2gpkg( minliste, filnavn, lagnavn, **kwargs):
    """
    Lagrer liste med NVDB-fagdata til geopackage
    ARGUMENTS: 
        minliste - liste med NVDB-objekt
        
        filnavn - navn på .gpkg-fil vi skal skrive til
        lagnavn - navn på tabellen vi skal lagre 
    KEYWORDS: 
        Blir videresendt til nvdbapiv3.nvdbfagdata2records

    RETURNS: 
        Geodataframe (for debugging / inspeksjon, du får den gdf'en vi skrev til fil)

    """

    liste2 = nvdbapiv3.nvdbfagdata2records( minliste, **kwargs )
    if len( liste2 ) > 0: 
        mindf = pd.DataFrame( liste2 )

        if 'vegsegmenter' in mindf.columns: 
            mindf.drop( ['vegsegmenter'], axis=1, inplace=True)

        mindf['geometry'] = mindf['geometri'].apply( wkt.loads )
        minGdf = gpd.GeoDataFrame( mindf, geometry='geometry', crs=25833 )
        minGdf.to_file(filnavn, layer=lagnavn, driver="GPKG")  

        return minGdf
    else: 
        print( 'Ingen forekomster å skrive til lag', lagnavn, 'fil', filnavn)

    return None

def bevartBKverdier( gammelbk, nybk ): 
    """
    Sammenligner dictionary med nytt forslag BK-verdier med det gamle 

    Vil ignorere strekningsbeskrivelse og en del andre mindre viktige ting... 

    ARGUMENTS
        gammelbk, nybk : string eller dictionary på formen { "egenskapTypeId" : "verdi" }

    KEYWORDS
        None

    RETURNS 
        True eller False 
    """

    # 905 BK uoff 
    # [{10902: 'Bruksklasse'},
    # {10908: 'Bruksklasse vinter'},
    # {10914: 'Maks vogntoglengde'},
    # {10920: 'Strekningsbeskrivelse'}, IGNORER 
    # {10927: 'Maks totalvekt kjøretøy, skiltet'}, IGNORER
    # {10928: 'Maks totalvekt vogntog, skiltet'}, IGNORER 
    # {11010: 'Merknad'}]

    # Har vi fått tomme data? 
    if not gammelbk or not nybk: 
        return False 

    ignorer = [ 10920, 10927, 10928, # 905 BK normal, uoff
                10916, 10918 # Strekningsbeskrivelser 901 tømmer og 903 spesial 
                 ] 

    s_ignorer = set( ignorer )

    gmlKey = set( gammelbk.keys())  - s_ignorer
    nyKey  = set( nybk.keys())      - s_ignorer

    if gmlKey != nyKey: 
        return False 
    
    else: 
        for akey in gmlKey: 
            if gammelbk[akey] != nybk[akey]:
                return False 

    return True 

def skriveegenskap2endringssett( egenskapdict ): 
    """
    Konverterer dictionary med egenskapid : verdi til den strukturen APISKRIV skal ha
    """

    skriveg = [ ]

    for eg in egenskapdict.items():
        skriveg.append( { 'typeId': eg[0], 'verdi' : [ eg[1] ] }  )

    return skriveg 

def d577_subset2endringssett( mydataframe  ): 
    """
    Se grab577.py. Spesialdesignet for å lage endringssett for vegfunksjon 
    """

    mal = skrivnvdb.endringssett_mal( operasjon='registrer')

    etobj =  {
            "stedfesting": {
                "linje": [ ]
            },
            "gyldighetsperiode": {
                "startdato": "2020-09-20"
            },
            "typeId": 577,
            "tempId": "577#1",
            "egenskaper": skriveegenskap2endringssett( json.loads( mydataframe.iloc[ 0, 1] ) )           
        }
    
    for index, row in mydataframe.iterrows(): 
        
        etobj['stedfesting']['linje'].append( {
                "fra": row['startposisjon'],
                "til": row['sluttposisjon'],
                "veglenkesekvensNvdbId": row['veglenkesekvensid']
            } ) 


    mal['registrer']['vegobjekter'].append( etobj ) 
    return mal 

