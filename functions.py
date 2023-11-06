import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import random
import math
import scipy.stats as stats
from typing import List, Tuple

#--- COLLECT DATA FROM OPEN STREET MAPS---
def assign_building_attributes(buildings_gdf):
    #give buildings area_m2 attribute
    crs_buildings_gdf = buildings_gdf.to_crs(epsg=32637)
    buildings_gdf['area_m2'] = crs_buildings_gdf['geometry'].area
    graph_bldg_flat = buildings_gdf.reset_index()
    # print(graph_bldg_flat.index)

    #FOR NOW WE RANDOMLY ASSIGN ATTRIBUTES TO THE CHOSEN NEIGHBOURHOOD IN GAZIANTEP BASED ON ESRM DATA TO CREATE A FAKE BUILDING ATTRIBUTE DATASET
    #START WITH COMPUTING THE DISTRIBUTION OF BUILDING TYPES IN GAZIANTEP BASED ON ESRM DATA
    exposure_res_turkey= pd.read_excel("Exposure_Model_Turkey_Res.xlsx")
    exposure_com_turkey= pd.read_excel("Exposure_Model_Turkey_Com.xlsx")
    exposure_ind_turkey= pd.read_excel("Exposure_Model_Turkey_Ind.xlsx")

    #total number of residential buildings in Gaziantep:
    condition1= exposure_res_turkey['NAME_1']=='Gaziantep'
    gazresbldgs= int(sum(exposure_res_turkey[condition1].BUILDINGS))
    # print (gazresbldgs)

    #total number of commercial buildings in Gaziantep:
    condition2= exposure_com_turkey['NAME_1']=='Gaziantep'
    gazcombldgs= int(sum(exposure_com_turkey[condition2].BUILDINGS))
    # print (gazcombldgs)

    #total number of industrial buildings in Gaziantep:
    condition3= exposure_ind_turkey['NAME_1']=='Gaziantep'
    gazindbldgs= int(sum(exposure_ind_turkey[condition3].BUILDINGS))
    # print (gazindbldgs)

    #percentage of residential, commercial and industrial buildings in Gaziantep:
    totalbldgs= gazresbldgs+gazcombldgs+gazindbldgs
    percent_gazres= gazresbldgs/totalbldgs
    percent_gazcom= gazcombldgs/totalbldgs
    percent_gazind= gazindbldgs/totalbldgs
    # print(percent_gazres, percent_gazcom,percent_gazind)

    #NOW BASED ON THESE PROPORTIONS WE CAN PROPORTIONALLY ASSIGN OUR GAZIANTEP BUILDING STOCK INTO RESIDENTIAL COMMERCIAL AND INDUSTRIAL TYPES
    #CLASS FOR BUILDING AND DEFINE ATTRIBUTES BASED ON THE RELEVANT PARAMETERS FOR BUILDING CODE CLASSIFICATION

    class Gaz_bldg:
        def __init__ (self_Gaz_bldg, serial, occupancytype, footprint, structural_system, lateral_resistance, code_compliance, height, occuday, occunight):
            self_Gaz_bldg.serial= serial  
            self_Gaz_bldg.occu_type= occupancytype  
            self_Gaz_bldg.footprint= footprint
            self_Gaz_bldg.strsys= structural_system
            self_Gaz_bldg.latres= lateral_resistance
            self_Gaz_bldg.codecomp= code_compliance
            self_Gaz_bldg.height= height
            self_Gaz_bldg.occu_day= occuday
            self_Gaz_bldg.occu_night= occunight
        
    #NOW PREPARE ALL THE GEOMETRY OF THE OSM IMPORT AS OBJECTS OF CLASS GAZ_BLDG, 
    # AND ASSIGN THEM ATTRIBTES BASED ON PREVAILING GAZIANTEP PATTERNS FROM XML AND CSV DATA ANALYSIS

    #ARBITRARY FOR NOW:
    #STRUCTURAL SYSTEM FROM HAND CALCS ON THE EXCEL FILE
    occtyp_statistical =['residential', 'commercial', 'industrial'] #occupancy type
    occtyp_weights = [percent_gazres, percent_gazcom, percent_gazind]

    strsys_statistical=['CR','MUR','W','S'] #structural system
    strsys_weights=[0.732,0.267,0.0007,0.0003]

    latres_statistical=['LFINF','LDUAL','LWAL','LFM'] #lateral forces resisting system
    latres_weights_CR=[0.209, 0.208, 0.583, 0.000]
    latres_weights_MUR=[0.0, 0.0, 1.0, 0.0]
    latres_weights_W=[0.0, 0.0, 1.0, 0.0]
    latres_weights_S=[0.0, 0.0, 0.0, 1.0]

    codecomp_statistical=['CDN', 'CDL', 'CDM', 'CDH'] #building code compliance
    codecomp_weights=[0.1, 0.3, 0.4, 0.2] # based on analysis of Gaziantep data- Approximate 

    ht_statistical=[1,2,3,4,5,6,7,8,9,10,11,12]
    ht_weights=[0.2, 0.15, 0.15, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05] # based on analysis of Gaziantep data- Approximate 

    bldngs = []
    for i in graph_bldg_flat.index:
        occtyp_random = random.choices(occtyp_statistical,weights=occtyp_weights)[0] # here the res, commm, and ind percentages were computed as 0.9283591028593825 0.0534356187548717 0.018205278385745805        
        strsys_random = random.choices(strsys_statistical,weights=strsys_weights)[0]        
        strsys=strsys_random
        
        latres = None
        if strsys=='CR':
            latres=random.choices(latres_statistical,latres_weights_CR)[0]
        elif strsys=='MUR':
            latres=random.choices(latres_statistical,latres_weights_MUR)[0]
        elif strsys=='W':
            latres=random.choices(latres_statistical,[0,0,0,1])[0]
        elif strsys=="S":
            latres=random.choices(latres_statistical, latres_weights_S)[0]
        else:
            latres = 'stinky whoopsie'
        
        codecomp_random = None
        if strsys=='CR' and latres=='LDUAL':
            codecomp_random=random.choices(codecomp_statistical, [0, 0.3, 0.4, 0.3])[0]
        elif strsys=='CR' and latres == 'LWAL':
            codecomp_random=random.choices(codecomp_statistical, [0, 0.3, 0.4, 0.3])[0]
        elif strsys=='MUR':
            codecomp_random=random.choices(codecomp_statistical, [0, 0, 1, 0])[0]
        elif strsys== 'S' and latres=='LFINF':
            codecomp_random=random.choices(codecomp_statistical, [0, 0, 0.4, 0.6])[0]
        elif strsys== 'S' and latres=='LFM':
            codecomp_random=random.choices(codecomp_statistical, [0, 0, 0.4, 0.6])[0]       
        elif strsys== 'S' and latres=='LWAL':
            codecomp_random=random.choices(codecomp_statistical, [0, 0, 0.4, 0.6])[0]   
        elif strsys== 'W':
            codecomp_random=random.choices(codecomp_statistical, [0, 0.3, 0.4, 0.3])[0]   
        else:   
            codecomp_random= random.choices(codecomp_statistical,codecomp_weights)[0]


        ht_random= None #random.choices(ht_statistical,ht_weights)[0]
        if strsys=='CR' and latres=='LFINF': 
            ht_random= random.choices(ht_statistical,[0.3,0.2,0.2,0.1,0.1,0.1,0,0,0,0,0,0])[0]
        elif strsys=='CR' and latres=='LFM': 
            ht_random= random.choices(ht_statistical,[0.3,0.2,0.2,0.1,0.1,0.1,0,0,0,0,0,0])[0]
        elif strsys== "MUR":
            ht_random= random.choices(ht_statistical,[0.3,0.3,0.2,0.1,0.1,0,0,0,0,0,0,0])[0]
        elif strsys== 'W':
            ht_random= random.choices(ht_statistical,[0.3,0.2,0.2,0.1,0.1,0.1,0,0,0,0,0,0])[0]
        else:
            ht_random=random.choices(ht_statistical,ht_weights)[0]

        occu_day = None
        if occtyp_random=='residential':
            occu_day=0.0171
        elif occtyp_random=='commercial':
            occu_day=0.077
        elif occtyp_random=='industrial':
            occu_day=0.087
        else:
            print('we do not know how many people are in these buildings, call the census takers!')

        occu_night = None
        if occtyp_random=='residential':
            occu_night=0.06
        elif occtyp_random=='commercial':
            occu_night=0.005
        elif occtyp_random=='industrial':
            occu_night=0.006
        else:
            print('we do not know how many people are in these buildings, call the census takers!')   

        #now we have a statistically believable distributon of building objcts and attributes for the buildings, and we can make the set of buildings
        bldg = Gaz_bldg(i,occtyp_random, [buildings_gdf['area_m2'][i]], strsys_random, latres ,codecomp_random,ht_random, occu_day, occu_night)
        bldngs.append(bldg)

    #NOW WE CREATE A DATADRAME OF THE GENERATED SYNTHETIC DATA FOR INSPECTION AND CHECKS
    # 1. We convert the list of objects into a dictionary
    bldgobjects = []
    for bldg in bldngs:
        bldgobjects.append({
            'occupancytype' : bldg.occu_type,
            'Footprint' : bldg.footprint[0],
            'structural_system' : bldg.strsys,
            'lateral_resistance' : bldg.latres,
            'code_compliance' : bldg.codecomp,
            'height' : bldg.height,
            'population day' : bldg.occu_day*bldg.footprint[0]*bldg.height,
            'population night' : bldg.occu_night*bldg.footprint[0]*bldg.height
        })
    # print(bldgobjects)
    
    # 2. we create a new dataframe and export it to xlsx
    bldgobjects_dataframe_flat= pd.DataFrame(bldgobjects)
    # bldgobjects_dataframe_flat.to_excel('bldgobjects_flat.xlsx', index=True)
    
    # # NOW WE COMBINE THE RANDOMLY ATTRIBUTED OBJECTS DATAFRAME, TO THE ORIGINAL OSM DATAFRAME TO CREATE ONE BIG DATAFRAME.

    consolidated_bldgdataframe = graph_bldg_flat.merge(bldgobjects_dataframe_flat, left_index=True, right_index=True)
    
    return consolidated_bldgdataframe, bldngs



