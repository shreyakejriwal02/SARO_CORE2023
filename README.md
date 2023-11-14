# Search and Research Optimization (SARO)
SARO is a search and rescue decision support system for estimating survival rate based on fragility curve based building model and thus efficiently allocating and scheduling resources in this case the rescue teams.

## Overview
In the aftermath of natural disasters like earthquakes, the efficient management of Search and Rescue operations is crucial. Injured people are in need of medical assistance, and time is of the essence, and there are not enough rescue teams for all people in distress. Accurate decision making is challenging given the limited time, resources and chaotic environment. ‘Saro’ is a Decision Support System Tool designed to address or prevent the challenges discussed in the previous page. It helps analyse the situation and make quick computational decisions, creating plans to allocate rescue teams of multiple organizations like Police and Firefighters, Task forces, Urban Search and Rescue Teams, and Volunteers, to various sites of action. The tool also prescribes an optimal sequence of allocation efforts for each team, in order to maximise the number of lives that can be saved, working to achieve the overarching goal:  

> "Minimize loss of life, alleviate suffering and prevent harm by more efficiently locating, rescuing and providing aid to individuals affected by the disaster."

## Installation (Libraries, packages and softwares)
### Dependencies
Make sure you have the following Python libraries installed:

- math
- numpy
- pandas
- matplotlib
- random
- shapely

> [!NOTE]
> Grasshopper in rhino environment is used to visualise some information in 3D layout.


Read below to install the libraries if they are missing.

### PyPI
Install relevant libraries:
```
pip install numpy
pip install pandas
pip install matplotlib
pip install shapely
pip install osmnx
pip install geopandas
pip install scipy
```
## Usage
Step 1: Clone the repository

Step 2: Navigate to the Project Directory to find trial_1.py and functions.py

Step 3: Install all the relevant dependencies

Step 4: Run clean_program.ipynb

## Project set up
The project is set up in two parts:
- Part A: Building & Context Assessment. 
  - In the immediate aftermath of the earthquake, the tool computes the probable damages and injuries incurred in buildings using theoretical models and heuristics. 

- Part B: Search and Rescue resource allocation and scheduling.
A two-phased framework is set up in order to optimally allocate resources.
  - Phase one relies on data gathered from part A and uses a ‘priority weighting method’ to estimate the ‘criticality’ of sites, allowing the allocation of first responders’ capabilities in the initial 24 hours. 
  - Phase two starts when real-time updates from drones, satellites, recon teams or other sources are received on building conditions and trapped victims. This information guides the preparation of a second phase response, including international specialized teams. The tool aims to optimize resource allocation by matching rescue competence to site requirements and providing a time-sensitive itinerary for response.

## Input data
As a proof of concept, we will apply our framework on a case study on the Turkish city of Gaziantep. We will consider three areas of Gaziantep for our framework:
- Pancarlı Mahallesi
- Gazi Mahallesi Muhtarlığı
- Sarıgüllük Mahallesi

### Part A Building & Context Assessment
The first part of the project pertains to trying to understand the problem. In this case, it means to gather data as quickly as possible about:
- The damages incurred by the buildings in the aftermath of the earthquake,
- The injuries suffered by the building occupants as a result of the above.

The actual surveilled data about injuries and building damages is a collection process that can take hours or days (and is beyond the scope of this project). This means that for a rapid response, the tool must have a  mechanism to predict or project the probable damages and injuries incurred, to facilitate a first phase of prompt SAR response.

Input data used for this process is:
- Earthquake data
  - This is a key parameter of the earthquake damage estimation- in this case we primarily use the Intensity Measures. This data is usually available minutes after an earthquake strikes. This data is saved in function called arthquake data which takes these data types for formulation (accg, pga, sa03, sa06, sa10, time). 
- Building data
  Building data is required to model the physical entities during the earthquake and measure the impact on its properties. In our case due to lack of formal data sources, distribution of data was used to create synthetic data from ESRM. The building data includes:
  - Site coordinates and geometry
  - Building area, height, typology
  - Primary building material
  - Occupancy at different times of the day
