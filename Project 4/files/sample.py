
import xml.etree.ElementTree as ET

OSM_FILE = "ottawa_canada.osm"  

SAMPLE_FILE = "ottawa_sample.osm"
def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(filename):
    if os.path.isfile(filename):
        file_info = os.stat(filename)
        return convert_bytes(file_info.st_size)
size = file_size(SAMPLE_FILE)
print('OSMsize',size)

k = 35
def get_element(osm_file, tags=('node', 'way', 'relation')):
    
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

with open(SAMPLE_FILE, 'wb') as output:
    b = bytearray()
    b.extend('<?xml version="1.0" encoding="UTF-8"?>\n'.encode())
    b.extend('<osm>\n  '.encode())
    output.write(b)

    # Write every kth top level element
    print (OSM_FILE)
    for i, element in enumerate(get_element(OSM_FILE)):

        if not i % k:
            output.write(ET.tostring(element, encoding='utf-8'))
    b_end = bytearray()
    b_end.extend('</osm>'.encode())
    output.write(b_end)

sample_size = file_size(SAMPLE_FILE)
print ('SampleSize', sample_size)