def assign_fragility_attributes(consolidated_bldgdataframe, bldngs, equake):
    # read the fragility table
    medbetatable= pd.read_excel("core- fragility values simplified.xlsx", sheet_name='Final')
    
    im_values = []
    imtype_values =[]
    median_ds2_values = []
    median_ds3_values = []
    median_ds4_values = []
    median_ds5_values = []
    beta_values=[]

    # Assuming bldngs is a list of buildings with attributes
    for bldg in bldngs:
        # Create a mask for the current building
        mask = (medbetatable['strsys'] == bldg.strsys) & \
            (medbetatable['latres'] == bldg.latres) & \
            (medbetatable['codecomp'] == bldg.codecomp) & \
            (medbetatable['height'] == bldg.height)
        
        # Use the mask to get the dominant IM and Median values for the current building
        im= medbetatable.loc[mask,'IMT'].values
        for i in im:
            if i == 'PGA':
                imvar= equake.pga
            elif i== 'SA(0.3)':
                imvar= equake.sa03
            elif i== 'SA(0.6)':
                imvar= equake.sa06
            elif i== 'SA(1.0)':
                imvar= equake.sa10
            else:
                print ('error retrieving intensity measure!')
                
        if len(im) > 0:
            im_values.append(imvar)

        imtype= medbetatable.loc[mask,'IMT'].values
        for i in imtype:
            if i == 'PGA':
                imvartype= 'PGA'
            elif i== 'SA(0.3)':
                imvartype= 'SA(0.3)'
            elif i== 'SA(0.6)':
                imvartype= 'SA(0.6)'
            else:
                imvartype= 'SA(1.0)'
                
        if len(imtype) > 0:
            imtype_values.append(imvartype)

        median_ds2 = medbetatable.loc[mask, 'Median_DS1'].values
        if len(median_ds2) > 0:
            median_ds2_values.append(median_ds2[0])
        median_ds3 = medbetatable.loc[mask, 'Median_DS2'].values
        if len(median_ds3) > 0:
            median_ds3_values.append(median_ds3[0])        
        median_ds4 = medbetatable.loc[mask, 'Median_DS3'].values
        if len(median_ds4) > 0:
            median_ds4_values.append(median_ds4[0])
        median_ds5 = medbetatable.loc[mask, 'Median_DS4'].values
        if len(median_ds5) > 0:
            median_ds5_values.append(median_ds5[0])
        beta = medbetatable.loc[mask, 'Beta'].values
        if len(beta) > 0:
            beta_values.append(beta[0])        

    # now we append the various mediand and beta columns to the geodataframe
    consolidated_bldgdataframe['IM_dom']= (im_values)
    consolidated_bldgdataframe['IMtype']= (imtype_values)
    consolidated_bldgdataframe['median_ds2']= (median_ds2_values)
    consolidated_bldgdataframe['median_ds3']= (median_ds3_values)
    consolidated_bldgdataframe['median_ds4']= (median_ds4_values)
    consolidated_bldgdataframe['median_ds5']= (median_ds5_values)
    consolidated_bldgdataframe['beta']= (beta_values)
    # consolidated_bldgdataframe.to_excel('consolidated_dataframe.xlsx', index=True)


    #now calculate the probability of damage states
    e= 2.71828
    pi= math.pi

    def p_ds2_compute(row):
        val1= row['median_ds2'] # the median value
        mean= np.log(val1) #mean median relation
        val2= row['beta'] # the beta (logstandard deviation)
        IM= row['IM_dom'] #goes in the x axis
        lognorm_dist= stats.lognorm(scale=np.exp(mean), s=val2)

        result= lognorm_dist.pdf(IM)
        return result

    def p_ds3_compute(row):
        val1= row['median_ds3'] # the median value
        mean= np.log(val1) #mean median relation
        val2= row['beta'] # the beta (logstandard deviation)
        IM= row['IM_dom'] #goes in the x axis
        lognorm_dist= stats.lognorm(scale=np.exp(mean), s=val2)

        result= lognorm_dist.pdf(IM)
        return result
    def p_ds4_compute(row):
        val1= row['median_ds4'] # the median value
        mean= np.log(val1) #mean median relation
        val2= row['beta'] # the beta (logstandard deviation)
        IM= row['IM_dom'] #goes in the x axis
        lognorm_dist= stats.lognorm(scale=np.exp(mean), s=val2)

        result= lognorm_dist.pdf(IM)
        return result
    def p_ds5_compute(row):
        val1= row['median_ds5'] # the median value
        mean= np.log(val1) #mean median relation
        val2= row['beta'] # the beta (logstandard deviation)
        IM= row['IM_dom'] #goes in the x axis
        lognorm_dist= stats.lognorm(scale=np.exp(mean), s=val2)

        result= lognorm_dist.pdf(IM)
        return result

    #append results
    consolidated_bldgdataframe['p_ds2'] = consolidated_bldgdataframe.apply(p_ds2_compute, axis =1)
    consolidated_bldgdataframe['p_ds3'] = consolidated_bldgdataframe.apply(p_ds3_compute, axis =1)
    consolidated_bldgdataframe['p_ds4'] = consolidated_bldgdataframe.apply(p_ds4_compute, axis =1)
    consolidated_bldgdataframe['p_ds5'] = consolidated_bldgdataframe.apply(p_ds5_compute, axis =1)

    def p_ds5_collapse_compute(row):
        val1= row['p_ds5']
        result= row['p_ds5']*0.1
        return result

    consolidated_bldgdataframe['p_ds5_collapse'] = consolidated_bldgdataframe.apply(p_ds5_collapse_compute, axis =1)
    # consolidated_bldgdataframe.to_excel('consolidated_dataframe.xlsx', index=True)
    return consolidated_bldgdataframe, medbetatable



