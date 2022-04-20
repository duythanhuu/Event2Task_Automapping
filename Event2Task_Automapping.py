import os
from lxml import etree
from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET
import re
import shutil

shutil.copyfile('conf_ecu_rte_ecucvalues.arxml', 'conf_ecu_rte_ecucvalues_OLD.arxml')
shutil.copyfile('fast_init.txt', 'fast_init_OLD.txt')
###############################################################################################################
##Read conf_ecu_rte_ecucvalues.arxml
ecuFile = 'conf_ecu_rte_ecucvalues.arxml'
tree = etree.parse(ecuFile)

BCEventEx = "//*[local-name() = 'SUB-CONTAINERS']/*[local-name() = 'ECUC-CONTAINER-VALUE']/*[local-name() = 'SHORT-NAME']/text()"
dataBCEvent= tree.xpath(BCEventEx)

PositionEx = "//*[local-name() = 'ECUC-NUMERICAL-PARAM-VALUE']/*[local-name() = 'VALUE']/text()"
dataPosition = sorted(list(dict.fromkeys(list(map(int, list(map(float,tree.xpath(PositionEx))))))), key=int, reverse=True)

maxPos = max(dataPosition)
##print(maxPos)
##print (dataPosition)

###############################################################################################################
##Read FCs .arxml
SwSPSA_path = r"..\..\SwSAPSA"
with open("FCs_new.txt", "r") as f_FCs_new:
    FCs_new = f_FCs_new.readlines()
file_paths = []
for FC_new in FCs_new:
    FC_new = FC_new.replace("\n","")
    FC_subpath = "\\" + FC_new + "\\" + FC_new + ".arxml"
    filepath = SwSPSA_path + FC_subpath
    #print(filepath)
    file_paths.append(filepath)  # Add it to the list.
    
data_redundant_events = []
data_new_events = []
for file_path in file_paths:
    tree = etree.parse(file_path)
    FCEventEx = "//*[local-name() = 'EVENTS']//*[local-name() = 'SHORT-NAME']/text()"
    dataFCEvent= tree.xpath(FCEventEx)
    #print (dataFCEvent)
    for event in dataFCEvent:
        if event not in dataBCEvent:
            #print (event)
            data_new_events.append(event)

    for FC_new in FCs_new:
        FC_new = FC_new.replace("\n","")
        if FC_new in file_path:
            for dataEvent in dataBCEvent:
                if FC_new in dataEvent:
                    if dataEvent not in dataFCEvent:
                        #print(dataEvent)
                        data_redundant_events.append(dataEvent)
                        
if data_new_events == []:
    print('No event added')
##else:
##    print(data_new_events)
if data_redundant_events == []:
    print('No event removed')
##else:
##    print(data_redundant_events)


###############################################################################################################
##Add new EV_ to conf_ecu_rte_ecucvalues.arxml
# 1_EV_REPLACE
# 2_POS_REPLACE
# 3_OS_REPLACE
# 4_Ti_MoW_REPLACE
# 5_FC_REPLACE
XMLexample_stored_in_a_string ='''                            <ECUC-CONTAINER-VALUE>
                              <SHORT-NAME>1_EV_REPLACE</SHORT-NAME>
                              <DEFINITION-REF DEST="ECUC-PARAM-CONF-CONTAINER-DEF">/AUTOSAR/EcucDefs/Rte/RteSwComponentInstance/RteEventToTaskMapping</DEFINITION-REF>
                              <PARAMETER-VALUES>
                                <ECUC-NUMERICAL-PARAM-VALUE>
                                  <DEFINITION-REF DEST="ECUC-INTEGER-PARAM-DEF">/AUTOSAR/EcucDefs/Rte/RteSwComponentInstance/RteEventToTaskMapping/RtePositionInTask</DEFINITION-REF>
                                  <VALUE>2_POS_REPLACE</VALUE>
                                </ECUC-NUMERICAL-PARAM-VALUE>
                                <ECUC-NUMERICAL-PARAM-VALUE>
                                  <DEFINITION-REF DEST="ECUC-FLOAT-PARAM-DEF">/AUTOSAR/EcucDefs/Rte/RteSwComponentInstance/RteEventToTaskMapping/RteActivationOffset</DEFINITION-REF>
                                  <VALUE>0.0</VALUE>
                                </ECUC-NUMERICAL-PARAM-VALUE>
                              </PARAMETER-VALUES>
                              <REFERENCE-VALUES>
                                <ECUC-REFERENCE-VALUE>
                                  <DEFINITION-REF DEST="ECUC-REFERENCE-DEF">/AUTOSAR/EcucDefs/Rte/RteSwComponentInstance/RteEventToTaskMapping/RteMappedToTaskRef</DEFINITION-REF>
                                  <VALUE-REF DEST="ECUC-CONTAINER-VALUE">/RB/PT/PCFG_ECU/RB/RTAOS/3_OS_REPLACE</VALUE-REF>
                                </ECUC-REFERENCE-VALUE>
                                <ECUC-REFERENCE-VALUE>
                                  <DEFINITION-REF DEST="ECUC-FOREIGN-REFERENCE-DEF">/AUTOSAR/EcucDefs/Rte/RteSwComponentInstance/RteEventToTaskMapping/RteEventRef</DEFINITION-REF>
                                  <VALUE-REF DEST="4_Ti_MoW_REPLACE">/5_FC_REPLACE_Package/5_FC_REPLACE/IB_5_FC_REPLACE/1_EV_REPLACE</VALUE-REF>
                                </ECUC-REFERENCE-VALUE>
                              </REFERENCE-VALUES>
                            </ECUC-CONTAINER-VALUE>
'''

