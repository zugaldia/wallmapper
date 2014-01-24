from mapbox_client import MapboxClient
import argparse

'''
Defaults
'''

# Nexus 5
DEFAULT_WIDTH = 1080 * 2
DEFAULT_HEIGHT = 1920

# Washington, DC
DEFAULT_LATITUDE = 38.91010
DEFAULT_LONGITUDE = -77.0485
DEFAULT_ZOOM = 17

# Some beautiful basemap to start with -- see /examples for more
DEFAULT_BASEMAP = 'eleanor.mnyzxgvi'  # Max zoom 21

# Output file
DEFAULT_OUTPUT = 'wallmapper.png'

# Stats
DEFAULT_STATS = True

'''
Parser
'''

parser = argparse.ArgumentParser(
    prog='Wallmapper',
    description='Create high resolution wallpapers from Mapbox maps.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    add_help=True)

parser.add_argument('--width',
    type=int, default=DEFAULT_WIDTH, help='Wallpaper width')
parser.add_argument('--height',
    type=int, default=DEFAULT_HEIGHT, help='Wallpaper height')
parser.add_argument('--latitude',
    type=float, default=DEFAULT_LATITUDE, help='Latitude')
parser.add_argument('--longitude',
    type=float, default=DEFAULT_LONGITUDE, help='Longitude')
parser.add_argument('--zoom',
    type=int, default=DEFAULT_ZOOM, help='Zoom level')
parser.add_argument('--basemap',
    type=str, default=DEFAULT_BASEMAP, help='Mapbox basemap')
parser.add_argument('--output',
    type=str, default=DEFAULT_OUTPUT, help='Output filename')
parser.add_argument('--stats',
    type=bool, default=DEFAULT_STATS, help='Print some raw statistics')

args = vars(parser.parse_args())

'''
Mapbox client
'''

try:
    print 'Generating wallpaper...'
    mapbox_client = MapboxClient(**args)
    mapbox_client.generate_wallpaper()
except Exception as e:
    print 'Error:', str(e)
else:
    print 'Done.'
