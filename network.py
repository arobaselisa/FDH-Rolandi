import numpy as np
import pandas as pd
import json
import collections
import string
import io
import os
import sys, getopt
import os.path
from os import path
import subprocess


"nodes": {POur chaque scène, ajouter +1 à un charactère}
    "links": {Pour chaque scène i de 0 à la fin
                "Order les noms des personnage dans la scène"
                Pour personnage p de 0 à la fin de la scène
                    Pour personne j de p+1 à la fin de cette scène
                        dic[p][j][act] += 1
                        }
}

