# !/bin/bash

echo "Installing packages"
#sudo pip3 install -r src/requirements.txt

echo "Installing hydroponic-system-application files..."
sudo rm -rf /usr/lib/hydroponic-system-application
sudo mkdir /usr/lib/hydroponic-system-application
sudo cp -rf src/* /usr/lib/hydroponic-system-application/
sudo cp hydroponic-system-application.service /etc/systemd/system/hydroponic-system-application.service
sudo systemctl disable hydroponic-system-application.service
sudo systemctl stop hydroponic-system-application.service
sudo systemctl enable hydroponic-system-application.service
sudo systemctl start hydroponic-system-application.service

echo "Finished hydroponic-system-application system installation."
exit 0