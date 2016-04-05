#!/usr/bin/python3
"""
The annoyer.py repeatedly sends E-Mails to remind people to do something.
Copyright © 2016 Janosch Deurer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This program sends reminder mails with an increasing frequency to remind people
to do something. The E-Mail itself as well as the frequency are configurable
for each mail seperately. Please have a look into the template_mail file.

Author: Janosch Deurer
E-Mail: janosch.deurer@geonautik.de

The script uses the python3 smtplib. It assumes that you have configured a
mailserver on the machine your are executing the script.  The script can be
executed with:
    ./annoyer.py <level>


Dependencies:
    The script is witten in python 3 it was tested with python 3.4.3.
    It furthermore assumes that a mailserver is running such that the python3
    smtplib works.
"""


import logging
import smtplib
import datetime
import sys
import os
import shutil
from email.mime.text import MIMEText

"""
In this section all configurations for the script are made
"""

# Specifies the sender of the e-mail
MAIL_FROM = 'janosch.deurer@geonautik.de'

# Configure the loglevel here
LOGLEVEL = logging.DEBUG

class EMail(object):

    """Docstring for EMail. """

    def __init__(self, file_path, level):
        """TODO: to be defined1. """
        self.recipients = []
        self.max_mail_on_level = -2
        self.level = level
        self.next_level = ""
        self.subject = ""
        self.mail_text = ""
        self.file_path = file_path
        self.logdir = os.path.join(os.path.pardir, "log", self.file_path)

    def load_file(self):
        """TODO: Docstring for load_file.
        :returns: TODO

        """
        with open(self.file_path, "r") as email_file:
            in_email_text = False
            for line in email_file:
                print(line)

                if line.startswith("{{mailtext}}"):
                    in_email_text = not in_email_text

                if in_email_text:
                    self.mail_text += line.replace("{{mailtext}}", "")

                if line.endswith("{{mailtext}}\n"):
                    # Prevent that in_email_text is toggled twice when only
                    # identifyer is in the line
                    if line == "{{mailtext}}\n":
                        continue
                    in_email_text = False
                    logging.debug(self.mail_text)
                    continue

                if line.startswith("{{reciepient}}"):
                    address = line.split()[1]
                    self.recipients.append(address)
                    logging.debug(self.recipients)
                    continue

                if line.startswith("{{intervall}}"):
                    if line.split()[1] == self.level:
                        self.max_mail_on_level = int(line.split()[2])
                        logging.debug(self.max_mail_on_level)
                        if self.max_mail_on_level != -1:
                            self.next_level = line.split()[3]
                    continue

                if line.startswith("{{subject}}"):
                    self.subject = line.replace("{{subject}} ", "")
                    logging.debug(self.subject)
                    continue



        if self.mail_text.startswith(" "):
            self.mail_text = self.mail_text[1:]
            logging.debug(self.mail_text)

    def send(self):
        """TODO: Docstring for send_mail.
        :returns: TODO

        """
        # for recipient in self.recipients:
        #     write_email(self.mail_text, self.subject, recipient)
        os.makedirs(name=self.logdir, exist_ok=True)
        touch(os.path.join(self.logdir, str(datetime.datetime.now())))



    def move_mail(self):
        """TODO: Docstring for move_mail.

        :arg1: TODO
        :returns: TODO

        """
        os.makedirs(name=self.logdir, exist_ok=True)

        num_executions = len(os.listdir(self.logdir))
        print(num_executions)
        if num_executions < self.max_mail_on_level or self.max_mail_on_level == -1:
            return
        new_filepath = os.path.join(os.path.pardir, self.next_level,
                                    self.file_path)
        os.rename(self.file_path, new_filepath)
        shutil.rmtree(self.logdir)
        

def main():
    """
    Entrypoint if called as an executable
    """

    logging.basicConfig(level=LOGLEVEL)

    if len(sys.argv) != 2:
        print_usage()

    logging.info('Script was started at ' + str(datetime.datetime.now()))

    level = sys.argv[1]
    os.chdir(level)
    email_files = [f for f in os.listdir() if
                   os.path.isfile(f)]
    print(email_files)

    emails = []

    for email in email_files:
        emails.append(EMail(email, level))

    for email in emails:
        email.load_file()
        email.send()
        email.move_mail()



def print_usage():
    """TODO: Docstring for print_usage.
    :returns: TODO

    """
    print("Usage: ./mailer.sh <intervall>")
    print("there must exist a directory for the given interval in this" +
          "directory")
    exit(1)

def touch(fname, times=None):
    """TODO:
    """
    with open(fname, 'a'):
        os.utime(fname, times)


def write_email(msg_text, msg_subject, mail_to):
    """ Writes an e-mail with the given text and subject

    :msg_text:(str) Message text
    :msg_subject:(str) Message subject
    :returns: None

    """

    msg = MIMEText(msg_text)
    msg['Subject'] = msg_subject
    msg['From'] = MAIL_FROM
    msg['To'] = mail_to

    # Send the message via our own SMTP server.
    smtpserver = smtplib.SMTP('localhost')
    smtpserver.send_message(msg)
    smtpserver.quit()
    logging.debug("A message was sent to" + mail_to)

if __name__ == "__main__":
    main()
