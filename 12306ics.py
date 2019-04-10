import re
import requests
import pytz
import sys

from datetime import datetime
from icalendar import Calendar, Event, vText

def getStations():
    resp = requests.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js')
    m = re.search(r'\'(.*)\'', resp.text)
    if not m:
        raise RuntimeError('Unable to parse station data!')
    return list(map(lambda s: s.split('|'), m.group(1).split('@')[1:]))

def isStationMatched(station, hint):
    return station[0].startswith(hint) or \
           station[1].startswith(hint) or \
           station[3].startswith(hint) or \
           station[4].startswith(hint)

def searchStations(stations, beginStation, endStation):
    beginMatched = []
    endMatched = []
    for s in stations:
        if isStationMatched(s, beginStation):
            beginMatched.append(s)
        if isStationMatched(s, endStation):
            endMatched.append(s)
    return beginMatched, endMatched

def resolveTrainInfo(beginStationID, endStationID, date, trainID):
    resp = requests.get('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (date, beginStationID, endStationID))
    try:
        trainInfo = resp.json()
    except:
        return None
    for train in trainInfo['data']['result']:
        columns = train.split('|')
        if columns[3] == trainID:
            return {
                'beginStation': trainInfo['data']['map'][columns[6]],
                'endStation': trainInfo['data']['map'][columns[7]],
                'beginTime': columns[8],
                'endTime': columns[9],
            }
    return None

def findTrain(beginStations, endStations, date, trainID):
    for bs in beginStations:
        for es in endStations:
            result = resolveTrainInfo(bs[2], es[2], date, trainID)
            if result:
                return result
    return None

def printUsage():
    print('Usage: python3 12306ics.py begin_station end_station yyyy-mm-dd train_id [seat]')
    print('Example: python3 12306ics.py 北京 上海 2019-05-01 G1 > 12306.ics')
    print('         python3 12306ics.py bj sh 2019-05-01 G1 1.1A > 12306.ics')
    exit(1)

def main():
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        printUsage()

    beginStationHint = sys.argv[1]
    endStationHint = sys.argv[2]
    date = sys.argv[3]
    trainID = sys.argv[4]
    seatID = (' @ ' + sys.argv[5]) if len(sys.argv) == 6 else ''

    stations = getStations()
    beginStations, endStations = searchStations(stations, beginStationHint, endStationHint)

    info = findTrain(beginStations, endStations, date, trainID)
    if not info:
        raise RuntimeError('Cannot find the specified train!')

    event = Event()
    event.add('summary', '%s: %s - %s%s' % (trainID, info['beginStation'], info['endStation'], seatID))
    dateComponents = list(map(int, date.split('-')))
    beginTimeComponents = list(map(int, info['beginTime'].split(':')))
    endTimeComponents = list(map(int, info['endTime'].split(':')))
    event.add('dtstart', datetime(*dateComponents, *beginTimeComponents, 0, tzinfo=pytz.timezone('Asia/Shanghai')))
    event.add('dtend', datetime(*dateComponents, *endTimeComponents, 0, tzinfo=pytz.timezone('Asia/Shanghai')))
    event.add('dtstamp', datetime(*dateComponents, 0, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai')))
    event['location'] = vText(info['beginStation'])
    event['uid'] = '12306ICS_%s_%s' % (date, trainID)

    cal = Calendar()
    cal.add('prodid', '-//12306ics//')
    cal.add('version', '2.0')
    cal.add_component(event)
    sys.stdout.buffer.write(cal.to_ical())

if __name__ == '__main__':
    main()