with open("conf_ecu_rte_ecucvalues.arxml", "r") as f:
    contents = f.readlines()
count = 2000
for event in data_new_events:
    FC_name = ''
    for FC_new in FCs_new:
        FC_new = FC_new.replace("\n","")
        if FC_new in event:
            FC_name = FC_new
    line_CPT_section = 0
    CPT_section = '<SHORT-NAME>CPT_' + FC_name + '</SHORT-NAME>'
    #print (CPT_section)
    for line in contents:
        if CPT_section in line:
            line_CPT_section = contents.index(line)
            print('\nNew event added:')
            print (event)
            #print(line_CPT_section+9)
            #print(line)

    EV_add = ''
    if '_Init' in event:
        EV_add = XMLexample_stored_in_a_string.replace('1_EV_REPLACE', event)
        EV_add = EV_add.replace('3_OS_REPLACE', 'OS_Ini_Task')
        EV_add = EV_add.replace('4_Ti_MoW_REPLACE', 'SWC-MODE-SWITCH-EVENT')
        EV_add = EV_add.replace('5_FC_REPLACE', FC_name)
        EV_add = EV_add.replace('2_POS_REPLACE', str(count))
        while count <= maxPos:
            count += 1
            if count not in dataPosition:
                #print(count)
                break
        #print(EV_add)
        
    if '_Run' in event:
        EV_add = XMLexample_stored_in_a_string.replace('1_EV_REPLACE', event)
        EV_add = EV_add.replace('3_OS_REPLACE', 'OS_10ms_Task')
        EV_add = EV_add.replace('4_Ti_MoW_REPLACE', 'TIMING-EVENT')
        EV_add = EV_add.replace('5_FC_REPLACE', FC_name)
        EV_add = EV_add.replace('2_POS_REPLACE', str(count))
        while count <= maxPos:
            count += 1
            if count not in dataPosition:
                #print(count)
                break
        #print(EV_add)
    contents.insert(line_CPT_section+9, EV_add)

###############################################################################################################
##Remove redundant EV_ to conf_ecu_rte_ecucvalues.arxml

print('*********************************************************************') 
line_Event_section = 0
for event in data_redundant_events:
    Event_section = '<SHORT-NAME>' + event + '</SHORT-NAME>'
    #print (Event_section)
    for line in contents:
        if Event_section in line:
            line_Event_section = contents.index(line)
            #print(line_Event_section)
            #print(line)
            if (line_Event_section!= 0):
                contents[line_Event_section-1] = '<!--' + contents[line_Event_section-1]
                contents[line_Event_section+22] = contents[line_Event_section+22].replace('\n','') + '-->\n'
                #print (contents[line_Event_section-1])
                #del contents[line_Event_section-1:line_Event_section+23]
                print('Redundant event commented:')
                print (event)
                #print(line_Event_section)
            

with open("conf_ecu_rte_ecucvalues.arxml", "w") as f:
    contents_str = "".join(contents)
    f.write(contents_str)

###############################################################################################################
##Read fast_init.txt
with open("fast_init.txt", "r") as f_fast_init:
    fast_init = f_fast_init.readlines()

for event in data_new_events:
    FC_name = ''
    line_add = 0
    for FC_new in FCs_new:
        if FC_new.replace('\n', '') in event:
            FC_name = FC_new.replace('\n', '')
    #print (FC_name)
    # -fi=/VehC_SwSPSA_Package/VehC_SwSPSA/IB_VehC_SwSPSA/EV_VehC_SwSPSA_Proc_031_Init
    fast_init_add = '-fi=/FC_REPLACE_Package/FC_REPLACE/IB_FC_REPLACE/EV_REPLACE\n'
    fast_init_add = fast_init_add.replace('FC_REPLACE', FC_name)
    fast_init_add = fast_init_add.replace('EV_REPLACE', event)
    #print(fast_init_add)
    for line in fast_init:
        if event in line:
            print('Event is existing in fast_init.txt')
            print(fast_init_add)
            line_add = 0
            break
        elif FC_name in line:
            line_add = fast_init.index(line)
    if (line_add != 0):
        fast_init.insert(line_add+1, fast_init_add)
        print('Event added: ')
        print(fast_init_add)
        
with open("fast_init.txt", "w") as f_fast_init:
    contents_fast_init = "".join(fast_init)
    f_fast_init.write(contents_fast_init)


    



    
