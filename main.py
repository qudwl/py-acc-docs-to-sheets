from __future__ import print_function


from get_auth import auth
from get_docs import get_data
from data_parser import convert_google_document_to_json
from data_reducer import reducer
from add_sheets import create_sheet, add_data_to_sheet

# The ID of a sample document.
DOCUMENT_ID = '142a2yhRqaEzMS2mcNBeiMH9FPQ_eGjedR59ilV1Apa0'


def main():
    creds = auth()
    document = get_data(creds, DOCUMENT_ID)
    if document is not None:
        data = reducer(convert_google_document_to_json(document))
        print(data.keys())
        title = document["title"]
        sp_id = create_sheet(creds, title)
        add_data_to_sheet(sp_id, creds, data)


if __name__ == '__main__':
    main()
