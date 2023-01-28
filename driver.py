import requests
from bs4 import BeautifulSoup
from datetime import datetime

class TidesData:
    def __init__(self, date, sunrise, sunset, tides):
        self.date = date
        self.sunrise = sunrise
        self.sunset = sunset
        self.tides = tides

    def __str__(self):
        return "Date: " + str(self.date) + ", Sunrise: " + str(self.sunrise) + ", Sunset: " + str(self.sunset) + ", Tides: " + str(self.tides)

class TideInfo:
    def __init__(self, time, height, type):
        self.time = time
        self.height = height
        self.type = type

    def __str__(self):
        return "Time: " + str(self.time.strftime('%I:%M %p')) + ", Height: " + self.height + ", Type: " + self.type

def parse_page(url):
    response = requests.get(url)

    if response.text == None or response.text == '':
        return None, "Could not get page " + url

    soup = BeautifulSoup(response.text, 'html.parser')
    tide_days = soup.find('div', attrs={"class":"tide_flex_start"})
    result = []
    for tide_day in tide_days.findChildren("div" , recursive=False):
        # get date
        date_str = tide_day.find('h4', attrs={"class":"tide-day__date"}).text
        date_str = date_str[date_str.find(':') + 1:].strip()
        date = datetime.strptime(date_str, '%A %d %B %Y')

        # tide data
        tides = tide_day.find('table', attrs={"class":"tide-day-tides"})
        headers = [header.text for header in tides.find_all('th')]
        tides_data = [{headers[i]: cell.text for i, cell in enumerate(row.find_all('td'))} for row in tides.find_all('tr')]
        tides_result = []
        for tide in tides_data:
            if tide == {}:
                continue
            try:
                time_str = tide['Time (PST)& Date']
                time_str = time_str[:time_str.find('(')].strip()
                time_data = datetime.strptime(time_str, '%I:%M %p')
                tides_result.append(TideInfo(time_data, tide['Height'], tide['Tide']))
            except:
                # print('Error parsing tide data')
                continue


        # sun and moon data
        sun_moon = tide_day.find('table', attrs={"class":"not-in-print tide-day__sun-moon"})
        sun_moon_data = [[cell.text for i, cell in enumerate(row.find_all('td'))] for row in sun_moon.find_all('tr')]

        sunrise = ''
        sunset = ''
        for sm in sun_moon_data[0]:
            if 'Sunrise' in sm:
                time_str = sm[sm.find(':') + 1:].strip()
                sunrise = datetime.strptime(time_str, '%I:%M%p')
            if 'Sunset' in sm:
                time_str = sm[sm.find(':') + 1:].strip()
                sunset = datetime.strptime(time_str, '%I:%M%p')
        
        result_json = TidesData(date, sunrise, sunset, tides_result)
        result.append(result_json)

    return result, None

def filter_day_tide_data(data):
    result = []
    for day in data:
        sunrise = day.sunrise
        sunset = day.sunset
        tides = day.tides
        date = day.date

        tides_filtered = []
        for tide in tides:
            tide_time = tide.time
            if tide_time > sunrise and tide_time < sunset:
                tides_filtered.append(tide)

        result.append(TidesData(date, sunrise, sunset, tides_filtered))
    return result
        


def print_result(location, day_tide_data):
    print('-------------------------------------')
    print('Tide Data for ' + location)
    for day in day_tide_data:
        print(day.date)
        for tide in day.tides:
            print(tide)

if __name__ == "__main__":
    inputs = [
        ('https://www.tide-forecast.com/locations/Half-Moon-Bay-California/tides/latest', 'Half Moon Bay')
    ]

    for url, location in inputs:
        data, err = parse_page(url)
        if err != None:
            print(err)
            continue

        day_tide_data = filter_day_tide_data(data)
        print_result(location, day_tide_data)