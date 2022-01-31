<p align="center">
  <a href="https://github.com/Stax124/Updater">
    <img src="images/updater.png" alt="Logo" width="260">
  </a>

  <h3 align="center">Updater</h3>

  <p align="center">
    🔥 An awesome Updater for small projects 🔥<hr /> 
  </p>
</p>

<!-- TABLE OF CONTENTS -->

- 1. [About The Project](#AboutTheProject)
  - 1.1. [Built With](#BuiltWith)
- 2. [Getting Started](#GettingStarted)
  - 2.1. [Binaries](#Binaries)
  - 2.2. [Building from source](#BuildingFromSource)
  - 2.3 [Setting Up](#SettingUp)
- 3. [Usage](#Usage)
     - 3.1. [Python](#Python)
     - 3.2. [Node.js](#Node.js)
     - 3.3. [Deno](#Deno)
     - 3.4. [C++](#C)
- 4. [Contributing](#Contributing)
- 5. [License](#License)
- 6. [Contact](#Contact)

## 1. <a name='AboutTheProject'></a>About The Project

There are some good updaters out there but I haven't found a single one that is small enough and easy to use, so I created this project

Main benefits:

- Your time should be focused on creating something amazing, not thinking about delivering the product via complex processes
- Most updaters are really complex to set up. This one is just a few clicks away

If you have any problem, feel free to fork this project and edit it to your needs or create a pull request, everything counts!

### 1.1. <a name='BuiltWith'></a>Built With

- [TQDM](https://github.com/tqdm/tqdm) (easy to use progress bars)
- [coloredlogs](https://pypi.org/project/coloredlogs/) (easy loggin solution)

## 2. <a name='GettingStarted'></a>Getting Started

**PLEASE CHECK IF YOUR `pip` is pip from python3, if not, use pip3 in all the commands bellow**

This is an example of how to install and set up your content delivery to your customers. These steps might require some knowledge of Linux and firewalls.

### 2.1. <a name='Binaries'></a>Using binaries (The fast method)

Binaries are probably the fastest way to get going. Feel free to grab one from [releases](https://github.com/Stax124/Updater/releases) (make sure you use the correct platform)

### 2.2. <a name='BuildingFromSource'></a>Building from source (The more customizable method)

1. Clone the repository
   ```
   git clone https://github.com/Stax124/Updater
   ```
2. Navigate to the created folder
   ```
   cd Updater
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Build the application

   ```
   $ pip install pyinstaller

   (Linux) chmod +x scripts/build.sh
   (Linux) ./scripts/build.sh

   (Windows) .\scripts\build.ps1
   ```

   There should be a folder called `dist` with the executable in it.

### 2.3. <a name="SettingUp"></a>Setting up

1. Install `Apache2`/`Nginx` (or similar) on your content distribution server

   ```
   sudo apt install apache2

   (optional) sudo systemctl status apache2
   ```

2. Upload all your files to the webserver via **sftp** of similar _(don't forget to add Updater executable to root of your project, so that it can be used from clients machine for downloading updates)_

   ```
   (local machine) cd [folder that you have your files for distribution]
   (local machine) sftp [username]@[server]

   (remote server) cd /var/www/html/[your folder that will be used as mirror]
   (remote machine) put *
   ```

3. Download Linux executable from [releases](https://github.com/Stax124/Updater/releases) and put it on path

   ```
   cd ~
   mkdir utils
   cd utils
   wget --no-check-certificate [link to executable from our releases]
   export PATH="~/utils:$PATH"
   ```

   Note that it will be usable only for this session. If you don't want to use the `export PATH=...` command, you can add the following line to your `~/.bashrc` file:

   ```
   export PATH="~/utils:$PATH"
   ```

4. Navigate to webserver folder and generate hashtable

   ```
   cd /var/www/html/[folder where you want to store the distributables]
   updater -g hashtable.hash [-e files_or_directories_to_exclude]
   ```

   File `hashtable.hash` will be generated. Client will then be able to download the latest version of your project.

5. Open port **80** (or the one you want to use) on both your webserver and firewall

   ```
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport [port] -j ACCEPT
   sudo netfilter-persistent save

   --- or if you have ufw---

   sudo ufw allow [port]
   ```

6. Test if the connection can be established ([nmap](https://nmap.org/) is a good tool to test this)
   ```
   nmap [remote server ip] -Pn -p [port] -sS
   ```

## 3. <a name='Usage'></a>Usage in your projects

Place snippets of code for your language into your projects

#### 3.1. <a name='Python'></a>Python

All of these snippets are using system calls to run the updater. Feel free to modify them or use something else.
Optionally, if you are using python in your project, you can just copy this source code and then call is similarly as they are called in the `main.py` file.

```py
import os
os.system("updater -m http://example/mirror http://example/hashtable.hash -y")
```

#### 3.2. <a name='Node.js'></a>Node.js

```js
const { exec } = require("child_process");

exec(
	"updater -m http://example/mirror http://example/hashtable.hash -y",
	(error, stdout, stderr) => {
		if (error) {
			console.log(`error: ${error.message}`);
			return;
		}
		if (stderr) {
			console.log(`stderr: ${stderr}`);
			return;
		}
		console.log(`stdout: ${stdout}`);
	}
);
```

#### 3.3. <a name='Deno'></a>Deno

```js
const process = Deno.run({
	cmd: ["updater", "-m http://example/mirror http://example/hashtable.hash -y"],
});
```

#### 3.4. <a name='C'></a>C++

```c++
#include <iostream>
using namespace std;

int update ()
{
    system("updater -m http://example/mirror http://example/hashtable.hash -y");
    return 0;
}
```

## 4. <a name='Contributing'></a>Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 5. <a name='License'></a>License

Distributed under the MIT License. See `LICENSE` file for more information.

<!-- CONTACT -->

## 6. <a name='Contact'></a>Contact ✉️

Tomáš Novák - tamoncz@gmail.com

Project Link: [https://github.com/Stax124/Updater](https://github.com/Stax124/Updater)
