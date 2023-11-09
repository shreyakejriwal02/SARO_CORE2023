import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import random
import math
import scipy.stats as stats
from typing import List, Tuple
from random import choices
from trial_1 import Building
from trial_1 import Area
from shapely.geometry import Polygon
from shapely.geometry import box
from trial_1 import Earthquake
from matplotlib.patches import Polygon as mpl_polygon
from trial_1 import Sub_Area
from trial_1 import Team
from trial_1 import Sub_Team
from trial_1 import Team_Member
import itertools
from typing import List, Tuple
import re
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap


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


# defines a function which imports multiple areas
def import_areas(addresses):
    areas = []
    areas_gdf = []
    for address in addresses:
        # loads the area as a geodataframe
        area_gdf = ox.geocode_to_gdf(address)
        # area_gdf = area_gdf.to_crs(epsg=32637)
        areas_gdf.append(area_gdf)

        # extracts the area id, name and addresstype
        area_id = area_gdf.loc[0, 'osm_id']
        geometry = area_gdf.loc[0, 'geometry']
        name = area_gdf.loc[0, 'name']
        address = address
        addresstype = area_gdf.loc[0, 'addresstype']

        minx = area_gdf.loc[0, 'bbox_west']
        miny = area_gdf.loc[0, 'bbox_south']
        maxx = area_gdf.loc[0, 'bbox_east']
        maxy = area_gdf.loc[0, 'bbox_north']
        bbox = box(minx, miny, maxx, maxy)

        # creates an area object and appends it to the list
        area = Area(area_id, geometry, bbox, name, address, addresstype)
        areas.append(area)
    return areas, areas_gdf

addresses = ['Sarıgüllük Mahallesi', 'Gazi Mah., Gaziantep', 'Pancarlı Mahallesi']
areas, areas_gdf = import_areas(addresses)



# defines a function which imports all buildings in an area
def import_buildings(area, earthquake):
    # importing osm location
    geometry = area.geometry
    buildings = ox.features.features_from_polygon(geometry, tags={'building': True})
    consolidated_bldgdataframe, bldngs = assign_building_attributes(buildings)
    consolidated_bldgdataframe, medbetatable = assign_fragility_attributes(consolidated_bldgdataframe, bldngs, earthquake)
    partA_data = assign_injury_numbers(consolidated_bldgdataframe, bldngs, medbetatable, earthquake)
    
    # creating object for each building
    bld_lst = []
    for i in partA_data.index:
        id = partA_data.loc[i, 'osmid']
        geo = partA_data.loc[i, 'geometry']
        center_point = geo.centroid
        occupancy_type = partA_data.loc[i, 'occupancytype']
        footprint = partA_data.loc[i, 'Footprint']
        structural_system = partA_data.loc[i, 'structural_system']
        lateral_resistance = partA_data.loc[i, 'lateral_resistance']
        stories = partA_data.loc[i, 'height']
        population_day = partA_data.loc[i, 'population day']
        population_night = partA_data.loc[i, 'population night']
        damage_state_probabilities = [partA_data.loc[i, 'p_ds2'], partA_data.loc[i, 'p_ds3'], partA_data.loc[i, 'p_ds4'], partA_data.loc[i, 'p_ds5']]
        injuries = partA_data.loc[i, 'injuries']

        bld = Building(id, geo, center_point, occupancy_type, footprint, structural_system, lateral_resistance, stories, population_day, population_night, damage_state_probabilities, injuries)
        bld_lst.append(bld)
        area.add_building(bld)

    return bld_lst



# defines a function which generates sub_areas by dividing the boundary of all combined buildings in cells, x_steps = n of cells in x dir, y_steps = n of cells in y dir, and associating buildings with sub_areas
def generate_sub_areas(area, buildings, x_steps, y_steps):
    # set bounds of graph to the bounds of center points
    xmin, ymin, xmax, ymax = area.bbox.bounds
    x_range = xmax - xmin
    y_range = ymax - ymin

    # set stepsize
    width = x_range / x_steps
    height = y_range / y_steps

    # create cols and rows based on bounds and stepsize
    cols = list(np.arange(xmin, xmax + width, width))
    rows = list(np.arange(ymin, ymax + height, height))

    # sort the list of buildings objects based on x coordinates, then y coordinates
    sorted_blds = sorted(buildings, key=lambda x: (x.center_point.x, x.center_point.y))

    # create cells and plot to graph, add buildings to subarea classes
    sub_areas = []
    i = 0
    j = 0
    for x in cols[:-1]:
        # while the buildings have x values in the range of this column, add them to a list
        filt_blds = []
        while (i < len(sorted_blds)) and (sorted_blds[i].center_point.x >= x) and (sorted_blds[i].center_point.x < (x+width)): 
            filt_blds.append(sorted_blds[i])
            filt_blds = sorted(filt_blds, key=lambda x: (x.center_point.y))
            i += 1
            
        for y in rows[:-1]:
            # create a cell, sub_area object, and associate the cell with the object
            polygon = Polygon([(x,y), (x+width, y), (x+width, y+height), (x, y+height)])
            sub_area = Sub_Area(j, polygon)
            
            # while the buildings in that column have y values in the range of this row, add them to the cell object 
            while (len(filt_blds) > 0) and (filt_blds[0].center_point.y >= y) and (filt_blds[0].center_point.y < (y+height)):
                sub_area.add_building(filt_blds.pop(0))

            # only add the sub_area if it has buildings in it
            if sub_area.buildings != []:
                sub_areas.append(sub_area)
            
                # add the sub_areas to the area
                area.add_sub_area(sub_area)

                # crop the geometry of the sub_area with the are geometry
                sub_area.crop_geometry()

                j += 1           
    return sub_areas



# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_geometry(areas):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    for a in areas:
        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', linewidth=0.2)
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # choices of different colours with corresponding weights
        # population = ['green', 'blue', 'yellow', 'orange', 'red']
        population = ['#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D']
        weights = [0.45, 0.05, 0.15, 0.12, 0.23]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for g in geos:
            c = choices(population, weights)[0]
            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    plt.show()
    


def allocate_teams_to_areas(areas, sector_n_heavy_teams, sector_n_med_teams, sector_n_light_teams, 
                            sector_n_task_force_teams, sector_n_fire_fighter_teams, 
                            sector_n_police_teams, sector_n_volunteer_teams):
    # define the number of people per team
    heavy_n_people = 24
    medium_n_people = 12
    light_n_people = 6
    task_force_n_people = 6
    fire_fighter_n_people = 6
    police_n_people = 6
    volunteer_n_people = 6

    # calculate the total number of people required
    total_people = (heavy_n_people * sector_n_heavy_teams) + (medium_n_people * sector_n_med_teams) + (light_n_people * sector_n_light_teams) + (task_force_n_people * sector_n_task_force_teams) + (fire_fighter_n_people * sector_n_fire_fighter_teams) + (police_n_people * sector_n_police_teams) + (volunteer_n_people * sector_n_volunteer_teams) 
    total_priority = 0
    for a in areas:
        total_priority += a.priority_weight
    
    # calculate the number of people required per priority weight
    people_per_priority = total_people / total_priority

    # calculate the number of people required per area
    for a in areas:
        a.people_requirement = a.priority_weight * people_per_priority

    # sort the areas by people requirement
    sorted_areas = sorted(areas, key=lambda x: (x.people_requirement), reverse=True)

    # reset allocation of teams
    for a in areas:
        a.heavy_teams = 0
        a.med_teams = 0
        a.light_teams = 0
        a.task_force_teams = 0
        a.fire_fighter_teams = 0
        a.police_teams = 0
        a.volunteer_teams = 0

    # allocate teams to areas
    while sector_n_heavy_teams > 0 or sector_n_med_teams > 0 or sector_n_light_teams > 0 or sector_n_task_force_teams > 0 or sector_n_fire_fighter_teams > 0 or sector_n_police_teams > 0 or sector_n_volunteer_teams > 0:
        if sector_n_heavy_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].heavy_teams += 1
            sector_n_heavy_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= heavy_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)
        elif sector_n_med_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].med_teams += 1
            sector_n_med_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= medium_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)
        elif sector_n_light_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].light_teams += 1
            sector_n_light_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= light_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)
        elif sector_n_task_force_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].task_force_teams += 1
            sector_n_task_force_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= task_force_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)
        elif sector_n_fire_fighter_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].fire_fighter_teams += 1
            sector_n_fire_fighter_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= fire_fighter_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)
        elif sector_n_police_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].police_teams += 1
            sector_n_police_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= police_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)   
        elif sector_n_volunteer_teams > 0:
            # allocate team to the area with highest people requirement
            sorted_areas[0].volunteer_teams += 1
            sector_n_volunteer_teams -= 1
            # edit the people requirement of the area and resort the list
            sorted_areas[0].people_requirement -= volunteer_n_people
            sorted_areas = sorted(sorted_areas, key=lambda x: (x.people_requirement), reverse=True)                                  



# defines a function which creates team, sub-team and team_member objects based on a number of heavy, medium and light teams in an area
def set_teams(heavy, med, light, task_force, fire_fighters, police, volunteer):
    # set number of heavy, medium, light, police, fire_fighters and task_force teams
    n_heavy = heavy
    n_med = med
    n_light = light
    n_police = police
    n_fire_fighters = fire_fighters
    n_task_force = task_force
    n_volunteer = volunteer

    # initialise list of teams and team ids
    teams = []
    team_id = 0
    sub_team_id = 0
    
    # create heavy teams, subteams and teammembers
    for i in range(n_heavy):
        team = Team(team_id, 'heavy')
        for j in range(4):
            sub_team = Sub_Team(sub_team_id, 'heavy')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id,'heavy')       # Create a team member
                sub_team.add_team_member(team_member)                   # Add the team member to the sub-team
                sub_team_member_id += 1                                     # Increment the sub_team_member_id
            sub_team.calculate_action_counts()          # Calculate action counts for the sub-team
            sub_team.calculate_phase1_competence()   # Calculate the phase1_competence for the sub-team
            team.add_sub_team(sub_team)                                 # Add the sub-team to the team
            sub_team_id += 1                                            # Increment the sub_team_id
        teams.append(team)                                              # Add the team to the teams list
        team_id += 1                                                    # Increment the team_id
   
    # create medium teams, subteams and teammembers
    for i in range(n_med):
        team = Team(team_id, 'medium')
        for j in range(4):
            sub_team = Sub_Team(sub_team_id, 'medium')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id, 'medium')       
                sub_team.add_team_member(team_member)           
                sub_team_member_id += 1                             
            sub_team.calculate_action_counts()              
            sub_team.calculate_phase1_competence()   
            team.add_sub_team(sub_team)                         
            sub_team_id += 1                                   
        teams.append(team)                                      
        team_id += 1                                            
        
    # create light teams, subteams and teammembers
    for i in range(n_light):
        team = Team(team_id, 'light')
        for j in range(1):
            sub_team = Sub_Team(sub_team_id, 'light')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id, 'light')      
                sub_team.add_team_member(team_member)           
                sub_team_member_id += 1                             
            sub_team.calculate_action_counts()  
            sub_team.calculate_phase1_competence()   
            team.add_sub_team(sub_team)                         
            sub_team_id += 1                                   
        teams.append(team)                                      
        team_id += 1  

    # create task force team, subteams and teammembers
    for i in range(n_task_force):
        team = Team(team_id, 'task_force')
        for j in range(1):
            sub_team = Sub_Team(sub_team_id, 'task_force')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id, 'task_force')       
                sub_team.add_team_member(team_member)           
                sub_team_member_id += 1                             
            sub_team.calculate_action_counts()              
            sub_team.calculate_phase1_competence()   
            team.add_sub_team(sub_team)                         
            sub_team_id += 1                                   
        teams.append(team)                                      
        team_id += 1         
   
    # create fire_fighters team, subteam and teammembers
    for i in range(n_fire_fighters):
        team = Team(team_id, 'fire_fighter')
        for j in range(1):
            sub_team = Sub_Team(sub_team_id, 'fire_fighter')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id, 'fire_fighter')       
                sub_team.add_team_member(team_member)           
                sub_team_member_id += 1                             
            sub_team.calculate_action_counts()
            sub_team.calculate_phase1_competence()   
            team.add_sub_team(sub_team)                         
            sub_team_id += 1                                   
        teams.append(team)                                      
        team_id += 1 
 
    # create police_team, subteam and teammembers
    for i in range(n_police):
        team = Team(team_id, 'police')
        for j in range(1):
            sub_team = Sub_Team(sub_team_id, 'police')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id, 'police')       
                sub_team.add_team_member(team_member)           
                sub_team_member_id += 1                             
            sub_team.calculate_action_counts()  
            sub_team.calculate_phase1_competence()   
            team.add_sub_team(sub_team)                         
            sub_team_id += 1                                   
        teams.append(team)                                      
        team_id += 1   

    # create volunteer, subteams and teammembers
    for i in range(n_volunteer):
        team = Team(team_id, 'volunteer')
        for j in range(1):
            sub_team = Sub_Team(sub_team_id, 'volunteer')
            sub_team_member_id = 0
            for k in range(6):
                team_member = Team_Member(sub_team_member_id, 'volunteer')       
                sub_team.add_team_member(team_member)           
                sub_team_member_id += 1                             
            sub_team.calculate_action_counts()              
            sub_team.calculate_phase1_competence()   
            team.add_sub_team(sub_team)                         
            sub_team_id += 1                                   
        teams.append(team)                                      
        team_id += 1 

    # Return the 'teams' list after creating all teams
    return teams



