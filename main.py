import json

import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

def lambda_handler(event, context):

    # TODO: Hardcode my owner id to use
    properties = get_properties('7b6db613-31a4-4b42-8b8b-91c11ebecb5d')

    for property in properties:
        try:
            print(property)

            # Process payment for each property
            process_payment(property)

            # Send success notification
            send_notification('success', property)


        except Exception as e:
            # Handle error and send notifications
            send_notification('error', property, str(e))
            print(e)

def get_properties(client):

    json_obj = [ { "account_id": "0044672", "billingInformation": { "billingAddressLine1": "134 Wakeman Ave", "billingAddressLine2": "", "cardholderFirstName": "Kevin", "cardholderLastName": "Dowdy", "city": "Newark", "contactPhoneNumber": "9175643523", "emailAddress": "kommunityworks.noreply@gmail.com", "state": "New Jersey", "zipCode": "07104" }, "ownerId": "7b6db613-31a4-4b42-8b8b-91c11ebecb5d", "paymentInformation": { "accountNumber": "381066650126", "checkType": "Checking", "paymentMethod": "Echeck", "routingNumber": "021200339" } }, { "account_id": "0005917", "billingInformation": { "billingAddressLine1": "134 Wakeman Ave", "billingAddressLine2": "", "cardholderFirstName": "Kevin", "cardholderLastName": "Dowdy", "city": "Newark", "contactPhoneNumber": "9175643523", "emailAddress": "kommunityworks.noreply@gmail.com", "state": "New Jersey", "zipCode": "07104" }, "ownerId": "7b6db613-31a4-4b42-8b8b-91c11ebecb5d", "paymentInformation": { "accountNumber": "381066650058", "checkType": "Checking", "paymentMethod": "Echeck", "routingNumber": "021200339" } } ]

    return json_obj

def process_payment(property):

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)


    try:
        # Open the payment page
        driver.get('https://payments.ci.newark.nj.us/OnlinePayment_WaterDepartment.aspx')
        time.sleep(2)

        # TODO: Get the page's HTML content
        html_content = driver.page_source

        # TODO: Print the HTML content
        print("page one")
        # print(html_content)

        # Enter account ID into the form and submit
        driver.find_element(By.ID, 'ContentPlaceHolder1_AccountID').send_keys(property['account_id'])
        driver.find_element(By.ID, 'ContentPlaceHolder1_btnFindAccounts').click()
        time.sleep(3.7)

        # TODO: Get the page's HTML content
        html_content = driver.page_source

        # TODO: Print the HTML content
        print("page two")
        # print(html_content)

        # Get the element containing the message
        message_element = driver.find_element(By.ID, 'ContentPlaceHolder1_divHeaderMessage')

        # Check if it contains the substring "1 record found"
        if "1 records found" not in message_element.text.lower():
            raise Exception("No records found for account")
        else:
            print("1 record found message is present.")

        select_element = driver.find_element(By.XPATH, "//a[contains(@href, '__doPostBack') and contains(@href, 'Select$0')]")
        select_element.click()
        time.sleep(2.2)

        # TODO: Get the page's HTML content
        html_content = driver.page_source

        # TODO: Print the HTML content
        print("page three")
        # print(html_content)

        # Press pay online button
        driver.find_element(By.ID, 'ContentPlaceHolder1_btnPayOnline').click()
        time.sleep(2.5)

        # TODO: Get the page's HTML content
        html_content = driver.page_source

        # TODO: Print the HTML content
        print("page four")
        # print(html_content)

        print(property)

        # Get the balance
        # Locate the input element by its ID
        payment_element = driver.find_element(By.ID, "ApiBillPay_PaymentAmount")

        # Get the value attribute of the input element
        balance = payment_element.get_attribute("value")

        print("Current balance: " + str(type(balance)))

        if float(balance) > 300.00:
            raise Exception('Balance exceeds maximum allowed payment')
        if float(balance) <= 0.00:
            raise Exception('No balance')

        # Proceed with payment
        # Locate the payment method element by its ID
        select_element = driver.find_element(By.ID, 'SelectedPaymentMethod')
        select = Select(select_element)
        select.select_by_value(property['paymentInformation']['paymentMethod'])

        # Locate the Check type by its ID
        select_element = driver.find_element(By.ID, 'EcheckObj_AccountType')
        select = Select(select_element)
        select.select_by_value('1')

        # Input the Bank Routing Number by its ID
        driver.find_element(By.ID, 'EcheckObj_BankRoutingNumber').send_keys(property['paymentInformation']['routingNumber'])

        # Input the Account Number by its ID
        driver.find_element(By.ID, 'EcheckObj_BankAccountNumber').send_keys(property['paymentInformation']['accountNumber'])

        # Input the Confirm Account Number by its ID
        driver.find_element(By.ID, 'EcheckObj_BankAccountNumberConfirm').send_keys(property['paymentInformation']['accountNumber'])

        # Input the Account Holder's First Name by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_FirstName').send_keys(property['billingInformation']['cardholderFirstName'])

        # Input the Account Holder's Last Name by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_LastName').send_keys(property['billingInformation']['cardholderLastName'])

        # Input the Account Holder's Address Line 1 by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_Address1').send_keys(property['billingInformation']['billingAddressLine1'])

        # Input the City by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_City').send_keys(property['billingInformation']['city'])

        # Input the State by its ID
        select_element = driver.find_element(By.ID, 'EcheckObj_Payer_UsState')
        select = Select(select_element)
        select.select_by_value('NJ')

        # Input the Zip Code by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_UsZipcode').send_keys(property['billingInformation']['zipCode'])

        # Input the Contact Phone Number by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_UsPhoneNumber').send_keys(property['billingInformation']['contactPhoneNumber'])

        # Input the Email Address by its ID
        driver.find_element(By.ID, 'EcheckObj_Payer_EmailAddress').send_keys(property['billingInformation']['emailAddress'])

        # TODO: Get the page's HTML content
        html_content = driver.page_source

        # TODO: Print the HTML content
        print("page five")
        # print(html_content)

        # Press pay online button
        driver.find_element(By.ID, 'Continue').click()
        time.sleep(2.2)

        # TODO: Get the page's HTML content
        html_content = driver.page_source

        # TODO: Print the HTML content
        print("page six")
        print(html_content)

        # Press pay online button
        driver.find_element(By.ID, 'submitprocess').click()
        time.sleep(15)

        # Locate the <div> element by its class name
        div_element = driver.find_element(By.CLASS_NAME, 'validation-summary-errors')

        # Check if there are any errors with the payment
        if div_element:
            # Extract the message inside the <li> tag
            li_elements = div_element.find_elements(By.TAG_NAME, 'li')
            raise Exception('Payment processing error ' + str(li_elements))
        else:
            print("Successfully processed payment")

    finally:
        driver.quit()

def send_notification(status, property, error_message=''):
    if status == 'success':
        message = f"Payment successful for property {property['billingInformation']['billingAddressLine1']}"
    else:
        message = f"Error processing payment for property {property['billingInformation']['billingAddressLine1']}: {error_message}"

    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:975050035941:water-bill-payment-tool-notifications',
        Message=message
    )

if __name__ == "__main__":
    lambda_handler("", "")
