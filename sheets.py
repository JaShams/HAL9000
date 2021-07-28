from googleapiclient.discovery import build
from google.oauth2 import service_account
from pprint import pprint

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of spreadsheet.
spreadsheet_id = '1klXV9Hr1qYu3P5Cj8FvmeQRWy8iA3OLZnvrIgzz9r0s'

service = build('sheets', 'v4', credentials=creds)

value_input_option = 'USER_ENTERED'
insert_data_option = 'INSERT_ROWS' 

StartCell = 'C'

def setSpreadsheetId(Id):
    global spreadsheet_id
    spreadsheet_id = Id

def exactCell(qnum,pnum):
    x = chr(ord(StartCell)+qnum)
    y = str(int(pnum)+1)
    return x+y

def quesCell(qnum):
    x = chr(ord(StartCell)+qnum)
    y = str(int(1)+1)
    return x+y

def exec(range_,value_range_body):
    sheet = service.spreadsheets()
    request = sheet.values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
    response = request.execute()

    pprint(response)

def insertAnswers(qnum,responses):
    range_ = 'Sheet1!' + quesCell(qnum)
    value_range_body = {
        "values" : [[i[qnum]] for i in responses]
    }
    exec(range_,value_range_body)
    

def createPlayers(players):
    range_ = 'Sheet1!A2'
    value_range_body = {
        "majorDimension" : "COLUMNS",
        "values" : [list(players.values()) ,list(players.keys())]
    }
    exec(range_,value_range_body)

def createHeader(total):
    range_ = 'Sheet1!C1'
    value_range_body = {
        "majorDimension" : "COLUMNS",
        "values" : [[i] for i in range(int(total))]
    }
    exec(range_,value_range_body)