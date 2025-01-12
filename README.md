# README: Servidor de Comunicación Multijugador

Este es un servidor de comunicación multijugador desarrollado en Python que permite la conexión y el intercambio de mensajes entre dos jugadores. El servidor utiliza sockets para manejar la comunicación y permite enviar un archivo `.exe` de un jugador a otro durante la sesión. El servidor también tiene un sistema de comandos para interactuar con los jugadores, como iniciar el juego o pedir ayuda.

## Requisitos

- Python 3.x
- Biblioteca `colorama` (para colores en la terminal)
  
Puedes instalar `colorama` usando el siguiente comando:
```bash
pip install colorama
```

## Descripción del Código

### Estructura Principal

- **Función `banner()`**: Muestra un banner con el nombre del juego o terminal de comunicación.
- **Función `iniciar_servidor()`**: Configura el servidor y espera conexiones.
- **Función `esperar_conexion()`**: Espera a que dos jugadores se conecten al servidor.
- **Función `manejar_cliente()`**: Gestiona la comunicación entre el servidor y un cliente, recibiendo y enviando mensajes.
- **Función `mostrar_carga()`**: Muestra una animación de carga al enviar el archivo.
- **Función `enviar_archivo()`**: Envía un archivo `.exe` desde el servidor a los jugadores.
- **Función `procesar_mensaje()`**: Procesa los mensajes de los jugadores y responde con mensajes predeterminados, o transmite las interacciones del juego entre los jugadores.
- **Función `aceptar_conexiones()`**: Configura el servidor para aceptar conexiones de los jugadores y gestionar la comunicación entre ellos.

### Flujo del Servidor

1. El servidor muestra un banner e inicia un socket en la dirección `127.0.0.1` y el puerto `12345`.
2. Espera a que se conecten dos jugadores.
3. Una vez ambos jugadores están conectados, se les asigna un nombre: "Jugador 1" y "Jugador 2".
4. Los jugadores pueden enviarse mensajes, y el servidor retransmite los mensajes entre ellos.
5. Si un jugador escribe el comando "sk.play", el servidor comenzará a enviar un archivo `.exe` al jugador correspondiente.
6. El servidor permite la desconexión de los jugadores con el comando "salir".

## Uso

1. Ejecuta el servidor en tu máquina local:
   ```bash
   python servidor.py
   ```

2. Los jugadores deben conectarse al servidor usando un cliente que se conecte a la IP `127.0.0.1` y al puerto `12345`.

3. Una vez conectado, el jugador puede usar comandos como:
   - `jugar`: Para recibir instrucciones sobre el juego.
   - `ayuda`: Para obtener ayuda sobre los comandos.
   - `elige`: Para hacer una elección en el juego, que se compartirá con el otro jugador.

## Archivos

- **`servidor.py`**: Código fuente del servidor de comunicación multijugador.
- **`juego.exe`**: Archivo que se enviará a los jugadores cuando se inicie el juego (especificado en el código).

## Contribuciones

Si deseas contribuir al proyecto, puedes hacerlo abriendo un "pull request" o creando un "issue" si encuentras algún problema o tienes sugerencias.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.# Chept
