apt update
apt install --assume-yes python3-pip
apt install --assume-yes redis-server

systemctl start redis-server.service
systemctl enable redis-server.service

pip3 install beautifulsoup4
pip3 install ujson
pip3 install redis
