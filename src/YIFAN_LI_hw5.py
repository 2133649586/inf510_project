import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os


def parse_args():

    parser = argparse.ArgumentParser(description = "you should add those parameter")

    parser.add_argument("-source", choices=["local", "remote","test"], nargs=1, help="where data should be gotten from")

    # parser.add_argument('--remote', type=str, help='remote')
    # parser.add_argument('--local', type=str, help='local')
    # parser.add_argument('--test', type=str, help='test')`
    args = parser.parse_args()
    return args




'''get latitude and longitude'''
def lat_long():
    r = requests.get("https://www.latlong.net/category/cities-235-15.html")
    soup = BeautifulSoup(r.content, 'lxml')
    main_table = soup.findAll('div', {"class": "col-8"})[0]
    main_body = main_table.find('table')

    city_name = []
    latitude = []
    longitude = []

    for place in main_body.findAll('tr'):
        if (len(place.findAll('td')) > 0):
            place_name = place.findAll('td')[0].text
            place_latitude = place.findAll('td')[1].text
            place_longitude = place.findAll('td')[2].text
            #print(place_name, place_latitude, place_longitude)

            city_name.append(place_name)
            latitude.append(place_latitude)
            longitude.append(place_longitude)

    latitude_longitude = pd.DataFrame({'city name': city_name, 'latitude': latitude, 'longitude': longitude})
    latitude_longitude.to_csv('latitude_longitude.csv', index=False)
    return latitude_longitude






'''get GDHI of 9 regions'''
def get_GDHI():
    r = requests.get(
        "https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome/bulletins/regionalgrossdisposablehouseholdincomegdhi/1997to2016")
    soup = BeautifulSoup(r.content, 'lxml')
    main_table = soup.findAll('div', {"id": "the-fastest-growing-nuts1-region-per-head-is-the-east-of-england"})[0]

    # main_body = main_table.find('table',{'class':'t1'})
    # main_body = main_body.find('tbody')
    main_body = main_table

    name = []
    pop = []
    GDHI = []

    for place in main_body.findAll('tr', {'class': "r-6c019d9b-8d71-42da-8b23-fef011a0e2d7-3"}):
        if (len(place.findAll('td')) > 4) and len(place.findAll('td')[0].text) > 2:
            place_name = place.findAll('td')[0].text
            place_population = place.findAll('td')[2].text
            place_GDHI = place.findAll('td')[5].text
            place_GDHI = place_GDHI.replace(',', '')
            name.append(place_name)
            pop.append(place_population)
            GDHI.append(place_GDHI)
            # print(place_name,'  pop:',place_population,'  GDHI:',place_GDHI)

    for place in main_body.findAll('tr', {'class': "r-6c019d9b-8d71-42da-8b23-fef011a0e2d7-4"}):
        if (len(place.findAll('td')) > 4 and len(place.findAll('td')[0].text) > 2):
            place_name = place.findAll('td')[0].text
            place_name = place.findAll('td')[0].text
            place_population = place.findAll('td')[2].text
            place_GDHI = place.findAll('td')[5].text
            place_GDHI = place_GDHI.replace(',', '')
            name.append(place_name)
            pop.append(place_population)
            GDHI.append(place_GDHI)
            # print(place_name,'  pop:',place_population,'  GDHI:',place_GDHI)

    pop_GDHI_df = pd.DataFrame({'region name': name, 'GDHI': GDHI})
    pop_GDHI_df = pop_GDHI_df.drop([0, 9, 11, 12], axis=0)

    pop_GDHI_df.to_csv('pop_GDHI.csv', index=False)
    return pop_GDHI_df




'''get all crime numbers of every city in 2017 in UK.
   This step will take more than half an hour, it is not recommended to try during testing '''