- HAZUS code for damage estimation
  - Data regarding damage states, injuries and occupancy is derived from this manual.
  - https://www.fema.gov/flood-maps/tools-resources/flood-map-products/hazus/user-technical-manuals

### Part B Search and Rescue resource allocation and scheduling
The second part of the project is in the aftermath of an earthquake, the allocation and scheduling of resources, particularly the deployment of rescue teams, play a pivotal role in mitigating casualties and minimizing damage. This means that rapid and accurate computing is required for:
- Allocating rescue teams to areas and sub areas
- Creating a detailed schedule for teams to know the sequence of buildings to go to.

Input data used for this process is:
- Building data linked to sub area and area zones. This will also include damage state and injury profile data from the previous part.
- Rescue team database
  - This includes the types of teams, no. of members in each team and their competencies
  - It also includes the list of possible actions each team can take and how they linked with building damage states. Each building in a certain damage state, height and typology has a set of actions associated to it. Currently these are synthetic but in future it would be from site inspection and better predicting models.
  - https://www.insarag.org/capacity-building/capacity-intro/

## Data Processing
- The first step is to check the dependencies and install all the relevant libraries as shown in requirements.txt
- Open the clean_program.py to see the example for the entire part A and part B process. Start with importing all the relevant libraries
- Input the address of the desired area for visualization and processing, in this case the following areas were visualised and processed.
```
addresses = ['Sarıgüllük Mahallesi', 'Gazi Mah., Gaziantep', 'Pancarlı Mahallesi']
```
- Using OpenStreetMaps and Matplotlib library we visualise the desired area in the python file.
![all_areas](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/26617910-9b16-4b48-9962-d4e83f31e3a7)

- Next we import the earthquake data in this format (accg, pga, sa03, sa06, sa10, time) from the available dataset of past earthquakes. In this particular case, the earthquake in Turkey was used.
```
Turkey_Feb2023_Quake= Earthquake(9.8, 0.49, 0.98, 0.98, 1.2, 400)
```
- Import buildings on the addresses mentioned earlier and call the function to add earthquake attribute to buildings for processing damage states and other impacts. We first visualise the base data like occupancy, structural_system and building_typology for one area to understand distribution of data and characteristics.
Building geometry: 
![all_geometry](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/58da1ff8-a2a4-4a4f-85be-d13e3014a4e0)
Occupancy:
![occupancy_type](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/a43949ea-c120-4ace-a8a7-ba145514d075)
Structural system:
![structural_systems](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/50fa561b-df37-4aab-b006-6f638958195c)

- Next we divide the area into multiple sub areas, generating the damage state and injury distribution.
![all_sub_areas](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/48478800-c7bb-45e4-b477-52e57c5f85ac)
Damage state distribution in an area:
![damage_states](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/c04b747f-2468-42d2-8006-e355e8706a32)
Overall injury profile in an area:
![injuries](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/552dee35-d325-4714-ac4f-2e5803ce86fc)

  - Injury class 0
    ![injury0](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/5c7985fd-96ab-41e9-aaa1-fb83c0aac292)
  - Injury class 1
    ![injury1](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/fc59d7b7-9918-47f4-b654-fbf57e98b170)
  - Injury class 2
    ![injury2](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/7e24a7f1-2f75-4132-9229-3ebc50b9be00)
  - Injury class 3
    ![injury3](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/6923beb9-b799-42b5-8b72-b2e8fc2a6053)
  - Injury class 4
    ![injury4](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/bf91d8c6-0e97-4566-bfef-b465fe69a5b5)

- We later use the damage state distribution and injury weights to generate priority weight for each building, sub area and area
![priority_weight](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/88918fce-fafd-468a-ae04-07ef625ebb75)

