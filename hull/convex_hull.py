import json
import os
from subprocess import Popen, PIPE, STDOUT
import numpy as np

"""
compile
"""
CONVEX_HULL_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'convex_hull')
if not os.path.exists(CONVEX_HULL_EXE):
    os.system('gcc %s.c -o %s' % (CONVEX_HULL_EXE, CONVEX_HULL_EXE))

"""
filter very far away junk
"""

def remove_outliers(collection):
    points = [feat['geometry']['coordinates'] for feat in collection['features']]
    median = np.median(points, axis=0)
    dist_from_med = np.sum((points - median) ** 2, axis=1)
    
    non_outliers, = np.where(dist_from_med <= np.std(dist_from_med) * 10)
    # points = points[dist_from_med <= np.std(dist_from_med) * 10]
    print "removed", np.count_nonzero(dist_from_med > np.std(dist_from_med))
    return {
        'type': 'FeatureCollection',
        'features': [collection['features'][i]
                    for i in non_outliers]
    }    

"""
see https://github.com/aviatorBeijing/concave_hull/blob/master/hull.c or better http://www.netlib.org/voronoi/hull.html for concave hull
"""

def convex_hull(collection):
    """
    input: FeatureCollection of type Point
    returns: Polygon convex hull 
    """
    points = '\n'.join(['%f %f' % tuple(feat['geometry']['coordinates']) for feat in collection['features']])

    pipe = Popen(['%s' % CONVEX_HULL_EXE], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    stdout = pipe.communicate(input=points)[0].decode()
    indices = [int(i) for i in stdout.strip().split()]

    # close polygon
    indices.append(indices[0])

    return {
        'type': 'Polygon', 
        'coordinates': [[
                    collection['features'][i]['geometry']['coordinates'] 
                    for i in indices
        ]]
    }


if __name__ == '__main__':

    with open('demo_points.json') as f:
        collection = json.load(f)

    collection = remove_outliers(collection)

    with open('demo_convex.json', 'w') as f:
        json.dump(convex_hull(collection), f)