def get_crime():
    latitude_longitude = lat_long()
    pop_GDHI_df = get_GDHI()
    first_city = []

    for i in range(0, latitude_longitude.shape[0]):
        all_city_name = latitude_longitude['city name'][i]
        single_name = all_city_name.split(',')[0]
        first_city.append(single_name)
    latitude_longitude.insert(0, 'single city name', first_city)

    city_dict = {'North East': 'Newcastle upon Tyne', 'North West': 'Manchester', 'Yorkshire and The Humber': 'Leeds', \
                 'East Midlands': 'Leicester', 'West Midlands': 'Birmingham', \
                 'East of England': 'Cambridge', 'South East': 'Winchester', 'South West': 'Bristol', \
                 'Northern Ireland': 'Belfast', 'London': 'London', 'Wales': 'St. Davids', 'Scotland': 'Glasgow'}

    data_list = ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06', '2017-07', '2017-08', \
                 '2017-09', '2017-10', '2017-11', '2017-12']

    crime_type = []
    region = []
    data = []

    for i in range(0, pop_GDHI_df.shape[0]):

        print(f'load data of {i+1}th city')
        biggest_city = (pop_GDHI_df.iloc[i])['region name']
        target_city = city_dict[biggest_city]
        city_address = latitude_longitude.loc[latitude_longitude['single city name'] == target_city]
        latitude = float(city_address['latitude'].values)
        longitude = float(city_address['longitude'].values)

        #print(f'{i}th time')

        for b in data_list:
            print(f'load data of {b}')
            # print(latitude,longitude,b)
            url = f"https://data.police.uk/api/crimes-street/all-crime?lat={latitude}&lng={longitude}&date={b}"


            # r = requests.get(url)
            # j = json.loads(r.content)
            # for c in j:
            #     crime_type.append(c['category'])
            #     region.append(biggest_city)
            #     data.append(c['month'])

            try:
                r = requests.get(url)
                j = json.loads(r.content)
                for c in j:
                    crime_type.append(c['category'])
                    region.append(biggest_city)
                    data.append(c['month'])
            except:
                try:
                    r = requests.get(url)
                    j = json.loads(r.content)
                    for c in j:
                        crime_type.append(c['category'])
                        region.append(biggest_city)
                        data.append(c['month'])
                except:
                    try:
                        r = requests.get(url)
                        j = json.loads(r.content)
                        for c in j:
                            crime_type.append(c['category'])
                            region.append(biggest_city)
                            data.append(c['month'])
                    except:
                        print('connot find this content')
                        pass
                    continue




    instance_df = pd.DataFrame({'crime type': crime_type, 'region': region, 'data': data})
    instance_df.to_csv('instance.csv', index=False)
    return instance_df







def get_part_of_crime():
    latitude_longitude = lat_long()
    pop_GDHI_df = get_GDHI()
    first_city = []

    for i in range(0, latitude_longitude.shape[0]):
        all_city_name = latitude_longitude['city name'][i]
        single_name = all_city_name.split(',')[0]
        first_city.append(single_name)
    latitude_longitude.insert(0, 'single city name', first_city)

    city_dict = {'North East': 'Newcastle upon Tyne', 'North West': 'Manchester', 'Yorkshire and The Humber': 'Leeds', \
                 'East Midlands': 'Leicester', 'West Midlands': 'Birmingham', \
                 'East of England': 'Cambridge', 'South East': 'Winchester', 'South West': 'Bristol', \
                 'Northern Ireland': 'Belfast', 'London': 'London', 'Wales': 'St. Davids', 'Scotland': 'Glasgow'}

    data_list = ['2017-01', '2017-02']

    crime_type = []
    region = []
    data = []

    for i in range(0, pop_GDHI_df.shape[0]):

        # print(f'load data of {i+1}th city')
        biggest_city = (pop_GDHI_df.iloc[i])['region name']
        target_city = city_dict[biggest_city]
        city_address = latitude_longitude.loc[latitude_longitude['single city name'] == target_city]
        latitude = float(city_address['latitude'].values)
        longitude = float(city_address['longitude'].values)

        #print(f'{i}th time')

        for b in data_list:
            # print(f'load data of {b}')
            # print(latitude,longitude,b)
            url = f"https://data.police.uk/api/crimes-street/all-crime?lat={latitude}&lng={longitude}&date={b}"


            # r = requests.get(url)
            # j = json.loads(r.content)
            # for c in j:
            #     crime_type.append(c['category'])
            #     region.append(biggest_city)
            #     data.append(c['month'])

            try:
                r = requests.get(url)
                j = json.loads(r.content)
                for c in j:
                    crime_type.append(c['category'])
                    region.append(biggest_city)
                    data.append(c['month'])
            except:
                try:
                    r = requests.get(url)
                    j = json.loads(r.content)
                    for c in j:
                        crime_type.append(c['category'])
                        region.append(biggest_city)
                        data.append(c['month'])
                except:
                    try:
                        r = requests.get(url)
                        j = json.loads(r.content)
                        for c in j:
                            crime_type.append(c['category'])
                            region.append(biggest_city)
                            data.append(c['month'])
                    except:
                        print('connot find this content')
                        pass
                    continue




    instance_df = pd.DataFrame({'crime type': crime_type, 'region': region, 'data': data})
    instance_df.to_csv('instance.csv', index=False)
    return instance_df







