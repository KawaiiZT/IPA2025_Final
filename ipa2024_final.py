#######################################################################################
# Yourname: Trisit Charoenparipat
# Your student ID: 66070069
# Your GitHub Repo: https://github.com/KawaiiZT/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.
from dotenv import load_dotenv
import time, os, requests, json
import restconf_final
from netmiko_final import gigabit_status
from ansible_final import showrun
from requests_toolbelt.multipart.encoder import MultipartEncoder 
#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
METHOD = None
#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.getenv("room_id")

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params={"roomId": roomIdToGetMessages, "max": 1},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"} 
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith("/66070069"):

        # extract the command
        command = message.split()[1]
        print(command)

# 5. Complete the logic for each command

        parts = message.strip().split()
        sid = parts[0][1:] if parts and parts[0].startswith("/") else ""

        command = parts[1].lower() if len(parts) > 1 else ""
        responseMessage = None

        if len(parts) == 2:
            if command == "restconf":
                METHOD = "restconf"
                responseMessage = "Ok: Restconf"
            elif command == "netconf":
                METHOD = "Netconf"
                responseMessage = "Ok: Netconf"
            elif command == "create":
                if METHOD is None:
                    responseMessage = "Error: No method specified"
                else:
                    responseMessage = "Error: No IP specified"
            elif command == "delete":
                responseMessage = "Error: No IP specified"
            else:
                if command == "gigabit_status":
                    result = gigabit_status()
                    responseMessage = result
                elif command == "showrun":
                    result = showrun()
                    responseMessage = result
                else:
                    responseMessage = "Error: No command found."

        elif len(parts) == 3:
            ip = parts[1]
            action = parts[2].lower()
            command = action

            if action == "create":
                if METHOD is None:
                    responseMessage = "Error: No method specified"
                elif METHOD.lower() == "restconf":
                    try:
                        responseMessage = restconf_final.create(ip, sid)
                    except Exception as e:
                        responseMessage = f"Error: {e}"
                elif METHOD.lower() == "netconf":
                    responseMessage = f"Interface loopback {sid} is created successfully using Netconf"
                else:
                    responseMessage = "Error: No method specified"
            else:
                responseMessage = "Error: No command found."
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail
        STUDENT_ID = os.getenv("STUDENT_ID", "66070069")
        ROUTER_NAME = os.getenv("ROUTER_NAME", "CSR1KV")  # ใช้ค่า router จาก .env

        if command == "showrun" and responseMessage == "ok":
            # ตั้งชื่อไฟล์ที่ playbook เซฟไว้ เช่น show_run_<studentID>_<router>.txt
            # สมมุติ router_name เอาเป็น CSR1KV-PodX-Y (คุณกำหนดใน playbook ให้ตรง)
            router_name = ROUTER_NAME   # แทน hardcode ด้วยค่าจาก .env
            filename = f"show_run_{STUDENT_ID}_{router_name}.txt"
            fileobject = open(filename, "rb")
            filetype = "text/plain"

            postData = {
                "roomId": roomIdToGetMessages,
                "text": "show running config",
                "files": (filename, fileobject, filetype),
            }
            postData = MultipartEncoder(postData)
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": postData.content_type,
            }
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=postData,
                headers=HTTPHeaders,
            )
            fileobject.close()
            if r.status_code != 200:
                raise Exception(f"Incorrect reply from Webex Teams API. Status code: {r.status_code}")

        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=json.dumps(postData),
                headers=HTTPHeaders,
            )
            if r.status_code != 200:
                raise Exception(f"Incorrect reply from Webex Teams API. Status code: {r.status_code}")
