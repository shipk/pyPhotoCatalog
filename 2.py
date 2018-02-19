import os,sys
from PIL import Image
from PIL.ExifTags import TAGS

for (k,v) in Image.open(sys.argv[1])._getexif().items():
    print('%s = %s' % (TAGS.get(k), v))