def data_process(latitude_longitude,pop_GDHI_df,instance_df):
    city_pop = {}
    city_dict = {'North East': 'Newcastle upon Tyne', 'North West': 'Manchester', 'Yorkshire and The Humber': 'Leeds', \
                 'East Midlands': 'Leicester', 'West Midlands': 'Birmingham', \
                 'East of England': 'Cambridge', 'South East': 'Winchester', 'South West': 'Bristol', \
                 'Northern Ireland': 'Belfast', 'London': 'London', 'Wales': 'St. Davids', 'Scotland': 'Glasgow'}


    r = requests.get("https://en.wikipedia.org/wiki/List_of_English_districts_by_population")
    soup = BeautifulSoup(r.content,'lxml')
    main_body = soup.findAll('table', {"class": "wikitable"})[0]
    # main_body = main_body.find('table',{"class":"wikitable"})
    # main_body = main_body.find('tbody')

    for place in main_body.findAll('tr'):
        if (len(place.findAll('td')) > 2) and (isinstance(place.findAll('td')[2].text, int) != True):
            city = place.findAll('td')[1].text
            pop = place.findAll('td')[2].text
            pop = int(pop.replace(',', ''))
            city_pop[city] = pop

    city_pop['London'] = 8900000
    city_pop['Birmingham'] = 210700

    from collections import Counter
    total_crime_number = []
    population = []
    crime_rate = []
    all_crime_number = Counter(instance_df['region'])

    for i in all_crime_number:
        total_crime_number.append(all_crime_number[i])

    pop_GDHI_df.insert(1, 'total crime number', total_crime_number)

    for i in range(0, pop_GDHI_df.shape[0]):
        pop = city_pop[city_dict[pop_GDHI_df['region name'][i]]]
        population.append(pop)

    pop_GDHI_df.insert(2, 'population', population)

    for i in range(0, pop_GDHI_df.shape[0]):
        rate = int(pop_GDHI_df['total crime number'][i]) / int(pop_GDHI_df['population'][i])
        crime_rate.append(rate)

    pop_GDHI_df.insert(3, 'crime rate', crime_rate)

    all_crime = Counter(instance_df['crime type'])
    crime_list = []

    for i in all_crime:
        crime_list.append(i)

    crime_dict = {
        'anti-social-behaviour': [],
        'bicycle-theft': [],
        'burglary': [],
        'criminal-damage-arson': [],
        'drugs': [],
        'other-theft': [],
        'possession-of-weapons': [],
        'public-order': [],
        'robbery': [],
        'shoplifting': [],
        'theft-from-the-person': [],
        'vehicle-crime': [],
        'violent-crime': [],
        'other-crime': [],
    }

    for i in crime_dict:
        for b in range(0, pop_GDHI_df.shape[0]):
            consequence = Counter((instance_df.loc[instance_df['region'] == pop_GDHI_df['region name'][b]])['crime type'])
            if consequence[i] > 0:
                crime_dict[i].append(consequence[i] / pop_GDHI_df['population'][b])
            else:
                crime_dict[i].append('None')

    for i in crime_dict:
        pop_GDHI_df.insert(1, f'{i}', crime_dict[i])

    plt.plot(pop_GDHI_df['region name'], pop_GDHI_df['crime rate'], 'red', marker='*', label='crime rate')
    plt.xticks(rotation=45)
    plt.xlabel("region name")
    plt.ylabel("crime rate")
    plt.title("crime rate in 9 regions")
    plt.show()

    sns.regplot(data=pop_GDHI_df, x=pop_GDHI_df['GDHI'], y=pop_GDHI_df['crime rate'], line_kws={'color': 'red'})
    plt.title("crime rate and GDHI")
    plt.show()

    for i in crime_list:
        sns.regplot(data=pop_GDHI_df, x=pop_GDHI_df['GDHI'], y=pop_GDHI_df[i], line_kws={'color': 'red'})
        plt.title(f"{i} rate and GDHI ")
        plt.show()









module_path = os.path.dirname(__file__)
filename = module_path[:-3]


def get_local_latitude_longitude():
    with open(filename + 'data/latitude_longitude.csv', 'r') as a:
        latitude_longitude = pd.read_csv(a)
    return latitude_longitude

def get_local_pop_GDHI_df():
    with open(filename + 'data/pop_GDHI.csv', 'r') as b:
        pop_GDHI_df = pd.read_csv(b)
    return pop_GDHI_df

def get_local_instance_df():
    with open(filename + 'data/instance.csv', 'r') as c:
        instance_df = pd.read_csv(c)
    return instance_df





if __name__ == '__main__':
    args = parse_args()
    location = args.source
    # if args.remote:
    if location==['remote']:
        print("Remote Processing")
        print('\n')
        print("get latitude and longitude of all cities")
        latitude_longitude = lat_long()

        print('\n')
        print(' get Gross disposable household income(GDHI) of every city ')
        pop_GDHI_df = get_GDHI()

        print('\n')
        print(' get total crime #')
        instance_df = get_crime()

        print('\n')
        print(' finished ')


    #if args.test:
    if location==['test']:
        print("Remote Processing")
        print('\n')
        print("get latitude and longitude of all cities")
        latitude_longitude = lat_long()

        print('\n')
        print(' get Gross disposable household income(GDHI) of every city ')
        pop_GDHI_df = get_GDHI()

        print('\n')
        print(' get total crime')
        instance_df = get_part_of_crime()

        print('\n')
        print(' finished ')



    # elif args.local:
    if location==['local']:
        print(" Remote Processing ")
        print('\n')
        print(" get latitude and longitude of all cities ")
        latitude_longitude = get_local_latitude_longitude()

        print('\n')
        print(' get Gross disposable household income(GDHI) of every city ')
        pop_GDHI_df = get_local_pop_GDHI_df()

        print('\n')
        print(' get total crime ')
        instance_df = get_local_instance_df()

    else:
        print("unavailable Parameter")

    data_process(latitude_longitude, pop_GDHI_df, instance_df)










