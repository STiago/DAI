#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from web import form
import numpy as np
import matplotlib.pyplot as plt
from web.contrib.template import render_mako
import pymongo
import feedparser
import urllib

# Para poder usar sesiones con web.py
web.config.debug = False
        
urls = (
    '/hello', 'hello',
    '/imagen', 'imagen',
    '/formulario' , 'index',
    '/fractal', 'fractal',
    '/formulario3', 'fomulprac3',
    '/template', 'templ',
    '/inicio', 'inicio',
    '/logout', 'logout',
    '/insercion', 'insercion',
    '/datos', 'datos',
    '/modifica', 'modifica',
    '/guarda', 'guarda',
	 '/rss', 'rss',
	 '/mapa', 'mapa',
	 '/charts', 'charts',
	 '/chartsmuestra', 'chartsmuestra',
	 '/mashup', 'mashup',
    '/(.*)', 'error'
)

app = web.application(urls, globals())
plantilla = web.template.render('./templates/')


############ MONGODB ##################################
#client = MongoClient('mongodb://localhost:27017/')

#db =  client['test-database']

#collection = db.test_collection
try:
    con=pymongo.Connection()
    print "Conexion realizada con exito"
except pymongo.errors.ConnectionFailure, e:
    print "No se puede conectar %s" %e
con

db = con.dni
db

coll = db.datos
coll

###################################################
sesion = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'usuario':'', 'vista1': '', 'vista2': '', 'vista3': ''})



# Templates de mako
render = render_mako (
	directories = ['templates'],
	input_encoding = 'utf-8',
	output_encoding = 'utf-8')


login_form = form.Form (
	form.Textbox ('username', form.notnull, description='Usuario:'),
	form.Password ('password', form.notnull, description=u'Contraseña:'),
	form.Button ('Login'),
)


def password_correcto_de (usuario):
	return usuario	+'3'         # concateno un '3' al nombre de usuario
    # En la realidad habría que guardar los
    # passwords de cada usuario en una base de datos


def comprueba_identificacion (): 
	usuario = sesion.usuario   # Devuelve '' cuando no está identificado
	return usuario              # que es el usuario inicial 
                                  


class logout:
	def GET(self):
		usuario = sesion.usuario
		sesion.kill()
		return 'adios ' + usuario



# Comprueba que el usuario esté identificado
# sino se lo pide
class inicio:
	def GET(self):
		usuario = comprueba_identificacion () 
		if usuario:
			return web.seeother('/template') # render.inicio (usuario = usuario)
		else:
			form = login_form ()
			return render.login(form=form, usuario=usuario)  
	def POST(self):

		form = login_form ()
		if not form.validates ():
			return render.login (form=form, usuario='', mensaje = '')

		i = web.input()
		usuario  = i.username
		password = i.password
		if password == password_correcto_de (usuario):
			sesion.usuario = usuario
			return web.seeother('/template')   # Redirige al formulario
		else:
			form = login_form ()
			return render.login (form=form, usuario='', 
                                 mensaje = u'[ERROR] - El password correcto que sería ' +
                                           password_correcto_de (usuario))




####################  FORMULARIOS  ###############################

formu = form.Form(
	form.Textbox("nombre", form.notnull),
	form.Textbox("otro", form.notnull),
   form.Button("Enviar")
)

form_fractal = form.Form(
	form.Textbox("x_min", form.notnull),
	form.Textbox("x_max", form.notnull),
	form.Textbox("y_min", form.notnull),
	form.Textbox("y_max", form.notnull),
	form.Textbox("pixeles", form.notnull),
	form.Textbox("iteraciones", form.notnull),
   form.Button("Enviar")
)

