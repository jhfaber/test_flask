import sqlite3
import pandas as pd

import sys, os

class Helpers:
    def fun_error(self,e):
        return 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e

    def code_status_error(self,e):
        print(self.fun_error(e))
        obj= {
            "Message": "Error interno",
            'Status Code': 501
        }
        return obj
    def no_loggueado(self):
        retMap = {
            'Message': "No estás loggueado",
            'Status Code': 301
            }   
        return retMap

    def validador_datos_entrantes(self,requeridos,data):
        list_requeridos = [ v for v in requeridos.keys() ]
        
        keys_necesarios=[]
        val_necesarios=[]
        
        for (i, item) in enumerate(list_requeridos):
            if(item in data):
                data[item]=str(data[item])
                ###################################
                #VALIDACIONES
                #########################################
                for (ii, item2) in enumerate(requeridos[item]):
                    if(item2=="largo"):
                        if(len(str(data[item]))<3 or len(str(data[item]))>10):
                            val_necesarios.append("El dato {item} debe ser >2 y menor a 10".format(item=item))
                    if(item2=="caracteres"):
                        if( any(not c.isalnum() for c in data[item]) ):
                            val_necesarios.append("El dato {item} no puede tener caracteres especiales".format(item=item))
                
                    
            else:
                #NO EXISTE LA LLAVE
                keys_necesarios.append("Llave necesaria {item}".format(item=item))
        return [keys_necesarios,val_necesarios]






