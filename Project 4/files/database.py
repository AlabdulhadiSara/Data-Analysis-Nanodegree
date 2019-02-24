import csv
import sqlite3


sqlite_file = 'ottawa.db'

conn = sqlite3.connect(dbfile)


# Get a cursor object

cur = conn.cursor()


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):

    # csv.py doesn't do Unicode; encode temporarily as UTF-8:

    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),

                            dialect=dialect, **kwargs)

    for row in csv_reader:

        # decode UTF-8 back to Unicode, cell by cell:

        yield [unicode(cell, 'utf-8') for cell in row]



def utf_8_encoder(unicode_csv_data):

    for line in unicode_csv_data:

        yield line.encode('utf-8')

        

def UnicodeDictReader(utf8_data, **kwargs):

    csv_reader = csv.DictReader(utf8_data, **kwargs)

    for row in csv_reader:

        yield {key: value.encode('utf-8') for key, value in row.items()}


# Create the table, specifying the column names and data types:

cur.execute('''

    CREATE TABLE IF NOT EXISTS nodes_tags(id INTEGER, key TEXT, value TEXT,type TEXT)

''')

cur.execute('''

    CREATE TABLE IF NOT EXISTS nodes(id INTEGER, lat REAL, lon REAL, user TEXT, uid INTEGER, 

    version INTEGER, changeset INTEGER, timestamp TIMESTAMP)

''')

cur.execute('''

    CREATE TABLE IF NOT EXISTS ways(id INTEGER, user TEXT, uid INTEGER, changeset INTEGER, timestamp TIMESTAMP)

''')

cur.execute('''

    CREATE TABLE IF NOT EXISTS ways_tags(id INTEGER, key TEXT, value TEXT, type TEXT) 

''')

cur.execute('''

    CREATE TABLE IF NOT EXISTS ways_nodes(id INTEGER, node_id INTEGER, position INTEGER)

''')



# commit the changes

conn.commit()



# Read in the csv file as a dictionary, format the

# data as a list of tuples:

with open('nodes_tags.csv','r') as fin:

    dr = UnicodeDictReader(fin) # comma is default delimiter

    to_db = [('id', 'key','value', 'type') for i in dr] 



with open('nodes.csv', 'r') as fin2:

    dr2 = UnicodeDictReader(fin2)

    to_db2 = [('id','lat','lon','user','uid', 'version','changeset','timestamp') for i in dr2]

    

with open('ways.csv', 'r') as fin3:

    dr3 = UnicodeDictReader(fin3)

    to_db3 = [('id','user','uid','changeset','timestamp') for i in dr3]

    

with open('ways_tags.csv', 'r') as fin4:

    dr4 = UnicodeDictReader(fin4)

    to_db4 = [('id','key','value','type') for i in dr4]  

    

with open('ways_nodes.csv', 'r') as fin5:

    dr5 = UnicodeDictReader(fin5)

    to_db5 = [('id','node_id','position') for i in dr5]  

    

    # insert the formatted data

cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)

cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db2)

cur.executemany("INSERT INTO ways(id, user, uid, changeset, timestamp) VALUES (?, ?, ?, ?, ?);", to_db3)

cur.executemany("INSERT INTO ways_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db4)

cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db5)



# commit the changes

conn.commit()
conn.close()