- Allocate teams to areas based of input of number of teams. This is a user input. It depends on the distribution of teams available when creating the allocation and scheduling. The different team types have been mentioned earlier in the document. This is done via a factored weight approach matching the demand of an area to the competency score of teams.
- Retrieve the sub_teams from the teams object that are allocated to a particular area to generate a list of area-sub_team relationship.
- Select a sub_team from the generated rooster and check for all the possible actions the team can take and its overall competency score for phase 1.
```
The phase1 overall competence weight of sub_team 0 is: 18.0
------------------------------
Command and Coordination: 1
Multiple Collapse Points: 1
Advanced Shoring and Heavy Machinery: 1
...
Advanced Knot Tying: 1
Complex Rope Systems: 1
Difficult Access: 1
Confined Space Rope Rescue: 1
Knot Tying: 3
...
```
- Using allocate_sub_team_phase1 function find the best match for the sub teams to the sub areas.
```
------------------------------
sub_team 5 assigned to sub_area <trial_1.Sub_Area object at 0x000002A756FF9F40>
amount of cleared buildings in area: 6
------------------------------
sub_team 4 assigned to sub_area <trial_1.Sub_Area object at 0x000002A756FF9700>
amount of cleared buildings in area: 12
------------------------------
sub_team 4 assigned to sub_area <trial_1.Sub_Area object at 0x000002A756FF9520>
amount of cleared buildings in area: 15
------------------------------
```
- We can then see which sub teams are allocated to which sub area within an area. It also shows how many buildings the team was able to clear.
![allocated_to](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/28730acd-217a-403e-b07a-72849066459c)
![buildings_cleared_by_sub_team](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/30f1a808-7f17-4c15-b38c-6de0fd001fcf)

- We use the same approach for phase 2 allocation
![allocated_to_p2](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/e3fb8bb7-6f1e-4c9d-bfa4-b7e30f2bc6f4)

- For the next part of the program we find the time required to save a person in a certain building using a predefined mathematical formulation.
![rescue_duration_person](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/1e810501-f056-43af-b155-7d60d8d24dfe)

- Using the simulation based algorithm we can define the number of simulations providing us with the best sequence for the team with their score, lives saved and time taken
```
Top 1 Sequence Score: 193.5
Total Rescued: 97
Total Rescue Time: 497
  Building ID: 10
  Initial People Count: [1, 1, 0, 0]
  Rescue distribution: [0, 0, 0, 0]
  Total Rescued: 0
  Total Rescue Time (in minutes): 0
--------------------
  Building ID: 8
  Initial People Count: [8, 4, 1, 2]
  Rescue distribution: [4, 3, 0, 1]
  Total Rescued: 8
  Total Rescue Time (in minutes): 46
--------------------
  Building ID: 6
  Initial People Count: [36, 18, 4, 9]
  Rescue distribution: [21, 13, 3, 8]
  Total Rescued: 45
  Total Rescue Time (in minutes): 173
  ...
```

- Using the result we plot them in a gantt chart to see the movement of team from one place to other. We also use the top 5 results rather than just the first one due to different focus based on real time situation.
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/1fe88ea7-23b2-434a-a096-3540ad150831)

## Known issues
### Capacity curves instead of fragility Curves:
Instead of prbabilistic fragility curves, it might be possible to simplify the building set into a SDOF model and apply the eartquake parameter as a demand spectrum for each building. It would better capture the nonlinear seismic behaviour of buildng materials and components, and take into accont the frequency parameters of the earthquake better.

### Probabilistic Estimation of Lives not advisable for SAR scheduling
Speaking of real data, it is important to take a step back... fragility curves are likely to provide a good estimatioon of PROBABLE damage states and injuries. This means that the larger the set of buildings in consideration, the closer the estimate.

### Lack of Data Validation:
The initial phase of the allocation process relies entirely on simulation results derived from Part A analysis. In real-world scenarios, this methodology may pose risks, potentially leading to the deployment of
teams to unsuitable locations or overlooking buildings erroneously classified, thereby jeopardizing team safety.

### Unforeseen Changes on Site:
In a disaster scenario, the most significant factor is the continually changing dynamics on site. The situation evolves over time periods, necessitating a robust system capable of updating and adapting to the
changing scenarios involving the site, teams, and resources. Eg. risk of secondary disasters, or critical rescue process.

## More details
For additional information on the process and research please check out the report in the report folder.

## Credits
Bo Valkenburg, Brent Smeekes, Pavan Sathyamurthy, Shreya Kejriwal.

The project is part of a master's quarter project at TU Delft, The Netherlands
Course Name: CORE (COmputational REpertoire for Architectural Design and Engineering)

Feel free to contribute, report issues, or provide feedback!
