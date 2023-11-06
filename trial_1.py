import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from shapely.geometry import Polygon
import pandas as pd
import re

# Load the Excel file into a pandas ExcelFile object
xls = pd.ExcelFile('damagestates.xlsx')

# Create a dictionary of DataFrames for each damage state
damage_state_data = {}
for ds in ['DS1', 'DS2', 'DS3', 'DS4', 'DS5']:
    damage_state_data[ds] = xls.parse(ds)

# create a list of damage states (DS1 not possible)
damage_states = ['DS2', 'DS3', 'DS4', 'DS5']


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
            "Technical Trench Rescue",
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
            "Dynamic Environments",
            "Rope-Based Confined Space Rescue",
            "Advanced Anchoring and Rigging"
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
            "Air Monitoring and Ventilation (Advanced)",
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
            "Personal Protective Equipment (PPE)",
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

class Earthquake:
    def __init__ (self, accg, pga, sa03, sa06, sa10, time):
        self.accg= accg #acceleration by Gravity
        self.pga= pga
        self.sa03= sa03
        self.sa06= sa06
        self.sa10= sa10
        self.time= time

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
        self.task_force_teams = 0
        self.fire_fighter_teams = 0
        self.police_teams = 0
        self.volunteer_teams = 0

    def add_sub_area(self, sub_area):
        self.sub_areas.append(sub_area)
        sub_area.area = self
        self.priority_weight = np.average([o.priority_weight for o in self.sub_areas])
    
    def add_building(self, building):
        self.buildings.append(building)
        building.area = self

    def _update_priority_weight(self):
        if self.sub_areas:
            self.priority_weight = np.average([o.priority_weight for o in self.sub_areas])

class Sub_Area:
    def __init__(self, sub_area_id, geometry):
        self.sub_area_id = sub_area_id
        self.geometry = geometry
        self.buildings = [] 
        self.area = None
        self.priority_weight = 0
        self.average_occupancy = None
        
        self.sub_team = None
        self.cleared = False

        # create a list of random required actions
        action_lists = competency_action_dict.values()
        actions = []
        for action_list in action_lists:
            for action in action_list:
                actions.append(action)
        self.required_actions = random.sample(actions, random.randint(1, 5))
        self.clear_time = None

    def add_building(self, building):
        self.buildings.append(building)
        building.sub_area = self          
        self._update_priority_weight()
        self.average_occupancy = self._calculate_average_occupancy()
        self.clear_time = np.sum([o.clear_time for o in self.buildings])
        
    def crop_geometry(self):
        self.geometry = self.geometry.intersection(self.area.geometry)

    def _update_priority_weight(self):
            if self.buildings:
                self.priority_weight = np.average([o.priority_weight for o in self.buildings])

    def _calculate_average_occupancy(self):
        if self.buildings:
            total_occupancy = sum(building.occupancy for building in self.buildings)
            return total_occupancy / len(self.buildings)
        return 0.0

