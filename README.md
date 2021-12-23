<a href="https://github.com/layereight/MFRC522-trigger/actions">
  <img alt="GitHub Actions status" src="https://github.com/layereight/MFRC522-trigger/workflows/test/badge.svg" />
</a>

# MFRC522-trigger

* trigger arbitrary action when the MFRC522 detects an NFC tag
* the MFRC522 is connected to a Raspberry Pi, for the wiring see [pirc522](https://github.com/ondryaso/pi-rc522#connecting)
* supported actions are
  * curling a URL
  * executing a command line
* based on [pirc522](https://github.com/ondryaso/pi-rc522) which is based on the famous 
[MFRC522-python](https://github.com/mxgxw/MFRC522-python)

# Prerequisites

* python3
* python modules RPi.GPIO, spidev, pi-rc522, assertpy
* enable the [SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) on the Raspberry Pi

# Wiring from MFRC522 to Raspberry PI
For SPI0 (original version, bus=0)
* SDA: pin 24 (GPIO8, SPI0 CE0)
* SCK: pin 23 (GPIO11, SPI0 SCKL)
* MOSI: pin 19 (GPIO10, SPI0 MOSI)
* MISO: pin 21 (GPIO9, SPI0 MISO)
* IRQ: pin 18 (GPIO24)
* GND: pin 20 or 39 (GND)
* RST: pin 22 (GPIO25, RST)
* 3.3V: pin 17 (3.3V power)

For SPI1 (my version: bus=1, pin_irq=31)
* SDA: pin 12 (GPIO18, SPI1 CE1)
* SCK: Pin 40 (GPIO21, SPI1 SCKL)
* MOSI: pin 38 (GPIO20, SPI1 MOSI)
* MISO: pin 35 (GPIO19, SPI1 MISO)
* IRQ: pin 31 (GPIO6)
* GND: pin 20 or 39 (GND)
* RST: pin 29 (GPIO5, RST)
* 3.3V: pin 17 (3.3V power)
IRQ,RST,GND,power must not necessarily be moved for SPI1 but at least for my setup this was necessary

# Manual Installation

* ssh into your Raspberry Pi and execute
```
$ sudo apt-get update
$ sudo apt-get install python3 python3-pip vim
$ sudo pip3 install RPi.GPIO
$ sudo pip3 install spidev
$ sudo pip3 install pi-rc522
$ sudo pip3 install fastjsonschema==2.14.1
$ sudo pip3 install assertpy
```
* edit Raspberry Pi's */boot/config.txt*: `$ sudo vi /boot/config.txt`
* add the following lines somewhere in the file
```
dtparam=spi=on
dtoverlay=spi1-1cs  # only if you use SPI1
dtoverlay=pi3-disable-bt
enable_uart=1
```
* reboot: `sudo reboot`

# Automated Installation

* all the steps from the manual installation can be done automatically
* automated installation is achieved using [Ansible](https://docs.ansible.com/ansible/latest/index.html)
* Ansible is an automation tool, if you wanna know more about it have a look at 
  https://docs.ansible.com/ansible/latest/index.html
* install Ansible on your local machine https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
* on your local machine clone the repo https://github.com/layereight/MFRC522-trigger
```
$ git clone https://github.com/layereight/MFRC522-trigger.git
$ cd MFRC522-trigger/ansible
$ vi inventory
```
* replace the contents of the file *inventory* to point to your music box (e.g. my_raspi_host)
```
[my_pi]
my_raspi_host ansible_host=192.168.1.100 ansible_user=pi ansible_ssh_pass=raspberry
```
* execute the ansible playbook, it runs for roughly 10 minutes, so go grab a coffee ;-)
```
$ ansible-playbook -i inventory MFRC522-trigger.yml 

PLAY [Install prerequisite software] ************************************************

TASK [Run apt-get update if cache is older than a week] *****************************
ok: [my_raspi_host]

TASK [Install prerequisite debian packages] *****************************************
changed: [my_raspi_host]

TASK [Install prerequisite pip packages] ********************************************
changed: [my_raspi_host]

TASK [Install pi-rc522 python library] **********************************************
changed: [my_raspi_host]

PLAY [Prepare Raspberry Pi's /boot/config.txt] **************************************

TASK [Alter /boot/config.txt] *******************************************************
changed: [my_raspi_host]

TASK [Reboot the machine when /boot/config.txt was changed] *************************
changed: [my_raspi_host]

PLAY [Clone MFRC522-trigger from github] ********************************************

TASK [Create devel directory] *******************************************************
changed: [my_raspi_host]

TASK [Clone MFRC522-trigger from github] ********************************************
changed: [my_raspi_host]

TASK [Copy config.json from sample file] ********************************************
changed: [my_raspi_host]

PLAY [Install MFRC522-trigger as systemd service] ***********************************

TASK [systemd : Copy custom systemd service file] ***********************************
changed: [my_raspi_host]

TASK [systemd : Enable custom systemd service] **************************************
changed: [my_raspi_host]

TASK [systemd : Copy custom systemd service file] ***********************************
changed: [my_raspi_host]

TASK [systemd : Enable custom systemd service] **************************************
changed: [my_raspi_host]

TASK [systemd : Copy custom systemd service file] ***********************************
skipping: [my_raspi_host]

TASK [systemd : Enable custom systemd service] **************************************
skipping: [my_raspi_host]

PLAY RECAP **************************************************************************
my_raspi_host            : ok=13   changed=12   unreachable=0    failed=0

```

# Configuration

## JSON schema

<!-- embedme config/config.schema.json -->

```json
{
  "definitions": {
    "actions": {
      "type": "array",
      "title": "Actions to trigger when the tag with the given id is detected for the given event.",
      "items": {
        "oneOf": [
          {
            "type": "object",
            "title": "Curl action",
            "required": ["type", "url"],
            "additionalProperties": false,
            "properties": {
              "type": {
                "type": "string",
                "title": "Type of action. Must be 'curl'.",
                "pattern": "^curl$"
              },
              "url": {
                "type": "string",
                "title": "Url to curl when the tag is detected.",
                "format": "uri"
              }
            }
          },
          {
            "type": "object",
            "title": "Command line action",
            "required": ["type", "command"],
            "additionalProperties": false,
            "properties": {
              "type": {
                "type": "string",
                "title": "Type of action. Must be 'command'.",
                "pattern": "^command$"
              },
              "command": {
                "type": "string",
                "title": "Command to execute when the tag is detected."
              }
            }
          }
        ]
      }
    }
  },

  "type": "object",
  "title": "The root schema",
  "additionalProperties": false,
  "patternProperties": {
    "^[0-9]+$": {
      "type": "object",
      "title": "Schema holding name and actions for a tag",
      "required": ["name", "ondetect"],
      "additionalProperties": false,
      "properties": {
        "name": {
          "type": "string",
          "title": "Alias name for the tag with the given id."
        },
        "ondetect": { "$ref": "#/definitions/actions" },
        "onremove": { "$ref": "#/definitions/actions" },
        "onredetect": { "$ref": "#/definitions/actions" }
      }
    }
  }
}

```

## Example configuration

<!-- embedme config.sample.json -->

```json
{
  "1234567890123": {
    "name": "A very nice tag, triggering 2 actions: playing a playlist and setting the volume.",
    "ondetect": [
      {
        "type": "curl",
        "url": "http://localhost:3000/api/v1/commands/?cmd=playplaylist&name=my_playlist_1"
      },
      {
        "type": "curl",
        "url": "http://localhost:3000/api/v1/commands/?cmd=volume&volume=40"
      }
    ]
  },
  "9876543210987": {
    "name": "An even nicer tag",
    "ondetect": [
      {
        "type": "curl",
        "url": "http://localhost:3000/api/v1/commands/?cmd=playplaylist&name=my_playlist_2"
      }
    ],
    "onremove": [
      {
        "type": "curl",
        "url": "http://localhost:3000/api/v1/commands/?cmd=pause"
      }
    ],
    "onredetect": [
      {
        "type": "curl",
        "url": "http://localhost:3000/api/v1/commands/?cmd=play"
      }
    ]
  },
  "5432109876543": {
    "name": "This tag is also nice",
    "ondetect": [
      {
        "type": "command",
        "command": "sudo shutdown -h now"
      }
    ]
  }
}
```

# Roadmap

* quit with error when config is broken
* more python unit tests
* Ansible playbook: set volumio logging level to error to reduce cpu load on Raspberry Pi Zero
* document logging.ini
* play beep sound when rfid tag is detected
* OTA updates

# Roadmap done

* validate config with JSON schema and log a warning when it's invalid
* multiple actions per event
* python unit tests
* githup actions ci
* document Ansible playbook
* command actions: execute a system command as action
* migrate to python3
* toggle actions: execute the same action when a rfid tag is removed from the reader and re-detected
* action on tag remove event
* action on tag re-detected event
* document config.json

# Inspiration

* https://github.com/MiczFlor/RPi-Jukebox-RFID
* https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/5

# Links

* https://github.com/ondryaso/pi-rc522
* http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio
* https://howchoo.com/g/mwnlytk3zmm/how-to-add-a-power-button-to-your-raspberry-pi
* https://howchoo.com/g/ytzjyzy4m2e/build-a-simple-raspberry-pi-led-power-status-indicator
* https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/master/scripts/installscripts/stretch-install-default.sh#L468
* https://volumio.org/forum/245-does-not-boot-with-enable-uart-t7194.html
* http://blog.mmone.de/2017/05/16/raspberry-pi-zero-w-disable-bluetooth/
* https://github.com/miguelbalboa/rfid
* http://praktische-elektronik.dr-k.de/Praktikum/Analog/Le-LED-Schaltungen.html
