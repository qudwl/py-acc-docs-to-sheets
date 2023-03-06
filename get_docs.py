from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_data(creds, DOCUMENT_ID):
    doc_content = None
    try:
        service = build('docs', 'v1', credentials=creds)
        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        doc_content = document
    except HttpError as err:
        print(err)
        return None

    return document
