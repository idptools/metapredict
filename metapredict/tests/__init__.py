"""

Empty init file in case you choose a package besides PyTest such as Nose which may look for such a rfile

"""

import os

dir = 'output/'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))
