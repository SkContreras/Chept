import socket
import os
from colorama import Fore, Style, init
import subprocess
import time
import threading
import json
import curses
from queue import Queue

# Inicializar colorama
init(autoreset=True)
# Estilo de la interfaz
def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
     ██████╗██╗  ██╗ █████╗ ██████╗ ██╗  ██╗███████╗
    ██╔════╝██║  ██║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝
    ██║     ███████║███████║██████╔╝█████╔╝ █████╗  
    ██║     ██╔══██║██╔══██║██╔═══╝ ██╔═██╗ ██╔══╝  
    ╚██████╗██║  ██║██║  ██║██║     ██║  ██╗███████╗
     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝
           Terminal de Cliente
    """ + Style.RESET_ALL)

# Configuración del cliente
host = "127.0.0.1"
port = 12345
save_as = "juego_descargado.exe"
# Cola para mensajes
message_queue = Queue()
clientes_colores = {}
# Función para mostrar la pantalla de carga
def mostrar_carga():
    print(Fore.YELLOW + "[*] Recibiendo archivo... Por favor espera.")
    for i in range(0, 101, 10):
        print(Fore.GREEN + f"[Cargando...] {i}%")
        time.sleep(0.5)

def recibir_archivo(cliente):
    try:
        mostrar_carga()
        tamanio_archivo = cliente.recv(1024).decode('utf-8')
        if not tamanio_archivo.isdigit():
            raise ValueError("Tamaño de archivo no válido.")
        tamanio_archivo = int(tamanio_archivo)

        cliente.send("OK".encode('utf-8'))

        with open("archivo_recibido", "wb") as archivo:
            bytes_recibidos = 0
            while bytes_recibidos < tamanio_archivo:
                data = cliente.recv(1024)
                if not data:
                    break
                archivo.write(data)
                bytes_recibidos += len(data)

        print(Fore.GREEN + "[+] Archivo recibido exitosamente.")
    except Exception as e:
        print(Fore.RED + f"[-] Error al recibir el archivo: {e}")

def recibir_mensaje(cliente):
    try:
        cliente.settimeout(2)
        mensaje = cliente.recv(1024).decode()
        return mensaje
    except socket.timeout:
        return None

def identificar_origen(mensaje):
    try:
        mensaje_json = json.loads(mensaje)
        return mensaje_json.get("origen", "servidor"), mensaje_json.get("contenido", mensaje)
    except json.JSONDecodeError:
        return "servidor", mensaje

def enviar_mensaje(cliente, mensaje):
    cliente.send(mensaje.encode())

def manejar_eleccion():
    opciones = ["piedra", "papel", "tijera"]
    while True:
        print(Fore.YELLOW + f"Elige una opción: {', '.join(opciones)}")
        eleccion = input(Fore.BLUE + "Tu elección: ").lower()
        if eleccion in opciones:
            return eleccion
        print(Fore.RED + "Opción no válida. Inténtalo de nuevo.")

def ejecutar_archivo():
    try:
        print(Fore.CYAN + f"[*] Ejecutando {save_as}...")
        subprocess.run([save_as], check=True)
    except Exception as e:
        print(Fore.RED + f"[-] Error al ejecutar el archivo: {e}")

def escuchar_mensajes(cliente, message_queue):
    while True:
        mensaje = recibir_mensaje(cliente)
        if mensaje:
            print(Fore.MAGENTA + f"Escuchando mensaje")
            try:
                message_queue.put(mensaje)
                #mensaje = message_queue.get()
                #print(Fore.MAGENTA + f"Mensaje añadido a la cola: {mensaje}")
            except Exception as e:
                # Inicializar pantalla curses
                stdscr = curses.initscr()
                curses.start_color()
                curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
                
                # Mostrar el mensaje de error en pantalla
                stdscr.clear()
                stdscr.addstr(0, 0, f"Error añadiendo mensaje a la cola: {str(e)}", curses.color_pair(1))
                stdscr.refresh()
                
                # Retornar al modo normal de pantalla
                curses.endwin()

def obtener_color_cliente(cliente_id):
    """Devuelve un color único para cada cliente."""
    if cliente_id not in clientes_colores:
        color_id = len(clientes_colores) + 3  # Para evitar los colores 0, 1, 2 ya asignados
        curses.init_pair(color_id, curses.COLOR_BLACK, curses.COLOR_YELLOW + (color_id % 7))
        clientes_colores[cliente_id] = color_id
    return clientes_colores[cliente_id]

def interfaz_principal(stdscr, cliente, nombre_usuario):
    curses.curs_set(1)  # Muestra el cursor
    stdscr.clear()  # Limpia la pantalla inicial
    # Configurar colores en curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Mensajes normales
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   # Mensajes de error
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Color por defecto para los mensajes de los clientes

    altura_chat, ancho_chat = curses.LINES - 3, curses.COLS
    altura_input = 3
    ventana_chat = curses.newwin(altura_chat, ancho_chat, 0, 0)
    ventana_input = curses.newwin(altura_input, ancho_chat, altura_chat, 0)

    ventana_chat.scrollok(True)  # Permite el desplazamiento automático del chat
    ventana_chat.idlok(True)  # Habilita el desplazamiento físico en la ventana

    # Inicia el hilo para recibir mensajes
    hilo_recibir = threading.Thread(target=escuchar_mensajes, args=(cliente, message_queue))
    hilo_recibir.daemon = True
    hilo_recibir.start()

    mensajes_mostrados = []  # Lista para almacenar los mensajes mostrados
    cliente_id = nombre_usuario  # Supuesto ID único del cliente (debes tenerlo en tu cliente)

    while True:
        # Recibe los mensajes en el hilo principal
        if not message_queue.empty():
            mensaje = message_queue.get()
            try:
                mensaje_json = json.loads(mensaje)
                origen = mensaje_json.get("origen", "Desconocido")
                contenido = mensaje_json.get("contenido", "")
                mensaje_formateado = f"{origen}: {contenido}"

                # Si el mensaje proviene del cliente, lo mostramos de una forma diferente
                if origen == "yo":
                    color_msg = curses.color_pair(1)  # Color para los mensajes del cliente
                else:
                    color_msg = curses.color_pair(obtener_color_cliente(origen))  # Color único para cada cliente

                mensajes_mostrados.append((mensaje_formateado, color_msg))  # Añade el mensaje a la lista
                if len(mensajes_mostrados) > altura_chat - 1:  # Limita la cantidad de mensajes mostrados
                    mensajes_mostrados.pop(0)  # Elimina el mensaje más antiguo si la lista es demasiado larga

                ventana_chat.clear()  # Borra la pantalla anterior
                for i, (msg, color) in enumerate(mensajes_mostrados):  # Muestra todos los mensajes almacenados
                    ventana_chat.addstr(i, 0, msg + '\n', color)

                ventana_chat.refresh()  # Refresca la ventana para mostrar el nuevo contenido

            except json.JSONDecodeError:
                ventana_chat.clear()
                ventana_chat.addstr(f"Error al procesar el mensaje: {mensaje}\n", curses.color_pair(2))
                ventana_chat.refresh()

        ventana_input.clear()  # Borra la línea de entrada
        ventana_input.addstr("Escribe un mensaje: ")
        ventana_input.refresh()

        # Obtiene la entrada del usuario
        mensaje = ventana_input.getstr(1, 0).decode('utf-8')
        if mensaje.lower() == "salir":
            break
        if mensaje.strip():  # Si el mensaje no está vacío
            # Se asume que el cliente envía el mensaje con "yo" como su origen
            enviar_mensaje(cliente, json.dumps({"origen": "yo", "contenido": mensaje}))

    cliente.close()


# Función principal del cliente
def cliente_serv():
    banner()
    print("[*] Conectando al servidor...")

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))  # Cambia por la IP y puerto del servidor
        print("[+] Conectado al servidor.")

        nombre_usuario = client_socket.recv(1024).decode()
        print(f"Nombre de usuario recibido: {nombre_usuario}")

        curses.wrapper(lambda stdscr: interfaz_principal(stdscr, client_socket, nombre_usuario))

    except ConnectionRefusedError:
        print("[-] No se pudo conectar al servidor.")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client_socket.close()
        print("[*] Conexión cerrada.")
# Llamada a la función principal
if __name__ == "__main__":
    cliente_serv()
