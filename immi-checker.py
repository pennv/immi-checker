# USER INFO AND CONFIG


# Immi credentials
immi_username = 'example@gmail.com'
immi_passwd = 'abc123'
# Sequence of the target visa application
seq = 1
# Frequency to check, by second
t = 30
# Time to pause checking
t_p = 19
# Time to resume checking
t_r = 7

# SMTP credentials
mail_sender_addr = 'example@gmail.com'
mail_sender_passwd = 'qwe234'
mail_recipient_addr = 'recipient@gmail.com'
mail_smtp_addr = 'smtp.gmail.com'
mail_smtp_port = 465
# Mail contents
mail_finalised_msg_subject = '! ! ! ! ! !'
mail_finalised_msg_body = ''
mail_updated_msg_subject = 'Immi Status Updated'
mail_updated_msg_body = ''


# SCRIPT


import requests, smtplib, time
from bs4 import BeautifulSoup
from datetime import datetime
from email.message import EmailMessage

# Immi URL
immi_url = 'https://online.immi.gov.au/lusc/login'


def check_immi():

    while True:

        try:

            # If now is the right time to start
            now = int(datetime.now().strftime('%H'))
            if (now < t_r) | (now > t_p):
                log('Sleep')
                time.sleep(t)
                continue

            # A session for all requests to share the same cookies
            s = requests.Session()

            # GET immi LOGIN page
            login_page = s.get(immi_url)

            # Capture session-unique param "wc_t"
            login_soup = BeautifulSoup(login_page.content, 'html.parser')
            wc_t = login_soup.find('input', {'name':'wc_t'})['value']

            # POST LOGIN form to get to CONTINUE page
            s.post(immi_url, data = {'password': immi_passwd, 'username': immi_username, 'wc_t': wc_t, 'wc_s': '1', 'login': 'x'})

            # POST CONTINUE form to get to APP page
            app_page = s.post(immi_url, data = {'wc_t': wc_t, 'wc_s': '2', 'continue': 'x'})
            app_soup = BeautifulSoup(app_page.content, 'html.parser')

            # Determine status of the application
            status = app_soup.find_all('strong')[seq - 1].get_text()
            log(status)
            if status == 'Received':
                time.sleep(t)
                continue
            # Send out notification
            if status == 'Finalised':
                 sendEmail(mail_finalised_msg_subject, mail_finalised_msg_body)
            else:
                sendEmail(mail_updated_msg_subject + ' - ' + status, mail_updated_msg_body)
            break

        except Exception as e:
            print(repr(e))
            # Send out notification
            sendEmail('Server Down', repr(e))
            break


def sendEmail(msg_subject, msg_body):

    # Set up mail server
    mail_server = smtplib.SMTP_SSL(mail_smtp_addr, mail_smtp_port)
    mail_server.ehlo()
    mail_server.login(mail_sender_addr, mail_sender_passwd)

    # Create message
    msg = EmailMessage()
    msg.set_content(msg_body)
    msg['Subject'] = msg_subject
    msg['From'] = mail_sender_addr
    msg['To'] = mail_recipient_addr
    mail_server.send_message(msg)
    mail_server.quit()


def log(status):
    f = open('./immi_log', 'a')
    now = datetime.now().strftime('%d/%m/%y %H:%M:%S')
    f.write(now + ' - ' + status + '\n')
    f.close()


def main():
    check_immi()


if __name__ == "__main__":
    main()
