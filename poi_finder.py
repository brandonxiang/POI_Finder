from __future__ import print_function
import json
import requests
import re
from geojson import Feature, FeatureCollection, Point, dump
try:
    import configparser
except:
    import ConfigParser as configparser

class poi_finder():

    def _request(self, url, params):
        req = requests.get(url, params)
        return json.loads(req.content.decode('utf-8'))

    def _dump_geojson(self, results, output, keyword):
        features = []
        for result in results:
            point = Point((result["lat"], result["lng"]))
            feature = Feature(geometry=point, properties={'name':result["name"], 'address': result["address"] })
            features.append(feature)
        geojson = FeatureCollection(features)
        with open(output+'/'+ keyword + '.json' , 'w', encoding="utf-8") as fp:
            dump(geojson, fp)


class amap_finder(poi_finder):
    def __init__(self):
        self.getParameters()

    def getParameters(self):
        conf  = configparser.ConfigParser()
        conf.read("./myconf.conf", encoding="utf-8")
        self.__url = conf.get("amap", "url")
        self.__params = {
            "key": conf.get("amap", "key"),
            "offset": conf.get("amap", "offset"),
            "citylimit":conf.get("amap", "citylimit"),
            "city":conf.get("amap", "city")
        }
        keywords = str(conf.get("amap", "keywords")) 
        self.__keywords = re.split(",|，",keywords)
        self.__output = conf.get("amap","output")

    def download(self):
        keywords = self.__keywords
        output = self.__output
        for keyword in keywords:
            pois = self._download(keyword)
            results = self._parse(pois)
            self._dump_geojson(results, output, keyword)
            
    def _download(self, keyword):
        pois = []
        page = 1
        offset = int(self.__params["offset"])
        params = self.__params
        params["keywords"] = keyword
        while(True):
            params["page"] = page
            result = self._request(self.__url, params)
            pois.extend(result["pois"])
            if len(result["pois"]) < offset:
                break
            page += 1
        print(page, len(pois))
        return pois

   
    def _parse(self, pois):
        results = []
        for poi in pois:
            location = poi["location"].split(",")
            result = {}
            result["lat"] = float(location[0])
            result["lng"] = float(location[1])
            result["name"] = poi["name"]
            result["address"] = poi["address"]
            results.append(result)
        return results


def main():
    finder = amap_finder()
    finder.download()

if __name__ == '__main__':
    main()
