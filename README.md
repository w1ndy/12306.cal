# 12306.ics
> A simple script that exports ``.ics`` calendar events for your train tickets booked on 12306.cn

## Usage

1. Install the requirements (icalendar, pytz, requests) with ``pip3 install -r requirements.txt``
2. Export .ics files with ``python3 12306ics.py begin_station end_station yyyy-mm-dd train_id [seat] > 12306.ics``.

## Examples

```
python3 12306ics.py 北京 上海 2019-05-01 G1 > 12306.ics
python3 12306ics.py bj sh 2019-05-01 G1 1.1A > 12306.ics
```

Licensed under [Anti 996](https://github.com/996icu/996.ICU/blob/master/LICENSE).
Copyright (c) 2019 [Project Contributors](https://github.com/w1ndy/12306.ics/graphs/contributors).