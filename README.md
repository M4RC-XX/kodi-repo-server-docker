
# Kodi Repository Server | Docker

This project provides a fully automated, Docker-powered server to host and manage your own Kodi addon repository. It's designed for simplicity and reliability, allowing anyone to maintain a repository with minimal effort.

## ✨ Features

+ **Works on Raspberry Pi (arm64)!**

+ **Automated Processing:** Actively monitors an input folder for new addon .zip files.

+ **Intelligent Versioning:** A new addon version will replace an older one. Older or identical versions are automatically ignored and archived, preventing accidental repository downgrades.

+ **Clean Archiving:** Successfully processed .zip files are moved to a zips archive for your records.
+ **Simple Deployment:** Uses Docker Compose to get the entire service running with a single command.

⚙️ Prerequisites
----------------

*   [Docker](https://www.docker.com/get-started) 
*   [Docker](https://docs.docker.com/compose/install/) Compose

## ⬇️ Option 1: Download & Compile
```
# Clone repo
git clone https://github.com/m4rc-xx/kodi-repo-server-docker/

cd kodi-repo-server-docker
mv kodi-repo-server-docker kodi-repo-server

# Build
docker build --no-cache -t kodi-repo-server .
```
## 🚀 Run
```
docker run -d \
  -p 8008:8008 \
  --user "$(id -u):$(id -g)" \
  -v /home/pi/kodi-repository:/app \
  --name mein-kodi-repo \
  --restart unless-stopped \
  kodi-repo-server
```

## ⬇️ Option 2: Docker-Compose
```
services:
  kodi-repo-server:
    image: ghcr.io/m4rc-xx/kodi-repo-server-docker:latest
    container_name: kodi-repo-server
    ports:
      - "80:80"
    volumes:
      - /home/pi/kodi-repository/input:/app/input
      - /home/pi/kodi-repository/addons:/app/addons
      - /home/pi/kodi-repository/web:/app/web
      - /home/pi/kodi-repository/zips:/app/zips
    user: "${UID}:${GID}"
    restart: unless-stopped
```

⁉️ How It Works
----------------------

This project automates your entire Kodi repository workflow. Here's the simple, step-by-step process:
1. **Add an Addon:** Copy your addon .zip file into the input folder.
    
2.  **Automatic Version Check:** The system automatically reads the addon.xml inside the .zip to check its version.
    
    *   **Newer Version:** If the version is newer than the one in your repository, the old version is replaced, and the repository is updated.
        
    *   **Older or Same Version:** If the version is older or the same, the process stops, and the .zip file is simply moved to the zips folder for archival.
        
3.  **Source Management:** All current addon versions are stored unpacked in the addons folder. This folder acts as the permanent source of truth for your repository.
    
4.  **Repository Generation:** The generator.py script uses the addons folder to build (or rebuild) the public web folder.
    
5.  **Kodi Access:** The web folder is the public root of your repository. This is the directory that Kodi will access to find your addons.xml and download the addon .zip files.


📁 Directory Structure
----------------------

After the first start, the following folders will be created inside kodi-repository:

*   **/input:** Drop new addon .zip files here.
    
*   **/addons:** The permanent source folder containing all unpacked addons.
    
*   **/web:** The public, network-accessible Kodi repository.
    
*   **/zips:** The archive for all successfully processed original .zip files.
