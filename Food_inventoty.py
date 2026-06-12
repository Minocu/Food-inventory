import tkinter as tk
import mysql.connector
from tkinter import messagebox, Toplevel, PhotoImage
from customtkinter import CTk, CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkImage, CTkCheckBox, CTkTextbox
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import threading




fecha_hora_actual = datetime.now()

año_actual = fecha_hora_actual.strftime("%Y")
dia_mes_año_actual = fecha_hora_actual.strftime("%Y-%m-%d")
dia_actual = fecha_hora_actual.strftime("%d")
dias_antes = 0
validar_alimetos_proximos = False
continuar_verificacion = True

c_amarillo_oscuro = "#FFDC00"
c_amarillo = "#FFF51F"
c_naranja = "#FFC520"
c_naranja_oscuro = "#FFB11E"
c_verde = "#39FF14"


usuario_actual = None
# Conectar a la base de datos (configura los datos de conexión)
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="inicio de seccion"
)
cursor = conexion.cursor()

# Crear la tabla de usuarios si no existe
# Crear la tabla de usuarios si no existe con restricciones únicas
cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INT AUTO_INCREMENT PRIMARY KEY, documento_identidad VARCHAR(255) UNIQUE, nombre VARCHAR(255) UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS alimentos (usuario_id INT(255), nombre VARCHAR(255), fecha_vencimiento DATE)")
cursor.execute("CREATE TABLE IF NOT EXISTS dia_de_antelcion (usuario_id INT(255), Dia INT(20))")


# Función para almacenar datos de usuario en la base de datos
def guardar_usuario(documento, nombre):
    cursor.execute("INSERT INTO usuarios (documento_identidad, nombre) VALUES (%s, %s)", (documento, nombre))
    conexion.commit()

# Función para comprobar si un usuario ya existe
def verificar_usuario(documento, nombre):
    
    cursor.execute("SELECT id FROM usuarios WHERE documento_identidad = %s AND nombre = %s", (documento, nombre))
    resultado = cursor.fetchone()
    if resultado:
        return resultado[0]
    else:
        return None


