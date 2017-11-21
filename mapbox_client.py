'''
Not as fun, and without caching, but this is an alternative to most of this code
using ModestMaps: https://gist.github.com/tmcw/4199233
'''

from __future__ import division  # divisions are float now
from PIL import Image
from urllib.request import urlopen
import math
import os

# Tiles are 256 pixels squares
TILE_SIZE = 256

# Cache tiles not to abuse our Mapbox friends
CACHE_FOLDER = 'cache'

API_URL = 'http://api.mapbox.com/styles/v1/%s/%s/tiles/256/%d/%d/%d?access_token=%s'
TILE_TEMPLATE = CACHE_FOLDER + '/%s-%s-%d-%d-%d.png'

class MapboxClientError(Exception):
    ''' Base class for exceptions in this module. '''
    pass

class MapboxClient():
    def __init__(self, width, height, latitude, longitude, zoom, basemap, output, stats, user, token):
        # Save properties
        self.wallpaper_width = width
        self.wallpaper_height = height
        self.zoom = zoom
        self.basemap = basemap
        self.output = output
        self.user = user
        self.token = token

        # Compute basic elements
        total_tiles = self.get_total_tiles(zoom=zoom)
        central_tile = self.deg2num(
            lat_deg=latitude, lon_deg=longitude, total_tiles=total_tiles)
        self.tile_set = self.get_tile_set(
            wallpaper_width=width, wallpaper_height=height,
            central_tile=central_tile, total_tiles=total_tiles)

        # Print stats
        if stats:
            print('This zoom level has this many tiles in total', total_tiles)
            print('The central tile is', central_tile)
            print('This is the tile set we will assemble', self.tile_set)
            print('The total number of required tiles is', len(self.tile_set[0]) * len(self.tile_set[1]))
            print('The raw width before cropping is', len(self.tile_set[0]) * TILE_SIZE)
            print('The raw height before cropping is', len(self.tile_set[1]) * TILE_SIZE)

    def generate_wallpaper(self):
        self.download_tiles(tile_set=self.tile_set, basemap=self.basemap, zoom=self.zoom, user=self.user, token=self.token)
        self.merge_tiles(
            tile_set=self.tile_set, basemap=self.basemap, zoom=self.zoom,
            wallpaper_width=self.wallpaper_width, wallpaper_height=self.wallpaper_height,
            output=self.output, user=self.user)

    '''
    Math helpers
    '''

    @staticmethod
    def get_total_tiles(zoom):
        ''' The total number of tiles at this zoom level '''
        return (2 ** zoom)

    @staticmethod
    def deg2num(lat_deg, lon_deg, total_tiles):
        ''' 
        Converts lon/lat to tile number.
        See http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2
        '''
        lat_rad = math.radians(lat_deg)
        xtile = int((lon_deg + 180.0) / 360.0 * total_tiles)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * total_tiles)
        return (xtile, ytile)

    @classmethod
    def get_tile_set(cls, wallpaper_width, wallpaper_height, central_tile, total_tiles):
        ''' Returns a tuple with the list of tiles needed in each direction '''
        return (
            cls.get_tile_set_dim(wallpaper_width, central_tile[0], total_tiles),
            cls.get_tile_set_dim(wallpaper_height, central_tile[1], total_tiles))

    @staticmethod
    def get_tile_set_dim(wallpaper_size, central_tile, total_tiles):
        ''' The math is the same in both dimensions '''
        extra_space = (wallpaper_size - TILE_SIZE) / 2
        extra_tiles = 0 if extra_space <= 0 else int(math.ceil(extra_space / TILE_SIZE))

        # Make sure the zoom level is high enough
        if (1 + (2 * extra_tiles)) > total_tiles:
            raise MapboxClientError('Zoom is not high enough to provide so many tiles')

        # The actual range
        tiles = range(central_tile - extra_tiles,
                      central_tile + (extra_tiles + 1))

        # Cyclic addition, there must be a better way for this
        for key, value in enumerate(tiles):
            if value < 0:
                tiles[key] = value + total_tiles
            elif value >= total_tiles:
                tiles[key] = value - total_tiles

        return tiles

    '''
    Image helpers
    '''

    @classmethod
    def download_tiles(cls, tile_set, basemap, zoom, user, token):
        ''' Download the images (if not present in the cache) '''
        for x in tile_set[0]:
            for y in tile_set[1]:
                tile_destination = TILE_TEMPLATE % (user, basemap, zoom, x, y)
                if not os.path.exists(tile_destination):
                    tile_url = API_URL % (user, basemap, zoom, x, y, token)
                    cls.download_tile(tile_url, tile_destination)

    @staticmethod
    def download_tile(tile_url, tile_destination):
        ''' Download an individual file'''
        f = urlopen(tile_url)
        with open(tile_destination, 'wb') as local_file:
            local_file.write(f.read())

    @staticmethod
    def merge_tiles(tile_set, basemap, zoom, wallpaper_width, wallpaper_height, output, user):
        ''' Merge all the tiles into one big image '''
        image_width = len(tile_set[0]) * TILE_SIZE
        image_height = len(tile_set[1]) * TILE_SIZE
        image = Image.new('RGB', (image_width, image_height))
        for posx in range(0, len(tile_set[0])):
            for posy in range(0, len(tile_set[1])):
                tile_file = TILE_TEMPLATE % (user, basemap, zoom, tile_set[0][posx], tile_set[1][posy])
                tile_image = Image.open(tile_file)
                image.paste(tile_image, (posx * TILE_SIZE, posy * TILE_SIZE))

        # Crop
        start_left = int((image_width - wallpaper_width) / 2)
        start_top = int((image_height - wallpaper_height) / 2)
        result = image.crop((start_left, start_top, start_left + wallpaper_width, start_top + wallpaper_height))

        # Save
        result.save(output)
