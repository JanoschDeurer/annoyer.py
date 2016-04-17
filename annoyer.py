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
for each mail seperately. Please have a look into the example_mail.yml file.

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


from email.mime.text import MIMEText
import logging
import smtplib
import datetime
import sys
import os
import re
import argparse
import yaml


class EMail(object):

    """Class for an EMail object """

    def __init__(self, file_path, interval):
        self.file_path = file_path
        self.interval = interval
        self.email_config = None
        if self.interval.endswith("/"):
            self.interval = self.interval[0:-1]

    def __str__(self):
        """ String representation of the class
        :returns: String representation of the class members

        """
        return "file_path: " + self.file_path + "\n" + \
            "interval: " + self.interval + "\n" + \
            "emai_config: " + str(self.email_config)

    def load_file(self):
        """ Loads configuration out of self.file_path into self.email_config
        :returns: None

        """
        # Load Yaml config for this mail
        with open(self.file_path, "r") as email_file:
            try:
                self.email_config = yaml.safe_load(email_file.read())
            except yaml.YAMLError as err:
                logging.critical("Yaml errror in the mail " + self.file_path + "\n"
                                 + str(err) + " \n Exiting program")
                exit(1)



        logging.debug("Succesfully read config from '" + self.file_path + "'\n" +
                      "The mail object now looks as follows: \n" + str(self))

    def _yaml_key_not_found(self, key):
        """ Prints out an error that the given key could not be found and exits the programm
        :key: Yaml key that was not found in the loaded config
        :returns: None

        """
        logging.critical("YAML Key '" + key + "' not found in the mail " + self.file_path)
        logging.critical("Exiting program due to previouse errors.")
        exit(1)


    def send(self):
        """ Parses email_config for mail configuration an sends emails to the
        given recipients with the given subject and body. load_file has to be
        executed before this method.
        :returns: None

        """

        # Check if recipients are given
        if "recipients" not in self.email_config:
            self._yaml_key_not_found("recipients")

        recipients = self.email_config["recipients"]

        # if only one recipient was given convert string to list
        if not hasattr(recipients, "append"):
            recipients = [recipients]


        # Check if subject is given
        if "subject" not in self.email_config:
            self._yaml_key_not_found("subject")

        subject = self.email_config["subject"]

        # Check if subject is given
        if "mailtext" not in self.email_config:
            self._yaml_key_not_found("mailtext")

        mail_text = self.email_config["mailtext"]

        # Send a seperate mail for each recipient
        for recipient in recipients:
            logging.info("sending mail '" + self.file_path + "' to " +
                         recipient)
            write_email(mail_text, subject, recipient)


    def move_mail(self):
        """Decreases the number of remaining repetitions of this mail and moves
        it to the next interval if they are zero

        :returns: None

        """
        # Check if intervals are given
        if "intervals" not in self.email_config:
            self._yaml_key_not_found("intervals")

        # Check if current interval is given
        if self.interval not in self.email_config["intervals"]:
            self._yaml_key_not_found("intervals: " + self.interval)

        # Check if file already has a number attached that counts the remaining
        # sends in this interval. Else read this number from the config
        ends_with_number = bool(re.findall(r"\.-?[0-9]*$", self.file_path))
        remaining_repetitions = 0
        logging.debug("Trying to determine number of remaining repetitions")
        new_file_path = self.file_path
        if ends_with_number:
            logging.debug("Filename ends on number, extracting number")
            remaining_repetitions = int(self.file_path.split(".")[-1])
            new_file_path = os.path.splitext(self.file_path)[0] + \
                            "." + str(remaining_repetitions)

        else:
            # Try to read remaining repetitions from config
            logging.debug("Filename does not end on number, extracting" +
                          "remaining_repetitions form config file")
            if "repetitions" not in self.email_config["intervals"][self.interval]:
                self._yaml_key_not_found("intervals: " + self.interval + " repetitions")
            remaining_repetitions = int(self.email_config["intervals"]
                                        [self.interval]["repetitions"])
            new_file_path = self.file_path + "." + str(remaining_repetitions)

        if remaining_repetitions > 0:
            remaining_repetitions -= 1

        # Check if mail hast to be moved into a new folder
        if remaining_repetitions == 0:
            # Check if next_interval is given
            if "next_interval" not in self.email_config["intervals"][self.interval]:
                self._yaml_key_not_found("intervals: " + self.interval + ": next_interval")

            next_interval = self.email_config["intervals"][self.interval]["next_interval"]

            # Check if repetitions for next_interval are given
            if "repetitions" not in self.email_config["intervals"][next_interval]:
                self._yaml_key_not_found("intervals: " + next_interval + ": repetitions")

            repetitions = self.email_config["intervals"][next_interval]["repetitions"]
            new_file_path = os.path.join(os.pardir, next_interval,
                                         os.path.splitext(new_file_path)[0] +
                                         "." + str(repetitions))


        os.rename(self.file_path, new_file_path)
        self.file_path = new_file_path


