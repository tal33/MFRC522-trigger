<a href="https://github.com/tal33/MFRC522-trigger/actions">
  <img alt="GitHub Actions status" src="https://github.com/tal33/MFRC522-trigger/workflows/test/badge.svg" />
</a>

# MFRC522-trigger

* trigger arbitrary action when the MFRC522 detects an NFC tag
* the MFRC522 is connected to a Raspberry Pi, for the wiring see [pirc522](https://github.com/ondryaso/pi-rc522#connecting)
* supported actions are
  * curling a URL
  * executing a command line
* This is just an experimental fork of [MFRC522-trigger from layereight](https://github.com/layereight/MFRC522-trigger/) to tailor it to my needs.
  For the time being I would recommend you use the original version instead of my fork. Big thanks to layereight for this nice implementation!
  Main modifications are
  * RGB status led (green when available, yellew when tag detected, red during startup/shutdown)
  * optimized for multiple tags all calling (parameterized) the same action by adding a tags.csv file and making the config provide templates (in my case every tag tells volumio to play a different playlist)
  * waiting for volumio availability during startup (configurable in config.json)
  * modified ansible deployment
    * no self-cloning of this repo
    * modifying /boot/userconfig.txt instead of /boot/config.txt as is recommended with volumio3
  * modified configuration
    * config.json now contains templates and not the tags itself
    * removed support for legacy configuration format
* MFRC522-trigger is based on [pirc522](https://github.com/ondryaso/pi-rc522) which is based on the famous 
[MFRC522-python](https://github.com/mxgxw/MFRC522-python)


# Prerequisites

* python3
* python modules RPi.GPIO, spidev, pi-rc522, assertpy
* enable the [SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) on the Raspberry Pi

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
dtoverlay=pi3-disable-bt
enable_uart=1
```
* reboot: `sudo reboot`

# Automated Installation

* all the steps from the manual installation can be done automatically
* automated installation is achieved by using [Ansible](https://docs.ansible.com/ansible/latest/index.html)
* Ansible is an automation tool, if you wanna know more about it have a look at 
  https://docs.ansible.com/ansible/latest/index.html
* install Ansible on your local machine https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
* The automated install assumes that you have a /boot/userconfig.txt that is included from /boot/config. This is the default-setup for volumio3 distributions. Otherwise add include userconfig.txt to the end of /boot/config.txt or modify ansible/MFRC522-trigger.yml to modify /etc/config instead od /etc/userconfig.txt
* on your local machine clone the repo https://github.com/layereight/MFRC522-trigger to a direcory named 'devel' (or adjust folder in MFRC522-trigger.yml)
```
$ mkdir devel
$ cd devel
$ git clone https://github.com/layereight/MFRC522-trigger.git
$ cd MFRC522-trigger/ansible
$ cp inventory my-inventory
$ vi my-inventory
```
* replace the contents of the file *inventory* to point to your music box (e.g. my_raspi_host)
* since this contains your password it is recommended that you *copy* inventory to a new file *my-inventory* (which is ignopred from git) so you don't accidentally push your settings
```
[my_pi]
my_raspi_host ansible_host=192.168.1.100 ansible_user=pi ansible_ssh_pass=raspberry
```
* execute the ansible playbook, it runs for roughly 10 minutes, so go grab a coffee ;-)
```
$ ansible-playbook -i my-inventory MFRC522-trigger.yml 

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

PLAY [Init MFRC522-trigger in devel directory] **************************************

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
* For every tag of yours add a line to tags.csv with 
  * first (tag): the unique id of that tag
  * second (template): id that defines what should be performed when this tag is detected or removed
    * the value corresponds to a tag-template name in config.json
  * third (param1): in the tag-template the string "<param1>" will be replaced by this value to customize the action of that template. For example specify the name of the playlist to play
* if you don't use volumio remove the "volumio" part from config.json

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
  "required": ["tag-templates"],
  "properties": {
    "volumio": {
      "type": "object",
      "title": "volumio configuration",
      "additionalProperties": false,
      "required": ["url", "startup-delay"],
      "properties": {
        "url": {
          "type": "string",
          "title": "base Url (without slash at the end) for volumio api",
          "format": "uri"
        },
        "startup-delay": {
          "type": "number",
          "title": "duration in seconds to wait after volumio api is ready to ensure volumio itself is ready",
          "format": "uri"
        }
      }
    },
    "tag-templates": {
      "type": "object",
      "title": "templates dictionary",
      "additionalProperties": false,
      "patternProperties": {
        "^.+$": {
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
  }
}


```

## Example configuration

<!-- embedme config.sample.json -->

```json
{
  "volumio": {
    "url": "http://localhost:3000",
    "startup-delay": 5
  },

  "tag-templates": {
    "volumio-play": {
      "name": "Volumio Playlist <param1>",
      "ondetect": [
        {
          "type": "curl",
          "url": "http://localhost:3000/api/v1/commands/?cmd=playplaylist&name=<param1>"
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
    "shutdown": {
      "name": "Shutdown (<param1>)",
      "ondetect": [
        {
          "type": "command",
          "command": "sudo shutdown -h now"
        }
      ]
    }
  }
}

```

## Example csv for tags

<!-- embedme tags.sample.csv -->

```csv
"tag","template","param1"
"123456789000","volumio-play","MyPlaylist"
"123456789001","shutdown",""
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
