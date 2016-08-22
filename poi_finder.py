from __future__ import print_function
import json
import requests
import re

try:
    import configparser
except:
    import ConfigParser as configparser


from geojson import Feature, FeatureCollection, Point, dump
# from merge import merge_featurecollection

class poi_finder():
    def __init__(self):
        self.getParameters()

    def getParameters(self):
        conf  = configparser.ConfigParser()
        conf.read("./myconf.conf", encoding="utf-8")
        self.amap_url = conf.get("amap", "url")
        self.amap_params = {
            "key": conf.get("amap", "key"),
            "offset": conf.get("amap", "offset"),
            "citylimit":conf.get("amap", "citylimit"),
            "city":conf.get("amap", "city")
        }
        keywords = str(conf.get("amap", "keywords")) 
        self.amap_keywords = re.split(",|，",keywords)
        self.outputpath = conf.get("output","pathname")

    def download(self):
        keywords = self.amap_keywords
        for keyword in keywords:
            pois = self._download(keyword)
            self._dump_geojson(pois, keyword)
            
    def _download(self, keyword):
        pois = []
        page = 1
        offset = int(self.amap_params["offset"])
        while(True):
            result = self._request(keyword,page)
            pois.extend(result["pois"])
            if len(result["pois"]) < offset:
                break
            page += 1
        print(page, len(pois))
        return pois

    def _request(self, keyword, page):
        params = self.amap_params
        params["keywords"] = keyword
        params["page"] = page

        req = requests.get(self.amap_url,params)
        return json.loads(req.content.decode('utf-8'))


    def _dump_geojson(self, pois, keyword):
        features = []
        for poi in pois:
            location = poi["location"].split(",")
            point = Point((float(location[0]), float(location[1])))
            feature = Feature(geometry=point, properties={'name':poi["name"], 'address': poi["address"]})
            features.append(feature)
        geojson = FeatureCollection(features)
        with open(self.outputpath+'/'+ keyword + '.json' , 'w', encoding="utf-8") as fp:
            dump(geojson, fp)


def main():
    finder = poi_finder()
    finder.download()

if __name__ == '__main__':
    main()
