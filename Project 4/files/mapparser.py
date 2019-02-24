
import xml.etree.cElementTree as ET

import pprint

OSM_FILE = "ottawa_canada.osm"  
SAMPLE_FILE = "ottawa_sample.osm"

def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags: 
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags
pprint.pprint(count_tags(SAMPLE_FILE))
