import geocoder
import pandas as pd
import geopandas as gpd
import folium
from folium.features import DivIcon
# import datetime
import requests

# get the data from the National Institute of Meteorology and Hydrology, Bulgaria
meteo = requests.get('http://meteo.bg/izmervania/tochki')  # use the requests module
df_meteo = pd.read_html(meteo.text)  # read the tables (if any) from the html text from the website

# get the table of interest
temp_wind = df_meteo[0]  

# check the data & datatypes
print(temp_wind.head())
print(temp_wind.info())

# getting the geographical coordinates for the stations with the geocoder package
stations = temp_wind['Станция'].unique()  # list with all the stations from the table
print(len(stations))  # check number of stations

# modify the list, so that we add Bulgaria to each item, it would help to the geocoder module
for i in range(len(stations)):
    stations[i] = stations[i] + ' България'
    
stations = ['Ново село България', 'Видин България', 'Враца България', 'Монтана България', 'Лом България', 'Оряхово България',
            'Кнежа България', 'Ловеч България', 'Плевен България', 'Велико Търново България', 'Свищов България', 'Русе България',
            'Шумен България', 'Разград България', 'Силистра България', 'Силистра България', 'Варна България', 'Шабла България',
            'Калиакра България', 'Добрич България', 'вр. Мургаш България', 'Кюстендил България', 'Драгоман България', 'Благоевград България',
            'Черни връх България', 'София България', 'Пловдив - Тракия България', 'Пазарджик България', 'Чирпан България', 'Казанлък България',
            'Стара Загора България', 'Сливен България', 'Елхово България', 'Карнобат България', 'нос Емине България', 'Бургас България',
            'Ахтопол България', 'Сандански България', 'Гоце Делчев България', 'Рожен България', 'Кърджали България', 'Хасково България']
   
# coordinates of the stations
coordinates_x = []
coordinates_y = []

for i in range(len(stations)):
    g = geocoder.osm(stations[i])  # using open street map (osm)
    coordinates_y.append(g.latlng[0])  # latitude
    coordinates_x.append(g.latlng[1])  # longitude

coords = {'X': coordinates_x, 'Y': coordinates_y}  # create a dictionary with lat,lon coordinates of the stations
df = pd.DataFrame(coords, index=None)  # creating dataframe from the dictionary
df = df.merge(temp_wind, left_index=True, right_on='ID', how='inner')  # merge with the meteo table

# weather conditions, manual work based on the information in the table
sunny = 'слънчево/ясно'
cloudy = ['облачно', 'значителна облачност', 'разкъсана облачност', 'мъгла', 'видимост под 10km']
rainy = ['слаб краткотраен дъжд', 'краткотраен дъжд в последния час', 'силен краткотраен дъжд',
'гръмотевична буря в последния час', 'гръмотевична буря', 'слаб дъжд']

sun = '../images/sun.png'  # we will use the sun image for sunny/clear weather
cloud = '../images/cloud.png'  # we will use the sun image for cloudy weather
rain = '../images/rain.png'  # we will use the sun image for rainy weather

# create the geodataframe
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['X'], df['Y']), crs="EPSG:4326")

weather_pp = gdf['Време'].to_list()

# use the list with weather conditions (weather_pp) to assign 1 of 3 types (sun, rain, cloud)
for x in range(len(weather_pp)):
	if weather_pp[x] in cloudy:
		weather_pp[x] = cloud
	elif weather_pp[x] in rainy:
		weather_pp[x] = rain
	else:
		weather_pp[x] = sun

# add a weather column in the gdf
gdf['weather'] = weather_pp
# attribution = source for the tiles to be loaded in the web map
attribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

# add folium.Map
m = folium.Map(location=[43.708902, 24.890053], zoom_start=8, tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-background/{z}/{x}/{y}{r}.png', attr=attribution)
for i in range(len(gdf)):
    location=[gdf['Y'][i], gdf['X'][i]]
    icon = folium.CustomIcon(icon_image=gdf['weather'][i], icon_size=(35,35))
    folium.Marker(location=location, icon=icon).add_to(m)

for i in range(len(gdf)):
    location=[gdf['Y'][i], gdf['X'][i]]
    # popups = "<iframe src='/home/user/filav/Danube_Map/html/Q_temp_{}.html' \
    # title='testo' height='300' width='400' ></iframe>".format(station_names[x])
    folium.Marker(location=location, icon=DivIcon(icon_size=(30,30),\
    icon_anchor=(-20,20),\
    html="""<div style="font-size:14px; white-space:nowrap"><b>{}</b></div>""".format(gdf['Станция'][i]))).add_to(m)

for i in range(len(gdf)):
    location=[gdf['Y'][i], gdf['X'][i]]
    # popups = "<iframe src='/home/user/filav/Danube_Map/html/Q_temp_{}.html' \
    # title='testo' height='300' width='400' ></iframe>".format(station_names[x])
    folium.Marker(location=location, icon=DivIcon(icon_size=(30,30),\
    icon_anchor=(-20,0),\
    html="""<div style="font-size:16px; backround-color:'white'"><b>{}</b></div>""".format(str(str(gdf['Температура [°C]'][i]) + '°C')))).add_to(m)
m.show_in_browser()
