import math
from copy import deepcopy
import json
from geojson_utils import point_distance

def merge_featurecollection(*jsons):
    features = []
    for json in jsons:
        if json['type'] == 'FeatureCollection':
            for feature in json['features']:
                features.append(feature)
    return {"type":'FeatureCollection',"features":features}

def simplify_other(major, minor, dist):
    """
    point featurecollection only
    """
    result = deepcopy(major)
    if major['type'] == 'FeatureCollection' and minor['type'] == 'FeatureCollection':
        arc = dist/6371000*180/math.pi*2
        for minorfeature in minor['features']:
            minorgeom = minorfeature['geometry']
            minorlng = minorgeom['coordinates'][0]
            minorlat = minorgeom['coordinates'][1]

            is_accept = True
            for mainfeature in major['features']:
                maingeom = mainfeature['geometry']
                mainlng = maingeom['coordinates'][0]
                mainlat = maingeom['coordinates'][1]
          
                if abs(minorlat-mainlat) <= arc and abs(minorlng-mainlng) <= arc:
                    distance = point_distance(maingeom, minorgeom)
                    if distance < dist:
                        is_accept = False
                        break
            if is_accept:
                result["features"].append(minorfeature)
    return result


def main():
    with open("G:/brandon/greenway/0819/qq/公厕.json", "r",encoding="utf-8") as fp:
        qq = json.load(fp)
    with open("G:/brandon/greenway/0819/amap/公厕.json","r",encoding="utf-8") as fp:
        amap = json.load(fp)
    with open("G:/brandon/greenway/0819/baidu/公厕.json","r",encoding="utf-8") as fp:
        baidu = json.load(fp)
    merge1 = simplify_other(qq, amap, 20)
    merge2 = simplify_other(merge1, baidu, 20)
    print(merge2)
    with open("G:/brandon/greenway/0819/merge2.json","w",encoding="utf-8") as fp:
        json.dump(merge2, fp)


if __name__ == '__main__':
    main()