def assign_injury_numbers(consolidated_bldgdataframe, bldngs, medbetatable, equake):
    #now we calculate the actual injury numbers for each building
    ds1_numbers=[]
    ds2_numbers=[]
    ds3_numbers=[]
    ds4_numbers=[]
    ds5_numbers=[]

    # 
    for bldg in bldngs:
        mask = (medbetatable['strsys'] == bldg.strsys) & \
                (medbetatable['latres'] == bldg.latres) & \
                (medbetatable['codecomp'] == bldg.codecomp) & \
                (medbetatable['height'] == bldg.height)   
        pds1n = [float(x) for x in medbetatable.loc[mask, 'injury severity DS1'].values[0].split(',')]
        pds2n = [float(x) for x in medbetatable.loc[mask, 'injury severity DS2'].values[0].split(',')]
        pds3n = [float(x) for x in medbetatable.loc[mask, 'injury severity DS3'].values[0].split(',')]
        pds4n = [float(x) for x in medbetatable.loc[mask, 'injury severity DS4'].values[0].split(',')]
        pds5n = [float(x) for x in medbetatable.loc[mask, 'injury severity DS5+collapse'].values[0].split(',')]
        ds1_numbers.append([pds1n])
        ds2_numbers.append([pds2n])
        ds3_numbers.append([pds3n])
        ds4_numbers.append([pds4n])
        ds5_numbers.append([pds5n])
    consolidated_bldgdataframe['ds1numbers'] = ds1_numbers
    consolidated_bldgdataframe['ds2numbers'] = ds2_numbers
    consolidated_bldgdataframe['ds3numbers'] = ds3_numbers
    consolidated_bldgdataframe['ds4numbers'] = ds4_numbers
    consolidated_bldgdataframe['ds5numbers'] = ds5_numbers
    # consolidated_bldgdataframe.to_excel('consolidated_dataframe.xlsx', index=True)



    def injury_profile_compute_day(row):
        popday= row['population day']
        popnight= row['population night']
        pds2 = row['p_ds2']
        pds3 = row['p_ds3']
        pds4 = row['p_ds4']
        pds5 = row['p_ds5']
        pds5col = row['p_ds5_collapse']
        p5= random.choices([pds5, pds5col], [9,1])
        
        b= [popday*pds2*i for i in pds2n]
        c= [popday*pds3*i for i in pds3n]
        d= [popday*pds4*i for i in pds4n]
        e= [popday*pds5*i for i in pds5n]

        q= ((b[0]*pds2)+(c[0]*pds3)+(d[0]*pds4)+(e[0]*pds5))/(pds2+pds3+pds4+pds5)
        r= ((b[1]*pds2)+(c[1]*pds3)+(d[1]*pds4)+(e[1]*pds5))/(pds2+pds3+pds4+pds5)
        s= ((b[2]*pds2)+(c[2]*pds3)+(d[2]*pds4)+(e[2]*pds5))/(pds2+pds3+pds4+pds5)
        t= ((b[3]*pds2)+(c[3]*pds3)+(d[3]*pds4)+(e[3]*pds5))/(pds2+pds3+pds4+pds5)
        p= (int(popday)-q-r-s-t)
        result= [p,q,r,s,t]
        resultfiction= [(int(popday)-2*q-2*r-2*s-2*t),2*q,2*r,2*s,2*t] #the result values were unrealistically low, - not meaningful for part B
        return np.round(resultfiction)



    def injury_profile_compute_night(row):
        popday= row['population day']
        popnight= row['population night']
        pds2 = row['p_ds2']
        pds3 = row['p_ds3']
        pds4 = row['p_ds4']
        pds5 = row['p_ds5']
        pds5col = row['p_ds5_collapse']
        p5= random.choices([pds5, pds5col], [9,1])
        
        b= [popnight*pds2*i for i in pds2n]
        c= [popnight*pds3*i for i in pds3n]
        d= [popnight*pds4*i for i in pds4n]
        e= [popnight*pds5*i for i in pds5n]

        q= ((b[0]*pds2)+(c[0]*pds3)+(d[0]*pds4)+(e[0]*pds5))/(pds2+pds3+pds4+pds5)
        r= ((b[1]*pds2)+(c[1]*pds3)+(d[1]*pds4)+(e[1]*pds5))/(pds2+pds3+pds4+pds5)
        s= ((b[2]*pds2)+(c[2]*pds3)+(d[2]*pds4)+(e[2]*pds5))/(pds2+pds3+pds4+pds5)
        t= ((b[3]*pds2)+(c[3]*pds3)+(d[3]*pds4)+(e[3]*pds5))/(pds2+pds3+pds4+pds5)
        p= (int(popnight)-q-r-s-t)
        result2= [p,q,r,s,t]
        resultfiction= [(int(popnight)-2*q-2*r-2*s-2*t),2*q,2*r,2*s,2*t] #the result values were unrealistically low, - not meaningful for part B    
        return np.round(resultfiction)







    if 900 < equake.time < 1800:
        consolidated_bldgdataframe['injuries'] = consolidated_bldgdataframe.apply(injury_profile_compute_day, axis =1)
        # print('day')
    elif (0 < equake.time < 899) or (1801 < equake.time < 2359):
        consolidated_bldgdataframe['injuries'] = consolidated_bldgdataframe.apply(injury_profile_compute_night, axis =1)
        # print('night')
    else:
        print ('arghhh')

    #final datafraem from part A
    partA_data= consolidated_bldgdataframe
    return partA_data



