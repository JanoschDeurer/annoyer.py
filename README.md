# annoyer.py

**Note:** This program is still in its testing phase and will probably contain
bugs.

This program sends reminder mails with an increasing frequency to remind people
to do something. The E-Mail itself as well as the frequency are configurable
for each mail separately. Please have a look into the example_mail.yml file.

## Installation

You can clone the repository or just get the executable itself with:

``` bash
wget https://raw.githubusercontent.com/JanoschDeurer/annoyer.py/master/annoyer.py
```

annoyer.py uses the python3 smtplib module. It assumes that you have a running
mail server on your computer.

## Usage

### Cronjob

The program is intended to be executed as a cronjob. A cronjob definition cold
look as follows:

``` bash
# For more information see the manual pages of crontab(5) and cron(8)
# m h  dom mon dow   command
30 * * * * /path/to/annoyer.py hourly
0 3 * * * /path/to/annoyer.py daily
0 4 * * 1 /path/to/annoyer.py weekly
0 5 1 * * /path/to/annoyer.py monthly

```

The concept is similar to the one used with rsnapshot. You can define
arbitrary intervals by writing them in your crontab. The script then looks for
a folder with mails for the given interval relative to the script location.
Therefore for this example the directories ```/path/to/hourly```
, ```/path/to/daily``` ect. should exist.

### Mail files

Mails are specified as YAML configuration files. Pleas take a look into
the ```example_mail.yml``` file. The supported values are:

* recipients: single value or dictionary of recipients
* subject: string with mail subject
* mailtext: string with mailtext
* intervals: dictionary of intervals containing
  * &lt;intervalname&gt;: specifies name of the interval and contains
    * repetitions: how often the mail will be send in this interval. Set
      this to -1 for infinite repetions.
    * next_interval: interval the mail will be moved to after this interval is completed

Here is an example configuration for the intervals:

```YAML
intervals:
  weekly:
    repetitions: 4
    next_interval: daily
  daily:
    repetitions: 7
    next_interval: hourly
  hourly:
    repetitions: -1
```

If you use this interval configuration and the above crotab the following
will happen: your mail is send once a week for 4 weeks, then it is send
once a day for 7 days, then it is send every hour until you remove the
mail.
