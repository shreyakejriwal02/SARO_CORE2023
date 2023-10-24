  <<<<<<< bsmeekes-patch-1
  ### Create area and sub-area class and link buildings in building class to it

  class Area:
      def __init__(self, area_id, name):
          self.area_id = area_id
          self.name = name
          self.sub_areas = []

      def add_sub_area(self, sub_area):
          self.sub_areas.append(sub_area)

  class Sub_Area:
      def __init__(self, sub_area_id, name):
          self.sub_area_id = sub_area_id
          self.name = name
          self.buildings = [] 
          self.area = None

      def add_building(self, building):
          self.buildings.append(building)
          building.sub_areas = self
          building.area = self.area

  class Building:
      def __init__(self, building_id, x_coordinate, y_coordinate, structure_type, functionality, plan_area, height, age):
          self.building_id = building_id    # from GIS data
          self.geometry = None   # from GIS data
          self.x_coordinate = x_coordinate    # from centroid_x
          self.y_coordinate = y_coordinate    # from centroid_y
          self.structure_type = structure_type
          self.functionality = functionality
          self.plan_area = plan_area  # ground cover in square meters
          self.height = height
          self.age = age  # from completion date
          self.area = None  # Reference to the Area object containing this building
          self.sub_area = None  # Reference to the SubArea object containing this building
          # self.priority_index = priority_index    # based on PI-USAR formula

  # We want to link buildings to sub areas based on a grid so we need to plot the buildings on a grid
  # We can use the x and y coordinates to plot the buildings on a grid
  # We create a grid layout in the graph
  # Each grid cell is a sub area
  # Assign buildings to sub areas based on the grid cell they are in
  # Same for area level

  \\\\\\\\
  Output: A dataset of buildings with attributes linked to a sub area which is ultimately linked to a area
  \\\\\\\\


  ### Part A analysis and visualisation

  \\\\\\\\
  Output: 
  - A dataset of buildings with attributes linked to a fragility curve, damage state, trapped people, injtuy profile
  - Create density maps for each type of findings
  \\\\\\\\


  ### Creating a rescue team database

  # define class for each rescue team:
  class Heavy_rescue_team:
      def __init__(self, team_id, cummulative_skill_level):
          self.team_id = team_id
          self.cummulative_skill_level = cummulative_skill_level

  # define subclass for different people in each team:
  class Member(Heavy_rescue_team):
      def __init__(self, member_id, x_coordinate, y_coordinate, skill_type, skill_level, allocation_type, associated_equipment):
          super().__init__(team_id, cumulative_skill_level)   # call parent class
          self.member_id = member_id
          self.x_coordinate = x_coordinate
          self.y_coordinate = y_coordinate
          self.skill_type = skill_type    # skill  that it can perform (structure, rope, etc)
          self.skill_level = skill_level  # Level 1, 2, 3 [is time to complete a task associated with levels?]
          self.allocation_type = allocation_type  # full (stay for complete op) or partial (can move to other site mid op)
          self.associated_equipment = associated_equipment

  # Create entries to create types of teams
  rescue_technician_1 = Heavy_rescue_team.Member(...)
  rescue_technician_2 = Medium_rescue_team.Member(...) 
  ...

  \\\\\\\\
  Output: Database of heavy, medium and light team with people of different attributes
  \\\\\\\\


  ### Based on ground search assessment create list of actions needed

  # list of actions to perform for each building
  class actions(Building):
  def __init__(self, actions):
      super().__init__(building_id, x_coordinate, y_coordinate, structure_type, functionality, plan_area, height, age)   # call parent class
      self.actions = actions  # this will be a list of actions

  # Create entries of actions for each building
  actions_building_1 = ['rescue', 'evacuate', 'shelter', 'medical']
  actions_1 = Building.actions(list_1)
  ...

  \\\\\\\\
  Output: A list type of dataset associated with each building
  \\\\\\\\


  ### Identify area priority based on part A building analysis to allocate rescue teams in next steps

  # define priority class: A (very high), B (high), C (moderate), D (low), E (very low)
  # define criterias for prioritization of areas for USAR operations(in Likert scale- 1 : “not important at all”, 2 : “little importance”, 3 : “average importance”, 4 : “very important”, 5 : “extremely important”)
      B # Damage state of building (DS1 to DS5): 4.60
      B # Total number of injured people: 4.53
      B # Severity of injuries (Level 1 to 4): 4.50
      B # Number of trapped people: 4.37
      B # Occupancy at time of earthquake: 4.37 (rated lower than 3 by experts)
      B # Risk level of building (Chance of further collapse or secondary disaster): 3.10
      B # Access time: 1.90 (rated lower than 3 by experts)
      --------------------
      A # Population density in that area: 4.57
      A # Vulnerable population (children, elderly, disabled): 2.30 (rated lower than 3 by experts)
      A # Number of floors: 1.50 (rated lower than 3 by experts)
      A # Summation of B-markers to be added when calculating area priority
  # calculate weights or degree of importance for each criteria using Analytical Hierarchy Process (AHP)

  # define priority weight for each building

  # calculate total priority weight of area based on building priority weight
  # area priority weight = sum of (building priority weight * number of buildings in that priority weight) / number of buildings in area
  for building in area:
      area.priority_weight = sum(building.priority_weight * building.in_priority_weight) / area.number_of_buildings

  \\\\\\\\
  Output: 
  - A priority rating or number for each building
  - A cummulative rating based on building priority list for each area
  \\\\\\\\
  https://www.tandfonline.com/doi/full/10.1080/19475705.2015.1058861


  ### 
  =======
  # CORE2023_SAR
  Search and rescue decision support system for estimating building damage, survival rate and injury profile based on building characteristics.
  Determining the allocation and scheduling of rescue groups and teams after the disaster.
  >>>>>>> main
  