class Building:
    def __init__(self, building_id, geometry, center_point, occupancy_type, footprint, structural_system, lateral_resistance, stories, population_day, population_night, damage_state_probabilities, injuries):
        self.building_id = building_id    # from GIS data
        self.geometry = geometry   # from GIS data
        self.center_point = center_point
        self.occupancy_type = occupancy_type
        self.footprint = footprint
        self.structural_system = structural_system
        self.lateral_resistance = lateral_resistance
        self.stories = stories
        self.population_day = population_day
        self.population_night = population_night
        self.damage_state_probabilities = damage_state_probabilities
        self.injuries = list(injuries)
        self.occupancy = sum(injuries)
        
        self.building_typology = None
        self.damage_state = damage_states[self.damage_state_probabilities.index(max(self.damage_state_probabilities))]
        self.set_typology()
        if stories <4:
            self.height_code = 'HBET:1-3'
        elif stories <7:
            self.height_code = 'HBET:4-6'
        elif stories >6:
            self.height_code = 'HBET:7-'
        self.actions = self.get_action_codes()
        if self.actions == []:
            self.safe = True
        else:
            self.safe = False

        self.cleared = False
        self.cleared_by = None
        self.priority_weight = 0
        self.clear_time = 45 # in minutes, estimated from certain criteria
        
        self.area = None  # Reference to the Area object containing this building
        self.sub_area = None  # Reference to the SubArea object containing this building
    
    # create a class method to calculate priority weight for each building in building class
    # this method will be called in the building class
    DS_RATINGS = [0.07, 0.22, 0.29, 0.39]
    SEVERITY_RATINGS = [0.05, 0.14, 0.25, 0.49]

    @classmethod
    def calculate_priority_weight(cls, building):
        ds_rating = cls._calculate_ds_rating(building.damage_state_probabilities)
        rl_rating = cls._calculate_rl_rating(building.damage_state_probabilities, building.occupancy_type, building.stories)
        sev_rating = cls._calculate_sev_rating(building.injuries[1:])
        trp_rating = cls._calculate_trp_rating(building.occupancy, building.sub_area.average_occupancy)

        print(ds_rating, rl_rating, sev_rating, trp_rating)
        building.priority_weight = round(cls._priority_rating(ds_rating, rl_rating, sev_rating, trp_rating),4)

        return building.priority_weight
    
    @staticmethod
    # calculate damage state rating based on damage state list [1, 2, 3, 4, 5]
    def _calculate_ds_rating(damage_state_probabilities):
        # Calculate the damage state rating
        ds_rating = sum(ds * rating for ds, rating in zip(damage_state_probabilities, Building.DS_RATINGS))
        return ds_rating
    
    @staticmethod
    def _calculate_rl_rating(damage_state_probabilities, occupancy_type, stories):
        max_ds3 = max(damage_state_probabilities[1:])
        if (max_ds3 > 0.6) and ((stories > 7) or (occupancy_type == "industrial")):
            return 0.81
        else:
            return 0.19
        
    @staticmethod
    # calculate injury_severity rating based on severity list [1, 2, 3, 4]
    def _calculate_sev_rating(injury_severity):
        injury_weight = sum(injury_severity)
        rating = sum(severity * rating for severity, rating in zip(injury_severity, Building.SEVERITY_RATINGS))
        if injury_weight == 0:
            overall_rating = 0
        else: 
            overall_rating = rating / injury_weight
        return round(overall_rating, 3)
    
    @staticmethod
    def _calculate_trp_rating(occupancy, average_occupancy):
        if average_occupancy is not None and (occupancy > average_occupancy):
            return 0.7
        else:
            return 0.3
        
    @staticmethod
    def _priority_rating(ds_rating, rl_rating, sev_rating, trp_rating):
        return (0.3 * ds_rating) + (0.2 * rl_rating) + (0.3 * sev_rating) + (0.2 * trp_rating)

    def set_cleared(self):
        self.cleared = True
        self.cleared_by = self.sub_area.sub_team
        if all([(b.cleared or b.safe) for b in self.sub_area.buildings]):
            self.sub_area.cleared = True
    
    def set_typology(self):
        if self.structural_system == 'CR' and self.lateral_resistance == 'LFINF':
            self.building_typology = 'Concrete Frame, Infill Panels'
        elif self.structural_system == 'CR' and self.lateral_resistance == 'LDUAL':
            self.building_typology = 'Concrete Frame, Structural Infill'
        elif self.structural_system == 'CR' and self.lateral_resistance == 'LWAL':
            self.building_typology = 'Concrete Walls'
        elif self.structural_system == 'MUR' and self.lateral_resistance == 'LWAL':
            self.building_typology = 'Unreinforced Masonry'
        elif self.structural_system == 'W' and self.lateral_resistance == 'LWAL':
            self.building_typology = 'Timber'
        elif self.structural_system == 'S' and self.lateral_resistance == 'LFM':
            self.building_typology = 'Steel'
        elif self.structural_system == 'CS' and self.lateral_resistance == 'LFM':
            self.building_typology = 'Construction Site'
    
    def get_action_codes(self):
        try:
            # Get the DataFrame corresponding to the specified damage state
            data = damage_state_data[self.damage_state]

            # Filter the data based on building_typology and height_code
            filtered_data = data[(data['Building typology'] == self.building_typology) & (data['height_code'] == self.height_code)]

            # Check if filtered_data is empty
            if filtered_data.empty:
                return []

            # Extract the action codes into a list based on the condition
            action_codes = [col for col in filtered_data.columns[2:] if filtered_data[col].values[0] == 1]

            return action_codes
        except KeyError:
            return []

       
    
