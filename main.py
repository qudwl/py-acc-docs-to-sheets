from __future__ import print_function


from get_auth import auth
from get_docs import get_data

# The ID of a sample document.
DOCUMENT_ID = '142a2yhRqaEzMS2mcNBeiMH9FPQ_eGjedR59ilV1Apa0'


def main():
    creds = auth()
    document = get_data(creds, DOCUMENT_ID)
    if document is not None:
        for i in range(0, len(document)):
            print(document[i].get('paragraph').)


if __name__ == '__main__':
    main()
