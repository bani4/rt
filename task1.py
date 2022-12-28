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
output_filename = 'results2.csv'

def address_translit(s, lang):
    new_s=''
    if lang=='bg':
        bg_lat_map={
            'bg':['а','б','в','г','д','е','ж', 'з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х', 'ц', 'ч', 'ш', 'щ','ъ','ь','ю','я'],
            'en':['a','b','v','g','d','e','zh','z','i','i','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sht','u','i','yu','ia']
        }
    for symbol in s:
        if symbol in bg_lat_map['bg']:
            poz = bg_lat_map['bg'].index(symbol)
            new_s+=bg_lat_map['en'][poz]
        else:
            new_s+=symbol
    return new_s

def normalize_address(s:str):
    words = s.split(' ')
    words = [i.replace(',','') for i in words]
    forbidden = ['ul.', 'ул.', 'Street', 'Str.']
    if any([i in forbidden for i in words]):
        s=s.replace('ul. ','').replace('ул. ','').replace('Street','').replace('Str.','')
    
    if any([i.count('.') for i in words]):
        for word in words:
            if word.count('.')>0:
                s=s.replace(word, '')
    address = s.split(', ')
    street= address_translit(address[0].lower(),'bg')
    s=s.replace(address[0],street)
    if street.split(' ')[0].isnumeric():
        print(1)
        street_number = street.split(' ')[0]
        old_street = street
        new_street = street.replace(street_number, '')+' '+street_number
        s=s.replace(old_street, new_street)
    city = address[1]
    city_code = re.findall(r'[0-9]+', city)
    if len(city_code)>0:
        s=s.replace(city_code[0], '')
    
    print('final: ',s)
    return s

def doit(inf, outf):

    df = pd.read_csv(inf)
    
    df['Address_normalized'] = df['Address']
    df['Address_normalized'] = df['Address_normalized'].apply(normalize_address)
    
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="my-app-here")
    pd.set_option('max_colwidth', None)
    pd.set_option('display.max_columns', 2)

    for row in df.index:
        try:
            df.loc[row,"location"] = geolocator.geocode(df.loc[row,'Address_normalized']).address
            ## test street address
            # df.loc[row,"location"] = geolocator.geocode('Свищовска 65, Габрово, България').address

            # df['location'] = geolocator.geocode(df['Address_normalized']).address ## not working, why?
        except:
            df.loc[row,"location"] = 'Need to be fixed/ normalized more'
    # print(df[['Name','location']])  
    df_names = pd.DataFrame(columns=['Name', 'Location'])
    df.sort_values(by=['Name'], inplace=True)
    for row in df.index:
        if df.loc[row, 'location'] not in df_names['Location'].unique():        
            new_df_to_add = pd.DataFrame({'Name':[df.loc[row, 'Name']], 'Location':[df.loc[row, 'location']]})
            df_names = pd.concat([df_names,new_df_to_add], ignore_index=True)
        else:
            df_names.loc[df_names['Location']==df.loc[row, 'location'],['Name']]+=', '+df.loc[row,'Name']
    print(df_names.head(5))
    df_names[['Name']].to_csv(outf, index=False )

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
    doit(input_file, output_file)


    

