import socket
import sys
import time

# Función para elegir el ganador
def determinar_ganador(opcion1, opcion2):
    if opcion1 == opcion2:
        return "Empate"
    elif (opcion1 == "piedra" and opcion2 == "tijeras") or \
         (opcion1 == "tijeras" and opcion2 == "papel") or \
         (opcion1 == "papel" and opcion2 == "piedra"):
        return "Jugador 1 gana"
    else:
        return "Jugador 2 gana"

# Función para interactuar con el servidor
def interactuar_con_servidor(socket_cliente):
    print("Esperando instrucciones del servidor...")

    # Recibir el saludo inicial
    mensaje = socket_cliente.recv(1024).decode()
    print(f"Servidor: {mensaje}")

    # Recibir las elecciones de los jugadores y mostrar
    while True:
        mensaje = socket_cliente.recv(1024).decode()
        if mensaje.startswith("Elige tu opción"):
            print(f"{mensaje}\n")
            # Enviar una respuesta (simula que el jugador elige aleatoriamente)
            opcion = input("Tu opción (piedra, papel o tijeras): ").lower().strip()
            socket_cliente.sendall(opcion.encode())
        elif mensaje.startswith("Resultado"):
            print(f"{mensaje}\n")
            break
        else:
            print(f"Servidor: {mensaje}")

# Función principal para conectar al servidor y ejecutar el juego
def main():
    # Configuración de la conexión con el servidor
    server_ip = sys.argv[1]  # IP del servidor, pasada como argumento
    server_port = int(sys.argv[2])  # Puerto, pasado como argumento

    # Crear un socket de cliente
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conectarse al servidor
        cliente.connect((server_ip, server_port))
        print("Conectado al servidor.\n")

        # Interactuar con el servidor para el juego
        interactuar_con_servidor(cliente)

    except Exception as e:
        print(f"No se pudo conectar al servidor: {e}")

    finally:
        cliente.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    main()
