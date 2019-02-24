import csv
import codecs
import re
import xml.etree.cElementTree as ET
from unittest import TestCase
import cerberus
import schema
import audit 


OSM_PATH = "ottawa_sample.osm"



NODES_PATH = "nodes.csv"

NODE_TAGS_PATH = "nodes_tags.csv"

WAYS_PATH = "ways.csv"

WAY_NODES_PATH = "ways_nodes.csv"

WAY_TAGS_PATH = "ways_tags.csv"







LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')






# Look for problematic tag names



filename = open("ottawa_sample.osm", "r", encoding="utf8")



lower = re.compile(r'^([a-z]|_)*$')

lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')





def key_type(element, keys):

    if element.tag == "tag":

        k = element.attrib['k']

        if re.search(lower, k):

            keys["lower"] += 1

        elif re.search(lower_colon, k):

            keys["lower_colon"] += 1

        elif re.search(problemchars, k):

            keys["problemchars"] += 1

        else:

            keys["other"] += 1

            

    return keys



def process_map(filename):

    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}

    for _, element in ET.iterparse(filename):

        keys = key_type(element, keys)



    return keys



process_map(filename)


process_map(OSM_PATH)




SCHEMA = {

    'node': {

        'type': 'dict',

        'schema': {

            'id': {'required': True, 'type': 'integer', 'coerce': int},

            'lat': {'required': True, 'type': 'float', 'coerce': float},

            'lon': {'required': True, 'type': 'float', 'coerce': float},

            'user': {'required': True, 'type': 'string'},

            'uid': {'required': True, 'type': 'integer', 'coerce': int},

            'version': {'required': True, 'type': 'string'},

            'changeset': {'required': True, 'type': 'integer', 'coerce': int},

            'timestamp': {'required': True, 'type': 'string'}

        }

    },

    'node_tags': {

        'type': 'list',

        'schema': {

            'type': 'dict',

            'schema': {

                'id': {'required': True, 'type': 'integer', 'coerce': int},

                'key': {'required': True, 'type': 'string'},

                'value': {'required': True, 'type': 'string'},

                'type': {'required': True, 'type': 'string'}

            }

        }

    },

    'way': {

        'type': 'dict',

        'schema': {

            'id': {'required': True, 'type': 'integer', 'coerce': int},

            'user': {'required': True, 'type': 'string'},

            'uid': {'required': True, 'type': 'integer', 'coerce': int},

            'version': {'required': True, 'type': 'string'},

            'changeset': {'required': True, 'type': 'integer', 'coerce': int},

            'timestamp': {'required': True, 'type': 'string'}

        }

    },

    'way_nodes': {

        'type': 'list',

        'schema': {

            'type': 'dict',

            'schema': {

                'id': {'required': True, 'type': 'integer', 'coerce': int},

                'node_id': {'required': True, 'type': 'integer', 'coerce': int},

                'position': {'required': True, 'type': 'integer', 'coerce': int}

            }

        }

    },

    'way_tags': {

        'type': 'list',

        'schema': {

            'type': 'dict',

            'schema': {

                'id': {'required': True, 'type': 'integer', 'coerce': int},

                'key': {'required': True, 'type': 'string'},

                'value': {'required': True, 'type': 'string'},

                'type': {'required': True, 'type': 'string'}

            }

        }

    }

}





NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']

NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']

WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']

WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']

WAY_NODES_FIELDS = ['id', 'node_id', 'position']





