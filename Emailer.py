import settings
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Emailer:
    def __init__(self):
        pass

    @staticmethod
    # TODO: send email sorted by most recent postings?
    def send_posts_email(newPosts: list, term: str, locations: list):
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls

        emailTo = 'ralphjgorham@gmail.com'

        capitalizer = lambda l: [city.capitalize() for city in l] # capitalize city names
        capitalizedCities = capitalizer(locations)

        body = ''

        for post in newPosts:
            print(post)
            body = body+post+"\n\n"

        msg = MIMEMultipart('alternative')
        msg['From'] = settings.EMAIL
        msg['To'] = emailTo
        msg['Subject'] = 'Subject: Craigslist Positions for {} queries in {}'.format(term, ', '.join(capitalizedCities))
        msg_text = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
        msg.attach(msg_text)
        
        text = msg.as_string()

        # Create a secure SSL context
        context = ssl.create_default_context()

        try:
            server = smtplib.SMTP(smtp_server, port) #Specify Gmail Mail server
            server.ehlo() #Send mandatory 'hello' message to SMTP server
            server.starttls(context=context)  #Start TLS Encryption
            server.login(settings.EMAIL, settings.PASSWORD)
            server.sendmail(settings.EMAIL, emailTo, text)

        except Exception as e:
            print(e)
        finally:
            server.quit()
            print('Emailing you new results')

    @staticmethod
    def send_reply_email(subject: str, reply_email: str='ralphjgorham@gmail.com'):
        # subject = "An email with attachment from Python"
        body = "To Whom It May Concern, \n \n \
            I have attached my resume with regards to the above Craigslist posting. You can access my portfolio as well at ralphjgorham.com. \
        Thank you for your time and consideration. I hope to hear from you soon. \n \n Best,\nRalph"
        sender_email = "imjustoneralph@gmail.com"

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = reply_email
        message["Subject"] = subject

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        filename = "resume.pdf"  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, settings.PASSWORD)
            server.sendmail(sender_email, reply_email, text)
            server.quit()
        print('Emailing Reply')


# if description contains 'to apply', dont send