def calculate_fade_away(t: float) -> list[float]:
    """
    Calculates the fade away of an injury class at a specific time t,
    for a given duration, injury severity, and deterioration rate.

    Formulation:
        Based on: https://www.iitk.ac.in/nicee/wcee/article/10_vol10_6043.pdf
        Fade away function = ((injury_severity ^ (1 / det_rate)) - (t / duration)) ^ det_rate

    Args:
        t (float): The specific time at which to calculate the fade away. (in minutes)
    
    Returns:
        list[float]: The deterioration value at time t for the given injury class.
    """
    
    # Define all the hyper parameters like duration, injury_severity and deterioration rate
    duration = 150 * 60    # in minutes
    injury_severity = [0.60, 0.75, 0.85, 0.94]    # Injury_severity = [highest, ..., lowest]
    det_rate = 0.3
    
    # Create an empty paceholder to store fade_away rate for each injury_severity
    fade_away = []
    
    # Create a for loop to find fade_away rate for each severity at 't' point of time
    for i in range(len(injury_severity)):
        t_value = math.pow(injury_severity[i], 1 / det_rate) - (t / duration)
        if t_value > 0:
            t_value = math.pow(t_value, det_rate)
            fade_away.append(t_value)
        else:
            fade_away.append(0)

    return fade_away    # Value between 0 to 1, proportion of people survived that survived at 't'



