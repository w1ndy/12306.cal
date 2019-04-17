# 12306.cal
> A simple script that adds your train tickets booked on 12306.cn to Google Calendar

A user script version is available at [here](https://raw.githubusercontent.com/w1ndy/12306.cal/master/12306cal.user.js).

## Usage

1. Install the requirements (icalendar, pytz, requests) with ``pip3 install -r requirements.txt``
2. Run with ``python3 12306cal.py begin_station end_station yyyy-mm-dd train_id``.

```
Usage: 12306cal.py [options] begin_station end_station yyyy-mm-dd train_id

Options:
  -h, --help            show this help message and exit
  -s SEAT, --seat=SEAT  specify the booked seat which will be displayed as '@
                        SEAT' after the title of an event
  -x, --no-browser      do not open the browser automatically
  -o FILE, --ical=FILE  write to an ical file
```

## Examples

```
python3 12306cal.py bjn shhq 2019-05-01 G1 -s 08-08A
python3 12306cal.py bjn shhq 2019-05-01 G1 -s 08-08A -o G1.ics
```

Licensed under [Anti 996](https://github.com/996icu/996.ICU/blob/master/LICENSE).
Copyright (c) 2019 [Project Contributors](https://github.com/w1ndy/12306.ics/graphs/contributors).