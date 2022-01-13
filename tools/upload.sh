rsync -azP --chmod=a+x ../src/main.py ../src/metrics.py service-restart.sh pi@192.168.1.234:/home/pi
ssh pi@192.168.1.234 "./service-restart.sh"