class SqlDatabase:
    def __init__(self,database=""):
      self.database=database
    def fun_error(self,e):
        return 'DB Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e

    def create_connection(self,db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Exception as e:
            print(self.fun_error(e))
    def ejecutar_consulta(self,create_table_sql):
        try:
            c=self.create_connection(self.database)
            c.execute(create_table_sql)
            c.commit()
            c.close()
        except Exception as e:
            print(self.fun_error(e))
    def insertar_registro(self,tabla,columnas,valores,serial="serial_tip"):
        try:
            #COLUMNAS
            str_col = "("
            for (i, item) in enumerate(columnas):

                str_col=str_col+str(item)
                if(i+1 ==len(columnas)):
                    str_col=str_col+")"
                else:
                    str_col=str_col+","
            #VALORES
            str_val = "("
            for (i, item) in enumerate(valores):

                str_val=str_val+ "'"+str(item)+"'"
                if(i+1 ==len(valores)):
                    str_val=str_val+")"
                else:
                    str_val=str_val+","
            c=self.create_connection(self.database)
            c.execute("""INSERT INTO {tabla} 
            {str_col} VALUES {str_val}""".format(
                tabla=tabla,
                str_col=str_col,
                str_val=str_val

            ))
            
            c.commit()           
            c.close()
            df= self.sql_select("SELECT * FROM {tabla}  ORDER BY {serial} DESC LIMIT 1".format(tabla=tabla,serial=serial))
            res=df.loc[0,serial]
            res=int(res)
            return res
        except Exception as e:
            print(self.fun_error(e))


    def sql_select(self,consulta):
        try:
            c=self.create_connection(self.database)
            # c = c.cursor
            df = pd.read_sql_query(consulta, c)
            c.close()
            return df
        except Exception as e:
            print(self.fun_error(e))

    def comprobar_existencia_usuario(self,nombre):
        try:
            c=self.create_connection(self.database)
            df = pd.read_sql_query("""
            SELECT * 
            FROM Usuarios WHERE nombre='{nombre}' 
            """.format(nombre=nombre)            
            , c)
            c.close()
            if not df.empty:
                res={
                    "correcto":1,
                    "tipo_usuario":int(df.loc[0,"serial_tip"]),
                    "nombre":df.loc[0,"nombre"],
                    "password":df.loc[0,"password"]
                }
            else:
                res= {
                    "correcto":0,
                    "tipo_usuario":0,
                    "nombre":"",
                    "password":""
                }

            return res
        except Exception as e:
            print(self.fun_error(e))

    def tabla_vacia(self,tabla):
        try:
            c=self.create_connection(self.database)
            df = pd.read_sql_query("""
            SELECT * 
            FROM {tabla}
            """.format(tabla=tabla)            
            , c)
            c.close()
            if df.empty:
                res=1
            else:
                res= 0

            return res
        except Exception as e:
            print(self.fun_error(e))

    def execute_many_selects(self, queries):
        c=self.create_connection(self.database)
        return [c.execute(query).fetchall() for query in queries]




if __name__ == "__main__":
    db=SqlDatabase(database="flask.db")
    db.ejecutar_consulta("""   
     CREATE TABLE IF NOT EXISTS [usuarios]( 
           [serial_usuario] INTEGER PRIMARY KEY AUTOINCREMENT,          
           [nombre] varchar(20),
           [password] varchar(20),
           [serial_tip] int          
    );""")
    db.ejecutar_consulta("""   
     CREATE TABLE IF NOT EXISTS [tipo_usuario]( 
           [serial_tip] INTEGER PRIMARY KEY AUTOINCREMENT,          
           [nombre] varchar(20)          
    );""")

    db.ejecutar_consulta("""   
     CREATE TABLE IF NOT EXISTS [puesto_votacion]( 
           [serial_puesto] INTEGER PRIMARY KEY AUTOINCREMENT,          
           [nombre] varchar(20),
           [serial_municipio] varchar(20),
           [coordenadas] varchar(20),
           [direccion] varchar(100)         
    );""")

    db.ejecutar_consulta("""   
     CREATE TABLE IF NOT EXISTS [votantes]( 
           [serial_vot] INTEGER PRIMARY KEY AUTOINCREMENT,  
           [direccion] varchar (100),        
           [nombre] varchar(20),
           [apellidos] varchar(20),
           [telefono] varchar(20),
           [cedula] varchar(20),
           [serial_puesto] int,
           [nombre_usuario] varchar (20),
           [serial_municipio] int,
           [nombre_municipio] varchar (20)

    );""")

    db.ejecutar_consulta("""   
     CREATE TABLE IF NOT EXISTS [municipios]( 
           [serial_municipio] INTEGER PRIMARY KEY AUTOINCREMENT,          
           [nombre] varchar(20),
           [departamento] varchar(20)           
    );""")

    db.ejecutar_consulta("""   
     CREATE TABLE IF NOT EXISTS [log]( 
           [serial_log] INTEGER PRIMARY KEY AUTOINCREMENT,          
           [serial_vot] int,
           [serial_usuario] int,
           [nombre_usuario] varchar(20),
           [nombre_votante] varchar(20)           
    );""")

    if(db.tabla_vacia("usuarios")==1):
        db.ejecutar_consulta("INSERT INTO usuarios (nombre,password,serial_tip) VALUES ('JOHN','1234',1); ")
        db.ejecutar_consulta("INSERT INTO usuarios (nombre,password,serial_tip) VALUES ('Gabriel','1234',2); ")
    
    if(db.tabla_vacia("tipo_usuario")==1):
        db.ejecutar_consulta("INSERT INTO tipo_usuario (nombre) VALUES ('administrador'); ")
        db.ejecutar_consulta("INSERT INTO tipo_usuario (nombre) VALUES ('lider'); ")

    if(db.tabla_vacia("municipios")==1):
        db.ejecutar_consulta("INSERT INTO municipios (nombre,departamento) VALUES ('Bogota','Bogota'); ")
        db.ejecutar_consulta("INSERT INTO municipios (nombre,departamento) VALUES ('Manizales','Caldas'); ")
        db.ejecutar_consulta("INSERT INTO municipios (nombre,departamento) VALUES ('Armenia','Quindio'); ")
        db.ejecutar_consulta("INSERT INTO municipios (nombre,departamento) VALUES ('Pereira','Risaralda'); ")


    if(db.tabla_vacia("puesto_votacion")==1):
        db.ejecutar_consulta("INSERT INTO puesto_votacion (nombre,serial_municipio,coordenadas,direccion) VALUES ('El rebaño','1','','Cl. 25f #34A-50, Bogotá'); ")
        db.ejecutar_consulta("INSERT INTO puesto_votacion (nombre,serial_municipio,coordenadas,direccion) VALUES ('El Recuerdo','1','','Cl. 25f #34A-50, Bogotá'); ")
        db.ejecutar_consulta("INSERT INTO puesto_votacion (nombre,serial_municipio,coordenadas,direccion) VALUES ('La Manzana','2','','calle 65 no 34a-66, Manizales'); ")
        db.ejecutar_consulta("INSERT INTO puesto_votacion (nombre,serial_municipio,coordenadas,direccion) VALUES ('La Petrusca','3','','calle 65 no 34a-66, Manizales'); ")
        db.ejecutar_consulta("INSERT INTO puesto_votacion (nombre,serial_municipio,coordenadas,direccion) VALUES ('El Puente','4','','calle 65 no 34a-66, Manizales'); ")

    if(db.tabla_vacia("votantes")==1):
        db.ejecutar_consulta("INSERT INTO votantes (nombre,apellidos,nombre_usuario,direccion) VALUES ('VOTANTE2','Ape prueba','Gabriel','calle 65 no 34a-66, Manizales'); ")
        db.ejecutar_consulta("INSERT INTO votantes (nombre,apellidos,nombre_usuario,direccion) VALUES ('VOTANTE1','Ape prueba','Gabriel','Cl. 25f #34A-50, Bogotá'); ")
    # s=db.insertar_registro("tipo_usuario",["nombre"],["tes"])
    # print(s)
    # registro= db.insertar_registro("INSERT INTO tipo_usuario (nombre) VALUES ('lider'); ")
    # print(registro)
    # res=db.comprobar_existencia_usuario("JOHN")
    # print(res)
    # df= db.sql_select("SELECT * FROM Usuarios")


    # print(type(df))
    # print(df.head())




