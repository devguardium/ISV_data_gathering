# ISV_data_gathering

## Development
- Activate virtual environment
```sh
  source venv/bin/activate
```

- Run server in development mode
  ```sh
    python server.py
  ```

- Ping server
  
  ```sh
  # In a second tab, execute
      curl -X POST http://localhost:2901/api/ \
    -H "Content-Type: application/json" \
    -d '{
      "text": "Яблоко слишком маленькое.",
      "lang": "ru"
    }'
    


- In case you need to

 ```sh
    # Exit venv
    deactivate

    # Remove venv
    rm -r venv
 ```

  - Apply PEP 8
  ```sh
    black . --exclude venv
  ```

## Setting up a development machine on Digital Ocean

  - Create a new Ubuntu 24 LTS droplet
    - Provide SSH key for accessing the droplet

  - Configure local SSH client to access the droplet
  ```ssh-config
    # ubuntu 24 machine as root
    Host do-ubuntu-24
        HostName [COPY-DROPLET-IP-HERE]
        IdentityFile ~/.ssh/id_digital_ocean
        IdentitiesOnly yes
        User root
   ```

  - Copy your github ssh key to droplet
  ```sh
    scp ~/.ssh/id_ed25519 do-ubuntu-24:/root/.ssh/
  ```

  - Connect to the droplet, e.g.
  ```sh
    ssh do-ubuntu-24
  ```
  
  - In case you like to use micro editor
  ```sh
    apt install micro
  ```

  - Clone repo
  ```sh
    git clone git@github.com:devguardium/ISV_data_gathering.git
  ```

  - Configure repo for your username and email, e.g.
  ```sh
    git config user.name "[YOUR USER]"
    git config user.email "YOUR EMAIL"

    git config --list
  ```

  - Install Python 3.9
  ```sh
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.9 python3.9-venv

    python3.9 --version
  ```

  - Create virtual environment
  ```sh
    python3.9 -m venv venv --without-pip
    source venv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.9 get-pip.py
  ```

  - Install project dependencies
  ```sh
    pip install -r requirements.txt
  ```

  - Install dev dependencies
  ```sh
    pip install -r dev-requirements.txt
  ```

  - Copy Slovnik files
  ```sh
    scp -r out_isv_cyr/ do-ubuntu-24:/root/ISV_data_gathering
    scp -r out_isv_etm/ do-ubuntu-24:/root/ISV_data_gathering
    scp -r out_isv_lat/ do-ubuntu-24:/root/ISV_data_gathering
  ```

## Deployment to Digital Ocean

### Prerequsites

  - Create a new Ubuntu 24 LTS droplet
    - Provide SSH key for accessing the droplet

  - Configure local SSH client to access the droplet
  ```ssh-config
    # ubuntu 24 machine as root
    Host do-ubuntu-24
        HostName [COPY-DROPLET-IP-HERE]
        IdentityFile ~/.ssh/id_digital_ocean
        IdentitiesOnly yes
        User root
   ```

  - Connect to the droplet, e.g.
  ```sh
    ssh do-ubuntu-24
  ```
  
  - In case you like to use micro editor
  ```sh
    apt install micro
  ```

  - Clone repo
  ```sh
    # Cloning is over https, so no ssh key required
    # N.B. No changes could be pushed back to git
    git clone https://github.com/devguardium/ISV_data_gathering.git
  ```

  - Checkout standalone_flask branch
  ```sh
    cd ISV_data_gathering/

    git checkout standalone_flask
  ```

   - Install Python 3.9
  ```sh
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.9 python3.9-venv

    python3.9 --version
  ```

  - Create virtual environment
  ```sh
    python3.9 -m venv venv --without-pip
    source venv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3.9 get-pip.py
  ```

  - Install project dependencies
  ```sh
    pip install -r requirements.txt
  ```

  - Configure firewall
  ```sh
    ufw status
    ufw allow 22
    ufw allow 2901
    ufw show added
    ufw enable
  ```

  - Copy Slovnik files
  ```sh
    scp -r out_isv_cyr/ do-ubuntu-24:/root/ISV_data_gathering
    scp -r out_isv_etm/ do-ubuntu-24:/root/ISV_data_gathering
    scp -r out_isv_lat/ do-ubuntu-24:/root/ISV_data_gathering
  ```

### Run in production
N.B. Flask development server is not recommended for production environment. Use e.g. gunicorn instead.

  - Run under gunicorn
  ```
    gunicorn --bind 0.0.0.0:2901 gunicorn_run:app
  ```
