from flask import Flask, jsonify, request,session, redirect, url_for
from flask_restful import Api, Resource
from functools import wraps
# from api import *

from lib import funcionesbasicas as fb
from lib import geoLocalizacion as gl




app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
api = Api(app)

helper = fb.Helpers()
db = fb.SqlDatabase(database="lib/flask.db")
            
def comprobarSession(f):
    # @wraps(f)
    def fun(*args, **kwargs):    
            if 'usuario' in session:  
                if session["usuario"] != None:
                    return f(*args, **kwargs)            
            return {"correcto":0,"msg":"!No estás loggueado!"}
          
    fun.__name__ = f.__name__
    return fun



@app.route("/login", methods=["POST","GET"])
def login():
    try:
        # print(session)
        data = request.get_json()


        if("usuario" in session):
            retMap= {
                "correcto":1,
                "msg":"Ya estás loggueado con el usuario: "+session["usuario"],
                'Status Code': 200
            }
            return jsonify(retMap)

        if("usuario" in data and "password"):
            user=data["usuario"]
            password= data["password"]
        else:
            retMap= {
                "correcto":0,
                "msg":"Ingresa todos los parametros: usuario,password",
                'Status Code': 301
            }
            return jsonify(retMap)

        #NO EXISTE
        # print(user)
        res= db.comprobar_existencia_usuario(user)
        if(res["correcto"]==0):
            retMap = {
            'Message': "Usuario o contraseña incorrecto ",
            'Status Code': 301
            }
            return jsonify(retMap)
        

        #COMPROBAR SI TIENE LA MISMA CONTRASEÑA
        if(user==res["nombre"] and str(password)==res["password"]):            
            session['usuario'] =user
            session['tipo_usuario']=res["tipo_usuario"]
            retMap = {
                'Message': "Usuario loggeado con exito",
                'Status Code': 200
            }
            return jsonify(retMap)
        else:

            retMap = {
                    'Message': "Usuario o contraseña incorrecto ",
                    'Status Code': 301
            }
            return jsonify(retMap)
    except Exception as e:
        return helper.code_status_error(e)



@app.route('/logout', methods=["POST"])
def logout():
    print(session)
    if("usuario" in session):
        session.pop('usuario', None)
        retMap = {
                'Message': "Te haz desconectado con éxito",
                'Status Code': 200
            }
    else:
        retMap = {
        'Message': "No estás loggeado",
        'Status Code': 200
        }

    return jsonify(retMap)


@app.route('/', methods=["POST"])
@comprobarSession
def hello_world():
    try: 
        retMap = {
            'Message': "Estás loggeado con usuario "+ session["usuario"] ,
            'Status Code': 200
        }
        return jsonify(retMap)

    except Exception as e:
        return helper.code_status_error(e)



################################################################
#  VOTANTES
##########################################################
@app.route('/api/votante/<accion>', methods=["POST","GET","DELETE"])
@comprobarSession
def admin_votante(accion=""):
    try:
        data = request.get_json()
        #COORDENADAS VOTANTES
        if request.method == 'GET' and accion=="coordenadas":
            df= db.sql_select("SELECT * FROM votantes")
            if(not df.empty):
                df["coordenadas"]=df["direccion"].apply(lambda x:gl.fun_consultar_coordenadas(x))
                          
                             
            retMap = {
            'registros': df.to_dict(orient="records"),
            'Message': "Consultado con éxito",
            'Status Code': 200,

            }
            return jsonify(retMap)
            




        #ACTUALIZAR
        if request.method == 'POST' and accion=="actualizar":
            re,va=helper.validador_datos_entrantes({"nombre":["largo","caracteres"],"cedula":["largo","caracteres"]},data)
            if(len(re)>0 or len(va)>0):
                retMap = {
                'Message': "Debe entregar los datos correctos",
                'Status Code': 302,
                'faltantes':re,
                'validaciones':va
                }
                return jsonify(retMap)


            # res= db.comprobar_existencia_usuario(session["usuario"])
            db.ejecutar_consulta("UPDATE votantes SET cedula='{cedula}' WHERE nombre='{nombre}'".format(nombre=data["nombre"],cedula=data["cedula"]))
            retMap = {
                'Message': "Usuario actualizado",
                'Status Code': 200,

                }
            return jsonify(retMap)



        #CREAR VOTANTE
        if request.method == 'POST':
            re,va=helper.validador_datos_entrantes({"nombre":["largo","caracteres"],
             "apellidos":["largo","caracteres"],"cedula":["largo","caracteres"],
             "telefono":["largo","caracteres"],"serial_puesto":["caracteres"],
             "direccion":[""]
            },data)

            if(len(re)>0 or len(va)>0):
                retMap = {
                'Message': "Debe entregar los datos correctos",
                'Status Code': 302,
                'faltantes':re,
                'validaciones':va
                }
                return jsonify(retMap)
            coordenadas= gl.fun_consultar_coordenadas(data["direccion"])
            id=db.insertar_registro("votantes",["nombre","apellidos","telefono","cedula","serial_puesto","nombre_usuario","serial_puesto","direccion"],
            [data["nombre"],data["apellidos"],data["telefono"],data["cedula"],data["serial_puesto"],session['usuario'],data["serial_puesto"],data["direccion"]
            ],serial="serial_vot")

            #LOG
            db.insertar_registro("log",["nombre_usuario","nombre_votante"],
            [session['usuario'],data["nombre"]
            ],serial="serial_log")


            retMap = {
                'Message': "Votante Creado",
                'Status Code': 200,
                "id":id,
                "data":data,
                "coordenadas":coordenadas
                }
            return jsonify(retMap)

        if request.method == 'GET' and accion=="cantidad":
            df= db.sql_select("SELECT COUNT(*) as cantidad_votantes FROM votantes") 
            retMap = {
                'Message': "Consulta éxitosa",
                'Status Code': 200,
                "registros":df.to_dict(orient="records")
                }
            return jsonify(retMap)



        if request.method == 'DELETE':            
            re,va=helper.validador_datos_entrantes({"nombre":["largo"]},data)
            if(len(re)>0 or len(va)>0):
                retMap = {
                'Message': "Debe entregar los datos correctos",
                'Status Code': 302,
                'faltantes':re,
                'validaciones':va
                }
                return jsonify(retMap)
            db.ejecutar_consulta("DELETE FROM votantes WHERE nombre='{nombre}'".format(nombre=data["nombre"]))
            retMap = {
                'Message': "Votante eliminado",
                'Status Code': 200,

                }
            return jsonify(retMap)
        
        retMap = {
        'Message': "Sin Fabricar",
        'Status Code': 200,
        "method":request.method, 
        "data":data
        }
        return jsonify(retMap)
    except Exception as e:
        return helper.code_status_error(e)



