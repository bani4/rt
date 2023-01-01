'''
Uses https://www.openstreetmap.org/, 
sotherefore Nominatim, or salution_nominatim()

Other maps/ APIs but not used:
https://www.arcgis.com/home/webmap/viewer.html
https://www.bing.com/maps/
https://www.google.com/maps
'''

import pandas as pd
import os
import re
from geopy.geocoders import Nominatim
import ssl
import certifi
import geopy.geocoders
from pathlib import Path


input_file = None ## input
output_directory = None ## input
output_file = None
output_filename = 'results.csv'

def transliterate(some_string, lang):
    '''MAKING it LOWERCASE'''
    string_transliterated=''
    if lang=='bg':
        bg_lat_map={
            'bg':['а','б','в','г','д','е','ж', 'з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х', 'ц', 'ч', 'ш', 'щ','ъ','ь','ю','я'],
            'en':['a','b','v','g','d','e','zh','z','i','i','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sht','u','i','yu','ia']
        }
    for symbol in some_string.lower():
        if symbol in bg_lat_map['bg']:
            indx = bg_lat_map['bg'].index(symbol)
            string_transliterated+=bg_lat_map['en'][indx]
        else:
            string_transliterated+=symbol
    return string_transliterated

def openstreetmap_normalize_address(address_non_normalized:str):
    address_list = address_non_normalized.split(', ')

    ## needed fixes for Nominatim
    street_transliterated= transliterate(address_list[0],'bg') 
    words_in_street = street_transliterated.split(' ')
    words_in_street = [i.replace(',','') for i in words_in_street]
    forbidden_words = ['ul.', 'ул.', 'street', 'str.', 'bulevard', 'булевард', 'бул.', 'tsar', '№']

    while any([i in forbidden_words for i in words_in_street]):
        found_list = [i in forbidden_words for i in words_in_street]
        index_found = found_list.index(True)
        del words_in_street[index_found]
    
    address_normalized=' '.join(words_in_street)+ ', '+', '.join(address_list[1:])
    # print("\tinside function, address_normalized: ", address_normalized)
    
    # fix for China
    if 'P.R.C' in address_normalized:
        address_normalized = address_normalized.replace('P.R.C', 'China')

    if words_in_street[0].isnumeric():
        street_number = words_in_street[0]
        old_street = ' '.join(words_in_street)
        new_street = ' '.join(words_in_street[1:])+' '+street_number
        address_normalized=address_normalized.replace(old_street, new_street)
    # print("\taddress_normalized -> street number moved: ",address_normalized)

    city = address_list[-2]
    # print(city)
    city_code = re.findall(r'[0-9]+', city)
    if len(city_code)>0:
        address_normalized=address_normalized.replace(city_code[0], '')
    
    # print('\tfinal: ',address_normalized)
    return address_normalized

def solution_nominatim(inf, outf):

    df = pd.read_csv(inf)
    
    df['Address_normalized'] = df['Address']
    df['Address_normalized'] = df['Address_normalized'].apply(openstreetmap_normalize_address)
    
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="my-app-here")
    pd.set_option('max_colwidth', None)
    pd.set_option('display.max_columns', 2)

    for row in df.index:
        try:
            df.loc[row,"nominatim_address_1"] = geolocator.geocode(df.loc[row,'Address_normalized']).address
            
        except:
            df.loc[row,"nominatim_address_1"] = 'Need to be fixed/ normalized more'
    # print(df[['Name','nominatim_address_1']])  

    df_result_names = pd.DataFrame(columns=['Names', 'Nominatim_address_1'])
    df.sort_values(by=['Name'], inplace=True)
    for row in df.index:
        if df.loc[row, 'nominatim_address_1'] not in df_result_names['Nominatim_address_1'].unique():        
            new_df_to_add = pd.DataFrame({'Names':[df.loc[row, 'Name']], 'Nominatim_address_1':[df.loc[row, 'nominatim_address_1']]})
            df_result_names = pd.concat([df_result_names,new_df_to_add], ignore_index=True)
        else:
            df_result_names.loc[df_result_names['Nominatim_address_1']==df.loc[row, 'nominatim_address_1'],['Names']]+=', '+df.loc[row,'Name']
    print(df_result_names.head(5))
    df_result_names[['Names']].to_csv(outf, index=False )

def get_input_data():
    global input_file
    global output_directory
    global output_file
    global output_filename
    while True:         
        input_file = Path(input("Path to input csv file: "))
        if input_file.exists() and input_file.is_file() and input_file.suffix=='.csv':
            break
        else:
            print("File does not exist or is not a file or not .csv at least")
    while True:
        output_directory = Path(input("Path to output directory: "))
        if output_directory.exists() and output_directory.is_dir():
            output_file = output_directory.joinpath(output_filename)
            break
        else:
            print("Directory does not exist or is a file!")
    print(input_file,output_file, output_directory, output_filename)
    return True

if __name__ == "__main__":
    print("----Resonanz Technologies Task1-----")
    get_input_data()
    solution_nominatim(input_file, output_file)

    ## testing single address
    # ctx = ssl.create_default_context(cafile=certifi.where())
    # geopy.geocoders.options.default_ssl_context = ctx
    # geolocator = Nominatim(user_agent="my-app-here")
    # address = 'ул. Копривщица 5, кв. Курило,  гр. Нови Искър, България'
    # address_normalized = normalize_address(address)
    # print("address normalized: ",address_normalized)
    # print(geolocator.geocode(address_normalized).address)


    

