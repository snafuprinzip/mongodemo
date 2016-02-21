#!/usr/bin/python

# Example taken from https://github.com/mongolab/mongodb-driver-examples/blob/master/python/pymongo_simple_example.py
# and added reading the necessary data from the environment in order to run it on openshift

__author__ = 'mleimenmeier'

import os
import sys
import pymongo
import web

SONG_DATA = [
    {
        'artist': 'Volbeat',
        'song': 'Still Counting',
        'genre': 'Heavy Metal, Hard Rock, Psychobilly',
        'year': 2007
    },
    {
        'artist': 'Aghora',
        'song': 'Mahayana',
        'genre': 'Progressive Metal',
        'year': 2006
    },
    {
        'artist': 'Frank Zappa',
        'song': 'Cheepnis',
        'genre': 'Jazz',
        'year': 1974
    }
]

urls = (
    '/', 'Index',
    '/dropdb', 'DropDB',
    '/add', 'AddSong'
)

def CreateTable():
    print("Collecting song information from mongodb...")
    entries = ""
    cursor = songs.find({'year': {'$gte': 0}}).sort('artist', 1)
    for entry in cursor:
        entries += """
<tr> 
    <td>%s</td> 
    <td>%s</td> 
    <td>%s</td> 
    <td>%s</td>
</tr>
        """ % (entry['artist'], entry['song'], entry['genre'], entry['year'])
    #    print(entries)
    return entries


class Index(object):
    def GET(self):
        print("Index.GET called")
        return render.index(table = CreateTable())


class AddSong(object):
    def GET(self):
        print("AddSong.GET called")
        return render.add_form()

    def POST(self):
        print("AddSong.POST called")
        global songs

        form = web.input(artist="Nobody", song="Nothing", genre="Classical", year="0")
        entry = {
            'artist': form.artist,
            'song':   form.song,
            'genre':  form.genre,
            'year':   int(form.year)
        }
        songs.insert_one(entry)

        return render.index(table = CreateTable())


class DropDB(object):
    def GET(self):
        print("DropDB.GET called")
        global db
        db.drop_collection('songs')
        return render.index(table = CreateTable())


app = web.application(urls, globals())
render = web.template.render("templates/", base="layout")

# read environment variables to collect information about the mongodb
mongohost = os.getenv("MONGODB_SERVICE_HOST", "localhost")
mongoport = os.getenv("MONGODB_SERVICE_PORT", 27017)
username  = os.getenv("MONGODB_USER")
password  = os.getenv("MONGODB_PASSWORD")
dbname    = os.getenv("MONGODB_DATABASE")
adminpwd  = os.getenv("MONGODB_ADMIN_PASSWORD")

### URI format: mongodb://[dbuser:dbpassword@]host:port/dbname
MONGODB_URI = 'mongodb://%s:%s@%s:%d/%s' % (username, password, 
                                            mongohost, int(mongoport), 
                                            dbname)
print ("Connecting to mongodb: %s ..." % MONGODB_URI)

client = pymongo.MongoClient(MONGODB_URI)
db     = client.get_default_database()
    
songs = db['songs']

query = {'song': 'Cheepnis'}
print query
if songs.find(query).count() == 0: # document doesn't exist
    print("Inserting some songs for your convenience...")
    songs.insert(SONG_DATA)

print("Testing the update of a song...")
songs.update(query, {'$set': {'artist': 'Frank Zappa & The Mothers of Invention'}})

def main():
    print("Starting the web application...") 
    app.run()

    print("closing mongodb client before exiting...")
    client.close()

if __name__ == "__main__":
    main()
