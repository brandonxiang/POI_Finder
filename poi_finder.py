from __future__ import print_function
import json
import requests
import re
import time
from geojson import Feature, FeatureCollection, Point, dump
try:
    import configparser
except:
    import ConfigParser as configparser

class poi_finder():

    def __init__(self, keywords, output):
        self.__keywords = keywords
        self.__output  = output

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

    def download(self):
        keywords = self.__keywords
        output = self.__output
        for keyword in keywords:
            pois = self._download(keyword)
            results = self._parse(pois)
            self._dump_geojson(results, output, keyword)

    def _download(self,keyword):
        pass
    
    def _parse(self,pois):
        pass


class amap_finder(poi_finder):

    def __init__(self):
        conf  = configparser.ConfigParser()
        conf.read("./myconf.conf", encoding="utf-8")
        keywords = str(conf.get("amap", "keywords")) 
        keywords = re.split(",|，",keywords)
        output = conf.get("amap","output")
        super().__init__(keywords, output)
        self.__url = conf.get("amap", "url")
        self.__params = {
            "key": conf.get("amap", "key"),
            "offset": conf.get("amap", "offset"),
            "citylimit":conf.get("amap", "citylimit"),
            "city":conf.get("amap", "city")
        }
            
    def _download(self, keyword):
        offset = int(self.__params["offset"])
        params = self.__params
        params["keywords"] = keyword
        pois = []
        page = 1
       
        while(True):
            params["page"] = page
            result = self._request(self.__url, params)
            pois.extend(result["pois"])
            if len(result["pois"]) < offset:
                break
            page += 1
        print(keyword, page, len(pois))
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

class qq_finder(poi_finder):

    def __init__(self):
        conf  = configparser.ConfigParser()
        conf.read("./myconf.conf", encoding="utf-8")
        keywords = str(conf.get("qq", "keywords")) 
        keywords = re.split(",|，",keywords)
        output = conf.get("qq","output")
        super().__init__(keywords, output)
        self.__url = conf.get("qq", "url")
        self.__params = {
            "key": conf.get("qq", "key"),
            "page_size": conf.get("qq", "page_size"),
            "boundary":"region("+conf.get("qq", "city")+",0)"
        }
        

    def _download(self, keyword):
        offset = int(self.__params["page_size"])
        params = self.__params
        params["keyword"] = keyword
        pois = []
        page = 1

        while(True):
            params["page_index"] = page
            result = self._request(self.__url, params)
            if "data" not in result:
                time.sleep(0.5)
                result = self._request(self.__url, params)

            pois.extend(result["data"])
            if len(result["data"]) < offset:
                break
            page += 1
        print(keyword, page, len(pois))
        return pois

   
    def _parse(self, pois):
        results = []
        for poi in pois:
            location = poi["location"]
            result = {}
            result["lat"] = location['lat']
            result["lng"] = location['lng']
            result["name"] = poi["title"]
            result["address"] = poi["address"]
            results.append(result)
        return results

class baidu_finder(poi_finder):

    def __init__(self):
        conf  = configparser.ConfigParser()
        conf.read("./myconf.conf", encoding="utf-8")
        keywords = str(conf.get("baidu", "keywords")) 
        keywords = re.split(",|，",keywords)
        output = conf.get("baidu","output")
        super().__init__(keywords, output)
        self.__url = conf.get("baidu", "url")
        self.__params = {
            "ak": conf.get("baidu", "key"),
            "page_size": conf.get("baidu", "page_size"),
            "region": conf.get("baidu", "city"),
            "output": conf.get("baidu","type")
        }
        

    def _download(self, keyword):
        offset = int(self.__params["page_size"])
        params = self.__params
        params["q"] = keyword
        pois = []
        page = 0

        while(True):
            params["page_num"] = page
            result = self._request(self.__url, params)
            
            pois.extend(result["results"])
            if len(result["results"]) < offset:
                break
            page += 1
        print(keyword, page, len(pois))
        return pois

   
    def _parse(self, pois):
        results = []
        for poi in pois:
            location = poi["location"]
            result = {}
            result["lat"] = location['lat']
            result["lng"] = location['lng']
            result["name"] = poi["name"]
            result["address"] = poi["address"]
            results.append(result)
        return results

def main():
    finder = baidu_finder()
    finder.download()

if __name__ == '__main__':
    main()
