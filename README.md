
# Device Onboarding
Onboard personal devices to a new org!

This application allows you to configure local device admins, a new macro + UI extension, as well as make configuration changes the first time a device appears in your org.  Currently, this application is configured to work only for newly activated personal mode devices in the org.

<!-- ![image/gif](insert img link here) -->


## Overview

This application uses Cloud xAPI commands to set user permissions and make configuration changes for new personal mode devices.  This application will also spin up a headless browser subprocess using [Playwright](https://playwright.dev/python/docs/library) in order to configure things like a macro and UI extension, because the Cloud xAPI commands for those features do not work for personal mode devices.  This limitation means that the personal mode devices must be on the same network or are otherwise accessible to this application.



### Flow Diagram

TBD
<!-- ![image/gif](insert img link here) -->



## Setup

### Prerequisites & Dependencies: 

1. A Webex Service App is required.  You can create a Service App [here](https://developer.webex.com/my-apps/new).  
+ Give it any name, icon, and description.  
+ The following scopes must be selected at minimum:  
```
spark:devices_read
spark:devices_write
spark:xapi_statuses
spark:xapi_commands
spark-admin:devices_read
spark-admin:devices_write
```
+ You will then need to request authorization for the Service App to run in your org.  Your org admin can enable the Service App under Integrations in Control Hub.  
+ Once the Service App is authorized, you can generate a token using your Client Secret.  Regenerate the Client Secret if you do not have it saved (and **save it somewhere safe for step 4**)
![generate-token](https://user-images.githubusercontent.com/19175490/236936890-fbf9dc4b-8305-4545-9629-71196dc1e528.png)
+ Generate a new token.  You can ignore the Authorization Token, but please **save the client_id, client_secret, and REFRESH token values somewhere safe for step 4**.


2. Whether you are building from source or simply running the executable, you will need to add a folder named ```config_files``` and a file named ```.env``` to the root directory where ```main.exe``` or ```main.py``` exists.  

![source](https://user-images.githubusercontent.com/19175490/236932847-e81c63a8-b02e-471d-b381-67a964bbd2e0.PNG)
or
![dist](https://user-images.githubusercontent.com/19175490/236932846-03f821a2-e56c-4906-bfc8-3bdc95ca8b0a.PNG)

3. The ```config_files``` folder contents should appear like so:  
![config](https://user-images.githubusercontent.com/19175490/236932844-1de42785-3542-4080-ae30-6743cb7a5350.PNG)
+ 1 macro file (a .js file)  
+ 1 UI Extensions file (.xml file)  
+ 1 Device Config File (.csv)

Only 1 of each file type is expected in this folder. Additional macros, ui extensions, or config files may cause unexpected results.

The folder called ```devices``` inside of the ```config_files``` folder will be generated automatically on the first run.  **Deleting the ```devices``` folder or its contents will cause the application's next run to be treated like it is being run for the first time.**

4. The ```.env``` file must contain the following lines:
```
MY_WEBEX_CLIENT_ID=
MY_WEBEX_SECRET=
MY_WEBEX_REFRESH_TOKEN=

ADMIN_ACCOUNT_PASSWORD=avalidadminpassword

SECONDARY_USERNAME=someuser
SECONDARY_ACCOUNT_PASSWORD=avaliddevicepassword
```

```MY_WEBEX_CLIENT_ID, MY_WEBEX_SECRET, MY_WEBEX_REFRESH_TOKEN``` will need to be the values that you stored from step ```1```.

```ADMIN_ACCOUNT_PASSWORD``` will change the device's local ```admin``` account password.  ```SECONDARY_USERNAME``` and ```SECONDARY_ACCOUNT_PASSWORD``` will be a new local admin account setup on the device.

5. If you already have the ```main.exe``` file and are not planning to run or build from source, you can skip **Installation Steps** and proceed to the **Execution Steps** section.

### Installation Steps: if building the executable or running from source
+ python >= v3.8.1
```
pip install aiohttp
pip install python-dotenv
pip install playwright
playwright install
```

#### Required only if building the executable    
```
pip install pyinstaller
```
```
set PLAYWRIGHT_BROWSERS_PATH=0
```
```
pyinstaller --onefile -F main.py
```
If you want to build in PowerShell or Bash, instead of Batch, follow the instructions [here](https://playwright.dev/python/docs/library#pyinstaller).

### Execution Steps

#### Notes Before Your First Execution
The first time the process runs, it will retrieve all devices in the org.  It will save all personal mode video devices to a new file: ```path/to/your_version/config_files/devices/list.csv```

Any devices in this list will not be "on-boarded." In other words, no changes will be made to any devices that already exist in the org at the time of the first run.  **Any personal mode devices that appear in the org for the first time after ```list.csv``` has been created will be modified.**

If you wish to on-board a device that exists in ```list.csv```, perhaps as a test, then you will need to manually open ```list.csv``` and delete the line for the device you wish to on-board (and save the file).  The next time you start the process, it will see the device in the org, but missing from  ```list.csv```, and therefore the device is considered new and it will be modified.

Please ensure you make any changes to the ```list.csv``` very carefully.  Corrupting this file could cause unintended results.

#### Run
**Open a command prompt or terminal.**  If you simply double click the process, the command prompt will close if it reaches any unexpected errors, and you will **not see the reason for the failure**.

Once you have opened a terminal, if running from source navigate to the source directory, then run:  
```python main.py```

If you are running the executable instead, you can simply enter it by name.  
![main.exe](https://user-images.githubusercontent.com/19175490/236932882-30a17fd0-4d94-4ad9-b310-c02fc7c40c87.PNG)

    
## Demo
*For more demos & PoCs like this, click [here](https://github.com/wxsd-sales).

<!-- [![Your Video Title ](assets/peer_support_main.PNG)](https://www.youtube.com/watch?v=SqZhiC8jHhU&t=10s, "<insert demo name here>") -->


## License
All contents are licensed under the MIT license. Please see [license](LICENSE) for details.


## Disclaimer
Everything included is for demo and Proof of Concept purposes only. Use of the site is solely at your own risk. This site may contain links to third party content, which we do not warrant, endorse, or assume liability for. These demos are for Cisco Webex usecases, but are not Official Cisco Webex Branded demos.


## Questions
Please contact the WXSD team at [wxsd@external.cisco.com](mailto:wxsd@external.cisco.com?subject=RepoName) for questions. Or, if you're a Cisco internal employee, reach out to us on the Webex App via our bot (globalexpert@webex.bot). In the "Engagement Type" field, choose the "API/SDK Proof of Concept Integration Development" option to make sure you reach our team. 
