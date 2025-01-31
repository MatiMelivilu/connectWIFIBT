export DISPLAY=:0

while true; do
	xterm -e "sudo python3 /home/IdeasDigitales/Desktop/bluethoot/conect_wifi_blue.py; exit" 
	sleep 1
done &

while true; do
        xterm -e "/home/IdeasDigitales/interfaz_MDB_old; exit" &
        MDB_PID=$!
        wait $MDB_PID
        sleep 1
done &

while true; do
        sudo bt-agent -c NoInputNoOutput &
        BTAG_PID=$!
        wait $BTAG_PID
        sleep 1
done
