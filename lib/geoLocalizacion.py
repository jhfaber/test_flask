import requests,json


def fun_consultar_coordenadas(direccion):
    try:
        if(type(direccion)==str):
            URL="https://maps.googleapis.com/maps/api/geocode/json"
            params= params={
                "address": direccion,
                "components": "country:CO",
                "key":"AIzaSyBD7B20X6nDgerRjuW84R3lf5TtqDO6AVg"

            }

            response = requests.get(URL,  params=params)
            res=json.loads(response.content)
            if(res["status"]=="OK"):
                lat= res["results"][0]["geometry"]["location"]["lat"]
                lng = res["results"][0]["geometry"]["location"]["lng"]
                return {"lat":lat,"lng":lng}
            else:
                return {"lat":0,"lng":0}   
        else:
            return {"lat":0,"lng":0}
    except:
        return {"lat":0,"lng":0}
