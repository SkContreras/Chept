import socket
import os
import time
from colorama import Fore, Style, init
import threading
import json

# Inicializar colorama
init(autoreset=True)

# Estilo de la interfaz
def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.GREEN + Style.BRIGHT + """
     ██████╗██╗  ██╗███████╗██████╗ ████████╗
    ██╔════╝██║  ██║██╔════╝██╔══██╗╚══██╔══╝
    ██║     ███████║█████╗  ██████╔╝   ██║   
    ██║     ██╔══██║██╔══╝  ██╔═══╝    ██║   
    ╚██████╗██║  ██║███████╗██║        ██║   
     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   
        Terminal de comunicación
    """ + Style.RESET_ALL)

# Configuración del servidor
host = "127.0.0.1"  # Dirección IP local
port = 12345        # Puerto
file_path = "C:/Users/shark/OneDrive/Documentos/smsTerminal/dist/juego.exe"  # Ruta al archivo .exe que quieres enviar

def iniciar_servidor():
    # Crear socket del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    return server_socket

def esperar_conexion(server_socket):
    print(Fore.CYAN + "[*] Esperando conexión...")
    cliente1, addr1 = server_socket.accept()
    print(f"Jugador 1 conectado desde {addr1}")
    cliente2, addr2 = server_socket.accept()
    print(f"Jugador 2 conectado desde {addr2}")
    return cliente1, addr1, cliente2, addr2

def mostrar_carga():
    print(Fore.YELLOW + "[*] Enviando archivo... Por favor espera.")
    for i in range(0, 101, 10):
        print(Fore.GREEN + f"[Cargando...] {i}%")
        time.sleep(0.5)
        
def manejar_cliente(cliente, addr, nombre_cliente, clientes_conectados):
    try:
        print(Fore.GREEN + f"[+] Conexión establecida con: {nombre_cliente} ({addr[0]}:{addr[1]})")
        cliente.settimeout(10)  # Establecer un tiempo de espera

        while True:
            try:
                # Recibir mensaje del cliente
                msg = cliente.recv(1024).decode('utf-8')
                if not msg:
                    print(Fore.RED + f"[-] {nombre_cliente} desconectado.")
                    break
                if msg.lower() == "salir":
                    print(Fore.RED + f"[*] {nombre_cliente} ha cerrado la conexión.")
                    break

                # Mostrar el mensaje solo en la terminal del servidor
                print(Fore.MAGENTA + f"{nombre_cliente}: {msg}")

                # Encontrar al jugador contrario y enviarle el mensaje
                jugador_opuesto = None
                for cliente_nombre, conexion_cliente in clientes_conectados.items():
                    if cliente_nombre != nombre_cliente:
                        jugador_opuesto = conexion_cliente
                        break

                if jugador_opuesto:
                    # Procesar el mensaje y añadir el identificador de origen
                    respuesta = procesar_mensaje(msg, nombre_cliente, clientes_conectados)
                    respuesta_con_nombre = {
                        "origen": nombre_cliente,
                        "contenido": respuesta
                    }
                    print("mensaje renviado desde el servidor")
                    jugador_opuesto.send(json.dumps(respuesta_con_nombre).encode())  # Enviar como JSON
            
                if respuesta.lower() == "salir":
                    print(Fore.RED + f"[*] Cerrando la conexión con {nombre_cliente}...")
                    break
                time.sleep(1)  # Pausa para evitar sobrecargar el servidor
            except socket.timeout:
                continue
            except Exception as e:
                print(Fore.RED + f"Error al manejar el cliente: {e}")
                break

    except Exception as e:
        print(Fore.RED + f"Error general al manejar la conexión con {nombre_cliente}: {e}")
    finally:
        cliente.close()
        print(Fore.YELLOW + f"[*] Conexión cerrada con: {nombre_cliente} ({addr[0]}:{addr[1]})")

def enviar_archivo(cliente):
    mostrar_carga()
    try:
        with open(file_path, "rb") as f:
            while True:
                file_data = f.read(1024)
                if not file_data:
                    break
                cliente.sendall(file_data)
        print(Fore.GREEN + f"[+] Archivo '{file_path}' enviado correctamente.")
    except FileNotFoundError:
        print(Fore.RED + f"[-] Archivo '{file_path}' no encontrado.")
        cliente.send(b"Error: archivo no encontrado.")

def procesar_mensaje(msg, nombre_cliente, clientes_conectados):
    if "jugar" in msg.lower():
        return "¡Estás listo para jugar! Espera a que el otro jugador se conecte."
    elif "ayuda" in msg.lower():
        return "Escribe 'sk.play' para iniciar el juego."
    elif "elige" in msg.lower():
        # Si hay una interacción de juego entre jugadores, se debe notificar a ambos jugadores
        if nombre_cliente == "Jugador 1":
            clientes_conectados[1].send(f"El Jugador 1 ha elegido: {msg}".encode())
        else:
            clientes_conectados[0].send(f"El Jugador 2 ha elegido: {msg}".encode())
        return "Esperando que el otro jugador elija..."
    
                # Procesar y enviar respuesta al cliente
    elif "sk.play" in msg.lower():
        enviar_archivo(nombre_cliente)
    else:
        return msg

def aceptar_conexiones():
    server_socket = iniciar_servidor()
    banner()
    print(Fore.YELLOW + "[*] Iniciando servidor...")
    time.sleep(1)

    cliente1, addr1, cliente2, addr2 = esperar_conexion(server_socket)

    # Asignamos nombres de usuario a cada cliente en un diccionario
    clientes_conectados = {
        "Jugador 1": cliente1,
        "Jugador 2": cliente2
    }

    # Enviar los nombres de usuario a los clientes
    cliente1.send(f"Jugador 1".encode())
    cliente2.send(f"Jugador 2".encode())

    # Crear hilos para manejar cada cliente
    hilo_cliente1 = threading.Thread(target=manejar_cliente, args=(cliente1, addr1, "Jugador 1", clientes_conectados))
    hilo_cliente2 = threading.Thread(target=manejar_cliente, args=(cliente2, addr2, "Jugador 2", clientes_conectados))
    hilo_cliente1.start()
    hilo_cliente2.start()

    # Esperar a que ambos hilos terminen
    hilo_cliente1.join()
    hilo_cliente2.join()

    server_socket.close()
    print(Fore.YELLOW + "[*] Servidor cerrado.")


# Ejecutar la función principal para aceptar conexiones y manejar clientes
if __name__ == "__main__":
    aceptar_conexiones()
