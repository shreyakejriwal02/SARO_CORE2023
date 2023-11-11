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
- Building data linked to sub area and area zones
- Rescue team database
  - This includes the types of teams, no. of members in each team and their competencies
  - It also includes the list if possible actions each team can take and how they linked with building damage states
  - https://www.insarag.org/capacity-building/capacity-intro/

## Data Processing
- The first step is to check the dependencies and install all the relevant libraries as shown in requirements.txt
- Input the address of the desired area for visualization and processing.
```
addresses = ['Sarıgüllük Mahallesi', 'Gazi Mah., Gaziantep', 'Pancarlı Mahallesi']
```
- Using OpenStreetMaps and Matplotlib library visualise the desired area.
  
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/ca4fdce0-4d6e-488a-96a6-53424b3e4573)
- Import earthquake data (accg, pga, sa03, sa06, sa10, time) from the available dataset of past earthquakes
- Import buildings on the addresses mentioned earlier and call the function to add earthquake attribute to buildings for processing damage states and other impacts.
- Visualise the damage states, occupancy and building_typology for one area to understand distribution of data and characteristics.
  
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/426b92bc-7d44-4d5a-9039-cb11e2ca5836)
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/ae4e9ad0-ac1d-41af-82fb-e54943649570)
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/d9139815-d7c8-4dfe-8ad3-b0faa3fe876b)
- Divide the area into multiple sub areas, generating the priority weight for each building, sub area and area.
  
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/7611564b-f6ff-4600-b3f2-815a5007a298)
- Allocate teams to areas based of input of number of teams. This is a user input. The different team types have been mentioned earlier in the document. This is done via a factored weight approach matching the demand of an area to the competency score of teams.
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
- 
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/2e8021ff-2547-4773-b184-67fc8220b77e)
![image](https://github.com/shreyakejriwal02/SARO_CORE2023/assets/146780231/6b9d8b7b-4ac7-46e7-82c6-e00ce39c8e4d)

## Known issues


## Credits
Bo Valkenburg, Brent Smeekes, Pavan Sathyamurthy, Shreya Kejriwal.

The project is part of a master's quarter project at TU Delft, The Netherlands
Course Name: CORE (COmputational REpertoire for Architectural Design and Engineering)

Feel free to contribute, report issues, or provide feedback!