#################################################
# LIDER
#########################################
@app.route('/api/lider/<accion>', methods=["POST","GET","DELETE"])
@comprobarSession
def admin_lider(accion=""):
    try:
        data = request.get_json()
        #CREAR LIDER
        if request.method == 'POST' and accion=="crear":
            if(session['tipo_usuario']==1):
                   
                id=db.insertar_registro("usuarios",["nombre","password","serial_tip"],
                [data["nombre"],data["password"],2]
                ,serial="serial_usuario")


                retMap = {
                    'Message': "Lider Creado",
                    'Status Code': 200,
                    "id":id,

                    }
                return jsonify(retMap)
            else:
                retMap = {
                    'Message': "Solo los admin pueden crear usuarios",
                    'Status Code': 301,

                    }
                return jsonify(retMap)




        if request.method == 'POST' and accion=="actualizar":
            if(session["tipo_usuario"]==1):
                re,va=helper.validador_datos_entrantes({"usuario":["largo","caracteres"],"password":["largo"]},data)
                if(len(re)>0 or len(va)>0):
                    retMap = {
                    'Message': "Debe entregar los datos correctos",
                    'Status Code': 302,
                    'faltantes':re,
                    'validaciones':va
                    }
                    return jsonify(retMap)


                # res= db.comprobar_existencia_usuario(session["usuario"])
                db.ejecutar_consulta("UPDATE usuarios SET password='{password}' WHERE nombre='{nombre}'".format(nombre=data["usuario"],password=data["password"]))
                retMap = {
                    'Message': "Usuario actualizado",
                    'Status Code': 200,

                    }
                return jsonify(retMap)
            else:
                retMap = {
                    'Message': "Solo los admin pueden actualizar usuarios",
                    'Status Code': 301,

                    }
                return jsonify(retMap)
            # print(df)
            


        

        if request.method == 'GET' and accion=="votantes":
            if(session["tipo_usuario"]!=1):
                df= db.sql_select("SELECT * FROM votantes where nombre_usuario='{usuario}'".format(usuario=session['usuario']))
                retMap = {
                    'Message': "OK",
                    'Status Code': 200,
                    'registros':df.to_dict(orient="records")
    
                    }
            else:
                
                df= db.sql_select("SELECT * FROM votantes")
                retMap = {
                    'Message': "OK",
                    'Status Code': 200,
                    'registros':df.to_dict(orient="records")
    
                    }
            # print(df)
            return jsonify(retMap)


        if request.method == 'GET' and accion=="conteo":
            df= db.sql_select("SELECT nombre_usuario,COUNT(*) as cant FROM votantes GROUP BY nombre_usuario")
            retMap = {
                    'Message': "OK",
                    'Status Code': 200,
                    'registros':df.to_dict(orient="records")
    
                    }
                    
            return jsonify(retMap)

        if request.method == 'DELETE':
            if(session["tipo_usuario"]==1):
                re,va=helper.validador_datos_entrantes({"usuario":[""]},data)
                if(len(re)>0 or len(va)>0):
                    retMap = {
                    'Message': "Debe entregar los datos correctos",
                    'Status Code': 302,
                    'faltantes':re,
                    'validaciones':va
                    }
                    return jsonify(retMap)
            db.ejecutar_consulta("DELETE FROM usuarios WHERE nombre='{nombre}'".format(nombre=data["usuario"]))
            retMap = {
                'Message': "Usuario eliminado",
                'Status Code': 200,

                }
        
        if request.method == 'GET' and accion=="consultar":            
            re,va=helper.validador_datos_entrantes({"usuario":["largo","caracteres"]},data)
            if(len(re)>0 or len(va)>0):
                retMap = {
                'Message': "Debe entregar los datos correctos",
                'Status Code': 302,
                'faltantes':re,
                'validaciones':va
                }
                return jsonify(retMap)
            df= db.sql_select("SELECT * FROM usuarios WHERE nombre='{nombre}'".format(nombre=data["usuario"]))
            retMap = {
                'registro': df.to_dict(orient="records"),
                'Message': "Consultado con éxito",
                'Status Code': 200,

                }
            return jsonify(retMap)
    except Exception as e:
        return helper.code_status_error(e)



if __name__=="__main__":

    if("usuario" in session):
        session.pop('usuario', None)
    if("tipo_usuario" in session):
        session.pop('tipo_usuario', None)
    app.run(debug=True)




