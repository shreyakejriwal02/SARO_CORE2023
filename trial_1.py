import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from shapely.geometry import Polygon

competency_action_dict = {
        # Structural Rescue
        "Structural Rescue level 1":[
            "Size-up and Scene Safety",
            "Casualty Assessment and Basic Medical Care",
            "Shoring and Stabilization (Basic)",
            "Safe Access and Egress"
        ],
        "Structural Rescue level 2":[
            "Advanced Scene Assessment",
            "Advanced Medical Care and Triage",
            "Advanced Shoring Techniques",
            "Complex Casualty Extrication"
        ],
        "Structural Rescue level 3":[
            "Command and Coordination",
            "Multiple Collapse Points",
            "Advanced Shoring and Heavy Machinery",
            "Urban Search and Rescue (USAR) Techniques"

        ],
        # Trench Rescue
        "Trench Rescue level 1":[
            "Scene Assessment and Safety",
            "Hazard Recognition",
            "Casualty Assessment and Basic Care",
            "Trench Shoring and Stabilization (Basic)"
        ],
        "Trench Rescue level 2":[
            "Advanced Hazard Recognition",
            "Advanced Shoring and Trench Box Systems",
            "Casualty Packaging and Extrication",
            "Equipment Operation"
        ],
        "Trench Rescue level 3":[
            "Incident Command and Coordination",
            "Multiple Casualties and Complex Trench Configurations",
            "Technical Trench Rescue:",
            "Integrate with Other Disciplines"
        ],
        # Technical Rope Rescue
        "Technical Rope Rescue level 1":[
            "Knot Tying",
            "Anchor Systems",
            "Ascending and Descending",
            "Rigging and Mechanical Advantage"
        ],
        "Technical Rope Rescue level 2":[
            "Advanced Knot Tying",
            "Complex Rope Systems",
            "Difficult Access",
            "Confined Space Rope Rescue"
        ],
        "Technical Rope Rescue level 3":[
            "Dynamic Environments:",
            "Rope-Based Confined Space Rescue",
            "Advanced Anchoring and Rigging:"
        ],
        # Confined Space Rescue
       "Confined Space Rescue level 1":[
            "Confined Space Hazard Assessment",
            "Safe Entry and Exit",
            "Retrieval Systems and Equipment",
            "Air Monitoring and Ventilation"
        ],
        "Confined Space Rescue level 2":[
            "Advanced Confined Space Entry",
            "Specialized Confined Space Equipment",
            "Air Monitoring and Ventilation (Advanced):",
            "Advanced Patient Care"
        ],
        "Confined Space Rescue level 3":[
            "Complex and Hazardous Incidents",
            "Leadership and Incident Command",
            "Integration with Other Disciplines"
        ],
        # HazMat Rescue
        "HazMat Rescue level 1":[
            "Hazard Identification",
            "Personal Protective Equipment (PPE):",
            "Decontamination Procedures",
            "Sampling and Analysis"
        ],
        "HazMat Rescue level 2":[
            "Advanced Hazard Recognition",
            "Advanced PPE",
            "Advanced Decontamination Techniques",
            "Detailed Hazardous Material Sampling and Analysis"
        ],

        "HazMat Rescue level 3":[
            "Large-Scale Incidents",
            "Incident Command and Coordination",
            "Environmental Protection",
            "Public Relations and Media Management"
        ], 
        # Heavy Rigging Rescue
        "Heavy Rigging level 1":[
            "Equipment Familiarization",
            "Basic Rigging Techniques",
            "Safe Operation",
            "Safety Protocols"
        ],
        "Heavy Rigging level 2":[
            "Advanced Equipment Operation",
            "Complex Rigging Configurations",
            "Load Handling and Balance",
            "Safety Risk Management"
        ],
        "Heavy Rigging level 3":[
            "High-Risk Scenarios",
            "Coordination and Incident Command",
            "Integrate with Other Disciplines"
        ],
    } 

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
        self.cleared = False
        # create a list of random required actions
        action_lists = competency_action_dict.values()
        actions = []
        for action_list in action_lists:
            for action in action_list:
                actions.append(action)
        self.required_actions = random.sample(actions, random.randint(3, round(len(actions) / 6)))
        self.clear_time = None
        

    def add_building(self, building):
        self.buildings.append(building)
        building.sub_areas = self
        self.clear_time = np.sum([o.clear_time for o in self.buildings])
        self.priority_weight = (np.sum([o.priority_weight for o in self.buildings])) / (self.clear_time)
        
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

        self.clear_time = 45 # in minutes, estimated from certain criteria
        
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

        self.total_competence = None
        self.rem_time = 1440 # time in minutes

        self.action_counts = None
        self.serveable_sub_areas = []
        
        self.sub_area = None
        self.sub_area_priority = None
        
    def add_team_member(self, team_member):
        self.team_members.append(team_member)
        team_member.sub_team = self
        team_member.team = self.team
        self.competence = random.randint(1, 100) #np.average([o.competence for o in self.team_members]) # NEED TO UPDATE THIS SO IT IS BASED ON ACTION COUNTS
    
    def assign_sub_area(self, sub_area):
        self.sub_area = sub_area
        sub_area.sub_team = self
    
    # should probably remove the return of these functions and store the values in the object   
    def calculate_action_counts(self):
        # Initialize an empty dictionary to store the actions and their counts
        action_counts = {}

        # Iterate through the team members in the sub_team
        for team_member in self.team_members:
            # Set actions based on competency levels
            team_member.set_actions()
            # Get available actions for the member
            actions = team_member.get_available_actions()

            for action_list in actions.values():
                for action in action_list:
                    # If the action is not in the dictionary, add it with a count of 1
                    if action not in action_counts:
                        action_counts[action] = 1
                    else:
                        # If the action is already in the dictionary, increment its count by 1
                        action_counts[action] += 1
        return action_counts

    def calculate_total_competence(self, weights):
        # If the weights are not provided, set them to 0
        if not weights:
            return 0
        # Initialize the overall competence to 0
        self.total_competence = 0

        for team_member in self.team_members:
            # Calculate the weighted sum of competence levels for each skill
            competence = sum(team_member.competence_struc) * weights['struc'] + \
                        sum(team_member.competence_trench) * weights['trench'] + \
                        sum(team_member.competence_rope) * weights['rope'] + \
                        sum(team_member.competence_conf_space) * weights['conf_space'] + \
                        sum(team_member.competence_hazmat) * weights['hazmat'] + \
                        sum(team_member.competence_rigging) * weights['rigging']
            self.total_competence += competence

