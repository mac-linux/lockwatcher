'''
Created on 5 Sep 2013

@author: Nia Catlin
'''
import smtplib, time, syslog, sys
import hashlib, hmac, os
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

import lwconfig
from lwconfig import config

#use a HMAC to prevent impersonation/replay
secret = bytes(lwconfig.HMAC_SECRET,'UTF-8')
def validHMAC(code,command):
            timenow = time.strftime('%d%m%Y%H%M') #day,month,year,hour,minute
            validTimes = (str(int(timenow)-1),timenow,str(int(timenow)+1)) #1 minute leeway
            
            validHashes = []
            for validTime in validTimes:
                validHashes = validHashes + [hmac.new(secret+bytes(str(command),'UTF-8'),bytes(validTime,'UTF-8'),hashlib.sha1)]
            
            validCodes = []
            for h in validHashes:
                smallDigest = h.hexdigest()
                validCodes = validCodes + [''.join([smallDigest[x].lower() for x in range(1,20,2)])]
            
            if code in validCodes:
                return True
            else:
                return False

def doSend(msg):
    try:
        s = smtplib.SMTP(lwconfig.EMAIL_SMTP_HOST)
        s.login(lwconfig.EMAIL_USERNAME, lwconfig.EMAIL_PASSWORD)
        s.sendmail(msg['To'],lwconfig.EMAIL_USERNAME, msg.as_string())
        syslog.syslog('connected to smtp server')       
    except InterruptedError:
        syslog.syslog('smtp connect error')
    except:
         syslog.syslog("Unexpected error: %s"%sys.exc_info()[0])
        
def sendEmail(subject,message,attachment=None):

    if attachment == None:
        msg = MIMEText(message)
    else:
        msg = MIMEMultipart()
        msg.attach( MIMEText(message) )
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(attachment,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment))
        msg.attach(part)
        
    msg['Subject'] = subject
    msg['From'] = config['EMAIL']['COMMAND_EMAIL_ADDRESS']
    msg['To'] = config['EMAIL']['ALERT_EMAIL_ADDRESS']
    
    try:
        doSend(msg)
        syslog.syslog('smtp: mail sent')   
    except:
        syslog.syslog('send failed')
    
        
    
        