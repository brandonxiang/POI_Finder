import json
import requests
from geojson import Feature, FeatureCollection, Point, dump
from merge import merge_featurecollection


def download():
    names = ['shenzhenwan']
    items = ['公厕', '公交站', '景点', '停车场', '驿站', '自行车租赁点']
    for name in names:
        for item in items:
            _download(name, item)
            print(name, item)


def merge_json():
    names = ['dapeng', 'dayun', 'fenghuang', 'guangming', 'longhua', 'luohu', 'meilin', 'pingshan', 'yantian', 'shenzhenwan']
    items = ['公厕', '公交站', '景点', '停车场', '驿站', '自行车租赁点']

    for item in items:
        jsons = []
        for name in names:
            with open('../绿道数据160714/%s/%s.json' % (name, item), 'r') as fp:
                jsons.append(json.load(fp))
        one = merge_featurecollection(*jsons)
        with open('../绿道数据160714/%s.json' % (item), 'w') as fp:
            json.dump(one, fp)


def _download(name, item):
    south, west, north, east = get_bounds(name)
    result = finder(item, west, south, east, north)
    dump_geojson(result, item, name)


def get_bounds(name):
    with open('../绿道数据160714/%s/%s.geojson' % (name, name), 'r', encoding='utf-8') as fp:
        geojson = json.load(fp)
        return bbox(geojson)


def bbox(geojson):
    x_mins = []
    y_mins = []
    x_maxs = []
    y_maxs = []

    features = geojson['features']
    for feature in features:
        geometry = feature['geometry']
        coords = [geometry['coordinates']] if geometry['type'] == 'LineString' else geometry['coordinates']
        x_min, y_min, x_max, y_max = _bbox_around_polycoords(coords)
        x_mins.append(x_min)
        y_mins.append(y_min)
        x_maxs.append(x_max)
        y_maxs.append(y_max)
    return [min(x_mins), min(y_mins), max(x_maxs), max(y_maxs)]


def _bbox_around_polycoords(coords):
    """
    bounding box
    """
    x_all = []
    y_all = []

    for first in coords[0]:
        x_all.append(first[1])
        y_all.append(first[0])

    return [min(x_all), min(y_all), max(x_all), max(y_all)]


def finder(item, west, south, east, north):

    url_demo = """http://ditu.amap.com/service/poiInfo?query_type=TQUERY&city=440300&keywords=%s&
    pagesize=20&pagenum=1&qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&
    addr_poi_merge=true&is_classify=true&geoobj=%s|%s|%s|%s"""
    url = url_demo % (item, west, south, east, north)
    req = requests.get(url)
    return json.loads(req.content.decode('utf-8'))


def dump_geojson(result, item, path):
    assert len(result['data']) == 1

    features = []
    for marker in result['data'][0]['list']:
        point = Point((float(marker['longitude']), float(marker['latitude'])))
        feature = Feature(geometry=point, properties={'name': marker['name'], 'address': marker['address']})
        features.append(feature)
    geojson = FeatureCollection(features)
    with open('../绿道数据160714/%s/%s.json' % (path, item), 'w') as fp:
        dump(geojson, fp)


def main():
    download()
    merge_json()

if __name__ == '__main__':
    main()