form_pract3 = form.Form(
	form.Textbox("Nombre", form.notnull),
	form.Textbox("Apellidos", form.notnull),
	form.Textbox("DNI", form.notnull, form.regexp('^([0-9]{8}[A-Z])$', "Formato de DNI no valido")),
	form.Textbox("email", form.notnull, form.regexp('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', "Formato de correo incorrecto")), 
	form.Textbox("VISA", form.notnull, form.regexp('^([0-9]{4}) ([0-9]{4}) ([0-9]{4}) ([0-9]{4})|([0-9]{4})-([0-9]{4})-([0-9]{4})-([0-9]{4})$', "Formato de tarjeta VISA no valido")),
	form.Dropdown("dia",[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], description="Día de nacimiento"),
	form.Dropdown("mes",[1,2,3,4,5,6,7,8,9,10,11,12], description="Mes de nacimiento"),
	form.Dropdown("anio",[1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014], description="Año de nacimiento"),
	form.Textarea("Direccion", form.notnull),
	form.Password("Contrasenia", form.notnull, post = "Su contraseña debe de tener mas de 7 caracteres"),
	form.Password("Verificacion", form.notnull, pre= "Repita su contraseña"),
	form.Radio("pago", ['Contra reembolso', 'VISA'],form.notnull),
	form.Checkbox("clausulas",form.Validator("Debes aceptar las cláusulas de la protección de datos", lambda i: "clausulas" not in i), description="Acepta las clausulas"),
	form.Button("Enviar"),
	validators = [form.Validator("No coinciden las contraseñas", lambda i: i.Contrasenia == i.Verificacion), form.Validator("Longitud de contraseña", lambda i: len(i.Contrasenia)>=7), form.Validator("Fecha de nacimiento no válida.", lambda i: (((int(i.mes) == 2) and ((int(i.dia) <= 28) and ((int(i.anio) % 4) != 0) or (int(i.dia) <= 29) and ((int(i.anio) % 4) == 0))) or ((int(i.dia) <= 30) and ((int(i.mes) == 4) or (int(i.mes) == 6) or (int(i.mes) == 9) or (int(i.mes) == 11)))))]	
)

form_pract4 = form.Form(
    form.Textbox("DNI", form.notnull, description='Inserte el usuario'),
    form.Button("Enviar")
)

form_pract5 = form.Form(
	form.Textbox("Nombre", form.notnull),
	form.Textbox("Apellidos", form.notnull),
	form.Textbox("DNI", form.notnull, form.regexp('^([0-9]{8}[A-Z])$', "Formato de DNI no valido")),
	form.Textbox("email", form.notnull, form.regexp('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', "Formato de correo incorrecto")), 
	form.Textbox("VISA", form.notnull, form.regexp('^([0-9]{4}) ([0-9]{4}) ([0-9]{4}) ([0-9]{4})|([0-9]{4})-([0-9]{4})-([0-9]{4})-([0-9]{4})$', "Formato de tarjeta VISA no valido")),
	form.Dropdown("dia",[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], description="Día de nacimiento"),
	form.Dropdown("mes",[1,2,3,4,5,6,7,8,9,10,11,12], description="Mes de nacimiento"),
	form.Dropdown("anio",[1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014], description="Año de nacimiento"),
	form.Textarea("Direccion", form.notnull),
	form.Password("Contrasenia", form.notnull, post = "Su contraseña debe de tener mas de 7 caracteres"),
	form.Password("Verificacion", form.notnull, pre= "Repita su contraseña"),
	form.Radio("pago", ['Contra reembolso', 'VISA'],form.notnull),
	form.Checkbox("clausulas",form.Validator("Debes aceptar las cláusulas de la protección de datos", lambda i: "clausulas" not in i), description="Acepta las clausulas"),
	form.Button("Enviar"),
	validators = [form.Validator("No coinciden las contraseñas", lambda i: i.Contrasenia == i.Verificacion), form.Validator("Longitud de contraseña", lambda i: len(i.Contrasenia)>=7), form.Validator("Fecha de nacimiento no válida.", lambda i: (((int(i.mes) == 2) and ((int(i.dia) <= 28) and ((int(i.anio) % 4) != 0) or (int(i.dia) <= 29) and ((int(i.anio) % 4) == 0))) or ((int(i.dia) <= 30) and ((int(i.mes) == 4) or (int(i.mes) == 6) or (int(i.mes) == 9) or (int(i.mes) == 11)))))]	
)