# Funciones para las opciones del menú (puedes personalizarlas)
def almacenar_alimentos():
    if usuario_actual is None:
        messagebox.showerror("Error", "Debe iniciar sesión para almacenar alimentos.")
        return

    print("Opción 1: Almacenar alimentos")
    
    def guardar_alimento():
        nombre_alimento = entry_nombre_alimento.get()
        dia = entry_dia.get()
        mes = entry_mes.get()
        año = entry_año.get()

        if not dia.isdigit() or not mes.isdigit() or not año.isdigit():
            messagebox.showerror("Error", "El día, mes y año deben ser números válidos.")
            return

        dia = int(dia)
        mes = int(mes)
        año = int(año)

        if dia <= 0 or dia > 31:
            messagebox.showerror("Error", "El día debe ser un número válido entre 1 y 31.")
            return
        if mes <= 0 or mes > 12:
            messagebox.showerror("Error", "El mes debe ser un número válido entre 1 y 12.")
            return
        if nombre_alimento == "":
            messagebox.showerror("Error", "Coloca un nombre válido.")
            return

        fecha_actual = datetime.now()
        fecha_vencimiento = datetime(año, mes, dia)

        if fecha_vencimiento <= fecha_actual:
            messagebox.showerror("Error", "La fecha de vencimiento no puede ser anterior o igual a la fecha actual.")
            return

        # Ahora puedes almacenar el alimento en la base de datos
        guardar_info_alimento(nombre_alimento, fecha_vencimiento)
        print("Alimento almacenado:", nombre_alimento)
        ventana_alimentos.destroy()
    
    # Esta funcion se encarga de limitar los caracteres del entry
    def limitar_caracteres(P, max_length):
        if len(P) <= int(max_length):
            return True
        else:
            return False
    
    def validar_mes(P, max_length):
        if P.isdigit() or P == "":
            # Eliminar ceros a la izquierda y limitar la longitud a dos dígitos
            P = P.lstrip('0')  # Eliminar ceros a la izquierda
            P = P.zfill(2) if P != "" else ""
        
            if len(P) <= int(max_length):
                return True
        return False
        

        
    # Crear una nueva ventana para ingresar información sobre alimentos
    ventana_alimentos = tk.Toplevel(ventana_inicio_sesion, bg= c_amarillo)
    ventana_alimentos.title("Almacenar Alimentos")
    ventana_alimentos.resizable(False, False)
    ventana_alimentos.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")

    validacion_dia = ventana_inicio_sesion.register(limitar_caracteres)
    validacion_mes = ventana_inicio_sesion.register(validar_mes)

    frame_fecha = CTkFrame(ventana_alimentos, fg_color=c_naranja)
    frame_fecha.grid(column=0, row=0, sticky="nsew", pady=10, padx=10)

    ventana_alimentos.columnconfigure(0, weight=1)
    ventana_alimentos.rowconfigure(0, weight=1)

    frame_fecha.columnconfigure([0,1,2,3,4], weight=1)
    frame_fecha.rowconfigure([0,1,2,3,4], weight=1)
    
    label_nombre_alimento = CTkLabel(frame_fecha, text="Nombre del Alimento:", font=("Fixedsys", 30))
    label_nombre_alimento.grid(columnspan= 2, row=1, pady=5, padx=5)
    entry_nombre_alimento = CTkEntry(frame_fecha, border_color= c_naranja, fg_color=c_naranja_oscuro, width=260, height=50, font=("Fixedsys", 40))
    entry_nombre_alimento.grid(columnspan= 2, row=2, pady=5, padx=5)
    
    label_fecha_vencimiento = CTkLabel(frame_fecha, text="Fecha de Vencimiento (DD-MM-AAAA):", font=("Fixedsys", 30))
    label_fecha_vencimiento.grid(columnspan= 2, row=3, pady=5, padx=5)

    frame_date = CTkFrame(frame_fecha, fg_color=c_naranja)
    frame_date.grid(columnspan= 2, row=4, pady=5, padx=5)

    entry_dia = CTkEntry(frame_date, border_color= c_naranja, fg_color=c_naranja_oscuro, width=60, height=50, font=("Fixedsys", 40))
    entry_dia.configure(validate="key", validatecommand=(validacion_dia, "%P", 2))
    entry_dia.grid(column= 0, row=4, padx=10, pady=10)

    label_sep1 = CTkLabel(frame_date, text="-", font=("Fixedsys", 40))
    label_sep1.grid(column= 1, row=4, padx=5, pady=10)

    entry_mes = CTkEntry(frame_date, border_color= c_naranja, fg_color=c_naranja_oscuro, width=60, height=50, font=("Fixedsys", 40))
    entry_mes.configure(validate="key", validatecommand=(validacion_mes, "%P", 2))
    entry_mes.grid(column= 2, row=4, padx=10, pady=10)

    label_sep2 = CTkLabel(frame_date, text="-", font=("Fixedsys", 40))
    label_sep2.grid(column= 3, row=4, padx=5, pady=10)

    entry_año = CTkEntry(frame_date, border_color= c_naranja, fg_color=c_naranja_oscuro, width=110, height=50, font=("Fixedsys", 40))
    entry_año.configure(validate="key", validatecommand=(validacion_dia, "%P", 4))
    entry_año.grid(column= 4, row=4, padx=10, pady=10)
    
    boton_guardar = CTkButton(frame_fecha, text="Guardar", command=guardar_alimento, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_guardar.grid(columnspan= 2, row=5, pady=5, padx=5)

def guardar_info_alimento(nombre_alimento, fecha_vencimiento):
    global usuario_actual

    if usuario_actual is not None:
        usuario_id = usuario_actual
        try:
            # Guarda la información del alimento junto con el ID del usuario en la base de datos
            cursor.execute("INSERT INTO alimentos (usuario_id, nombre, fecha_vencimiento) VALUES (%s, %s, %s)", (usuario_id, nombre_alimento, fecha_vencimiento))
            conexion.commit()
            print("Alimento almacenado en la base de datos:", nombre_alimento)
        except mysql.connector.Error as err:
            print(f"Error al guardar el alimento en la base de datos: {err}")
    else:
        print("No se puede almacenar el alimento. El usuario no ha iniciado sesión.")

def obtener_alimentos_del_usuario(usuario_id):
    alimentos = []
    if usuario_id is not None:
        # Realiza una consulta a la base de datos para obtener los alimentos del usuario actual, ordenados por fecha de vencimiento.
        cursor.execute("SELECT nombre, fecha_vencimiento FROM alimentos WHERE usuario_id = %s ORDER BY fecha_vencimiento", (usuario_id,))
        alimentos_data = cursor.fetchall()
        for alimento_data in alimentos_data:
            nombre = alimento_data[0]
            fecha_vencimiento = alimento_data[1]
            alimentos.append({'nombre': nombre, 'fecha_vencimiento': fecha_vencimiento})
    return alimentos



# Configuración de la ventana principal
ventana_inicio_sesion= CTk()
ventana_inicio_sesion.title("Gestión de Alimentos")

ventana_inicio_sesion.geometry("500x500")
ventana_inicio_sesion.minsize(600,600)

def retirar_alimentos():
    if usuario_actual is None:
        messagebox.showerror("Error", "Debe iniciar sesión para retirar alimentos.")
        return

    alimentos = obtener_alimentos_del_usuario(usuario_actual)

    if not alimentos:
        messagebox.showinfo("Información", "No tienes alimentos almacenados.")
        return

    def retirar_seleccionados():
        for idx, alimento in enumerate(alimentos):
            if seleccionados[idx].get() == 1:
                print(f"Alimento retirado: {alimento['nombre']}")
                cursor.execute("DELETE FROM alimentos WHERE usuario_id = %s AND nombre = %s AND fecha_vencimiento = %s", (usuario_actual, alimento['nombre'], alimento['fecha_vencimiento']))
                # Aquí puedes agregar el código para eliminar el alimento de la base de datos si es necesario.
        ventana_retirar.destroy()
        # Actualiza la lista de alimentos después de eliminar los seleccionados


    ventana_retirar = tk.Toplevel(ventana_inicio_sesion, bg= c_amarillo)
    ventana_retirar.title("Retirar Alimentos")
    ventana_retirar.resizable(False, False)
    ventana_retirar.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")

    ventana_retirar.columnconfigure(0, weight=1)
    ventana_retirar.rowconfigure(0, weight=1)

    frame_retirar = CTkFrame(ventana_retirar, fg_color=c_naranja)
    frame_retirar.grid(column=0 , row=0, sticky="nsew", pady=10, padx=10)

    frame_retirar.columnconfigure(0, weight=1)
    frame_retirar.rowconfigure(0, weight=1)

    seleccionados = []

    for alimento in alimentos:
        seleccionados.append(tk.IntVar())
        checkbox = CTkCheckBox(frame_retirar, text=f"{alimento['nombre']} (Vencimiento: {alimento['fecha_vencimiento']})", variable=seleccionados[-1], font=("Fixedsys", 30), hover_color=c_naranja_oscuro, fg_color=c_verde)
        checkbox.pack()

    boton_retirar = CTkButton(frame_retirar, text="Retirar alimentos seleccionados", command=retirar_seleccionados, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_retirar.pack()
    
    


def reportar_alimentos_vencidos():
    if usuario_actual is None:
        messagebox.showerror("Error", "Debe iniciar sesión para verificar alimentos próximos a vencerse.")
        return
    print("Opción 3: Reportar cantidad de alimentos vencidos")
      # Agrega esta línea para acceder a reportar_entry en todo el script


    def validar_limite(P, max_length):
        if P.isdigit() or P == "":
            # Eliminar ceros a la izquierda y limitar la longitud a dos dígitos
            P = str(int(P)) if P != "" else ""  # Convertir a entero si no está vacío, de lo contrario, dejarlo vacío
        
            if len(P) <= int(max_length):
                return True
        return False

    
    def alimentos_vencidos():
        ventana_vencidos = tk.Toplevel(ventana_inicio_sesion, bg=c_amarillo)
        ventana_vencidos.title("Vencidos")
        ventana_vencidos.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")

        ventana_vencidos.columnconfigure(0, weight=1)
        ventana_vencidos.rowconfigure(0, weight=1)

        frame_vencidos = CTkFrame(ventana_vencidos, fg_color= c_naranja)
        frame_vencidos.grid(column=0 , row=0, sticky="nsew", pady=10, padx=10)
        
        mensaje = CTkLabel(frame_vencidos, text="Alimentos vencidos:",font=("Fixedsys", 30))
        mensaje.grid(columnspan= 2, row=1, pady=10, padx=10)

        fecha_actual = datetime.now()

        fecha_antelacion = fecha_actual   

        alimentos = obtener_alimentos_del_usuario(usuario_actual)
        alimentos_proximos_a_vencer = []

        for alimento in alimentos:
            fecha_vencimiento_str = str(alimento['fecha_vencimiento'])  # Convierte a cadena
            fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, "%Y-%m-%d")
            if fecha_vencimiento <= fecha_antelacion:
                alimentos_proximos_a_vencer.append(alimento)

        if alimentos_proximos_a_vencer:
            for alimento in alimentos_proximos_a_vencer:
                mensaje = CTkLabel(frame_vencidos, text=f"{alimento['nombre']} - Fecha de vencimiento: {alimento['fecha_vencimiento']}\n", font=("Fixedsys", 30))
                mensaje.grid(columnspan = 2, row=alimento, pady=10, padx=10)
        
        else:
            messagebox.showinfo("Información", "No tienes alimentos próximos a vencerse.") 

    def verificar_entry():
        global dias_antes
        dias_antes = int(reportar_entry.get())
        verificar_alimentos_a_vencer()
        

    # Obtener la cantidad de días de antelación desde un entry (debes obtenerlo previamente)
    validacion_limite_de_caracteres = ventana_inicio_sesion.register(validar_limite)

    ventana_reportados = tk.Toplevel(ventana_inicio_sesion, bg= c_amarillo)
    ventana_reportados.title("Reportar productos")
    ventana_reportados.resizable(False,False)
    ventana_reportados.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")

    ventana_reportados.columnconfigure(0, weight=1)
    ventana_reportados.rowconfigure(0, weight=1)

    frame_reportados = CTkFrame(ventana_reportados, fg_color=c_naranja)
    frame_reportados.grid(column= 0, row= 0, sticky="nsew", pady=10, padx=10)

    frame_reportados.columnconfigure([0,1], weight=1)
    frame_reportados.rowconfigure([0,1,2,3,4], weight=1)


    
    label_reportar = CTkLabel(frame_reportados, text="Ver alimetos vencidos", font=("Fixedsys", 30))
    label_reportar.grid(columnspan=2, row=1, pady=10, padx=10)

    boton_retirar = CTkButton( frame_reportados, text="Enviar", command=alimentos_vencidos, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_retirar.grid(columnspan=2, row=2, pady=10, padx=10)

    label_reportar = CTkLabel(frame_reportados, text="Coloca cuantos dias antes quieren que te aparezcan las notificaciones de aliemtos proximos a vencer", font=("Fixedsys", 30))
    label_reportar.grid(columnspan=2, row=3, pady=10, padx=10)

    reportar_entry = CTkEntry(frame_reportados, justify="center", font=("Fixedsys", 30),  border_color= c_naranja, fg_color=c_naranja_oscuro, width=60, height=50,)
    reportar_entry.configure(validate="key", validatecommand=(validacion_limite_de_caracteres, "%P", 2))
    reportar_entry.grid(columnspan=2, row=4, pady=10, padx=10)

    boton_vencido = CTkButton(frame_reportados, text="Enviar", command=verificar_entry, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_vencido.grid(columnspan=2, row=5, pady=10, padx=10)

def verificar_alimentos_a_vencer():
    global usuario_actual
    global dias_antes
    global validar_alimetos_proximos

    fecha_actual = datetime.now()
    delta = timedelta(days=dias_antes)
    fecha_antelacion = fecha_actual + delta

    alimentos = obtener_alimentos_del_usuario(usuario_actual)
    alimentos_proximos_a_vencer = []

    for alimento in alimentos:
        fecha_vencimiento_str = alimento['fecha_vencimiento'].strftime("%Y-%m-%d")
        fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, "%Y-%m-%d")
        if fecha_vencimiento < fecha_antelacion and fecha_vencimiento > fecha_actual:
            alimentos_proximos_a_vencer.append(alimento)

    if alimentos_proximos_a_vencer:
        mensaje = "Alimentos próximos a vencerse:\n"
        for alimento in alimentos_proximos_a_vencer:
            mensaje += f"{alimento['nombre']} - Fecha de vencimiento: {alimento['fecha_vencimiento']}\n"
        messagebox.showinfo("Alimentos Próximos a Vencerse", mensaje)
        validar_alimetos_proximos = True
    else:
        messagebox.showerror("Alerta", "No tienes alimentos proximos a vencerse")
        validar_alimetos_proximos = False
    
   



def mostrar_cantidad_almacenada():
    alimentos = obtener_alimentos_del_usuario(usuario_actual)

    if not alimentos:
        messagebox.showinfo("Información", "No tienes alimentos almacenados.")
    else:
        ventana_mostrar_alimentos = tk.Toplevel(ventana_inicio_sesion, bg=c_amarillo)
        ventana_mostrar_alimentos.title("Alimentos Almacenados")
        ventana_mostrar_alimentos.minsize(200,200)
        ventana_mostrar_alimentos.resizable(False,False)
        ventana_mostrar_alimentos.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")

        ventana_mostrar_alimentos.columnconfigure(0, weight=1)
        ventana_mostrar_alimentos.rowconfigure(0, weight=1)

        frame_mostrar_alimentos = CTkFrame(ventana_mostrar_alimentos, fg_color=c_naranja)
        frame_mostrar_alimentos.grid(column= 0, row= 0, sticky="nsew", pady=10, padx=10)

        frame_mostrar_alimentos.columnconfigure([0,1], weight=1)
        frame_mostrar_alimentos.rowconfigure([0,1,2,3,4], weight=1)

        # Crea un widget de lista para mostrar los alimentos
        lista_alimentos = CTkTextbox(frame_mostrar_alimentos, width=1000, font=("Fixedsys", 30), fg_color=c_naranja_oscuro)
        lista_alimentos.grid(columnspan=2, row=0)

        for alimento in alimentos:
            nombre = alimento['nombre']
            fecha_vencimiento = alimento['fecha_vencimiento']
            info_alimento = f"Nombre: {nombre}, Fecha de vencimiento: {fecha_vencimiento}\n"
            lista_alimentos.insert("0.0", info_alimento * 1) 


        # Calcula el ancho y alto requeridos de la lista
        ancho_requerido = lista_alimentos.winfo_reqwidth()
        alto_requerido = lista_alimentos.winfo_reqheight()

        # Configura el tamaño de la ventana según el ancho y alto requeridos
        ventana_mostrar_alimentos.minsize(ancho_requerido,alto_requerido + 60)

        # Agrega un botón para cerrar la ventana
        boton_cerrar = CTkButton(frame_mostrar_alimentos, text="Cerrar", command=ventana_mostrar_alimentos.destroy, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
        boton_cerrar.grid(columnspan=2, row=3)

# Función para iniciar sesión
def iniciar_sesion():
    global usuario_actual

    documento = entry_documento.get()
    nombre = entry_nombre.get()

    usuario_id = verificar_usuario(documento, nombre)

    if usuario_id:
        usuario_actual = usuario_id
        mensaje_label.configure(text="Sesión iniciada")
        ventana_bienvenida()  # Llama a la función para mostrar la ventana de bienvenida

    else:
        mensaje_label.configure(text="Datos incorrectos")

def ventana_bienvenida():
    global ventana_inicio_sesion
    ventana_inicio_sesion.withdraw()
    ventana_bienvenida = tk.Toplevel(ventana_inicio_sesion, bg=c_amarillo)
    ventana_bienvenida.title("¡Bienvenido!")
    ventana_bienvenida.resizable(False,False)
    ventana_bienvenida.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")

    frame_bienvenida = CTkFrame(ventana_bienvenida, fg_color=c_naranja)
    frame_bienvenida.grid(column= 0, row=0, sticky="nsew", padx=10, pady=10)

    ventana_bienvenida.columnconfigure(0, weight=1)
    ventana_bienvenida.rowconfigure(0, weight=1)

    frame_bienvenida.columnconfigure([0,1], weight=1)
    frame_bienvenida.rowconfigure([0,1,2,3,4,5,6,7], weight=1)
    
    def cerrar_ventana_bienvenida():
        ventana_bienvenida.destroy()
        ventana_inicio_sesion.deiconify() 
        
        
    mensaje_bienvenida = CTkLabel(frame_bienvenida, text=f"Bienvenido, {entry_nombre.get()}!", font=("Fixedsys", 30))
    mensaje_bienvenida.grid(columnspan=2, row=1, pady=10, padx=10)

    label_bienvenida = CTkLabel(frame_bienvenida, text="¿Que desea hacer hoy?", font=("Fixedsys", 25))
    label_bienvenida.grid(columnspan=2, row=2, pady=10, padx=10)

    boton_almacenar_alimetos = CTkButton(frame_bienvenida, text="Almacenar alimetos", command=almacenar_alimentos, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_almacenar_alimetos.grid(columnspan=2, row=3, pady=10, padx=10)

    boton_retirar_alimetos = CTkButton(frame_bienvenida, text="Retirar alimetos", command=retirar_alimentos, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_retirar_alimetos.grid(columnspan=2, row=4, pady=10, padx=10)

    boton_reportar_alimetos = CTkButton(frame_bienvenida, text="Reportar alimetos", command=reportar_alimentos_vencidos, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_reportar_alimetos.grid(columnspan=2, row=5, pady=10, padx=10)

    boton_mostrar_alimetos = CTkButton(frame_bienvenida, text="Mostrar cantidad almacenada", command=mostrar_cantidad_almacenada, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_mostrar_alimetos.grid(columnspan=2, row=6,pady=10, padx=10)

    label_bienvenida = CTkLabel(frame_bienvenida, text="¿Deseas volver al inicio de sesion?", font=("Fixedsys", 25))
    label_bienvenida.grid(columnspan=2, row=7, pady=10, padx=10)

    boton_cerrar_bienvenida = CTkButton(frame_bienvenida, text="Volver", command=cerrar_ventana_bienvenida, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_cerrar_bienvenida.grid(columnspan=2, row=8, pady=10, padx=10)

    
    
    def cerrar_programa():
        global continuar_verificacion  # Accede a la variable global
        t.cancel()
        continuar_verificacion = False  # Establece la variable en False para detener la verificación
        conexion.close()
        ventana_bienvenida.quit()
        
        

    def verificar_alimentos_periodicamente():
        global continuar_verificacion  # Accede a la variable global
        global t
        if continuar_verificacion:  # Verifica si la verificación debe continuar
            intervalo_de_tiempo = 10

            if validar_alimetos_proximos == True:
                verificar_alimentos_a_vencer()
                t =threading.Timer(intervalo_de_tiempo, verificar_alimentos_periodicamente)
                t.start()
                
            else:
                t =threading.Timer(intervalo_de_tiempo, verificar_alimentos_periodicamente)
                t.start()

    # Configura el evento de cierre de la ventana principal
    ventana_bienvenida.protocol("WM_DELETE_WINDOW", cerrar_programa)
    ventana_inicio_sesion.protocol("WM_DELETE_WINDOW", cerrar_programa)

    # Inicia la verificación periódica de alimentos
    verificar_alimentos_periodicamente()
    

    



 

# Función para abrir la ventana de registro
def abrir_ventana_registro():
    ventana_registro = tk.Toplevel(ventana_inicio_sesion, bg=c_amarillo)
    ventana_registro.resizable(False, False)
    ventana_registro.title("Registro de Usuario")
    ventana_registro.minsize(200,200)
    ventana_registro.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")
    
    frame_registro = CTkFrame(ventana_registro, fg_color=c_naranja)
    frame_registro.grid(column= 0, row=0, sticky="nsew", padx=10, pady=10)

    ventana_inicio_sesion.columnconfigure(0, weight=1)
    ventana_inicio_sesion.rowconfigure(0, weight=1)

    frame_registro.columnconfigure([0,1], weight=1)
    frame_registro.rowconfigure([0,1,2,3], weight=1)


    label_documento_registro = CTkLabel(frame_registro, text="Documento de Identidad:", font=("Fixedsys", 30))
    label_documento_registro.grid(column= 2, row=1,  padx=10, pady=10)
    entry_documento_registro = CTkEntry(frame_registro, font=("Fixedsys", 30), border_color= c_naranja, fg_color=c_naranja_oscuro, width=260, height=50)
    entry_documento_registro.grid(column= 2, row=2,  padx=10, pady=10)

    label_nombre_registro = CTkLabel(frame_registro, text="Nombre:", font=("Fixedsys", 30))
    label_nombre_registro.grid(column= 2, row=3,  padx=10, pady=10)
    entry_nombre_registro = CTkEntry(frame_registro, font=("Fixedsys", 30), border_color= c_naranja, fg_color=c_naranja_oscuro, width=260, height=50)
    entry_nombre_registro.grid(column= 2, row=4,  padx=10, pady=10)

    boton_registrar = CTkButton(frame_registro, text="Registrar", command=lambda: registrar_usuario(entry_documento_registro.get(), entry_nombre_registro.get()), font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
    boton_registrar.grid(column= 2, row=5,  padx=10, pady=10)

# Función para registrar al usuario
def registrar_usuario(documento, nombre):
    if not documento or not nombre:
        messagebox.showerror("Error", "Por favor, ingrese el documento de identidad y el nombre.")
        return

    try:
        # Intenta guardar el usuario en la base de datos
        guardar_usuario(documento, nombre)
        mensaje_registro.configure(text="Usuario registrado con éxito")
    except mysql.connector.IntegrityError as e:
        # Maneja el error si hay una violación de restricción única
        if "Duplicate entry" in str(e):
            messagebox.showerror("Error", "Ya existe un usuario con el mismo ID o nombre.")
        else:
            messagebox.showerror("Error", "Error desconocido al registrar el usuario.")




imagen_original = Image.open("D:\Files\phyton\imagenes\Logo food inventory.png")


ventana_inicio_sesion.iconbitmap("D:\Files\phyton\imagenes\Logo-food-inventory.ico")



# Configuración de la ventana principal

ctk_image = CTkImage(light_image=imagen_original, size=(150,150))

ventana_inicio_sesion.config(bg=c_amarillo)

frame = CTkFrame(ventana_inicio_sesion, fg_color=c_naranja)
frame.grid(column= 0, row=0, sticky="nsew", padx=10, pady=10)

frame.columnconfigure([0,1], weight=1)
frame.rowconfigure([0,1,2,3,4,5,6,7,8], weight=1)

ventana_inicio_sesion.columnconfigure(0, weight=1)
ventana_inicio_sesion.rowconfigure(0, weight=1)

# Agregar la etiqueta del logo en la parte superior
label = CTkLabel(frame, image=ctk_image, text="", bg_color=c_naranja)
label.grid(columnspan=2, row=0)

# Luego, configura las otras filas y elementos
label_nombre_software = CTkLabel(frame, text="Food Inventory", font=("Fixedsys", 50), bg_color= c_naranja)
label_nombre_software.grid(columnspan=2, row=1, pady=5)


entry_documento = CTkEntry(frame, font=("Fixedsys", 20), placeholder_text="Documeto de identidad", border_color= c_naranja, fg_color=c_naranja_oscuro, width=260, height=50)
entry_documento.grid(columnspan=2, row=2, pady=5, padx=5)


entry_nombre = CTkEntry(frame, font=("Fixedsys", 20), placeholder_text="Nombre", border_color= c_naranja, fg_color=c_naranja_oscuro, width=260, height=50)
entry_nombre.grid(columnspan=2, row=4, pady=5, padx=5)

boton_iniciar_sesion = CTkButton(frame, text="Iniciar Sesión", command=iniciar_sesion, font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro)
boton_iniciar_sesion.grid(columnspan=2, row=5, pady=5, padx=5)

boton_registro = CTkButton(frame, text="Registrarte",  font=("Fixedsys", 30), fg_color=c_amarillo, hover_color= c_amarillo_oscuro, text_color="black", corner_radius= 12, border_width=5,border_color= c_amarillo_oscuro, command=abrir_ventana_registro)
boton_registro.grid(columnspan=2, row=6, pady=5, padx=5)

mensaje_registro = CTkLabel(frame, text="", font=("Fixedsys", 30))
mensaje_registro.grid(columnspan=2, row=7, pady=5, padx=5)

mensaje_label = CTkLabel(frame, text="", font=("Fixedsys", 30))
mensaje_label.grid(columnspan=2, row=8, pady=9, padx=5)

ventana_inicio_sesion.resizable(False, False)

# Configurar la geometría para que esté en el centro de la pantalla
ventana_inicio_sesion.update_idletasks()
ancho = ventana_inicio_sesion.winfo_width()
alto = ventana_inicio_sesion.winfo_height()
x = (ventana_inicio_sesion.winfo_screenwidth() // 2) - (ancho // 2)
y = (ventana_inicio_sesion.winfo_screenheight() // 2) - (alto // 2)
ventana_inicio_sesion.geometry(f'{ancho}x{alto}+{x}+{y}')

ventana_inicio_sesion.mainloop()
