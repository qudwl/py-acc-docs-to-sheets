from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def create_sheet(creds, title):
    try:
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet = {
            'properties': {
                "title": title
            }
        }

        spreadsheet = service.spreadsheets().create(
            body=spreadsheet, fields='spreadsheetId').execute()

        sp_id = spreadsheet.get('spreadsheetId')

        print(f"Spreadsheet ID: {sp_id}")

        requests = []
        requests.append({
            'addSheet': {
                'properties': {
                    'title': "Summary"
                }
            },
        })

        requests.append({
            'addSheet': {
                'properties': {
                    'title': "Success Criteria"
                }
            },
        })

        requests.append({
            'addSheet': {
                'properties': {
                    'title': "Findings"
                }
            },
        })

        requests.append({
            'deleteSheet': {
                'sheetId': 0
            }
        })

        body = {
            'requests': requests
        }

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=sp_id, body=body).execute()

        return sp_id

    except HttpError as err:
        print(err)


def add_data_to_sheet(sp_id, creds, data={"findings"}):
    value_input_option = "USER_ENTERED"
    values = []
    findings = data["findings"]
    print(type(findings))
    for i in range(0, len(data["findings"])):
        row = []
        row.append(data["findings"][i]["page"])
        row.append(data["findings"][i]["title"])
        row.append(data["findings"][i]["desc"])
        row.append(data["findings"][i]["rec"])
        row.append(data["findings"][i]["succ"])
        values.append(row)

    body = {
        'valueInputOption': value_input_option,
        'data': [
            {
                "range": "Summary!A1:B5",
                "values": [
                    ['Executive Summary', data["Executive Summary"]],
                    ["Browsers used", data["Browsers"].join(", ")],
                    ["AT used", data["Tools"].join(", ")],
                    ["URL", data["URL"]]
                ]
            },
            {
                "range": "Success Criteria!A1:A" + str(len(data["wcag"])),
                "values": data["wcag"]
            },
            {
                "range": "Findings!A1:E1",
                "values": ["Page", "Finding", "Description", "Recommendation", "Success Criteria"]
            },
            {
                "range": "Findings!A2:E" + str(len(data["findings"]) + 1),
                "values": values
            }
        ]
    }

    try:
        service = build('sheets', 'v4', credentials=creds)
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sp_id, body=body).execute()
    except HttpError as err:
        print(err)