formu_mapa = form.Form(
	form.Textbox("nombre", form.notnull, description = 'Introduzca el nombre del lugar'),
   form.Button("Enviar")
)

formu_charts = form.Form(
	form.Textbox("nombre", form.notnull, description = 'Introduzca el nombre del gráfico'),
	form.Textbox("enero", form.notnull, description = 'Introduzca el numero de entradas vendidas en Enero'),
	form.Textbox("febrero", form.notnull, description = 'Introduzca el numero de entradas vendidas en Febrero'),
	form.Textbox("marzo", form.notnull, description = 'Introduzca el numero de entradas vendidas en Marzo'),
	form.Textbox("abril", form.notnull, description = 'Introduzca el numero de entradas vendidas en Abril'),
	form.Textbox("mayo", form.notnull, description = 'Introduzca el numero de entradas vendidas en Mayo'),
	form.Textbox("junio", form.notnull, description = 'Introduzca el numero de entradas vendidas en Junio'),
	form.Textbox("julio", form.notnull, description = 'Introduzca el numero de entradas vendidas en Julio'),
	form.Textbox("agosto", form.notnull, description = 'Introduzca el numero de entradas vendidas en Agosto'),
	form.Textbox("septiembre", form.notnull, description = 'Introduzca el numero de entradas vendidas en Septiembre'),
	form.Textbox("octubre", form.notnull, description = 'Introduzca el numero de entradas vendidas en Octubre'),
	form.Textbox("noviembre", form.notnull, description = 'Introduzca el numero de entradas vendidas en Noviembre'),
	form.Textbox("diciembre", form.notnull, description = 'Introduzca el numero de entradas vendidas en Diciembre'),
	form.Button("Enviar")
)

formu_nombre = form.Form(
	form.Textbox("nombre", form.notnull, description = 'Introduzca el nombre del gráfico'),
   form.Button("Enviar")
)



######################################################## FIN FORMULARIOS ########################################################################

def img_fractal(x_minimo, x_maximo, y_minimo, y_maximo, pixeles, iteraciones):
	x, y = np.meshgrid(np.linspace(x_minimo, x_maximo, pixeles), np.linspace(y_minimo, y_maximo, pixeles))

	# Funcion de recurrencia para el conjunto de mandelbrot
	def znn(z, cc):
		return z**2 + cc

	c = x + 1j*y # Cuadricula compleja
	z = c.copy()
	fractal = np.zeros(z.shape, dtype=np.uint8) + 255 # Color inicial (lo que no pertenece al fractal)

	# Iterar
	for n in range(iteraciones):

		# Se actualiza z recursivamente
		z = znn(z, c)

		# Mascara
		mask = (np.abs(z) > 2)

		# Actualizar el color del fractal
		# Color depende de la iteracion actual
		fractal[mask] =  255 *  (n / float(iteraciones))

	# Mostrar la imagen usando como pixeles el fractal y mapa de colores "hot"
	plt.imshow(np.log(fractal), cmap=plt.cm.hot, extent=(x_minimo, x_maximo, y_minimo, y_maximo))
	plt.title('Conjunto de Mandelbrot')
	plt.show()

class hello:
	def GET(self):
		name = 'Desarrollo de app para internet'
		return 'Practica 2 -' + name


class imagen:        
   def GET(self):
   	return '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>practica2</title></head><body><img src="static/images/etsiit.jpg" alt="imagen1"/><img src="static/images/logougr.jpg" alt="imagen"/></body></html>' 

class index:
	def GET(self):
		form = formu()
		return plantilla.formulario(form)

	def POST(self):
		form = formu()
		if not form.validates():
			return plantilla.formulario(form)
		else:
			return "Mensaje enviado correctamente %s %s" % (form.d.nombre, form.d.otro)