class Team:
    def __init__(self, team_id, team_type):
        self.team_id = team_id
        self.team_type = team_type  # heavy, medium, or light
        self.sub_teams = []

    def add_sub_team(self, sub_team):
        self.sub_teams.append(sub_team)
        sub_team.team = self
        
class Sub_Team:
    def __init__(self, sub_team_id, team_type):
        self.sub_team_id = sub_team_id
        self.team_members = []
        self.team = None
        self.team_type = team_type

        # Define the serveable damage states for each team type
        if self.team_type == 'heavy':
            self.serveable_damage_states = ['DS1', 'DS2', 'DS3', 'DS4', 'DS5']
        elif self.team_type == 'medium':
            self.serveable_damage_states = ['DS1', 'DS2', 'DS3', 'DS4', 'DS5']
        elif self.team_type == 'light':
            self.serveable_damage_states = ['DS1', 'DS2', 'DS3', 'DS4', 'DS5'] 
        elif self.team_type == 'task_force':
            self.serveable_damage_states = ['DS1', 'DS2', 'DS3', 'DS4']    
        elif self.team_type == 'fire_fighter':
            self.serveable_damage_states = ['DS1', 'DS2', 'DS3']                   
        elif self.team_type == 'police':
            self.serveable_damage_states = ['DS1', 'DS2']
        elif self.team_type == 'volunteer':
            self.serveable_damage_states = ['DS1', 'DS2']                    

        self.phase1_competence = None
        self.rem_time = 1440 # time in minutes

        self.action_counts = None
        self.serveable_sub_areas = []
        self.serveable_buildings = []
        
        self.sub_area = None
        self.sub_area_priority = None
        
    def add_team_member(self, team_member):
        self.team_members.append(team_member)
        team_member.sub_team = self
        team_member.team = self.team
        self.competence = random.randint(1, 100) #np.average([o.competence for o in self.team_members]) # NEED TO UPDATE THIS SO IT IS BASED ON ACTION COUNTS
    
    def assign_sub_area(self, sub_area):
        self.sub_area = sub_area
        if sub_area != None:
            sub_area.sub_team = self
    
    # should probably remove the return of these functions and store the values in the object   
    def calculate_action_counts(self):
        action_counts = {}

        for team_member in self.team_members:
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
        self.action_counts = action_counts  # Set the action counts for the sub team
    
    def calculate_phase1_competence(self):
        # Define the phase1_competence weights for each skill
        weights ={
            'struc': 1,                 
            'trench': 0.0,             
            'rope': 0.7,                
            'conf_space': 0.7,         
            'hazmat': 0.7,             
            'rigging': 0.0 
            }            
        phase1_competence = 0
        
        # Calculate the weighted sum of competence levels for each skill
        for team_member in self.team_members:
            competence = sum(team_member.competence_struc) * weights['struc'] + \
                         sum(team_member.competence_trench) * weights['trench'] + \
                         sum(team_member.competence_rope) * weights['rope'] + \
                         sum(team_member.competence_conf_space) * weights['conf_space'] + \
                         sum(team_member.competence_hazmat) * weights['hazmat'] + \
                         sum(team_member.competence_rigging) * weights['rigging']
            phase1_competence += competence
        self.phase1_competence = phase1_competence