# defines a function which puts all subteams in multiple teams 
def get_sub_teams(teams):
    # access and create sub_teams list
    sub_teams = []
    for tm in teams:
        for stm in tm.sub_teams:
            sub_teams.append(stm)
    return sub_teams



def print_phase1_competence(teams):
    # Create lists to store the data
    team_ids = [] 
    team_class = []
    sub_team_ids = []
    sub_team_competence = []

    # Iterate through the teams and their sub-teams
    for team in teams:
        for sub_team in team.sub_teams:
            team_ids.append(team.team_id)
            team_class.append(team.team_type)
            sub_team_ids.append(sub_team.sub_team_id)
            sub_team_competence.append(sub_team.phase1_competence)

    # Create a dictionary from the lists
    data = {
        'Team_ID': team_ids,
        'Team_Class': team_class,
        'Sub_Team_ID': sub_team_ids, 
        'Phase1_Competence': sub_team_competence
    }

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data)

    # Display the DataFrame
    print(df)



# defines a function which allocates sub_team(s) to sub_area(s) based on priority weight and competence, works with sub_teams list or single object
def allocate_sub_team_phase1(sub_areas, sub_teams):
    # sorts the sub_areas so that the sub_areas with the highest priority weight are first in the list
    sub_areas = sorted(sub_areas, key=lambda x: (x.priority_weight), reverse=True)

    # links the objects of sub_teams to sub_areas and removes the sub_areas that are allocated from the sub_areas list
    if hasattr(sub_teams, '__iter__'):

        # sorts the sub_teams so that the sub_teams with the highest competence are first in the list
        sub_teams = sorted(sub_teams, key=lambda x: (x.phase1_competence), reverse=True)
        
        # assigns sub_areas to sub_teams
        for i, o in enumerate(sub_teams):
            # filters the sub_areas so that only the sub_areas that haven't been cleared are in the list
            filtered_sub_areas = [sub_area for sub_area in sub_areas if (sub_area.cleared == False)]
            # filters the sub_areas so that only the sub_areas that can be served by the sub_team are in the list
            filtered_sub_areas = [sub_area for sub_area in sub_areas if any((building.damage_state in o.serveable_damage_states and building.cleared == False and building.safe == False) for building in sub_area.buildings)]
            print('-'*30)
            # print(f'amount of sub_areas filtered: {len(sub_areas) - len(filtered_sub_areas)}')            

            # Calculate the priority weights for each sub-area only including buildings that are in a damage state that the sub-team can serve
            DS_priority_weights = []
            DS_clear_times = []
            for sub_area in filtered_sub_areas:
                # Initialize a running total for the new priority weight
                new_priority_weight = 0
                new_clear_time = 0

                # Iterate through buildings in the sub_area
                for building in sub_area.buildings:
                    if building.damage_state in o.serveable_damage_states and building.cleared == False and building.safe == False:
                        # Add the building's priority weight to the total
                        new_priority_weight += (building.priority_weight / building.clear_time)
                        new_clear_time += building.clear_time
                DS_priority_weights.append(new_priority_weight)
                DS_clear_times.append(new_clear_time)

            # Pair each sub-area with its DS priority weight
            sub_area_priority_pairs = list(zip(filtered_sub_areas, DS_priority_weights, DS_clear_times))

            # Sort the sub-areas based on DS priority weights
            sorted_sub_areas = [sub_area for sub_area, _, _ in sorted(sub_area_priority_pairs, key=lambda x: x[1], reverse=True)]
            DS_priority_weights = sorted(DS_priority_weights, key=lambda x: x, reverse=True)
            DS_clear_times = [DS_clear_time for _, _, DS_clear_time in sorted(sub_area_priority_pairs, key=lambda x: x[1], reverse=True)] 
            # print(f'sorted_sub_areas: {sorted_sub_areas}')
            # print(f'DS_priority_weights: {DS_priority_weights}')
            # print(f'DS_clear_times: {DS_clear_times}')

            # assign the sub_area to the sub_team
            o.assign_sub_area(sorted_sub_areas[0])
            print(f'sub_team {o.sub_team_id} assigned to sub_area {o.sub_area}')

            o.rem_time -= DS_clear_times[0]
            for building in o.sub_area.buildings:
                if building.damage_state in o.serveable_damage_states and building.cleared == False and building.safe == False:
                    building.set_cleared()
                    # print(f'building {building.building_id} cleared')
                    # print(f'building clear_time: {building.clear_time}')
            if o.sub_area.cleared == True:
                sub_areas.remove(o.sub_area)

            print(f'amount of cleared buildings in area: {len([building for building in sub_areas[0].area.buildings if building.cleared == True])}')
            
    else:
        # filters the sub_areas so that only the sub_areas that haven't been cleared are in the list
        filtered_sub_areas = [sub_area for sub_area in sub_areas if (sub_area.cleared == False)]
        # filters the sub_areas so that only the sub_areas that can be served by the sub_team are in the list
        filtered_sub_areas = [sub_area for sub_area in sub_areas if any((building.damage_state in sub_teams.serveable_damage_states and building.cleared == False and building.safe == False) for building in sub_area.buildings)]
        print('-'*30)
        # print(f'amount of sub_areas filtered: {len(sub_areas) - len(filtered_sub_areas)}')            

        # Calculate the priority weights for each sub-area only including buildings that are in a damage state that the sub-team can serve
        DS_priority_weights = []
        DS_clear_times = []
        for sub_area in filtered_sub_areas:
            # Initialize a running total for the new priority weight
            new_priority_weight = 0
            new_clear_time = 0

            # Iterate through buildings in the sub_area
            for building in sub_area.buildings:
                if building.damage_state in sub_teams.serveable_damage_states and building.cleared == False and building.safe == False:
                    # Add the building's priority weight to the total
                    new_priority_weight += (building.priority_weight / building.clear_time)
                    new_clear_time += building.clear_time
            DS_priority_weights.append(new_priority_weight)
            DS_clear_times.append(new_clear_time)

        # Pair each sub-area with its DS priority weight
        sub_area_priority_pairs = list(zip(filtered_sub_areas, DS_priority_weights, DS_clear_times))

        # Sort the sub-areas based on DS priority weights
        sorted_sub_areas = [sub_area for sub_area, _, _ in sorted(sub_area_priority_pairs, key=lambda x: x[1], reverse=True)]
        DS_priority_weights = sorted(DS_priority_weights, key=lambda x: x, reverse=True)
        DS_clear_times = [DS_clear_time for _, _, DS_clear_time in sorted(sub_area_priority_pairs, key=lambda x: x[1], reverse=True)] 
        # print(f'sorted_sub_areas: {sorted_sub_areas}')
        # print(f'DS_priority_weights: {DS_priority_weights}')
        # print(f'DS_clear_times: {DS_clear_times}')

        # assign the sub_area to the sub_team
        if sorted_sub_areas != []:
            sub_teams.assign_sub_area(sorted_sub_areas[0])
            print(f'sub_team {sub_teams.sub_team_id} assigned to sub_area {sub_teams.sub_area}')

            sub_teams.rem_time -= DS_clear_times[0]
            for building in sub_teams.sub_area.buildings:
                if building.damage_state in sub_teams.serveable_damage_states and building.cleared == False and building.safe == False:
                    building.set_cleared()
            if sub_teams.sub_area.cleared == True:
                sub_areas.remove(sub_teams.sub_area)
            print(f'amount of cleared buildings in area: {len([building for building in sub_areas[0].area.buildings if building.cleared == True])}')

        else:
            sub_teams.rem_time = 0
        # sub_teams.assign_sub_area(sub_areas.pop(0))
        # sub_teams.rem_time -= sub_teams.sub_area.clear_time
        # sub_teams.sub_area.cleared = True
    return sub_areas