class fractal:
	def GET(self):
		form = form_fractal()
		return plantilla.formulario(form)
	
	def POST(self):
		form = form_fractal()
		if not form.validates():
			return plantilla.formulario(form)
		else:
			return img_fractal(float(form.d.x_min), float(form.d.x_max), float(form.d.y_min), float(form.d.y_max), int(form.d.pixeles), int(form.d.iteraciones))	


#Practica 3
class fomulprac3:
	def GET(self):
		form = form_pract3()
		return plantilla.formulario(form)

	def POST(self):
		form = form_pract3()
		if not form.validates():
			return plantilla.formulario(form)
		else:
			return "Formulario practica 3 enviado correctamente" #%s %s" % (form.d.nombre, form.d.otro)	


class templ:
	def GET(self):
		usuario = comprueba_identificacion () 
		form = form_pract3()
		sesion.vista3=sesion.vista2
		sesion.vista2=sesion.vista1
		sesion.vista1= 'template'
		if usuario:
			return render.inicio (usuario = usuario, form = form, mensaje='', vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			form = login_form ()
			return render.login(form=form, usuario=usuario)
	def POST(self):
	    return web.seeother('/insercion')
	
		 
class insercion:
    def GET(self):
	 	usuario = comprueba_identificacion ()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'insercion'
		form = form_pract3()
		return render.insercion (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
    def POST(self):
		usuario = comprueba_identificacion () 
		form = form_pract3()
		if not form.validates():
			 return render.insercion (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			nombres = {"Nombre": form.d.Nombre,
				    "Apellidos": form.d.Apellidos,
				    "Dia": form.d.dia,
				    "Mes": form.d.mes,
				    "Anio": form.d.anio,
				    "DNI": form.d.DNI,
				    "VISA": form.d.VISA,
				    "email": form.d.email,
				    "Direccion": form.d.Direccion,
				    "Contrasenia": form.d.Contrasenia,
				    "pago": form.d.pago}

			coll.insert(nombres)
  
			return render.inicio(usuario=usuario, form=form, mensaje='los datos han sido insertados correctamente', vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	
    
class datos:
	def GET(self):
		usuario = comprueba_identificacion () 
		form = form_pract4()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'datos'
		return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	def POST(self):
		usuario = comprueba_identificacion () 
		form = form_pract4()
	
		if not form.validates():
			return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			try:
		
				cursor=coll.find({"DNI":form.d.DNI})
				nombre = cursor[0]["Nombre"]
				apellidos = cursor[0]["Apellidos"]
				dni = cursor[0]["DNI"]
				email = cursor[0]["email"]
				contrasenia = cursor[0]["Contrasenia"]
				dia = cursor[0]["Dia"]
				mes = cursor[0]["Mes"]
				anio = cursor[0]["Anio"]
				nacimiento = dia + '/' + mes + '/' + anio
				visa = cursor[0]["VISA"]
				direccion = cursor[0]["Direccion"]
				pago = cursor[0]["pago"]
		
				return render.vista(form=form, usuario=usuario, nombre=nombre, apellidos=apellidos, nacimiento=nacimiento, dni=dni, visa=visa, email=email, direccion=direccion, contrasenia=contrasenia, pago=pago, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)

			except:
				return render.inicio(form=form, usuario=usuario, mensaje="Usuario no existente en la base de datos.", vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)

class modifica:
	def GET(self):
		usuario = comprueba_identificacion ()
		form = form_pract4()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'modifica'
		return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	def POST(self):
		usuario = comprueba_identificacion () 
		form = form_pract4()
	
		if not form.validates():
			return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			try:
				cursor=coll.find({"DNI":form.d.DNI})
				nombre = cursor[0]["Nombre"]
				apellidos = cursor[0]["Apellidos"]
				dni = cursor[0]["DNI"]
				email = cursor[0]["email"]
				contrasenia = cursor[0]["Contrasenia"]
				dia = cursor[0]["Dia"]
				mes = cursor[0]["Mes"]
				anio = cursor[0]["Anio"]
				nacimiento = dia + '/' + mes + '/' + anio
				visa = cursor[0]["VISA"]
				direccion = cursor[0]["Direccion"]
				pago = cursor[0]["pago"]
		
				formi = form_pract3()
		
				formi.Nombre.value = nombre
				formi.Apellidos.value = apellidos
				formi.dia.value = int(dia)
				formi.mes.value = int(mes)
				formi.anio.value= int(anio)
				formi.DNI.value = dni
				formi.VISA.value = visa
				formi.pago.value = pago
				formi.email.value = email
				formi.Direccion.value = direccion
				formi.Contrasenia.value = contrasenia
				formi.Verificacion.value = contrasenia		
		
				return render.guarda(form=formi, usuario=usuario, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
			except:
				return render.inicio(form=form, usuario=usuario, mensaje="Usuario no existente en la base de datos.", vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		 
class guarda:
    def GET(self):
		usuario = comprueba_identificacion () 
		form = form_pract4()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'guarda'
		if not form.validates():
			return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			try:
				cursor=coll.find({"DNI":form.d.DNI})
				nombre = cursor[0]["Nombre"]
				apellidos = cursor[0]["Apellidos"]
				dni = cursor[0]["DNI"]
				email = cursor[0]["email"]
				contrasenia = cursor[0]["Contrasenia"]
				dia = cursor[0]["Dia"]
				mes = cursor[0]["Mes"]
				anio = cursor[0]["Anio"]
				nacimiento = dia + '/' + mes + '/' + anio
				visa = cursor[0]["VISA"]
				direccion = cursor[0]["Direccion"]
				pago = cursor[0]["pago"]
		
				formi = form_pract3()
		
				formi.Nombre.value = nombre
				formi.Apellidos.value = apellidos
				formi.dia.value = int(dia)
				formi.mes.value = int(mes)
				formi.anio.value= int(anio)
				formi.DNI.value = dni
				formi.VISA.value = visa
				formi.pago.value = pago
				formi.email.value = email
				formi.Direccion.value = direccion
				formi.Contrasenia.value = contrasenia
				formi.Verificacion.value = contrasenia		
		
				return render.guarda(form=formi, usuario=usuario, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
			except:
				return render.inicio(form=form, usuario=usuario, mensaje="Usuario no existente en la base de datos.", vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	    
    def POST(self):
		usuario = comprueba_identificacion () 
		form = form_pract3()
	
		if not form.validates():
			 return render.insercion (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			 nombres = {"Nombre": form.d.Nombre,
				    "Apellidos": form.d.Apellidos,
				    "Dia": form.d.dia,
				    "Mes": form.d.mes,
				    "Anio": form.d.anio,
				    "DNI": form.d.DNI,
				    "VISA": form.d.VISA,
				    "email": form.d.email,
				    "Direccion": form.d.Direccion,
				    "Contrasenia": form.d.Contrasenia,
				    "pago": form.d.pago 
			 }
			 coll.remove({"DNI":form.d.DNI})
			 coll.insert(nombres)
			 
			 return render.inicio(usuario=usuario, form=form, mensaje='Los datos han sido insertados correctamente',vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)


# Practica 4.a
class rss:
	def GET(self):
		usuario = comprueba_identificacion ()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'rss'

		url = 'http://ep00.epimg.net/rss/elpais/portada.xml' # usamos para no sobrecargar el proveedor del RSS, nos descargamos el archivo y ya se va mostrando
		urllib.urlretrieve(url, "portada.xml") 

		d = feedparser.parse('portada.xml') 

		tamanio = len(d.entries)
		lista=[]
		posi = 0

		while posi < tamanio:
			lista.insert(posi, d.entries[posi].title)  # para mostrar los titulares 
			posi +=1
	
		return render.rss(usuario=usuario, lista=lista, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)


# Practica 4.b
class mapa:
	def GET(self):
		usuario = comprueba_identificacion ()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'mapa'

		form = formu_mapa()

		return render.mapa(usuario=usuario, form=form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)


class charts:
	def GET(self):
		usuario = comprueba_identificacion ()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'charts'
		form = formu_charts()
		return render.insercion (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
   
	def POST(self):
		usuario = comprueba_identificacion () 
		form = formu_charts()
		if not form.validates():
			 return render.insercion (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			meses = {"nombre":form.d.nombre,
					 "enero": form.d.enero,
				    "febrero": form.d.febrero,
				    "marzo": form.d.marzo,
				    "abril": form.d.abril,
				    "mayo": form.d.mayo,
				    "junio": form.d.junio,
				    "julio": form.d.julio,
				    "agosto": form.d.agosto,
				    "septiembre": form.d.septiembre,
				    "octubre": form.d.octubre,
				    "noviembre": form.d.noviembre,
					 "diciembre": form.d.diciembre}

			coll.insert(meses)
	    	    
			return render.inicio(usuario=usuario, form=form, mensaje='Los datos han sido insertados correctamente', vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)


class chartsmuestra:
	def GET(self):
		usuario = comprueba_identificacion () 
		form = formu_nombre()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'chartsmuestra'
		return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	def POST(self):
		usuario = comprueba_identificacion () 
		form = formu_nombre()
	
		if not form.validates():
			return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			try:
		
				cursor=coll.find({"nombre":form.d.nombre})
				enero = cursor[0]["enero"]
				febrero = cursor[0]["febrero"]
				marzo = cursor[0]["marzo"]
				abril = cursor[0]["abril"]
				mayo = cursor[0]["mayo"]
				junio = cursor[0]["junio"]
				julio = cursor[0]["julio"]
				agosto = cursor[0]["agosto"]
				septiembre = cursor[0]["septiembre"]
				octubre = cursor[0]["octubre"]
				noviembre = cursor[0]["noviembre"]
				diciembre = cursor[0]["diciembre"]
		
				return render.charts(usuario=usuario, enero=enero, febrero=febrero, marzo=marzo, abril=abril, mayo=mayo, junio=junio, julio=julio, agosto=agosto, septiembre=septiembre, octubre=octubre, noviembre=noviembre, diciembre=diciembre, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)

			except:
				return render.inicio(form=form, usuario=usuario, mensaje="Usuario no existente en la base de datos.", vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)


class mashup:
	def GET(self):
		usuario = comprueba_identificacion () 
		form = formu_nombre()
		sesion.vista3 = sesion.vista2
		sesion.vista2 = sesion.vista1
		sesion.vista1 = 'mashup'
		return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	def POST(self):
		usuario = comprueba_identificacion () 
		form = formu_nombre()
	
		if not form.validates():
			return render.datos (usuario = usuario, form = form, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
		else:
			try:
		
				cursor=coll.find({"nombre":form.d.nombre})
				enero = cursor[0]["enero"]
				febrero = cursor[0]["febrero"]
				marzo = cursor[0]["marzo"]
				abril = cursor[0]["abril"]
				mayo = cursor[0]["mayo"]
				junio = cursor[0]["junio"]
				julio = cursor[0]["julio"]
				agosto = cursor[0]["agosto"]
				septiembre = cursor[0]["septiembre"]
				octubre = cursor[0]["octubre"]
				noviembre = cursor[0]["noviembre"]
				diciembre = cursor[0]["diciembre"]
		
				return render.mashup(usuario=usuario, enero=enero, febrero=febrero, marzo=marzo, abril=abril, mayo=mayo, junio=junio, julio=julio, agosto=agosto, septiembre=septiembre, octubre=octubre, noviembre=noviembre, diciembre=diciembre, vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)

			except:
				return render.inicio(form=form, usuario=usuario, mensaje="Usuario no existente en la base de datos.", vista1=sesion.vista1, vista2=sesion.vista2, vista3=sesion.vista3)
	


class error:
   def GET(self, name):
	return '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>ERROR</title></head><body><header>[ERROR 404] - NOT FOUND</header></body></html>' 

if __name__ == "__main__":
    app.run()
