import xml.etree.cElementTree as ET

from collections import defaultdict

import re

import pprint
OSM_FILE = "ottawa_canada.osm"  

SAMPLE_FILE = "ottawa_sample.osm"

regex = re.compile(r'\b\S+\.?', re.IGNORECASE)
expected = ["Rue", "Road", "Street", "Avenue", "Way", "Circle", "Drive", "Court", "Crescent","Lane", "Parkway", "Garden", "Private", "Palce", "Bridge", "Boulevard", "Square", "Ridge", "Gate", "Grove"] #expected names in the dataset

def audit_street(street_types, street_name): 
    m = regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r", encoding='utf-8')
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
    
def pretty_print(d):
    for sorted_key in sorted(d, key=lambda k: len(d[k]), reverse=True):
        v = d[k]
        print (sorted_key.title(), ':', len(d[sorted_key]))

print('Numbers of different street types in Ottawa:')
pretty_print(audit(SAMPLE_FILE))

mapping = {"Ave": "Avenue",
            "Ave.": "Avenue",
            "avenue": "Avenue",
            "ave": "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Blvd,": "Boulevard",
            "Boulavard": "Boulevard",
            "Boulvard": "Boulevard",
            "Ct": "Court",
            "Dr": "Drive",
            "Dr.": "Drive",
            "Ln": "Lane",
            "Ln.": "Lane",
            "Pl": "Place",
            "Plz": "Plaza",
            "Rd": "Road",
            "Rd.": "Road",
            "St": "Street",
            "St.": "Street",
            "st": "Street",
            "street": "Street",
            "square": "Square",
            "parkway": "Parkway"
            }

def string_case(s): 
    if s.isupper():
        return s
    else:
        return s.title()
    
def update_name(name, mapping):
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
            name[i] = string_case(name[i])
        else:
            name[i] = string_case(name[i])
    name = ' '.join(name)
    return name

update_street = audit(SAMPLE_FILE)
for street_type, ways in update_street.items():
    for name in ways:
        better_name = update_name(name, mapping)
        print(name, "=>", better_name)

postal_type_re = re.compile(r'^[kj]\d\w \d\w\d', re.IGNORECASE)
postal_types = defaultdict(set)

def audit_postal_code(postal_value, elem):
    m = postal_type_re.search(postal_value)
    if not m:
        postal_types[elem.attrib['k']].add(postal_value)

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode" )


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding='utf-8')
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag in["node", "way", "relation"] :
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    audit_postal_code(tag.attrib['v'], tag)
    osm_file.close()
    return postal_types


audit(SAMPLE_FILE)
pprint.pprint(dict(postal_types))

def is_incorrect_postal_code(postal_value, tag):
    if is_postal_code(tag):
        m = postal_type_re.search(postal_value)
        if not m:
            return True
        return False

def audit_pin(osmfile):
    osm_file = open(osmfile, "r", encoding='utf-8')
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag in["node", "way", "relation"] :
            for tag in elem.iter("tag"):
                 if is_incorrect_postal_code(tag.attrib['v'], tag):
                    print(tag.attrib['v'], '==>', update_postal_code(tag.attrib['v'], elem))
    osm_file.close()    

def update_postal_code(postal_value, element):
    if len(postal_value) != 7:
        if ' ' not in postal_value:
            return (postal_value[0:3]+ ' ' + postal_value[3:6])
        
        elif 'ON' in postal_value:
            return postal_value[3:]
        
audit_pin(SAMPLE_FILE) 
