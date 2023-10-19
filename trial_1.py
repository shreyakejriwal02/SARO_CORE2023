import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

# # import building polygons and road network from GIS data

# # create a centroid for each building polygon
# def centroid(x, y):
#     # sum of all x coordinates divided by number of x coordinates
#     # sum of all y coordinates divided by number of y coordinates
#     x = np.array(x)
#     y = np.array(y)
#     centroid_x = np.sum(x)/len(x)
#     centroid_y = np.sum(y)/len(y)
#     return centroid_x, centroid_y

# # create a building class with multiple attributes
# class Building:
#     def __init__(self, id, x_coordinate, y_coordinate, structure_type, functionality, plan_area, height, age):
#         self.id = id    # from GIS data
#         self.x_coordinate = x_coordinate    # from centroid_x
#         self.y_coordinate = y_coordinate    # from centroid_y
#         self.structure_type = structure_type
#         self.functionality = functionality
#         self.plan_area = plan_area  # ground cover in square meters
#         self.height = height
#         self.age = age  # from completion date

#     # find building damage states
#     def damage_state(self, damage_state):
#         self.damage_state = damage_state

# # calculate estimated number of people in each building
# # calculate estimated number of trapped people
# # define severity levels
# # calculate number of people in each severity level
# # determine type of actions required for each building

# # create a rescue team class with multiple attributes
# class RescueTeam:
#     def __init__(self, id, x_coordinate, y_coordinate, main_team, skill_level, allocation_type, capacity):
#         self.id = id
#         self.main_team = main_team
#         self.x_coordinate = x_coordinate
#         self.y_coordinate = y_coordinate 
#         self.skill_level = skill_level
#         self.allocation_type = allocation_type  # preemption type (full, partial, none)
#         self.capacity = capacity    # number of people it can rescue
    
#     # create sub class of individual rescue team members
#     class Member:
#         def __init__(self, id, skill_level, capacity):
#             self.id = id
#             self.skill_level = skill_level
#             self.capacity = capacity

# # add rescue team members to rescue team
# member_1 = RescueTeam.Member(1, 1, 1)
# member_2 = RescueTeam.Member(2, 1, 1)
# # matrix of rescue team with SAR actions for each damage state, severity level, and building type

# # create a flow graph for each rescue team (sink, source, edges)
# def flow_graph():
#     # source node
#     # sink node
#     # edges

#     # return flow graph   
#     pass


class Area:
    def __init__(self, area_id, name):
        self.area_id = area_id
        self.name = name
        self.priority_weight = None
        self.sub_areas = []

    def add_sub_area(self, sub_area):
        self.sub_areas.append(sub_area)
        self.priority_weight = np.average([o.priority_weight for o in self.sub_areas]) 

class Sub_Area:
    def __init__(self, sub_area_id):
        self.sub_area_id = sub_area_id
        self.buildings = [] 
        self.area = None
        self.priority_weight = None

    def add_building(self, building):
        self.buildings.append(building)
        building.sub_areas = self
        building.area = self.area
        self.priority_weight = np.average([o.priority_weight for o in self.buildings]) 

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
        
    def add_team_member(self, team_member):
        self.team_members.append(team_member)
        team_member.sub_team = self
        team_member.team = self.team
        self.competence = np.average([o.competence for o in self.team_members])
    
class Team_Member:
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