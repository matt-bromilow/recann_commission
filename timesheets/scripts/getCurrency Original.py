
def convertFile(fname):
    #ConvertCSVFormat - For use prior to file selection
    import pandas as pd
    import xlrd
    import re
    from forex_python.converter import CurrencyRates
    import numpy as np


    c = CurrencyRates()


    f = fname
    sheet = 'Report'
    df = pd.read_excel (f, skiprows=[0])
    print (df)

    USD = c.get_rate('GBP', 'USD')
    print("GOT USD")
    CURRENCY_MAPPING = {
        "$":"USD",
        "['£']": "GBP",
        "['kr']": "SEK",
        "['€']": "EUR",
        "['zł']": "EUR",
    "['CHF']":"CHF",
    "['лв']":"BGN",
    "['lei']":"RON",
        "[]":""
    }

    CURRENCY_VAL = {
        "['£']": 1,
        "['kr']": c.get_rate('GBP', 'SEK'),
        "['€']": c.get_rate('GBP', 'EUR'),
        "['zł']":c.get_rate('GBP', 'EUR'),
        "['$']": c.get_rate('GBP', 'USD'),
        "['CHF']":c.get_rate('GBP', 'CHF'),
        "['лв']":c.get_rate('GBP', 'BGN'),
        "['lei']":c.get_rate('GBP', 'RON'),
        "[]":""
    }

    book = xlrd.open_workbook(f, formatting_info=True)  
    sheet = book.sheet_by_index(0)
    paycurr=[]
    payval=[]
    for row_idx in range(2, sheet.nrows):
        xf_index = book.sheet_by_index(0).cell_xf_index(row_idx, 9)  
        xf = book.xf_list[xf_index]  
        fmt = book.format_map[xf.format_key]  
        curr =re.findall(r'"([^"]*)"', str(fmt.format_str))
        curr= str(curr)
        curr_str = CURRENCY_MAPPING[curr]
        curr_val = CURRENCY_VAL[curr]
        if len(curr)>2:
            paycurr.append(curr_str)
            payval.append(curr_val)
            
    print("paycurr")
    print( paycurr)
    print("payval")
    print(payval)
    df['pay_currency'] = paycurr
    df['pay_currency_fx'] = payval

    print(df.head)

    print("Changed Currencies")


    # In[17]:


    chgcurr=[]
    chgval=[]
    for row_idx in range(2, sheet.nrows):
        xf_index = book.sheet_by_index(0).cell_xf_index(row_idx, 11)  
        xf = book.xf_list[xf_index]  
        fmt = book.format_map[xf.format_key]  
        currz =re.findall(r'"([^"]*)"', str(fmt.format_str))
        currz= str(currz)
        currz_str = CURRENCY_MAPPING[currz]
        currz_val = CURRENCY_VAL[currz]
        if len(currz)>2:
            chgcurr.append(currz_str)
            chgval.append(currz_val)
            
    df['charge_currency'] = chgcurr
    df['charge_currency_fx'] = chgval


    # In[18]:


    #print(df.tail())

    print("UP TO ADD HHOURS")


    # In[19]:


    df['hours'] = df['EntryQuantity'] * np.where(df['Units']== 'Days', 8, 1)
    df['gross_pay_rate']=df['EntryQuantity'] *df['PayRate']
    df['gross_charge_rate']=df['EntryQuantity'] *df['ChargeRate']
    df['gross_pay_rate_gbp']=df['gross_pay_rate']/df['pay_currency_fx']
    df['gross_charge_rate_gbp']=df['gross_charge_rate']/df['charge_currency_fx']
    df['margin'] = df['gross_charge_rate_gbp']-df['gross_pay_rate_gbp']
    df['timesheet_key'] = pd.util.hash_pandas_object(df)
    df['id']=df['timesheet_key']
    print("ADDED ALL CALCS")


    # In[22]:


    df.rename(columns={"Date": "date", "Unnamed: 1": "job", "CompanyName": "company_name", "EntryQuantity":"entry_quantity","Units":"units", "PayRate":"pay_rate", "ChargeRate":"charge_rate",
                    "MarginSplitConsultantFullName":"employee", "MarginSplitPercent":"margins_plit",
                    },  inplace = True)
    print(df.head())
    df.to_csv('./output.csv')


    # In[23]:


  #  jdf = df