def write_email(msg_text, msg_subject, mail_to):
    """ Writes an e-mail with the given text and subject

    :msg_text:(str) Message text
    :msg_subject:(str) Message subject
    :returns: None

    """

    msg = MIMEText(msg_text)
    msg['Subject'] = msg_subject
    msg['From'] = "janosch.deurer@geonautik.de"
    msg['To'] = mail_to

    # Send the message via our own SMTP server.
    smtpserver = smtplib.SMTP('localhost')
    smtpserver.send_message(msg)
    smtpserver.quit()
    logging.debug("A message was sent to" + mail_to)

def is_dir(path):
    """ Checks whether a directory exists and raises an argparse Error
    otherwise

    :path: path to check for the directory
    :returns: path if path is an existing directory

    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("{0} is not an existing directory".format(path))
    return path

def get_commandline_arguments():
    """ Commandline argument parser for this module
    :returns: namespace with parsed arguments

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("intervall", help="directory with the mails to be progressed",
                        type=is_dir)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbosity", help="increase output verbosity", action="store_true")
    group.add_argument("-q", "--quiet", help="no output except errors", action="store_true")
    args = parser.parse_args()
    return args


def read_config():
    """ Config parser for this module. If no config can be found at
    ./config.yml one will be created
    :returns: dictionary with parsed cofing

    """
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               "config.yml"))
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            config_str = config_file.read()
        config = yaml.safe_load(config_str)
        if config["mail_from"] == "john.doe@example.com":
            print("Please change the sender mail adress in the config file")
            print("john.doe@example.com should not be used")
            exit(1)
        return config

    # If we reach this point, there is no config yet.
    print("No config file found at expected path: " + config_path)
    print("A default config file will be created...")
    config = \
"""# This is an example config file, please configure it for your needs.

# Please coose an E-Mail that will be send in the from header.
mail_from: john.doe@example.com

# For debugging purposes you can change this to logging.DEBUG
loglevel: logging.INFO
"""

    with open(config_path, "w") as config_file:
        config_file.write(config)
    print("Please review your new config and start again.", file=sys.stderr)
    exit(1)


def main():
    """
    Entrypoint if called as an executable
    """
    commandline_args = get_commandline_arguments()
    config = read_config()

    # override config with commandline arguments
    if commandline_args.verbosity:
        config["loglevel"] = "DEBUG"
    if commandline_args.quiet:
        config["loglevel"] = "ERROR"

    loglevel = getattr(logging, config["loglevel"].upper())
    logging.basicConfig(level=loglevel)


    logging.info('Script was started at ' + str(datetime.datetime.now()))

    intervall = commandline_args.intervall

    logging.info("Switching to directory " + intervall)
    os.chdir(intervall)
    email_files = [f for f in os.listdir() if
                   os.path.isfile(f)]
    logging.debug("The following Mail files where found: " + str(email_files))

    emails = []

    for email in email_files:
        emails.append(EMail(email, intervall))

    for email in emails:
        email.load_file()

        email.send()
        email.move_mail()

if __name__ == "__main__":
    main()
