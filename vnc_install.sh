#!/bin/bash
apt update -qq
apt upgrade -qq
apt install -y python xfce4 xfce4-goodies tightvncserver git torbrowser-launcher
mkdir -p ~/.vnc
echo "password" | vncpasswd -f > ~/.vnc/passwd
cat > ~/.vnc/xstartup << EOF
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF
chmod 755 ~/.vnc/xstartup
chmod 400 ~/.vnc/passwd
sudo vncserver
git clone https://github.com/novnc/noVNC.git /opt/noVNC
openssl req -new -x509 -days 365 -nodes -subj "/C=US/ST=ABC/L=123/O=Haha/CN=www.example.com" -out /opt/noVNC/self.pem -keyout /opt/noVNC/self.pem
sudo /opt/noVNC/utils/launch.sh --vnc localhost:5901 --cert /opt/noVNC/self.pem --web /opt/noVNC/ --ssl-only --listen 443 &
