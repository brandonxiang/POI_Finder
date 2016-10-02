# POI_Finder
A finder for POI in Chinense webgis platform.


## Usage

You can copy `conf_demo.conf` into another config file. Then, you can fill config parameter into it.

```
[amap]
url = http://restapi.amap.com/v3/place/text
key = 
city = 
citylimit = 
keywords = 
offset = 
output = 

[qq]
url = http://apis.map.qq.com/ws/place/v1/search
key = 
city = 
keywords = 
page_size = 
output = 

[baidu]
url = http://api.map.baidu.com/place/v2/search
key = 
city = 
keywords = 
page_size = 
type = 
output = 
```

You can run `POI_Finder.py`.

## License

[MIT](LICENSE)
