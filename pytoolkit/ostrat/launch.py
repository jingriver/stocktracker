import sys
import os
import string, traceback

bin_dir = os.path.join(sys.prefix, "bin")
pkg_dir = os.path.join(sys.prefix, "package")

libdirs = [
    os.path.join(pkg_dir, "ostrat"),
    bin_dir,
]

sys.path = libdirs + sys.path

import ostrat

ostrat.run()
