from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'albums.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def execute_query(query, values=()):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    db.close()

def query_db(query, values=(), one=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, values)
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return (results[0] if results else None) if one else results


@app.route('/update_from_spotify', methods=['POST'])
def update_from_spotify():
    data = request.json
    # Assuming the data contains a list of albums in JSON format
    albums_data = data.get('albums', [])

    # Mark all existing albums as hidden if they are from the library
    execute_query("UPDATE Albums SET hidden = 'yes' WHERE type = 'from_library'")

    for album_data in albums_data:
        album = album_data.get('album', {})
        title = album.get('name', '')
        artists = album.get('artists', [])
        artist = artists[0]['name'] if artists else ''
        year = int(album.get('release_date', '').split('-')[0]) if album.get('release_date') else None
        # Set type to 'from_library' always
        type_ = 'from_library'
        
        # Check if the album already exists in the database based on title and year
        existing_album = query_db("SELECT * FROM Albums WHERE title = ? AND year = ? AND type = ?", (title, year, type_), one=True)
        
        if existing_album:
            # If album exists, mark it as not hidden
            execute_query("UPDATE Albums SET hidden = 'no' WHERE id = ?", (existing_album['id'],))
        else:
            # Insert album into the database
            execute_query("INSERT INTO Albums (title, artist, year, type, hidden) VALUES (?, ?, ?, ?, ?)",
                          (title, artist, year, type_, 'no'))
    
    return jsonify({'message': 'Albums added or updated successfully'}), 200


@app.route('/add_album', methods=['POST'])
def add_album():
    data = request.json
    title = data['title']
    artist = data['artist']
    year = data['year']
    type_ = data['type']
    tags = data.get('tags', [])
    execute_query("INSERT INTO Albums (title, artist, year, type, tags) VALUES (?, ?, ?, ?, ?)",
                  (title, artist, year, type_, ','.join(tags)))
    return jsonify({'message': 'Album added successfully'}), 200

@app.route('/edit_title/<int:album_id>', methods=['PUT'])
def edit_title(album_id):
    new_title = request.json['title']
    execute_query("UPDATE Albums SET title = ? WHERE id = ?", (new_title, album_id))
    return jsonify({'message': 'Title updated successfully'}), 200

@app.route('/edit_artist/<int:album_id>', methods=['PUT'])
def edit_artist(album_id):
    new_artist = request.json['artist']
    execute_query("UPDATE Albums SET artist = ? WHERE id = ?", (new_artist, album_id))
    return jsonify({'message': 'Artist updated successfully'}), 200

@app.route('/edit_year/<int:album_id>', methods=['PUT'])
def edit_year(album_id):
    new_year = request.json['year']
    execute_query("UPDATE Albums SET year = ? WHERE id = ?", (new_year, album_id))
    return jsonify({'message': 'Year updated successfully'}), 200

@app.route('/toggle_hide/<int:album_id>', methods=['PUT'])
def toggle_hide(album_id):
    album = query_db("SELECT hidden FROM Albums WHERE id = ?", (album_id,), one=True)
    new_hidden = 'yes' if album['hidden'] == 'no' else 'no'
    execute_query("UPDATE Albums SET hidden = ? WHERE id = ?", (new_hidden, album_id))
    return jsonify({'message': 'Album hidden/unhidden successfully'}), 200

@app.route('/add_tags/<int:album_id>', methods=['PUT'])
def add_tags(album_id):
    tags = request.json.get('tags', [])
    current_tags = query_db("SELECT tags FROM Albums WHERE id = ?", (album_id,), one=True)['tags']
    
    if current_tags:
        new_tags = ','.join(set(current_tags.split(',') + tags))
    else:
        new_tags = ','.join(set(tags))
    
    execute_query("UPDATE Albums SET tags = ? WHERE id = ?", (new_tags, album_id))
    return jsonify({'message': 'Tags added successfully'}), 200

@app.route('/remove_tags/<int:album_id>', methods=['PUT'])
def remove_tags(album_id):
    tag_to_remove = request.json['tag']
    current_tags = query_db("SELECT tags FROM Albums WHERE id = ?", (album_id,), one=True)['tags']
    remaining_tags = [tag for tag in current_tags.split(',') if tag != tag_to_remove]
    new_tags = ','.join(remaining_tags)
    execute_query("UPDATE Albums SET tags = ? WHERE id = ?", (new_tags, album_id))
    return jsonify({'message': 'Tag removed successfully'}), 200

@app.route('/remove_album/<int:album_id>', methods=['DELETE'])
def remove_album(album_id):
    execute_query("DELETE FROM Albums WHERE id = ?", (album_id,))
    return jsonify({'message': 'Album removed successfully'}), 200

@app.route('/get_all_albums', methods=['GET'])
def get_all_albums():
    albums = query_db("SELECT * FROM Albums WHERE hidden = 'no'")
    return jsonify([dict(album) for album in albums]), 200

if __name__ == '__main__':
    app.run(debug=True)
