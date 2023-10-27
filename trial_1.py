import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from shapely.geometry import Polygon

class Area:
    def __init__(self, area_id, geometry, bbox, name, address, addresstype):
        self.area_id = area_id
        self.geometry = geometry
        self.bbox = bbox
        self.name = name
        self.address = address
        self.addresstype = addresstype
        
        self.priority_weight = None
        self.sub_areas = []
        self.buildings = []

        self.people_requirement = None
        self.heavy_teams = 0
        self.med_teams = 0
        self.light_teams = 0

    def add_sub_area(self, sub_area):
        self.sub_areas.append(sub_area)
        sub_area.area = self
        self.priority_weight = np.average([o.priority_weight for o in self.sub_areas])
    
    def add_building(self, building):
        self.buildings.append(building)
        building.area = self

class Sub_Area:
    def __init__(self, sub_area_id, geometry):
        self.sub_area_id = sub_area_id
        self.geometry = geometry
        self.buildings = [] 
        self.area = None
        self.priority_weight = 0
        self.sub_team = None

    def add_building(self, building):
        self.buildings.append(building)
        building.sub_areas = self
        self.priority_weight = np.average([o.priority_weight for o in self.buildings]) 

    def crop_geometry(self):
        self.geometry = self.geometry.intersection(self.area.geometry)

class Building:
    def __init__(self, building_id, geometry, center_point, building_function):
        self.building_id = building_id    # from GIS data
        self.geometry = geometry   # from GIS data
        self.center_point = center_point
        self.building_function = building_function
        # self.structure_type = structure_type
        # self.plan_area = plan_area  # ground cover in square meters
        # self.height = height
        # self.age = age  # from completion date
        
        self.priority_weight = random.randint(0, 100)
        
        self.area = None  # Reference to the Area object containing this building
        self.sub_area = None  # Reference to the SubArea object containing this building
    
       
    
class Team:
    def __init__(self, team_id, team_type):
        self.team_id = team_id
        self.team_type = team_type  # heavy, medium, or light
        self.sub_teams = []

    def add_sub_team(self, sub_team):
        self.sub_teams.append(sub_team)
        
class Sub_Team:
    def __init__(self, sub_team_id):
        self.sub_team_id = sub_team_id
        self.team_members = []
        self.team = None
        self.competence = None
        self.sub_area = None
        
    def add_team_member(self, team_member):
        self.team_members.append(team_member)
        team_member.sub_team = self
        team_member.team = self.team
        self.competence = np.average([o.competence for o in self.team_members])
    
    def assign_sub_area(self, sub_area):
        self.sub_area = sub_area
        sub_area.sub_team = self

        # 
    def update_action_categories(self):
        self.action_categories = set()

        for member in self.members:
            for action in member['actions']:
                if action in RescueTeam.action_categories:
                    self.action_categories.add(RescueTeam.action_categories[action])

class Team_Member:
    # creates a list of all actions that can be required in a rescue operation
    action_categories = {
    "surface rescue": "level 1 rescue",
    "light debris clean up": "level 1 rescue",
    "low intensity rescue": "level 2 rescue",
    "block debris clean up": "level 2 rescue",
    
    "com. & nav. management": "supply operations",
    "supplies distribution": "supply operations",
    "patrolling and traffic control": "security operations",
    "site management": "security operations",
    "fire hazard": "fire fighting",
    "low rise rope rescue": "fire fighting",
    "first aid": "medical operations",
    "emergency medical services": "medical operations",


    "medium intensity str rescue": "level 3 rescue",
    "medium debris clean up": "level 3 rescue",
    "high intensity str rescue": "level 4 rescue",
    "heavy debris clean up": "level 4 rescue",
    "very high intensity str rescue": "level 5 rescue",
    "hydraulic debris removal": "level 5 rescue",
    "hazardous materials": "hazmat rescue",
    "medium rise rope rescue": "level 3 rescue",
    "high rise rope rescue": "level 4 rescue"
    }

    def __init__(self, team_member_id, competence):
        self.team_member_id = team_member_id
        self.competence = competence
        
        self.sub_team = None 
        self.team = None


# # add a building entry to the building list
# building_1 = Building(1, 1, 1, 1, 1, 1, 1, 1)
# building_2 = Building(2, 2, 2, 2, 2, 2, 2, 2)

# # add buildings to sub areas
# sub_area_1 = Sub_Area(1, "sub_area_1")
# sub_area_1.add_building(building_1)

# sub_area_2 = Sub_Area(2, "sub_area_2")
# sub_area_2.add_building(building_2)

# # add sub areas to areas
# area_1 = Area(1, "area_1")
# area_1.add_sub_area(sub_area_1)
# area_1.add_sub_area(sub_area_2)

# # create a csv file with building data in each sub area and area
# import pandas as pd

# # create a csv file with building data in each sub area and area
# df = pd.DataFrame(columns=["building_id", "sub_area_id", "area_id"])
# # add data to df from building class, subarea class and area class
# for sub_area in area_1.sub_areas:
#     for building in sub_area.buildings:
#         df = pd.concat([df, pd.DataFrame({"building_id": [building.building_id], "sub_area_id": [sub_area.sub_area_id], "area_id": [area_1.area_id]})], ignore_index=True)

# print(df)