def allocate_sub_team_phase2(sub_areas, sub_teams):
    # allocation of sub_teams in an area to sub_areas phase 2
    total_action_count_list = []
    
    for s in sub_teams:
        # filters the sub_areas so that only the sub_areas that haven't been cleared are in the list
        filtered_sub_areas = [sub_area for sub_area in sub_areas if (sub_area.cleared == False)]
        # filters the sub_areas so that only the sub_areas that can be served by the sub_team are in the list
        filtered_sub_areas = [sub_area for sub_area in sub_areas if any((building.damage_state in s.serveable_damage_states and building.cleared == False and building.safe == False) for building in sub_area.buildings)]
        
        # print('-'*30)
        # print(f'amount of sub_areas filtered: {len(sub_areas) - len(filtered_sub_areas)}') 
        
        # create empty dictionary to store the serveable sub_areas and their priority weights
        serveable_sub_areas = {}
        serveable_buildings = {}
        # sub_areas_priorities = []
        # print(f'sub_team.action_counts: {s.action_counts}')
        # filter the sub_areas list to only include sub_areas that have not been cleared and that have required actions that the sub_team can perform
        for sa in filtered_sub_areas:
            # check if the sub_team has the available actions required to clear the sub_area
            if (all(required_action in s.action_counts for required_action in sa.required_actions)) and (sa.cleared == False):
                # create priority weights for each sub_area based on the criteria and how well the required actions match the available actions
                # adding up all the counts of people who can perform each required action
                total_action_count = 0
                for required_action in sa.required_actions:
                    total_action_count += s.action_counts[required_action]
                
                # creating a factor based on the total_action_count, to multiply the estimated time with
                sub_team_efficiency = 1.5 * (1 - math.exp(- (0.0193 * total_action_count))) + 0.5

                # Initialize a running total for the new priority weight
                new_priority_weight = 0
                new_clear_time = 0

                
                # Iterate through buildings in the sub_area
                for building in sa.buildings:
                    if building.damage_state in s.serveable_damage_states and building.cleared == False and building.safe == False:
                        # Add the building's priority weight to the total
                        new_priority_weight += (building.priority_weight / building.clear_time)
                        new_clear_time += building.clear_time
                        factored_building_priority_weight = (building.priority_weight / building.clear_time) * sub_team_efficiency
                        serveable_buildings[building] = factored_building_priority_weight

                DS_priority_weight = new_priority_weight
                
                # creating the factored priority weight
                factored_priority_weight = DS_priority_weight * sub_team_efficiency
                serveable_sub_areas[sa] = factored_priority_weight
                

                total_action_count_list.append(total_action_count)

                # print('sub_team_actions:', s.action_counts.keys())
                # print('sub_area_req_actions:', sa.required_actions)
                # print('total_action_count:', total_action_count)
                # print('clear_time:', sa.clear_time)
                # print('priority_weight:', sa.priority_weight)
                # print('sum_building_weights:', sa.clear_time * sa.priority_weight)
                # print('sub_team_efficiency:', sub_team_efficiency)
                # print('factored_clear_time:', sa.priority_weight / sub_team_efficiency)
                # print('factored_priority_weight:', factored_priority_weight)
        
        serveable_sub_areas = sorted(serveable_sub_areas.items(), key=lambda x: (x[1]), reverse=True)
        s.serveable_sub_areas = serveable_sub_areas
        s.serveable_buildings = serveable_buildings
        # print(f'serveable_sub_areas: {serveable_sub_areas}')

    if len(sub_teams) > 1:
        # slice the serveable_sub_areas dictionary to the amount of subteams in the area
        sliced_sub_areas = [dict(itertools.islice(o.serveable_sub_areas, len(sub_teams))) for o in sub_teams]
        # print('sliced_sub_areas:', sliced_sub_areas)
        
        # create the option for no sub_area to be assigned to a sub_team
        for i, sub_area_list in enumerate(sliced_sub_areas):
            sub_area_list[None] = 0

        # Create an empty list to store all combinations
        all_combinations = []

        # Calculate the Cartesian product of serveable sub-areas for each sub-team
        for combination in itertools.product(*sliced_sub_areas):
            # append combination to all_combinations, 'combination' is a list sub_area objects
            all_combinations.append(combination)
        # print(all_combinations)
        # Filter any combinations that contain duplicate sub-areas
        filtered_combinations = list(filter(lambda x: len(list([sub_area for sub_area in x if sub_area != None])) <= len(set(sub_area for sub_area in x)), all_combinations))
        print('amount of combinations:', len(all_combinations),
            '\namount of combinations after filtering:', len(filtered_combinations))
        # print('filtered_combinations:', filtered_combinations)
        
        # Associating the sub_area objects with their priority weights and finding the highest priority combination
        best_combination_score = 0
        best_combination = None

        for i, combination in enumerate(filtered_combinations):
            combination_score = 0
            # print(f"Combination {i}:")
            for j, sub_area in enumerate(combination):
                priority = sliced_sub_areas[j][sub_area] # Access the sub-area object and priority
                # print(f"Sub-area: {sub_area}, Priority: {priority}")
                combination_score += priority
            # print(f"Combination score: {combination_score}")
            if combination_score >= best_combination_score:
                best_combination_score = combination_score
                best_combination = combination

        # Getting priority weights for the best combination
        print(f"Best combination score: {best_combination_score}")
        for i, sub_area in enumerate(best_combination):
                priority = sliced_sub_areas[i][sub_area] # Access the sub-area object and priority
                print(f"Sub-area: {sub_area}, Priority: {priority}")
                if sub_area != None:
                    sub_teams[i].assign_sub_area(sub_area)
                    sub_teams[i].sub_area_priority = priority
                    for building in sub_teams[i].sub_area.buildings:
                        if building.damage_state in sub_teams[i].serveable_damage_states and building.cleared == False and building.safe == False:
                            building.set_cleared()
                else:
                    sub_teams[i].assign_sub_area(None)
                    sub_teams[i].sub_area_priority = 0
    else:
        # Assign sub_teams to sub_areas
        sub_teams[0].assign_sub_area(sub_teams[0].serveable_sub_areas[0][0])
        sub_teams[0].sub_area_priority = sub_teams[0].serveable_sub_areas[0][1]
        for building in sub_teams[0].sub_area.buildings:
            if building.damage_state in sub_teams[0].serveable_damage_states and building.cleared == False and building.safe == False:
                building.set_cleared()



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



