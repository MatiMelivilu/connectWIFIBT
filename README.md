# Configuración de Wi-Fi en Raspberry Pi 4 mediante Bluetooth

Este documento describe los pasos necesarios para configurar la conexión Wi-Fi en una Raspberry Pi 4 utilizando Bluetooth en Raspberry Pi OS Bookworm.

## Instalación de paquetes necesarios

Ejecuta los siguientes comandos para instalar los paquetes requeridos:

```bash
sudo apt-get install bluez && sudo apt-get install bluez-tools
sudo apt install bluetooth bluez python3-bluez
```

Verifica la versión de `NetworkManager` con:

```bash
nmcli --version
```

Si no está instalado, instálalo con:

```bash
sudo apt install network-manager
```

## Configuración de Bluetooth

### Modificación de archivos de configuración

Edita el siguiente archivo:

```bash
sudo nano /etc/systemd/system/dbus-org.bluez.service
```

Si el archivo está vacío, usa:

```bash
sudo nano /etc/systemd/system/dbus.org.bluez.service
```

Modifica la línea `ExecStart` y agrega `ExecStartPost`:

```ini
ExecStart=/usr/libexec/bluetooth/bluetoothd -C
ExecStartPost=/usr/bin/sdptool add SP
```

Edita otro archivo de configuración:

```bash
sudo nano /etc/bluetooth/main.conf
```

Descomenta o agrega las siguientes líneas:

```ini
DiscoverableTimeout = 0  # Siempre visible
PairableTimeout = 0      # Siempre emparejable
Discoverable = true
Pairable = true
```

Reinicia los servicios de Bluetooth:

```bash
sudo systemctl daemon-reload
sudo systemctl restart bluetooth
```

### Configuración de Bluetooth con `bluetoothctl`

Ejecuta:

```bash
sudo bluetoothctl
```

ingresa los siguientes comandos:

```bash
[bluetooth] power on
[bluetooth] discoverable on
[bluetooth] pairable on
[bluetooth] agent NoInputNoOutput
[bluetooth] default-agent
[bluetooth] system-alias "Nombre para bluetooth" # Opcional
[bluetooth] exit
```

Asigna permisos al usuario para Bluetooth:

```bash
sudo usermod -a -G bluetooth $(whoami)
```

Reinicia el servicio de Bluetooth:

```bash
sudo systemctl restart bluetooth
```

Para conectar un dispositivo sin requerir código de validación:

```bash
sudo bt-agent -c NoInputNoOutput
```

## Configuración de Wi-Fi mediante Bluetooth

Ejecuta el script como superusuario:

```bash
sudo python3 connectWIFIBT.py
```

Para enviar credenciales de red desde un dispositivo móvil con una aplicación de terminal Bluetooth, usa el siguiente formato:

```
WIFI:"SSID";"PASSWORD"
```

- `SSID`: Nombre de la red Wi-Fi
- `PASSWORD`: Contraseña de la red Wi-Fi

Si la conexión es exitosa, el terminal mostrará una confirmación y se desconectará. Si hay un error, revisa las credenciales e inténtalo nuevamente.

## Ejecución automática al iniciar la Raspberry Pi

Crea un script de arranque:

```bash
nano arranque.sh
```

Agrega el siguiente contenido:

```bash
export DISPLAY=:0

while true; do
    xterm -e "sudo python3 /home/pi/bluetooth/conect_wifi_blue.py; exit"
    sleep 1
done &

while true; do
    sudo bt-agent -c NoInputNoOutput &
    BTAG_PID=$!
    wait $BTAG_PID
    sleep 1
done
```

Guarda el archivo y agrega su ejecución a `crontab`:

```bash
crontab -e
```

Agrega la siguiente línea:

```bash
@reboot /home/pi/arranque.sh
```

Reinicia la Raspberry Pi:

```bash
sudo reboot
```

Cada vez que la Raspberry Pi se encienda, el servicio de configuración de Wi-Fi mediante Bluetooth se iniciará automáticamente.
