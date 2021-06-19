<p align="center">
  <a href="https://github.com/Stax124/Updater">
    <img src="images/updater.png" alt="Logo" width="260">
  </a>

  <h3 align="center">Updater</h3>

  <p align="center">
    An awesome Updater for small projects<hr />
  </p>
</p>


<!-- TABLE OF CONTENTS -->
* 1. [About The Project](#AboutTheProject)
	* 1.1. [Built With](#BuiltWith)
* 2. [Getting Started](#GettingStarted)
	* 2.1. [Prerequisites](#Prerequisites)
	* 2.2. [Installation](#Installation)
* 3. [Usage](#Usage)
		* 3.1. [Python](#Python)
		* 3.2. [Node.js](#Node.js)
		* 3.3. [Deno](#Deno)
		* 3.4. [C++](#C)
* 4. [Contributing](#Contributing)
* 5. [License](#License)
* 6. [Contact](#Contact)


##  1. <a name='AboutTheProject'></a>About The Project

There are many great README templates available on GitHub, however, I didn't find one that really suit my needs so I created this enhanced one. I want to create a README template so amazing that it'll be the last one you ever need -- I think this is it.

There are some good updaters out there but a haven't found a single one that is small enough and easy to use, so I created this project

Main benefits:
* Your time should be focused on creating something amazing, not thinking about delivering the product via complex processes
* Most updaters are really complex, I cannot say this about this project. Its just few clicks away


Of course, implementing this updater can take a while, but from my perspective, its mediocre between bad ones. If you have any problem, feel free to fork this project and edit it to your needs, or create pull request


###  1.1. <a name='BuiltWith'></a>Built With

* [TQDM](https://github.com/tqdm/tqdm)


##  2. <a name='GettingStarted'></a>Getting Started
This is an example of how to install and set up your content delivery to your customers. These steps might require some knowledge of Linux and firewall rules.

###  2.1. <a name='Prerequisites'></a>Prerequisites

Clone this repo and build it yourself or download executable from [releases](https://github.com/Stax124/Updater/releases)
* git
  ```sh
  git clone https://github.com/Stax124/Updater
  ```

###  2.2. <a name='Installation'></a>Installation

1. Set up your webserver ([get one free](https://www.oracle.com/cloud/))
   ```sh
   sudo apt install apache2
   ```
2. Upload all your files to webserver via **sftp** of similar _(don't forget to add Updater to root of your project, that will be used from clients machine for downloading updates)_
   ```sh
   cd /var/www/html/[your folder that will be used as mirror]
   put *
   ```
3. Download Linux executable from [releases](https://github.com/Stax124/Updater/releases) and put it on path (use ~ to store it)
   ```sh
   cd ~
   wget --no-check-certificate [link to executable from our releases]
   export PATH="[directory, where the executable is located]:$PATH"
   ```
4. Navigate to webserver folder and generate hashtable
   ```sh
   cd /var/www/html/[mirror folder]
   updater -g hashtable.hash [-e files_or_directories_to_exclude]
   ```
5. Open port **80** on both your webserver and router
6. Test if connection can be achieved


<!-- USAGE EXAMPLES -->
##  3. <a name='Usage'></a>Usage

Place snippets of code for your language into your projects

####  3.1. <a name='Python'></a>Python
```py
import os
os.system("updater -m http://example/mirror http://example/hashtable.hash -y")
```

####  3.2. <a name='Node.js'></a>Node.js
```js
const { exec } = require("child_process");

exec("updater -m http://example/mirror http://example/hashtable.hash -y", (error, stdout, stderr) => {
    if (error) {
        console.log(`error: ${error.message}`);
        return;
    }
    if (stderr) {
        console.log(`stderr: ${stderr}`);
        return;
    }
    console.log(`stdout: ${stdout}`);
});
```

####  3.3. <a name='Deno'></a>Deno
```js
const process = Deno.run({
  cmd: ["updater", "-m http://example/mirror http://example/hashtable.hash -y"]
});
```

####  3.4. <a name='C'></a>C++
```c++
#include <iostream>
using namespace std;

int update ()
{
    system("updater -m http://example/mirror http://example/hashtable.hash -y");
    return 0;
}
```

##  4. <a name='Contributing'></a>Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



##  5. <a name='License'></a>License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
##  6. <a name='Contact'></a>Contact

Tomáš Novák - tamoncz@gmail.com

Project Link: [https://github.com/Stax124/Updater](https://github.com/Stax124/Updater)