def convert_to_dict(sub_area, sub_team):
    # Convert the building data into a list of dictionaries
    sub_area = sub_area
    sub_team = sub_team
    buildings = []
    for i, b in enumerate(sub_area.buildings):
        building = {
            'Building_Id': sub_area.buildings.index(b),
            'Damage_State': int(re.search(r'\d+', b.damage_state).group()),
            'Building_Height': b.stories,
            'Building_Area': int(b.footprint),
            'Injury_Severity': [int(i) for i in b.injuries[1:]],
        }
        buildings.append(building)
    return buildings



def show_person_rescue_duration(sub_team, buildings):
    # Calculate the duration of to save one life for each building and create a dictionary for it
    Rescue_duration = Rescue_Duration(buildings, sub_team)
    # print(Rescue_duration)

    # extract the values from the dictionary
    building_ids = list(Rescue_duration.keys())
    rescue_durations = list(Rescue_duration.values())

    # change aspect ratio of the plot
    plt.figure(figsize=(7, 4))

    # create a bar chart of building vs rescue duration
    plt.bar(building_ids, rescue_durations, color='grey')

    # show all building ids on the x-axis
    # plt.xticks(building_ids)

    # label the axes
    plt.ylabel('Rescue Duration as a team of 2 (in minutes)')
    # plt.xlabel('Building IDs')
    plt.title('Rescue Duration per person for each building')

    plt.show()
    
    return Rescue_duration
    


