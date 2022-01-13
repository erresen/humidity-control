echo "Stopping humidity.service"
sudo systemctl stop humidity.service
echo "Stopping humidity-metrics.service"
sudo systemctl stop humidity-metrics.service
echo "Starting humidity.service"
sudo systemctl start humidity.service
echo "Starting humidity-metrics.service"
sudo systemctl start humidity-metrics.service
echo "Services restarted"