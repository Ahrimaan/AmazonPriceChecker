import requests
from bs4 import BeautifulSoup
import smtplib
import time
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
import datetime

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36 OPR/62.0.3331.72'}

with open(sys.argv[1],'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)
run = True
def check_price():
    url = config['product']['url']
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find(id="productTitle").get_text()
    amazonPrice = soup.find(id="priceblock_ourprice").get_text()
    convertedPrice = float(amazonPrice.replace('€','').replace(' ','').replace(',','.'))
    price = float(config['product']['desiredPrice'])
    print('Checking Price for : ', title.strip())
    print('Price is : ' , convertedPrice)
    if(convertedPrice <= price):
        send_mail(url,title,price)
        return True
    else:
        print('still too high :(')

    
    

def send_mail(url, product,price):
    server = smtplib.SMTP(config['maiLServer']['smtpAdress'], config['maiLServer']['smtpPort'])
    server.ehlo_or_helo_if_needed()
    if(config['maiLServer']['ttls'] == True):
        server.starttls()
    server.login(config['maiLServer']['username'],config['maiLServer']['password'])
    fromMail = config['mail']['from']
    toMail = config['mail']['to']
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Price for " + product + " has dropped"
    msg['From'] = fromMail
    msg['To'] = toMail
    html = """\
    <html>
        <head></head>
        <body>
            <p>Hi!<br>
            your price dropped to {price}<br>
            Visit <a href="{url}">link</a> you wanted.
            </p>
        </body>
    </html>
    """.format(price=price,url=url)
    msg.attach(MIMEText(html,'html'))
    server.sendmail(fromMail,toMail,msg.as_string())
    print('Email send')
    server.quit()

while(run):
    result = check_price()
    if(result != True and config['script']['periodicrun'] != False):
        waitMinutes = config['script']['periodictime']
        future = datetime.datetime.now() + datetime.timedelta(minutes = waitMinutes)
        print("Wating until " , future, " for next call")
        time.sleep(60 * waitMinutes)
    else:
        print('Stopping polling the Price')
        print('Goodbye, see you next time :)')
        run = False    