# a function that calculates the total rescue time for a given sequence of buildings
def analyse_sequences(sequences, Rescue_duration):
    # Initialize best scores, sequences, total rescue, and total rescue time variables
    best_scores = []
    best_sequences = []
    total_rescue = []
    total_rescue_time = []  # Initialize as an empty list

    # Run the simulations using the generated sequences
    for sequence in sequences:
        current_time = 0    # Reset the current_time for each sequence
        sequence_scores = 0    # Reset the score for each sequence
        sequence_building_data = []

        # Initialize variables to store cumulative results for all injury classes
        all_initial_people_counts = []
        all_people_alive = []
        all_total_rescued = 0
        all_total_rescue_time = 0

        for building in sequence:
            initial_people_counts, people_alive, total_rescued, rescue_time, current_time = calculate_rescue_time(building,
                                                                                                                        current_time,
                                                                                                                        Rescue_duration=Rescue_duration,
                                                                                                                        buffer_time=20)
            # Accumulate results for all injury classes
            all_initial_people_counts.append(initial_people_counts)
            all_people_alive.append(people_alive)
            all_total_rescued += total_rescued
            all_total_rescue_time += rescue_time

            # Calculate the score for the building and add it to the sequence_scores
            building_score = calculate_score(initial_people_counts, people_alive)
            sequence_scores += building_score

            # Append building data for the sequence
            sequence_building_data.append({
                "Building_ID": building["Building_Id"],
                "Initial_People_Count": initial_people_counts,
                "People_Alive": people_alive,
                "Total_Rescued": total_rescued,
                "Total_Rescue_Time": rescue_time
            })

        # Add the sequence and its score to the list of best sequences
        best_scores.append(sequence_scores)
        best_sequences.append(sequence_building_data)
        total_rescue.append(all_total_rescued)
        total_rescue_time.append(all_total_rescue_time)

    # Sort the sequences and scores based on scores (in descending order)
    sorted_data = sorted(zip(best_sequences, best_scores), key=lambda x: x[1], reverse=True)

    # Print the top 5 sequences and their scores, total rescue, and total rescue time
    top_5_sequences = sorted_data[:5]

    for i, (sequence, score) in enumerate(top_5_sequences, start=1):
        print(f"Top {i} Sequence Score: {score}")
        print(f"Total Rescued: {total_rescue[i - 1]}")
        print(f"Total Rescue Time: {total_rescue_time[i - 1]}")  # Access the corresponding total rescue time
    #     print("Sequence:")

        for building_data in sequence:
            print(f"  Building ID: {building_data['Building_ID']}")
            print(f"  Initial People Count: {building_data['Initial_People_Count']}")
            print(f"  Rescue distribution: {building_data['People_Alive']}")
            print(f"  Total Rescued: {building_data['Total_Rescued']}")
            print(f"  Total Rescue Time (in minutes): {building_data['Total_Rescue_Time']}")
            print('-' * 20)

        print('-' * 40)
        
    return top_5_sequences



def show_schedule(top_5_sequences):    
    # Initialize a dictionary to keep track of building labels and their colors
    building_colors = {}
    legend_labels = {}

    # Create a Gantt chart for each of the top 5 sequences
    for i, (sequence, _) in enumerate(top_5_sequences, start=1):
        plt.figure(figsize=(12, 5))
        plt.title(f"Top {i} Sequence")

        current_time = 0  # Initialize current time in minutes
        for j, building_data in enumerate(sequence):
            building_id = building_data['Building_ID']
            initial_people_count = building_data['Initial_People_Count']
            rescue_time = building_data['Total_Rescue_Time']

            if building_id not in building_colors:
                # Generate a random color for each building
                building_colors[building_id] = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])

            if building_id not in legend_labels:
                legend_labels[building_id] = f"Building {building_id}"

            # Plot the Gantt bar for each building with its unique color
            plt.barh(building_id, rescue_time, left=current_time, label=legend_labels[building_id], color=building_colors[building_id])

            # Update current time for the next building
            current_time += rescue_time

        # Customize the x-axis to display building IDs
        plt.yticks(list(legend_labels.keys()), list(legend_labels.values()))

        # Customize the y-axis to display time in hours
        plt.ylabel("Building ID")
        
        # Customize the x-axis to display time in hours
        plt.xlabel("Time (hours)")
        x_ticks = [i * 60 for i in range(int(current_time / 60) + 1)]  # Convert to hours (1 hour = 60 minutes)
        x_labels = [str(int(t / 60)) for t in x_ticks]
        plt.xticks(x_ticks, x_labels)

        # Show the Gantt chart
        plt.grid(True)

    # Create a common legend for all sequences at the end and position it outside
    legend_labels_list = list(legend_labels.values())
    # plt.legend(legend_labels_list, loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()
  
    

# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_all_geometry(areas):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots()

    # '#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D', '#D3D3D3'
    for a in areas:
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')

        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")
        
        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha = 0.5, linewidth=0.4, linestyle=(0, (4, 8)))
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for i, g in enumerate(geos):
            c = 'black'
            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    fig.savefig('images/all_geometry.png', dpi=300)
    plt.show()
    # print(f'safe_count: {safe_count}')
    


# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_cleared_buildings(areas):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots()

    # create legend
    legend_elements = [
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize='10', label='cleared'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize='10', label='safe'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#D3D3D3', markersize='10', label='not cleared'),
    ]

    # add legend to graph
    ax.legend(handles=legend_elements, loc='upper right')

    # '#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D', '#D3D3D3'
    for a in areas:
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")
        
        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha = 0.5, linewidth=0.4, linestyle=(0, (4, 8)))
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for i, g in enumerate(geos):
            if a.buildings[i].cleared == True:
                c = '#133046'
            elif a.buildings[i].safe == True:
                c = '#15959F'
            else:
                c = '#D3D3D3'
            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    fig.savefig('images/buildings_cleared.png', dpi=300)
    plt.show()
    # print(f'safe_count: {safe_count}')



# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_cleared_by(areas, sub_teams):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots(dpi=100)
    ax.set_aspect('equal')

    # create legend
    marker_size = '6'
    if len(sub_teams) > 0:
        legend_elements = [
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize=marker_size, label='sub_team: '+str(sub_teams[0].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#D3D3D3', markersize=marker_size, label='not cleared'),
        ]
    if len(sub_teams) > 1:
        legend_elements = [
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize=marker_size, label='sub_team: '+str(sub_teams[0].sub_team_id)),        
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize=marker_size, label='sub_team: '+str(sub_teams[1].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#D3D3D3', markersize=marker_size, label='not cleared'),
        ]
    if len(sub_teams) > 2:        
        legend_elements = [
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize=marker_size, label='sub_team: '+str(sub_teams[0].sub_team_id)),        
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize=marker_size, label='sub_team: '+str(sub_teams[1].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#F1E4B3', markersize=marker_size, label='sub_team: '+str(sub_teams[2].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#D3D3D3', markersize=marker_size, label='not cleared'),
        ]
    if len(sub_teams) > 3:
        legend_elements = [
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize=marker_size, label='sub_team: '+str(sub_teams[0].sub_team_id)),        
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize=marker_size, label='sub_team: '+str(sub_teams[1].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#F1E4B3', markersize=marker_size, label='sub_team: '+str(sub_teams[2].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#EC9770', markersize=marker_size, label='sub_team: '+str(sub_teams[3].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#D3D3D3', markersize=marker_size, label='not cleared'),
        ]
    if len(sub_teams) > 4:
        legend_elements = [
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize=marker_size, label='sub_team: '+str(sub_teams[0].sub_team_id)),        
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize=marker_size, label='sub_team: '+str(sub_teams[1].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#F1E4B3', markersize=marker_size, label='sub_team: '+str(sub_teams[2].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#EC9770', markersize=marker_size, label='sub_team: '+str(sub_teams[3].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#C7402D', markersize=marker_size, label='sub_team: '+str(sub_teams[4].sub_team_id)),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#D3D3D3', markersize=marker_size, label='not cleared'),
        ]

    # add legend to graph
    legend = ax.legend(handles=legend_elements, loc='upper right')
    for label in legend.get_texts():
        label.set_fontsize(6)
    # ax.legend(handles=legend_elements, loc='upper right')

    # '#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D', '#D3D3D3'
    for a in areas:
        # Plot the network in the area
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")

        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha = 0.5, linewidth=0.4, linestyle=(0, (4, 8)))
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for i, g in enumerate(geos):
            # if a.buildings[i].cleared_by != None:
                # print(a.buildings[i].cleared_by, i)
            
            c = '#D3D3D3'
            if len(sub_teams) > 0 and a.buildings[i].cleared_by != None:
                if a.buildings[i].cleared_by.sub_team_id == sub_teams[0].sub_team_id:
                    c = '#133046'
            if len(sub_teams) > 1 and a.buildings[i].cleared_by != None:
                if a.buildings[i].cleared_by.sub_team_id == sub_teams[1].sub_team_id:
                    c = '#15959F'
            if len(sub_teams) > 2 and a.buildings[i].cleared_by != None:
                if a.buildings[i].cleared_by.sub_team_id == sub_teams[2].sub_team_id:
                    c = '#F1E4B3'
            if len(sub_teams) > 3 and a.buildings[i].cleared_by != None:
                if a.buildings[i].cleared_by.sub_team_id == sub_teams[3].sub_team_id:
                    c = '#EC9770'
            if len(sub_teams) > 4 and a.buildings[i].cleared_by != None:
                if a.buildings[i].cleared_by.sub_team_id == sub_teams[4].sub_team_id:
                    c = '#C7402D'

            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    fig.savefig('images/buildings_cleared_by_sub_team.png', dpi=300)
    plt.show()
    # print(f'safe_count: {safe_count}')



# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_damage_states_buildings(areas):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots()

    # create legend
    # '#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D'
    legend_elements = [
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize='10', label='DS2'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize='10', label='DS3'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#F1E4B3', markersize='10', label='DS4'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#C7402D', markersize='10', label='DS5')
    ]

    # add legend to graph
    ax.legend(handles=legend_elements, loc='upper right')

    for a in areas:
        # Plot the network in the area
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')        
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")        

        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha = 0.5, linewidth=0.4, linestyle=(0, (4, 8)))
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for i, g in enumerate(geos):
            if a.buildings[i].damage_state == 'DS2':
                c = '#133046'
            elif a.buildings[i].damage_state == 'DS3':
                c = '#15959F'
            elif a.buildings[i].damage_state == 'DS4':
                c = '#F1E4B3'
            else:
                c = '#C7402D'
            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    fig.savefig('images/damage_states.png', dpi=300)
    plt.show()
  


# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_structural_system_buildings(areas):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots()

    # create legend
    # '#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D', '#D3D3D3'
    legend_fig, legend_ax = plt.subplots()
    legend_elements = [
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize='10', label='Concrete Frame, Infill Panels'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#F1E4B3', markersize='10', label='Concrete Frame, Structural Infill'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize='10', label='Concrete Walls'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#EC9770', markersize='10', label='Unreinforced Masonry'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#C7402D', markersize='10', label='Timber'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#FFC107', markersize='10', label='Steel'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#FFA726', markersize='10', label='Construction Site'),
    ]

    # add legend to graph
    legend_ax.legend(handles=legend_elements, loc='upper right')

    for a in areas:
        # Plot the network in the area
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')              
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")        

        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha = 0.5, linewidth=0.4, linestyle=(0, (4, 8)))
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for i, g in enumerate(geos):
            if a.buildings[i].building_typology == 'Concrete Frame, Infill Panels':
                c = '#133046'
            elif a.buildings[i].building_typology == 'Concrete Frame, Structural Infill':
                c = '#F1E4B3'
            elif a.buildings[i].building_typology == 'Concrete Walls':
                c = '#15959F'
            elif a.buildings[i].building_typology == 'Unreinforced Masonry':
                c = '#EC9770'                
            elif a.buildings[i].building_typology == 'Timber':
                c = '#C7402D'       
            elif a.buildings[i].building_typology == 'Steel':
                c = '#FFC107'  
            elif a.buildings[i].building_typology == 'Construction Site':
                c = '#FFA726'                                                 
            else:
                c = '#D3D3D3'
            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    ax.axis('off')    
    fig.savefig('images/structural_systems.png', dpi=300)
    legend_fig.savefig('images/structural_systems_legend.png', dpi=300)
    plt.show()



# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_occupancy_type_buildings(areas):
    # create empty graph and plot sub_area geometry to graph
    fig, ax = plt.subplots()

    # create legend
    # '#133046', '#15959F', '#F1E4B3', '#EC9770', '#C7402D', '#D3D3D3'
    legend_fig, legend_ax = plt.subplots()
    legend_elements = [
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#133046', markersize='10', label='residential'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#15959F', markersize='10', label='commercial'),
    Line2D([0],[0], marker='s', color='w', markerfacecolor='#F1E4B3', markersize='10', label='industrial'),
    ]

    # add legend to graph
    legend_ax.legend(handles=legend_elements, loc='upper right')

    for a in areas:
        # Plot the network in the area
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')           
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")        

        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # plot the sub_area geometry        
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha = 0.5, linewidth=0.4, linestyle=(0, (4, 8)))
        
        # plot the building geometry
        # save each building geometry attribute in a list
        geos = [o.geometry for o in a.buildings]

        # for every geometry choose a colour, fill the geometry and plot to graph
        for i, g in enumerate(geos):
            if a.buildings[i].occupancy_type == 'residential':
                c = '#133046'
            elif a.buildings[i].occupancy_type == 'commercial':
                c = '#15959F'
            elif a.buildings[i].occupancy_type == 'industrial':
                c = '#F1E4B3'                                               
            else:
                c = '#D3D3D3'
            x, y = g.exterior.xy
            ax.fill(x, y, color = c)

    # Display the plot
    # ax.set_aspect('equal')
    plt.axis('off')
    ax.axis('off')    
    fig.savefig('images/occupancy_type.png', dpi=300)
    legend_fig.savefig('images/occupancy_type_legend.png', dpi=300)
    plt.show()



# Define a function which plots the geometry of the areas, sub-areas, and buildings
def show_population_night_buildings(areas):
    # Create an empty figure and axes
    fig, ax = plt.subplots()

    # Create a legend figure and axes
    # legend_fig, legend_ax = plt.subplots()

    # Define a color map for the population gradient
    cmap = LinearSegmentedColormap.from_list("population", ['#15959F', '#EC9770', '#C7402D'], N=256)

    for a in areas:
        # Plot the network in the area
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')      
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")

        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # Plot the sub-area geometry
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha=0.5, linewidth=0.4, linestyle=(0, (4, 8)))

        # Plot the building geometry with population gradient
        populations = [building.population_night for building in a.buildings]
        norm = plt.Normalize(min(populations), max(populations))
        colors = cmap(norm(populations))
        
        for i, building in enumerate(a.buildings):
            x, y = building.geometry.exterior.xy
            ax.fill(x, y, color=colors[i])

    # Create a colorbar for the population gradient
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, label='Population')

    # Customize the plot
    ax.set_aspect('equal')
    ax.axis('off')

    # Save the figure with a higher resolution
    fig.savefig('images/population_night.png', dpi=300)

    # Display the plot
    plt.show()



# defines a function which plots the geometry of the areas, sub_areas and buildings
def show_priority_score_buildings(areas, sub_team):
    # Create an empty figure and axes
    fig, ax = plt.subplots()

    # Create a legend figure and axes
    # legend_fig, legend_ax = plt.subplots()

    # Define a color map for the population gradient
    cmap = LinearSegmentedColormap.from_list('Priority score for sub_team '+str(sub_team.sub_team_id), ['#15959F', '#EC9770', '#C7402D'], N=256)

    for a in areas:
        # Plot the network in the area
        network = ox.graph_from_polygon(a.geometry, network_type='all')
        nodes, edges = ox.graph_to_gdfs(network)
        network_gdf = edges.to_crs('EPSG:4326')            
        
        # Plot the network in the area
        network_gdf.plot(ax=ax, linewidth=0.4, edgecolor="#D3D3D3")

        # Plot the area exterior boundary
        x, y = a.geometry.exterior.xy
        ax.plot(x, y, 'black')  # You can set a specific color

        # Plot the sub-area geometry
        for s in a.sub_areas:
            ax.plot(*s.geometry.exterior.xy, 'black', alpha=0.5, linewidth=0.4, linestyle=(0, (4, 8)))

        # Plot the building geometry with population gradient
        priority_scores = list(sub_team.serveable_buildings.values())
        norm = plt.Normalize(min(priority_scores), max(priority_scores))
        
        for i, building in enumerate(a.buildings):
            x, y = building.geometry.exterior.xy
            if building in sub_team.serveable_buildings.keys():
                colors = cmap(norm(sub_team.serveable_buildings[building]))
            else:
                colors = '#D3D3D3'
            ax.fill(x, y, color=colors)

    # Create a colorbar for the population gradient
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, label='Factored priority score for sub_team '+str(sub_team.sub_team_id))

    # Customize the plot
    ax.set_aspect('equal')
    ax.axis('off')

    # Save the figure with a higher resolution
    fig.savefig('images/priority_score.png', dpi=300)

    # Display the plot
    plt.show()