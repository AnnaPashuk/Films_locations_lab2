import folium
import math
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def main_func():
    year = input('Please enter a year you would like to have a map for:' )
    your_location = input('Please enter your location (format: lat, long):' )
    general_list = read_file("loc.txt")
    locations_list = create_locations_list(general_list)
    new_file = write_in_file(locations_list)
    films_year = find_films_year(year)
    films_near = nearest_films(your_location, films_year)
    cities = read_cities_file()
    final_map = create_map(your_location, films_near, cities)
    return final_map


def read_file(path):
    """
    read information from file and create general list
    (Note) -> (list)
    """
    with open(path, "r", encoding="UTF-8", errors='ignore') as f:
        general_list = []
        for line in f:
            general_list.append(line.strip().split("\t"))
    general_list = general_list[14:]
    return general_list


def create_locations_list(general_list):
    """
    create sorted by years list
    (list) -> (list)
    >>> create_locations_list([['"#15SecondScare" (2015)', 'England, UK'], ['"#1 Single" (2006)', '','New York, USA']])
    [['"#1 Single"', 2006, 'New York, USA'], ['"#15SecondScare"', 2015, 'England, UK']]
    """
    locations_list = []
    for i in general_list:
        line = []
        try:
            for j in i:
                if j:
                    line.append(j)
            if len(line) >= 3:
                line = line[:2]
            name_year = line[0].split(" (")
            line[0] = name_year[0]
            line.insert(1, int(name_year[1][:4]))
            locations_list.append(line)
        except IndexError:
            continue
        except ValueError:
            continue
    locations_list.sort(key=lambda x: x[1])
    return locations_list


def write_in_file(locations_list):
    """
    create a new file with sorted by years list of films
    (list) -> (Note)
    """
    with open("sorted_films.txt", "w", encoding="UTF-8") as f:
        for line in locations_list:
            try:
                f.write(f"{line[1]} | {line[0]} | {line[2]}\n")
            except TypeError:
                continue


def find_films_year(year):
    """
    read from file films which were produced only on a particular year
    create a list of their names and location
    (Note) -> (list)
    """
    films_year = []
    with open("sorted_films.txt", "r", encoding="UTF-8") as f:
        for line in f:
            if int(line[:4]) == int(year):
                line = line.strip().split(" | ")
                films_year.append(line[1:])
    return films_year


def interprite_names_into_coordinates(loc):
    """
    this function interprates names of locations into coordinates
    (string) -> (list)
    >>> interprite_names_into_coordinates('Los Angeles, California, USA')
    [34.0536909, -118.2427666]
    >>> interprite_names_into_coordinates('Kyiv, Ukraine')
    [50.4500336, 30.5241361]
    """
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    location = geolocator.geocode(loc, timeout=10)
    if location != None:
        return [location.latitude, location.longitude]


def nearest_films(your_location, films_year):
    """
    function calculates all distances from given location to films and finds only 10 nearest
    (string, list) -> (list)
    """
    distances = []
    your_location = your_location.split(",")
    lat = float(your_location[0])
    long = float(your_location[1])
    for i in range(len(films_year)):
        cords = interprite_names_into_coordinates(films_year[i][1])
        if cords != None:
            dist = math.sqrt((lat - cords[0])**2 + (long - cords[1])**2)
            distances.append([films_year[i][0], cords, dist])
    distances.sort(key= lambda x: x[2])
    return distances[:10]


def read_cities_file():
    """
    function reads information from file with 5 the biggest cities in the world an makes a list of them
    and their coordinates
    (Note) -> list
    """
    cities = []
    with open("biggest_cities.txt", "r", encoding="UTF-8") as f:
        for line in f:
            line = line.strip().split()
            cities.append(line)
    return cities


def create_map(your_location, films, cities):
    your_location = your_location.split(",")

    lat1 = float(your_location[0])
    long1 = float(your_location[1])
    m = folium.Map(location=your_location,
                   zoom_start=12)
    your_loc = folium.FeatureGroup(name="Your location")
    your_loc.add_child(folium.CircleMarker(location=(lat1, long1), popup="Your location", color='red', icon=folium.Icon()))

    fm = folium.FeatureGroup(name="Films near you")
    for film in films:
        fm.add_child(folium.Marker(location=film[1], popup=film[0], icon=folium.Icon()))

    fs = folium.FeatureGroup(name="Top 5 biggest cities in the world")
    for city in cities:
        lat2 = float(city[1])
        long2 = float(city[2])
        ltt = (lat2, long2)
        fs.add_child(folium.CircleMarker(location=ltt, popup=city[0], color='green', icon=folium.Icon()))

    m.add_child(fm)
    m.add_child(fs)
    m.add_child(your_loc)
    m.add_child(folium.LayerControl())
    m.save("films_locations.html")


if __name__ == "__main__":
    main_func()
    print("Finished. Please have a look at the map films_locations.html")


