import re
import requests
import pytz
import sys
import webbrowser

from datetime import datetime
from optparse import OptionParser
from urllib.parse import quote
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

def buildOptionParser():
    usage = 'usage: %prog [options] begin_station end_station yyyy-mm-dd train_id'
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--seat', dest='seat', help='specify the booked seat which will be displayed as \'@ SEAT\' after the title of an event', metavar='SEAT')
    parser.add_option('-x', '--no-browser', dest='noBrowser', help='do not open the browser automatically', action='store_true')
    parser.add_option('-o', '--ical', dest='icalOutputFile', help='write to an ical file', metavar='FILE')
    return parser

def main():
    parser = buildOptionParser()
    (opts, args) = parser.parse_args()
    if len(args) != 4:
        parser.print_help()
        exit(1)

    beginStationHint = args[0]
    endStationHint = args[1]
    date = args[2]
    trainID = args[3]
    seatID = (' @ ' + opts.seat) if opts.seat else ''

    stations = getStations()
    beginStations, endStations = searchStations(stations, beginStationHint, endStationHint)

    info = findTrain(beginStations, endStations, date, trainID)
    if not info:
        raise RuntimeError('Cannot find the specified train!')

    dateComponents = list(map(int, date.split('-')))
    beginTimeComponents = list(map(int, info['beginTime'].split(':')))
    endTimeComponents = list(map(int, info['endTime'].split(':')))
    eventSummary = '%s: %s - %s%s' % (trainID, info['beginStation'], info['endStation'], seatID)
    eventLocation = info['beginStation'] + '火车站'
    eventBeginTime = datetime(*dateComponents, *beginTimeComponents, 0, tzinfo=pytz.timezone('Asia/Shanghai'))
    eventEndTime = datetime(*dateComponents, *endTimeComponents, 0, tzinfo=pytz.timezone('Asia/Shanghai'))

    if opts.icalOutputFile:
        event = Event()
        event.add('summary', eventSummary)
        event.add('dtstart', eventBeginTime)
        event.add('dtend', eventEndTime)
        event.add('dtstamp', datetime.now(pytz.timezone('Asia/Shanghai')))
        event['location'] = vText(eventLocation)
        event['uid'] = '12306CAL_%s_%s' % (date, trainID)

        cal = Calendar()
        cal.add('prodid', '-//12306cal//')
        cal.add('version', '2.0')
        cal.add_component(event)

        with open(opts.icalOutputFile, 'wb') as f:
            f.write(cal.to_ical())
    else:
        url = 'https://www.google.com/calendar/render?action=TEMPLATE&text=%s&location=%s&dates=%s%%2F%s' % (quote(eventSummary), quote(eventLocation), eventBeginTime.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ'), eventEndTime.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ'))
        print(url)
        if not opts.noBrowser:
            webbrowser.open_new_tab(url)

if __name__ == '__main__':
    main()