class Team_Member:
    def __init__(self, team_member_id):
       
        mylist_0 = [1, 2, 3]
        mylist_1 = [0, 1, 2, 3]

        self.team_member_id = team_member_id
        
        self.competency_action_dict = competency_action_dict  # Pass the dictionary
        self.competence_struc = random.choices(mylist_0, weights=[1, 2, 1])
        self.competence_trench = random.choices(mylist_1, weights=[3, 1, 1, 1])
        self.competence_rope = random.choices(mylist_1, weights=[3, 1, 2, 1])
        self.competence_conf_space = random.choices(mylist_1, weights=[4, 2, 2, 1])
        self.competence_hazmat = random.choices(mylist_1, weights=[5, 2, 1, 1])
        self.competence_rigging = random.choices(mylist_1, weights=[6, 2, 1, 1])
        self.available_actions = None

        self.sub_team = None
        self.team = None
    
    def set_actions(self):
        # Set actions based on competence levels

        # For each type of rescue, fetch the corresponding list of actions from the competency_action_dict
        self.actions_struc = self.competency_action_dict.get(f"Structural Rescue level {self.competence_struc[0]}", [])
        self.actions_trench = self.competency_action_dict.get(f"Trench Rescue level {self.competence_trench[0]}", [])
        self.actions_rope = self.competency_action_dict.get(f"Technical Rope Rescue level {self.competence_rope[0]}", [])
        self.actions_conf_space = self.competency_action_dict.get(f"Confined Space Rescue level {self.competence_conf_space[0]}", [])
        self.actions_hazmat = self.competency_action_dict.get(f"HazMat Rescue level {self.competence_hazmat[0]}", [])
        self.actions_rigging = self.competency_action_dict.get(f"Heavy Rigging level {self.competence_rigging[0]}", [])
        
    def get_available_actions(self):
        # Create an empty dictionary to store available actions for different rescue types
        available_actions = {
            "Structural Rescue": [],
            "Trench Rescue": [],
            "Technical Rope Rescue": [],
            "Confined Space Rescue": [],
            "HazMat Rescue": [],
            "Heavy Rigging": [] }

        # Include actions for the current competence level in the dictionary "available_actions"
        available_actions["Structural Rescue"].extend(self.actions_struc)
        available_actions["Trench Rescue"].extend(self.actions_trench)
        available_actions["Technical Rope Rescue"].extend(self.actions_rope)
        available_actions["Confined Space Rescue"].extend(self.actions_conf_space)
        available_actions["HazMat Rescue"].extend(self.actions_hazmat)
        available_actions["Heavy Rigging"].extend(self.actions_rigging)
        
        # Since the dictoinary only includes its current competence level, we need to add actions for lower competence levels
        # Include actions for competence levels 1 if competence level is 2 or 3
        if self.competence_struc[0] > 1:
            available_actions["Structural Rescue"].extend(self.competency_action_dict.get(f"Structural Rescue level 1", []))
        if self.competence_trench[0] > 1:
            available_actions["Trench Rescue"].extend(self.competency_action_dict.get(f"Trench Rescue level 1", []))
        if self.competence_rope[0] > 1:
            available_actions["Technical Rope Rescue"].extend(self.competency_action_dict.get(f"Technical Rope Rescue level 1", []))
        if self.competence_conf_space[0] > 1:
            available_actions["Confined Space Rescue"].extend(self.competency_action_dict.get(f"Confined Space Rescue level 1", []))
        if self.competence_hazmat[0] > 1:
            available_actions["HazMat Rescue"].extend(self.competency_action_dict.get(f"HazMat Rescue level 1", []))
        if self.competence_rigging[0] > 1:
            available_actions["Heavy Rigging"].extend(self.competency_action_dict.get(f"Heavy Rigging level 1", []))

        # Include actions for competence level 2 if competence level is 3
        if self.competence_struc[0] == 3:
            available_actions["Structural Rescue"].extend(self.competency_action_dict.get(f"Structural Rescue level 2", []))
        if self.competence_trench[0] == 3:
            available_actions["Trench Rescue"].extend(self.competency_action_dict.get(f"Trench Rescue level 2", []))
        if self.competence_rope[0] == 3:
            available_actions["Technical Rope Rescue"].extend(self.competency_action_dict.get(f"Technical Rope Rescue level 2", []))
        if self.competence_conf_space[0] == 3:
            available_actions["Confined Space Rescue"].extend(self.competency_action_dict.get(f"Confined Space Rescue level 2", []))
        if self.competence_hazmat[0] == 3:
            available_actions["HazMat Rescue"].extend(self.competency_action_dict.get(f"HazMat Rescue level 2", []))
        if self.competence_rigging[0] == 3:
            available_actions["Heavy Rigging"].extend(self.competency_action_dict.get(f"Heavy Rigging level 2", []))

        return available_actions


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

# read the action dictionary and create a list of actions
action_lists = competency_action_dict.values()
actions = []
for action_list in action_lists:
    for action in action_list:
        actions.append(action)

# create a list of random actions
random_items = random.sample(actions, random.randint(4, round(len(actions) / 5)))
