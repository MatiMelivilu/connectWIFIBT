import bluetooth
import subprocess

def configure_wifi(ssid, password):
    """Configura la red WiFi usando nmcli."""
    try:
        subprocess.run(
            ["sudo", "nmcli", "dev", "wifi", "connect", ssid, "password", password],
            check=True
        )
        print("Wi-Fi configurada correctamente.")
        return True  # Conexion exitosa
    except subprocess.CalledProcessError as e:
        print(f"Error al configurar Wi-Fi: {e}")
        return False  # Error al conectar

def pair_and_accept(bdaddr):
    """Empareja y acepta automaticamente un dispositivo Bluetooth."""
    try:
        subprocess.run(["bluetoothctl", "pair", bdaddr], check=True)
        print(f"Dispositivo {bdaddr} emparejado.")

        subprocess.run(["bluetoothctl", "trust", bdaddr], check=True)
        print(f"Dispositivo {bdaddr} marcado como confiable.")
    except subprocess.CalledProcessError as e:
        print(f"Error al emparejar o aceptar el dispositivo: {e}")

def is_device_connected_pybluez(bdaddr):
    """Verifica si un dispositivo esta conectado usando PyBluez."""
    try:
        connected_devices = bluetooth.find_service(address=bdaddr)
        if connected_devices:
            print(f"Dispositivo {bdaddr} esta conectado.")
            return True
        else:
            print(f"Dispositivo {bdaddr} no esta conectado.")
            return False
    except Exception as e:
        print(f"Error al verificar el dispositivo con PyBluez: {e}")
        return False

def start_bluetooth_server():
    """Inicia el servidor Bluetooth para recibir datos."""
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", bluetooth.PORT_ANY))
    server_socket.listen(1)
    port = server_socket.getsockname()[1]

    bluetooth.advertise_service(
        server_socket, "WiFiConfigurator",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print(f"Esperando conexiones en el puerto {port}...")

    client_socket, client_info = server_socket.accept()
    print(f"Conexion aceptada de {client_info[0]} ({client_info[1]}).")

    try:
        if not is_device_connected_pybluez(client_info[0]):
            print(f"Dispositivo {client_info[0]} no esta conectado. Intentando emparejar...")
            pair_and_accept(client_info[0])

        while True:
            data = client_socket.recv(1024).decode("utf-8").strip()
            print(f"Datos recibidos: {data}")

            if data.startswith("WIFI:"):
                try:
                    ssid, password = data[5:].split(";")
                    ssid, password = ssid.strip(), password.strip()

                    if configure_wifi(ssid, password):
                        client_socket.send("Wi-Fi configurada con exito.".encode("utf-8"))
                        break
                    else:
                        client_socket.send("Error al conectar. Verifica los datos y envialos nuevamente.".encode("utf-8"))
                except ValueError:
                    client_socket.send("Error: Formato invalido. Usa WIFI:ssid;password.".encode("utf-8"))
                except Exception as e:
                    client_socket.send(f"Error inesperado: {e}".encode("utf-8"))
            else:
                client_socket.send("Error: Comando desconocido. Usa el formato WIFI:ssid;password.".encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    start_bluetooth_server()
