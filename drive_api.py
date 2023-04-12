import gspread
import pandas as pd

def api_drive():
    client = gspread.service_account(filename='key/client-service-key.json')

    wb1 = client.open('city-transactions')
    wb2 = client.open('date-transactions')

    wb1_name = wb1.get_worksheet(0)
    wb2_name = wb2.get_worksheet(0)

    return wb1_name, wb2_name

if __name__ == '__main__':
    test = api_drive()
    print(pd.DataFrame(test[0].get_all_records()))