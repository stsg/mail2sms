#!/usr/bin/env python
# -* coding: utf-8 -*-

import sys
import os
import logging
import smtplib
import string
from email.parser import Parser

from config import *


class SMSBot(object):

    def __init__(self, mailto, mailfrom, mailhost, msg, logfile=None):
        self.home = os.environ['HOME']
        self.mailto = mailto
        self.mailfrom = mailfrom
        self.mailhost = mailhost
        self.mailsubj = 'XXXXXXXXXXX'
        self.comingfrom = ''
        self.rawmessage = ''
        self.message = self.decode_email(msg)
        self.log = self.setlogging(self.home + '/' + logfile)

    def setlogging(self, logfile=None):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(process)d - %(levelname)s - %(message)s')
        if logfile:
            filelevel = logging.INFO
            fh = logging.FileHandler(logfile)
            fh.setLevel(filelevel)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger

    def decode_email(self, msg_str):
        p = Parser()
        msg = p.parsestr(msg_str)
        for part in msg.walk():
            charset = part.get_content_charset()
            if not charset:
                charset = 'utf-8'
            if part.get_content_type() == 'text/plain':
                part_str = part.get_payload(decode=1)
                self.rawmessage += part_str.decode(charset)
        self.rawmessage.strip()
        self.rawmessage = ' '.join(self.rawmessage.split())
        self.rawmessage = self.rawmessage[0:153]
        self.mailsubj = msg['subject']
        self.comingfrom = msg['from']

        return string.join((
            "From: %s" % self.mailfrom,
            "To: %s" % self.mailto,
            "Subject: %s" % self.mailsubj,
            "",
            self.rawmessage), "\r\n").encode('utf-8')

    def sendemail(self):
        server = smtplib.SMTP(self.mailhost)
        # server.set_debuglevel(1)
        server.sendmail(self.mailfrom, self.mailto, self.message)
        server.quit()

if __name__ == '__main__':

    message = ''
    for line in sys.stdin.readlines():
        message += line

    sms = SMSBot(
                 smsgate['mailto'],
                 smsgate['mailfrom'],
                 smsgate['mailhost'],
                 message,
                 'smsbot.log'
                )
    sms.log.info('SMS bot started')
    sms.log.info('Message from: %s' % sms.comingfrom)
    sms.log.info('Message to: %s' % sms.mailsubj)
    sms.log.info('Message length: %s' % len(sms.rawmessage))
    sms.log.info('Message text:\n%s' % sms.rawmessage)
    sms.sendemail()
    sms.log.info('SMS bot ended')
