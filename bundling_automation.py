import pandas as pd
import streamlit as st
import numpy as np
import requests
import json
import gspread as gs
from google.oauth2 import service_account



st.set_page_config('Bundling Automation',
                    page_icon= ':factory:',
                    layout= 'wide'
                    )

st.title(':orange[Bundling] Automation Service :factory:')


def get_dataframe_name(file):
    """
    Generates a name for the DataFrame based on the file name.
    """
    
    file_name = file.name.split(".")[0][:16]  # Get the file name without extension
    df_name = file_name.replace(" ", "_")  # Remove spaces and replace with underscores
    return df_name


def load_dataframe(file):
    """
    Loads the uploaded file into a Pandas DataFrame.
    """
    
    file_extension = file.name.split(".")[-1]

    if file_extension == "csv":
        df = pd.read_csv(file)
    
    elif file_extension == "xlsx":
        df = pd.read_excel(file)

    return df


def update_gs_byID_append(gs_ID, df_values, sheet_name):
    scope = ['https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/spreadsheets']

    # Creating the credentials variable to connect to the API
    credentials = service_account.Credentials.from_service_account_info(st.secrets['gcp_service_account'], scopes=scope)

    # Passing the credentials to gspread
    client = gs.authorize(credentials=credentials)

    # Opening Google sheet using the ID
    google_sheet = client.open_by_key(gs_ID)

    # Get the worksheet
    worksheet = google_sheet.worksheet(sheet_name)

    # Convert the DataFrame to a list of lists
    data = df_values.astype(str).values.tolist()

    # Find the last row with data
    last_row = len(worksheet.get_all_values())

    # Update the sheet by appending new rows
    for row in data:
        worksheet.append_row(row)



