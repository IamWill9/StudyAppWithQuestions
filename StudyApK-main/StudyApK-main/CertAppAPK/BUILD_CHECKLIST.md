# First-Time Buildozer Setup Checklist (for Android APKs on WSL/Ubuntu)

## Install system packages

```bash
sudo apt install python3.10 python3.10-venv python3.10-dev build-essential zip unzip openjdk-17-jdk ...
```

## Create a venv with Python 3.10

```bash
python3.10 -m venv ~/.venvs/buildozer310
source ~/.venvs/buildozer310/bin/activate
```

## Upgrade pip and install buildozer/cython

```bash
pip install --upgrade pip
pip install buildozer cython
```

## Create or edit buildozer.spec

- Set `requirements = python3==3.10.12,kivy`
- Set your app details (title, package, version, etc)

## Clean previous build artifacts

```bash
rm -rf .buildozer
buildozer android clean
```

## Build your APK

```bash
buildozer -v android debug
```

## Install on your phone

1. Connect via USB (with USB debugging enabled)
2. `adb devices` (should show your phone)
3. `buildozer android deploy run`

## Debug logs (optional)

```bash
buildozer android logcat
```

## Pro tips

- If you get weird errors, always check your Python version (`python --version`) and that your venv is active.
- If you're using WSL2, make sure your Android SDK/NDK are not on the Windows file system for best speed.
