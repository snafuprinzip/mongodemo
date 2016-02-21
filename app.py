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
        'genre': 'Metal',
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

app = web.application(urls, globals())
render = web.template.render("templates/", base="layout")

class Index(object):
    def GET(self):
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
            """ % (entry.artist, entry.song, entry.genre, entry.year)
        return render.index(table = entries)


class AddSong(object):
    def GET(self):
        return render.add_form()

    def POST(self):
        global songs

        form = web.input(artist="Nobody", song="Nothing", genre="Classical", year="0")
        entry = {
            'artist': form.artist,
            'song':   form.song,
            'genre':  form.genre,
            'year':   int(form.year)
        }
        songs.insert(entry)

        return render.index()


class DropDB(object):
    def GET(self):
        global db
        db.drop_collection('songs')
        return render.index()


###############################################################################
# main
###############################################################################

if __name__ == '__main__':
    global db
    global songs

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
    print("Inserting some songs if they aren't already there...")
    songs.insert(SONG_DATA)

    print("Testing the update of a song...")
    query = {'song': 'Cheepnis'}
    songs.update(query, {'$set': {'artist': 'Frank Zappa & The Mothers of Invention'}})

    # start the web application 
    app.run()

    # close mongodb client before exiting
    client.close()