@st.cache_data
def get_bearer_token(user,password):
    user = user
    psswrd = password

    headers = {
    'authority': 'api.nabis.com',
    'accept': '*/*',
    'accept-language': 'es-ES,es;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://app.getnabis.com',
    'referer': 'https://app.getnabis.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }


    json_data = {
    'operationName': 'SignIn',
    'variables': {
        'input': {
            'email': user,
            'password': psswrd,
            },
        },
        'query': 'mutation SignIn($input: LoginUserInput!) {\n  loginUser(input: $input) {\n    token\n    user {\n      ...userFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment userFragment on User {\n  id\n  email\n  firstName\n  lastName\n  address1\n  address2\n  city\n  state\n  zip\n  phone\n  profilePicture\n  isAdmin\n  isDriver\n  driversLicense\n  __typename\n}\n',
    }   

    response = requests.post('https://api.nabis.com/graphql/admin', headers=headers, json=json_data)

    bearer_token = response.json()
    token = bearer_token['data']['loginUser']['token']
    
    return token


@st.cache_data
def create_headers(token):

    headers = {
    'authority': 'api.nabis.com',
    'accept': '*/*',
    'accept-language': 'es-ES,es;q=0.9',
    'authorization': 'Bearer '+ token,
    'content-type': 'application/json',
    'origin': 'https://app.getnabis.com',
    'referer': 'https://app.getnabis.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    return headers


st.cache()
def pricing_change(qb_invoice_data,pricing_amt,headers):
    json_data = {
        'operationName': 'UpdateOrder',
        'variables': {
            'input': {
                'id': qb_invoice_data["orderId"],
                'pricingFee': pricing_amt,
            },
            'isFromOrderForm': False,
        },
        'query': 'mutation UpdateOrder($input: UpdateOrderInput!, $isFromOrderForm: Boolean) {\n  updateOrder(input: $input, isFromOrderForm: $isFromOrderForm) {\n    changedOrder {\n      ...orderFragment\n      shipments {\n        ...shipmentFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment orderFragment on Order {\n  action\n  accountingNotes\n  additionalDiscount\n  adminNotes\n  createdAt\n  date\n  daysTillPaymentDue\n  paymentDueDate\n  totalAmountDue\n  requestedDaysTillPaymentDue\n  discount\n  distroFees\n  estimatedArrivalTimeAfter\n  estimatedArrivalTimeBefore\n  exciseTax\n  exciseTaxCollected\n  extraFees\n  gmv\n  gmvCollected\n  id\n  infoplus\n  internalNotes\n  irn\n  isArchived\n  manifestGDriveFileId\n  invoicesS3FileLink\n  name\n  notes\n  number\n  orgLicenseNum\n  paymentStatus\n  promotionsDiscount\n  siteLicenseNum\n  status\n  timeWindow\n  warehouseId\n  surcharge\n  mustPayPreviousBalance\n  nabisDiscount\n  issueReason\n  pricingFee\n  pricingPercentage\n  retailerConfirmationStatus\n  retailerNotes\n  creditMemo\n  netGmv\n  secondaryInfoplus\n  orderInventoryStatus\n  asnInventoryStatus\n  isEditableByBrand\n  isAtStartingStatus\n  shouldEnableOrderForm\n  isReceived\n  metrcWarehouseId\n  referrer\n  isSampleDemo\n  paymentTermsRequestStatus\n  brandManifestNotes\n  nabisManifestNotes\n  retailerManifestNotes\n  qrcodeS3FileLink\n  metrcManifestS3FileLink\n  isPrinted\n  isStaged\n  isCrossHubRetailTransfer\n  driverConfirmedAt\n  isSingleHubOrigin\n  firstShipmentId\n  lastShipmentId\n  lastNonReturnShipmentId\n  pickupDropoffWarehouseId\n  manufacturerOrgId\n  ACHAmountCollectedRetailer\n  ACHACRetailerUnconfirmed\n  ACHAmountPaidBrand\n  isExciseTaxable\n  orderLockdown {\n    ...orderLockdownFragment\n    __typename\n  }\n  mustPayExternalBalance\n  externalPaymentMin\n  externalPaymentDesired\n  externalPaymentNotes\n  __typename\n}\n\nfragment orderLockdownFragment on OrderLockdown {\n  id\n  createdAt\n  updatedAt\n  deletedAt\n  isArchived\n  orderEditLockdownTimestamp\n  isCreditMemoLocked\n  __typename\n}\n\nfragment shipmentFragment on Shipment {\n  id\n  orderId\n  originLicensedLocationId\n  destinationLicensedLocationId\n  status\n  stagingAreaId\n  isUnloaded\n  unloaderId\n  isLoaded\n  loaderId\n  arrivalTime\n  departureTime\n  isShipped\n  vehicleId\n  driverId\n  previousShipmentId\n  nextShipmentId\n  infoplusOrderId\n  infoplusAsnId\n  infoplusOrderInventoryStatus\n  infoplusAsnInventoryStatus\n  createdAt\n  updatedAt\n  shipmentNumber\n  queueOrder\n  isStaged\n  isPrinted\n  arrivalTimeAfter\n  arrivalTimeBefore\n  fulfillability\n  pickers\n  shipmentType\n  intaken\n  outtaken\n  metrcWarehouseLicenseNumber\n  __typename\n}\n',
    }

    response = requests.post('https://api.getnabis.com/graphql/admin', headers=headers, json=json_data)
    return response


st.cache()
def regenerate_inv_B(qb_invoice_data,headers):
    json_data = {
    'operationName': 'GenerateQuickbooksInvoice',
    'variables': {
        'input': {
            "orderId": qb_invoice_data["orderId"],
            "pricingPercentage": qb_invoice_data["pricingPercentage"],
            "pricingFee": qb_invoice_data["pricingFee"],
            "nabisDiscount": qb_invoice_data["nabisDiscount"],
            'invoiceTypesToGenerate': [
                'B',
            ],
        },
    },
    'query': 'mutation GenerateQuickbooksInvoice($input: GenerateQuickbooksInvoiceInput!) {\n  generateQuickbooksInvoice(input: $input) {\n    orderId\n    __typename\n  }\n}\n',
    }

    response = requests.post('https://api.getnabis.com/graphql/admin', headers=headers, json=json_data)
    return response


def all_admin_orders_accounting_page(order_number,headers):
    json_data = {
        "operationName": "AllAdminOrdersAccountingPage",
        "variables": {
            "pageInfo": {
                "numItemsPerPage": 25,
                "orderBy": [
                    {
                        "attribute": "date",
                        "order": "DESC",
                    },
                    {
                        "attribute": "createdAt",
                        "order": "DESC",
                    },
                ],
                "page": 1,
            },
            "search": order_number,
            "status": [
                "DELIVERED",
                "DELIVERED_WITH_EDITS",
                "DELAYED",
                "REJECTED",
                "ATTEMPTED",
            ],
        },
        "query": "query AllAdminOrdersAccountingPage($organizationId: ID, $search: String, $status: [OrderStatusEnum], $paymentStatus: [OrderPaymentStatusEnum], $disputeStatus: [OrderDisputeStatus!], $start: DateTime, $end: DateTime, $paymentProcessedAtStart: DateTime, $paymentProcessedAtEnd: DateTime, $paymentSentAtStart: DateTime, $paymentSentAtEnd: DateTime, $paidAtStart: DateTime, $paidAtEnd: DateTime, $irn: String, $orderFees: [String], $pageInfo: PageInfoInput, $collectionStatus: [BrandFeesCollectionCollectionStatusEnum]) {\n  viewer {\n    allAdminAccountingOrders(organizationId: $organizationId, search: $search, status: $status, irn: $irn, paymentStatus: $paymentStatus, disputeStatus: $disputeStatus, start: $start, end: $end, paymentProcessedAtStart: $paymentProcessedAtStart, paymentProcessedAtEnd: $paymentProcessedAtEnd, paymentSentAtStart: $paymentSentAtStart, paymentSentAtEnd: $paymentSentAtEnd, paidAtStart: $paidAtStart, paidAtEnd: $paidAtEnd, orderFees: $orderFees, pageInfo: $pageInfo, collectionStatus: $collectionStatus) {\n      results {\n        id\n        adminNotes\n        action\n        accountingNotes\n        ACHAmountCollectedRetailer\n        ACHAmountPaidBrand\n        internalNotes\n        createdAt\n        creditMemo\n        date\n        daysTillPaymentDue\n        distroFees\n        dueToBrand\n        discount\n        surcharge\n        edited\n        exciseTax\n        exciseTaxCollected\n        extraFees\n        gmv\n        gmvCollected\n        wholesaleGmv\n        priceDifference\n        irn\n        manifestGDriveFileId\n        apSummaryGDriveFileId\n        apSummaryS3FileLink\n        invoicesS3FileLink\n        packingListS3FileLink\n        mustPayPreviousBalance\n        nabisDiscount\n        name\n        notes\n        number\n        isSampleDemo\n        parentOrder {\n          id\n          totalGMV\n          shouldRemoveMinFee\n          __typename\n        }\n        paymentStatus\n        paymentTermsRequestStatus\n        hasSingleQBInvoice\n        hasMultiQBInvoices\n        hasMultiAQBInvoice\n        hasMultiBQBInvoice\n        hasMultiCQBInvoice\n        hasMultiC1QBInvoice\n        hasMultiC2QBInvoice\n        isAfterQuickbooksDeploy\n        lastPaymentTermOrderChange {\n          submitter {\n            id\n            firstName\n            lastName\n            isAdmin\n            __typename\n          }\n          id\n          description\n          createdAt\n          __typename\n        }\n        orderFees {\n          ...feeOrderFragment\n          __typename\n        }\n        pricingFee\n        pricingPercentage\n        basePricing {\n          pricingFee\n          pricingPercentage\n          __typename\n        }\n        status\n        creator {\n          id\n          email\n          firstName\n          lastName\n          __typename\n        }\n        licensedLocation {\n          ...licensedLocationFragment\n          __typename\n        }\n        organization {\n          id\n          doingBusinessAs\n          alias\n          name\n          owner {\n            id\n            email\n            firstName\n            lastName\n            __typename\n          }\n          __typename\n        }\n        site {\n          id\n          name\n          address1\n          address2\n          city\n          state\n          zip\n          pocName\n          pocPhoneNumber\n          pocEmail\n          licensedLocationId\n          licensedLocation {\n            id\n            __typename\n          }\n          __typename\n        }\n        paidAt\n        paymentMethod\n        remittedAt\n        factorStatus\n        calculateMoneyValues {\n          subtotal\n          orderDiscount\n          lineItemDiscounts\n          totalExciseTax\n          totalBalance\n          discountedSubtotal\n          taxRate\n          netOffTotal\n          __typename\n        }\n        nabisManifestNotes\n        referrer\n        orderFiles {\n          ...orderFileFragment\n          __typename\n        }\n        writeOffReasons\n        paymentSentAt\n        processingAt\n        ...lastAccountingOrderIssues\n        brandFeesCollection {\n          ...BrandFeesCollectionFragment\n          user {\n            id\n            firstName\n            lastName\n            email\n            __typename\n          }\n          __typename\n        }\n        willAutoRegenerateInvoices\n        __typename\n      }\n      pageInfo {\n        page\n        numItemsPerPage\n        orderBy {\n          attribute\n          order\n          __typename\n        }\n        totalNumItems\n        totalNumPages\n        __typename\n      }\n      nextOrders {\n        number\n        date\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment feeOrderFragment on OrderFee {\n  id\n  feeId\n  feeName\n  feePrice\n  feeNotes\n  createdBy {\n    firstName\n    lastName\n    email\n    __typename\n  }\n  fee {\n    ...feeFragment\n    __typename\n  }\n  __typename\n}\n\nfragment feeFragment on Fee {\n  id\n  basePrice\n  description\n  name\n  feeType\n  groupTag\n  startDate\n  endDate\n  isArchived\n  __typename\n}\n\nfragment licensedLocationFragment on LicensedLocation {\n  id\n  name\n  address1\n  address2\n  city\n  state\n  zip\n  siteCategory\n  lat\n  lng\n  billingAddress1\n  billingAddress2\n  billingAddressCity\n  billingAddressState\n  billingAddressZip\n  warehouseId\n  isArchived\n  doingBusinessAs\n  noExciseTax\n  phoneNumber\n  printCoas\n  hoursBusiness\n  hoursDelivery\n  deliveryByApptOnly\n  specialProtocol\n  schedulingSoftwareRequired\n  schedulingSoftwareLink\n  centralizedPurchasingNotes\n  payByCheck\n  collectionNotes\n  deliveryNotes\n  collect1PocFirstName\n  collect1PocLastName\n  collect1PocTitle\n  collect1PocNumber\n  collect1PocEmail\n  collect1PocAllowsText\n  collect1PreferredContactMethod\n  collect2PocFirstName\n  collect2PocLastName\n  collect2PocTitle\n  collect2PocNumber\n  collect2PocEmail\n  collect2PocAllowsText\n  collect2PreferredContactMethod\n  delivery1PocFirstName\n  delivery1PocLastName\n  delivery1PocTitle\n  delivery1PocNumber\n  delivery1PocEmail\n  delivery1PocAllowsText\n  delivery1PreferredContactMethod\n  delivery2PocFirstName\n  delivery2PocLastName\n  delivery2PocTitle\n  delivery2PocNumber\n  delivery2PocEmail\n  delivery2PocAllowsText\n  delivery2PreferredContactMethod\n  unmaskedId\n  qualitativeRating\n  creditRating\n  trustLevelNabis\n  trustLevelInEffect\n  isOnNabisTracker\n  locationNotes\n  infoplus\n  w9Link\n  taxIdentificationNumber\n  sellerPermitLink\n  nabisMaxTerms\n  __typename\n}\n\nfragment orderFileFragment on OrderFile {\n  id\n  type\n  s3Link\n  mimeType\n  notes\n  createdAt\n  updatedAt\n  orderId\n  __typename\n}\n\nfragment lastAccountingOrderIssues on AccountingOrder {\n  lastDispute {\n    id\n    reason\n    initiatedNotes\n    initiatedAt\n    issueType\n    resolvedAt\n    __typename\n  }\n  lastNonpayment {\n    id\n    reason\n    initiatedNotes\n    initiatedAt\n    issueType\n    __typename\n  }\n  __typename\n}\n\nfragment BrandFeesCollectionFragment on BrandFeesCollection {\n  id\n  createdAt\n  updatedAt\n  deletedAt\n  isArchived\n  submitterId\n  collectionStatus\n  collectionStatusUpdatedAt\n  notes\n  __typename\n}\n",
    }

    response = requests.post(
        "https://api.getnabis.com/graphql/admin", headers=headers, json=json_data
    )
    return response


def process_fee_amt_change(data,headers):
    
    fee_dict = dict(zip(data['Order'],data['Final Amt Fee']))
    
    for order in data['Order']:

        order_number = order
        order_data = all_admin_orders_accounting_page(order_number,headers)
        order_data = order_data.json()
        
      
        flat_fee_amt = fee_dict[order]
        

        qb_invoice_data = {
            "orderId": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['id'],
            "pricingPercentage": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['pricingPercentage'],
            "pricingFee": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['pricingFee'],
            "nabisDiscount": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['nabisDiscount'],
        }

        response = pricing_change(qb_invoice_data,flat_fee_amt,headers)
        if response.status_code == 200:
            st.write(f'{order} Processed')
        else:
            st.write(f'{order} failed, Status Code {response.status_code}')   


def regenerate(data,headers):

    list_orders = list(data['Order'])
    for order in list_orders:
        order_number = order
        order_data = all_admin_orders_accounting_page(order_number,headers)
        order_data = order_data.json()
        
         
        qb_invoice_data = {
            "orderId": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['id'],
            "pricingPercentage": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['pricingPercentage'],
            "pricingFee": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['pricingFee'],
            "nabisDiscount": order_data['data']['viewer']['allAdminAccountingOrders']['results'][0]['nabisDiscount'],
        }

        regenerate_inv_B(qb_invoice_data,headers)
        
        st.write(f'{order} Processed')



with st.form(key='log_in',):

    email = st.text_input('email:'),
    password_st = st.text_input('Password:',type='password')

    submitted = st.form_submit_button('Log in')

try:
    if submitted:

        user = email[0]
        password = password_st
        token = get_bearer_token(user,password)
        headers = create_headers(token)
        st.session_state['headers'] = headers
        
except:
    st.warning('Incorrect Email or Password, Try again')



if submitted:
    st.session_state['initialize'] = 'initialize'


if "initialize" not in st.session_state:
    st.write('Enter Your Credentials to Upload Files')
else:

    headers = st.session_state['headers']
    
    files = st.file_uploader('Upload Files to Process',accept_multiple_files=True)


    if files is not None:

        # Create a dictionary to store dataframes
        dataframes = {}

        # Iterate through each uploaded file
        for file in files:
            df_name = get_dataframe_name(file)
            df = load_dataframe(file)
            dataframes[df_name] = df

        col_names_sales = ['Order', 'Brand', 'Retailer', 'Delivery Date', 'Stop ID', 'Created At', 'Min Fee', 'Stop Subtotal Threshold Met?']
        col_names_brand = ['Order', 'Brand', 'Retailer', 'Delivery Date', 'Stop ID', 'Created At', 'Order Min Fee', 'Final Fee (Adjusted for Any Proration & Excluding Flat Order Fee)','Script Trigger']

      
        if len(dataframes) > 0:

            if 'table-data_Brand' in dataframes:
                df_Brand = dataframes['table-data_Brand'].copy()
                df_Brand = df_Brand[col_names_brand].copy()
                df_Brand.rename(columns={'Final Fee (Adjusted for Any Proration & Excluding Flat Order Fee)':'Final Amt Fee'}, inplace=True)
                df_Brand['Final Amt Fee'] = np.where(df_Brand['Script Trigger']== True, 0 ,df_Brand['Final Amt Fee'].round(2))
                df_Brand['Brand or Sales'] = 'Brand'
                df_Brand['Order'] = df_Brand['Order'].astype('str')
                st.dataframe(df_Brand)
                pricing_change_button = st.button('Pricing Change brand',key='pricing_change_brand')
                if pricing_change_button:
                    process_fee_amt_change(df_Brand,headers)

            if 'table-data_Sales' in dataframes:
                df_Sales = dataframes['table-data_Sales'].copy()
                df_Sales = df_Sales[col_names_sales].copy()
                df_Sales.rename(columns={'Min Fee': 'Order Min Fee', 'Stop Subtotal Threshold Met?': 'Script Trigger'}, inplace=True)
                df_Sales['Script Trigger'] = True
                df_Sales['Final Amt Fee'] = 0
                df_Sales['Brand or Sales'] = 'Sales'
                df_Sales['Order'] = df_Sales['Order'].astype('str')
                st.dataframe(df_Sales)
                pricing_change_button = st.button('Pricing Change Sales',key='pricing_change_sales')
                
                if pricing_change_button:
                    process_fee_amt_change(df_Sales,headers)

        st.markdown('***')
        st.text('Data Frame concatenated to regenerate invoices')

        if len(dataframes) >= 2:        
            bundling_dfs = pd.concat([df_Sales,df_Brand],ignore_index=True)
            bundling_dfs['Order'] = bundling_dfs['Order'].astype('str')
            st.dataframe(bundling_dfs)
            
        regenerate_invs = st.button('Regenerate Invoices',key='regenerate')
        send_to_google_sheets = st.button('Send to Google Sheets',key='google_sheets')

        if regenerate_invs:
            regenerate(bundling_dfs,headers)

        if send_to_google_sheets:
            #uploading data to google sheets
            update_gs_byID_append(st.secrets['gs_ID']['Bundling'],bundling_dfs,sheet_name='Data_processed')
    

st.markdown('---')
left_col,center_col,right_col = st.columns(3)

with center_col:
    st.title('**Powered by HQ**')
    st.image('https://www.dropbox.com/s/twrl9exjs8piv7t/Headquarters%20transparent%20light%20logo.png?dl=1')