def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,

                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    """Clean and shape node or way XML element to Python dict"""



    node_attribs = {}

    way_attribs = {}

    way_nodes = []

    tags = []  # Handle secondary tags the same way for both node and way elements

    poscounter = 0 #for way nodes position

    

    if element.tag == 'node':

        for field in NODE_FIELDS:

            node_attribs[field] = element.attrib[field]

        for tag in element.iter('tag'):

            tag_dict = {}

            tag_dict['id'] = element.attrib['id'] #id (NODE_TAGS_FIELDS)
            if tag.attrib["k"] == 'addr:street':
                tag_dict["value"] = update_name(tag.attrib["v"], mapping)
            if tag.attrib["k"] == 'addr:postcode':
                tag_dict["value"] = update_postalcode(tag.attrib["v"], mapping)

            #key and type (NODE_TAGS_FIELDS)

            if PROBLEMCHARS.match(tag.attrib["k"]):

                pass

            elif ':' in tag.attrib['k']:

                tag_dict['type'] = tag.attrib['k'].split(':')[0]

                tag_dict['key'] = tag.attrib["k"].split(':',1)[1]

            else:

                tag_dict['type'] = 'regular'

                tag_dict['key'] = tag.attrib['k']

                

            #value (NODE_TAGS_FIELDS)

            tag_dict['value'] = tag.attrib['v']

            

            tags.append(tag_dict)

        return {'node': node_attribs, 'node_tags': tags}

        

    elif element.tag == 'way':

        for field in WAY_FIELDS:

            way_attribs[field] = element.attrib[field]

        for nd in element.iter('nd'):

            nd_dict = {}

            nd_dict['id'] = element.attrib['id']

            nd_dict['node_id'] = nd.attrib['ref']

            nd_dict['position'] = poscounter

            poscounter += 1

            way_nodes.append(nd_dict)

        for tag in element.iter('tag'):

            tag_dict = {}

            tag_dict['id'] = element.attrib['id'] #id

            #key and type

            if PROBLEMCHARS.match(tag.attrib["k"]):

                pass

            elif ':' in tag.attrib['k']:

                tag_dict['type'] = tag.attrib['k'].split(':')[0]

                tag_dict['key'] = tag.attrib["k"].split(':',1)[1]

            else:

                tag_dict['type'] = 'regular'

                tag_dict['key'] = tag.attrib['k']

            #value

            tag_dict['value'] = tag.attrib['v']

            

            tags.append(tag_dict)    

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

    

# HELPER FUNCTIONS    

    

def get_element(osm_file, tags=('node', 'way', 'relation')):

    """Yield element if it is the right type of tag"""



    context = ET.iterparse(osm_file, events=('start', 'end'))

    _, root = next(context)

    for event, elem in context:

        if event == 'end' and elem.tag in tags:

            yield elem

            root.clear()





def validate_element(element, validator, schema=SCHEMA):

    """Raise ValidationError if element does not match schema"""

    if validator.validate(element, schema) is not True:

        field, errors = next(validator.errors.iteritems())

        message_string = "\nElement of type '{0}' has the following errors:\n{1}"

        error_strings = (

            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))

            for k, v in errors.iteritems()

        )

        raise cerberus.ValidationError(

            message_string.format(field, "\n".join(error_strings))

        )





class UnicodeDictWriter(csv.DictWriter, object):

    """Extend csv.DictWriter to handle Unicode input"""



    def writerow(self, row):

        super(UnicodeDictWriter, self).writerow({

            k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()

        })



    def writerows(self, rows):

        for row in rows:

            self.writerow(row)





# MAIN FUNCTION



def process_map(file_in, validate):

    """Iteratively process each XML element and write to csv(s)"""



    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:



        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)

        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)

        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)

        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)

        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)



        nodes_writer.writeheader()

        node_tags_writer.writeheader()

        ways_writer.writeheader()

        way_nodes_writer.writeheader()

        way_tags_writer.writeheader()



        validator = cerberus.Validator()



        for element in get_element(file_in, tags=('node', 'way')):

            el = shape_element(element)

            if el:

                if validate is True:

                    validate_element(el, validator)



                if element.tag == 'node':

                    nodes_writer.writerow(el['node'])

                    node_tags_writer.writerows(el['node_tags'])

                elif element.tag == 'way':

                    ways_writer.writerow(el['way'])

                    way_nodes_writer.writerows(el['way_nodes'])

                    way_tags_writer.writerows(el['way_tags'])
process_map(OSM_PATH, validate=False)

   

