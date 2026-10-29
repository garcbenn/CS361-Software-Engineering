
import math
import pprint


# Stores information about one event
class Event:
    def __init__(self, name, event_type, lat, lon, time):
        self.name = name
        self.event_type = event_type
        self.lat = float(lat)
        self.lon = float(lon)
        self.time = time

    def __str__(self):
        return f"{self.name}:{self.event_type}:{self.lat}:{self.lon}:{self.time}"


# Calculates the distance between two locations
class DistanceCalculator:
    R = 6378100

    def deg2rad(self, degrees):
        return degrees * math.pi / 180

    def distance(self, lat1, lon1, lat2, lon2):
        dLat = self.deg2rad(lat2 - lat1)
        dLon = self.deg2rad(lon2 - lon1)

        a = math.sin(dLat / 2) ** 2 + \
            math.cos(self.deg2rad(lat1)) * \
            math.cos(self.deg2rad(lat2)) * \
            math.sin(dLon / 2) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return self.R * c


# Manages a collection of events
class EventManager:
    def __init__(self, event_list):
        self.events = []
        self.calculator = DistanceCalculator()

        for event in event_list:
            name, event_type, lat, lon, time = event.split(":")
            self.addEvent(name, event_type, lat, lon, time)

    # Adds a new event
    def addEvent(self, name, event_type, lat, lon, time):
        event = Event(name, event_type, lat, lon, time)
        self.events.append(event)

    # Finds events within a certain distance
    def findEventsNear(self, lat, lon, maxDist=5000):
        nearby = []

        for event in self.events:
            dist = self.calculator.distance(
                lat, lon, event.lat, event.lon
            )

            if dist < maxDist:
                nearby.append(str(event))

        return nearby

    # Finds earthquakes near a city
    def findEarthquakesNear(self, cityName):
        city = None

        for event in self.events:
            if event.event_type == "city" and event.name == cityName:
                city = event

        if city is None:
            return None

        nearby = self.findEventsNear(city.lat, city.lon)

        earthquakes = []

        for event in nearby:
            if event.split(":")[1] == "earthquake":
                earthquakes.append(event)

        return earthquakes


# Starting events
starting_events = [
    "some volcano:volcano:40.12120:-121.3455:21451",
    "some earthquake:earthquake:40.51230:-121.23425:87153",
    "another earthquake:earthquake:39.23890:-120.23985:17354",
    "yet another earthquake:earthquake:39.23223:-120.23125:16524",
    "another volcano:volcano:43.32890:-122.3289:23856",
    "a geyser:geyser:39.23223:-120.23125:-1",
    "Townville:city:44.05645:-121.30812:-1"
]

em = EventManager(starting_events)

em.addEvent("my favorite hotspring", "hotspring", 46.1231, -115.23234, -1)
em.addEvent("Cityton", "city", 40.5232, -121.23453, -1)
em.addEvent("yet another volcano", "volcano", 15.52232, -107.03521, 256923)

x = em.findEventsNear(40.5, -121.2, 163000)
pprint.pprint(x)

print("------------------------")

x = em.findEarthquakesNear("Cityton")
pprint.pprint(x)
