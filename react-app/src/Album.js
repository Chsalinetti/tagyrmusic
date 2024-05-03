// Album.js
import React from 'react';
import './Album.css';

function Album({ album, fetchAllAlbums }) {
  const handleHide = async () => {
    try {
      const response = await fetch(`/toggle_hide/${album.id}`, {
        method: 'PUT',
      });
      if (response.ok) {
        console.log('Album hidden/unhidden successfully');
        fetchAllAlbums();
      } else {
        console.error('Failed to toggle hide album');
      }
    } catch (error) {
      console.error('Error toggling hide album:', error);
    }
  };

  return (
    <div className="Album">
      <div className="Album-top">
        <button>Edit Title</button>
        <button>Edit Artist</button>
        <button>Edit Year</button>
        <button className="hide-button" onClick={handleHide}>Toggle Hide</button>
      </div>
      <div className="Album-bottom">
        {Array.isArray(album.tags) && album.tags.map(tag => (
          <button key={tag}>{tag}</button>
        ))}
        <button>Add Tag</button>
      </div>
    </div>
  );
}

export default Album;