class Team_Member:
    def __init__(self, sub_team_member_id, team_type):
        self.sub_team_member_id = sub_team_member_id
        self.team_type = team_type 
        self.sub_team = None
        self.team = None
        
        self.competency_action_dict = competency_action_dict  # Pass the dictionary of actions and competencies to the team member

        # Initiate a list for which competency levels can be achieved by the Team_Memebers
        mylist_0 = [1, 2, 3]
        mylist_1 = [0, 1, 2, 3]
        # Define rules for competence levels based on team type 
        # Every sub_team has a team leader with higher compentece levels 
        if self.team_type == 'heavy' and self.sub_team_member_id == 0:
            self.competence_struc = [3] 
            self.competence_trench = [2]  
            self.competence_rope = [2]   
            self.competence_conf_space = [2]  
            self.competence_hazmat = [2]     
            self.competence_rigging = [2]
        elif self.team_type == 'heavy' and self.sub_team_member_id > 0:
            self.competence_struc = random.choices      (mylist_0, weights=[2, 2, 3])
            self.competence_trench = random.choices     (mylist_1, weights=[3, 2, 1, 1])
            self.competence_rope = random.choices       (mylist_1, weights=[3, 2, 1, 1])
            self.competence_conf_space = random.choices (mylist_1, weights=[3, 2, 1, 1])
            self.competence_hazmat = random.choices     (mylist_1, weights=[3, 2, 1, 1])
            self.competence_rigging = random.choices    (mylist_1, weights=[3, 2, 1, 1])
        elif self.team_type == 'medium' and self.sub_team_member_id == 0:
            self.competence_struc = [3] 
            self.competence_trench = [2]  
            self.competence_rope = [2]   
            self.competence_conf_space = [2]  
            self.competence_hazmat = [2]     
            self.competence_rigging = [2]
        elif self.team_type == 'medium' and self.sub_team_member_id > 0:
            self.competence_struc = random.choices      (mylist_0, weights=[1, 3, 1])
            self.competence_trench = random.choices     (mylist_1, weights=[7, 2, 3, 1])
            self.competence_rope = random.choices       (mylist_1, weights=[7, 2, 3, 1])
            self.competence_conf_space = random.choices (mylist_1, weights=[7, 2, 3, 1])
            self.competence_hazmat = random.choices     (mylist_1, weights=[7, 2, 3, 1])
            self.competence_rigging = random.choices    (mylist_1, weights=[7, 5, 2, 0])
        elif self.team_type == 'light' and self.sub_team_member_id == 0:
            self.competence_struc = [3] 
            self.competence_trench = [2]  
            self.competence_rope = [2]   
            self.competence_conf_space = [2]  
            self.competence_hazmat = [2]     
            self.competence_rigging = [2]
        elif self.team_type == 'light'and self.sub_team_member_id > 0:
            self.competence_struc = random.choices      (mylist_0, weights=[3, 2, 1])
            self.competence_trench = random.choices     (mylist_1, weights=[10, 2, 1, 1])
            self.competence_rope = random.choices       (mylist_1, weights=[10, 4, 2, 1])
            self.competence_conf_space = random.choices (mylist_1, weights=[10, 2, 2, 1])
            self.competence_hazmat = random.choices     (mylist_1, weights=[10, 2, 1, 0])
            self.competence_rigging = random.choices    (mylist_1, weights=[6, 0, 0, 0])
        elif self.team_type == 'police' and self.sub_team_member_id == 0:
            self.competence_struc = [2] 
            self.competence_trench = [1]  
            self.competence_rope = [1]   
            self.competence_conf_space = [1]  
            self.competence_hazmat = [1]     
            self.competence_rigging = [1]
        elif self.team_type == 'police'and self.sub_team_member_id > 0:
            self.competence_struc = random.choices      (mylist_0, weights=[1, 0, 0])
            self.competence_trench = random.choices     (mylist_1, weights=[10, 2, 0, 0])
            self.competence_rope = random.choices       (mylist_1, weights=[10, 3, 0, 0])
            self.competence_conf_space = random.choices (mylist_1, weights=[1, 0, 0, 0])
            self.competence_hazmat = random.choices     (mylist_1, weights=[10, 3, 0, 0])
            self.competence_rigging = random.choices    (mylist_1, weights=[1, 0, 0, 0])
        elif self.team_type == 'fire_fighter' and self.sub_team_member_id == 0:
            self.competence_struc = [3] 
            self.competence_trench = [1]  
            self.competence_rope = [2]   
            self.competence_conf_space = [2]  
            self.competence_hazmat = [1]     
            self.competence_rigging = [1]
        elif self.team_type == 'fire_fighter' and self.sub_team_member_id > 0:
            self.competence_struc = random.choices      (mylist_0, weights=[5, 2, 0])
            self.competence_trench = random.choices     (mylist_1, weights=[5, 3, 0, 0])
            self.competence_rope = random.choices       (mylist_1, weights=[5, 3, 1, 0])
            self.competence_conf_space = random.choices (mylist_1, weights=[5, 3, 1, 0])
            self.competence_hazmat = random.choices     (mylist_1, weights=[1, 0, 0, 0])
            self.competence_rigging = random.choices    (mylist_1, weights=[1, 0, 0, 0])
        elif self.team_type == 'task_force' and self.sub_team_member_id == 0:
            self.competence_struc = [3] 
            self.competence_trench = [2]  
            self.competence_rope = [2]   
            self.competence_conf_space = [2]  
            self.competence_hazmat = [2]     
            self.competence_rigging = [2]
        elif self.team_type == 'task_force' and self.sub_team_member_id > 0:
            self.competence_struc = random.choices      (mylist_0, weights=[6, 3, 0])
            self.competence_trench = random.choices     (mylist_1, weights=[3, 3, 1, 0])
            self.competence_rope = random.choices       (mylist_1, weights=[3, 3, 1, 0])
            self.competence_conf_space = random.choices (mylist_1, weights=[3, 3, 1, 0])
            self.competence_hazmat = random.choices     (mylist_1, weights=[3, 3, 1, 0])
            self.competence_rigging = random.choices    (mylist_1, weights=[1, 0, 0, 0])
        elif self.team_type == 'volunteer' and self.sub_team_member_id <= 1:
            self.competence_struc = [2] 
            self.competence_trench = [1]  
            self.competence_rope = [1]   
            self.competence_conf_space = [1]  
            self.competence_hazmat = [1]     
            self.competence_rigging = [1]  
        # Creates an exception for the volunteer team members because volunteers , expect for their two team leaders. 
        elif self.team_type == 'volunteer' and self.sub_team_member_id > 1:
            self.competence_struc = [1]
            self.competence_trench = [0]  
            self.competence_rope = [0]   
            self.competence_conf_space = [0]  
            self.competence_hazmat = [0]     
            self.competence_rigging = [0]                 
    
    def get_available_actions(self):
        # Create an empty dictionary to store available actions for different rescue types
        self.actions_struc = self.competency_action_dict.get(f"Structural Rescue level {self.competence_struc[0]}", [])
        self.actions_trench = self.competency_action_dict.get(f"Trench Rescue level {self.competence_trench[0]}", [])
        self.actions_rope = self.competency_action_dict.get(f"Technical Rope Rescue level {self.competence_rope[0]}", [])
        self.actions_conf_space = self.competency_action_dict.get(f"Confined Space Rescue level {self.competence_conf_space[0]}", [])
        self.actions_hazmat = self.competency_action_dict.get(f"HazMat Rescue level {self.competence_hazmat[0]}", [])
        self.actions_rigging = self.competency_action_dict.get(f"Heavy Rigging level {self.competence_rigging[0]}", [])

        # Creates an exception for the volunteer team because volunteers are not trained like all other teams, expect for their two team leaders. 
        # Two team leaders are trained, but the other members are only trained in two rescue actions.
        if self.team_type == 'volunteer' and self.sub_team_member_id > 1:
            self.actions_struc = ["Safe Access and Egress", "Casualty Assessment and Basic Medical Care"]
     
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