def Rescue_Duration(buildings: list[dict], team_assigned: str) -> dict:
    """
    Calculates the time to save one person based on building empirical data.

    Args:
        buildings (list[dict]): A list of dictionaries for each building with id, damage state, height, and area.
    
    Returns:
        dict: A relationship of building id and the time to save one person in that building.
    """
    
    # An empty dictionary to store rescue time for each building (building: rescue time)
    rescue_times = {}
    
    # Extracting necessary information from the list of building dictionaries
    for building in buildings:
        Id = building['Building_Id']
        Bh = building['Building_Height']
        Ba = building['Building_Area']
        Ds = building['Damage_State']
        
        # Calculation of rescue_time based on a pre defined mathematical formulation
        # (1.6 * Damage_state) + (2.1 * building_height^0.5) + (0.01 * building_area^0.5)
        rescue_time = (1.16 * Ds + 2.1 * math.sqrt(Bh) + 0.01 * math.sqrt(Ba))/3
        
        # Based on the team assigned the overall rescue time differs based on competency
        if team_assigned == 'light':
            rescue_time = 1.5 * rescue_time
        elif team_assigned == 'medium':
            rescue_time = 1.25 * rescue_time
        else:
            rescue_time = 1 * rescue_time

        rescue_times[Id] = round(rescue_time, 4)

    return rescue_times



