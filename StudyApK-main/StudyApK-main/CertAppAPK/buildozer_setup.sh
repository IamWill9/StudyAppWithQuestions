sudo apt update && sudo apt upgrade -y

# Essential Python and Build Tools
sudo apt install -y python3.10 python3.10-venv python3.10-dev \
    build-essential git zip unzip openjdk-17-jdk \
    libffi-dev libssl-dev libsqlite3-dev zlib1g-dev \
    libjpeg-dev libpng-dev

# (optional but helpful) For sound support
sudo apt install -y ffmpeg libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0

# For running Android builds in WSL (optional, for graphics forwarding)
sudo apt install -y mesa-utils

# Set up your venv and activate
python3.10 -m venv ~/.venvs/buildozer310
source ~/.venvs/buildozer310/bin/activate

# Upgrade pip, install buildozer and cython
pip install --upgrade pip
pip install buildozer cython

echo "Done! Now edit your buildozer.spec for:"
echo "requirements = python3==3.10.12,kivy"
echo "And you are ready to build!"