def calculate_rescue_time(building: dict, current_time: int, Rescue_duration: dict, buffer_time: int) -> Tuple[list[int], list[int], int, int]:
    """
    Calculates the rescue time for each building based on the start time(current time)
    and the time to save each life. It also implements the fade away function.

    Args:
        building (dict): A dictionary of a building with id, damage state, height, area, and injury distribution.
        current_time (int): The start time of operations in a building. (in minutes)
        Rescue_duration (dict): A dictionary of time to save a life per damage state. (in minutes)
        buffer_time (int): Buffer time between two sites for movement and redirection.

    Returns:
        initial_people_counts (list): A list of people at t=0 with different injury classes.
        people_alive (list): A list of people at t=current_time with different injury classes.
        total_rescued (int): Sum of all the people rescued irrespective of injury severity.
        total_rescue_time (int): Time taken to complete the rescue operation. (in minutes)
    """
#     # Debugging: Print the building dictionary to check its contents
#     print("Building Dictionary:", building)
    
    # Calculate the fade away at current_time i.e. start time of a building operation
    fade_away = calculate_fade_away(current_time)

    # extract building_id and initial_count for a specific building from the building dictionary
    Id = building["Building_Id"]
    initial_people_counts = building["Injury_Severity"]

    total_rescue_time = 0
    total_rescued = 0
    people_alive = []

    # loop through every injury severity in initial count
    for i in range(len(initial_people_counts)):
        initial_people_count = initial_people_counts[i]

        # Calculate the number of people alive based on the injury class and fade_away values
        people_alive_i = int(initial_people_count * fade_away[i])
        people_alive.append(people_alive_i)

    # Calculate the rescue time based on the number of people alive
    total_rescued_i = sum(people_alive)

    # rescue time is already stated as a relationship between empirical building data and time to save one life
    rescue_time = Rescue_duration[Id] if Id in Rescue_duration else 0
    total_rescue_time_i = rescue_time * total_rescued_i
    total_rescue_time_i = math.floor(total_rescue_time_i)

    # If there are people alive, add buffer time to the rescue time
    # else the buffer time is nil
    if total_rescued_i > 0:
        total_rescue_time_i += buffer_time
    else:
        total_rescue_time_i = 0

    total_rescue_time += total_rescue_time_i
    total_rescued += total_rescued_i

    # Update the current time for the next building
    current_time += total_rescue_time

    return initial_people_counts, people_alive, total_rescued, total_rescue_time, current_time



def calculate_score(initial_people_counts: list[int], people_alive: list[int]) -> float:
    """
    Calculate the score for the given sequence of injury classes for each building.
    
    Args:
        initial_people_counts (list): List of people at t=0 with different injury classes.
        people_alive (list): List of people at t=current_time with different injury classes.
    
    Returns:
        total_score (float): Total score for the sequence based on injury classes.
    """
    # Define the points for each injury class based on whether saved or dead
    points_saved = [4, 3, 2, 1]
    points_not_saved = [-2, -1.5, -1, -0.5]

    # Create an empty placeholder for the points achieved
    total_score = 0
    
    # Loop through each severity and see people saved and not_saved
    for i in range(len(initial_people_counts)):
        saved = people_alive[i]
        not_saved = initial_people_counts[i] - saved

        total_score += saved * points_saved[i] + not_saved * points_not_saved[i]
#         total_score += saved * points_saved[i]
    
    return total_score



def generate_building_sequences(buildings: list[dict], n: int) -> list[list[dict]]:
    """
    Generates a list a of random sequences from the available buildings.
    
    Args:
        buildings (list): A dictionary of a building with id, damage state, height, area, and injury distribution.
        n (int): Number of generations.
    
    Returns:
        sequences (list): A list of random sequences.
    """
    
    damaged_buildings_priority = [b for b in buildings if b["Damage_State"] in [3, 4, 5]]
    damaged_buildings_normal = [b for b in buildings if b["Damage_State"] in [1, 2]]

    sequences = []

    for _ in range(n):
        # Shuffle the buildings with damage states 3, 4, 5
        random.shuffle(damaged_buildings_priority)
        
        # Shuffle the buildings with damage states 1, 2
        random.shuffle(damaged_buildings_normal)

        # Randomly select a sequence length between 1 and the total number of buildings
        sequence_length = random.randint(round(len(buildings)/2), len(buildings))

        # Take the first 'sequence_length' buildings from each category
        sequence = damaged_buildings_priority[:sequence_length] + damaged_buildings_normal[:sequence_length]

        # Add the sequence to the list of sequences
        sequences.append(sequence)

    return sequences



