// ==UserScript==
// @name         12306cal
// @namespace    http://github.com/w1ndy/12306.cal
// @version      0.1
// @description  A simple script that adds your train tickets booked on 12306.cn to Google Calendar
// @author       w1ndy
// @match        https://kyfw.12306.cn/otn/view/train_order.html
// @grant        none
// ==/UserScript==

(function() {
    'use strict'

    function attachButton() {
        document.querySelectorAll('.has-order-num:not(.item-disabled) .ticket-status-name:not(.cal-injected)')
        .forEach(el => {
            el.classList.add('cal-injected')
            const cancellationLink = el.querySelector('a')
            if (!cancellationLink) {
                return
            }

            const fromStationTelecode = cancellationLink.getAttribute('data-from-station-telecode')
            const toStationTelecode = cancellationLink.getAttribute('data-to-station-telecode')
            const train = cancellationLink.getAttribute('data-train-no')
            const date = cancellationLink.getAttribute('data-train-date').split(' ')[0]
            const seat = cancellationLink.getAttribute('data-coach-name') + '车' +
                         cancellationLink.getAttribute('data-seat-name')

            const button = document.createElement('a')
            button.className = 'txt-primary'
            button.style = 'display: inline-block'
            button.href = `javascript: addToGoogleCalendar("${fromStationTelecode}", "${toStationTelecode}", "${train}", "${date}", "${seat}")`
            button.appendChild(document.createTextNode('添加到 Google 日历'))
            el.appendChild(button)
        })
    }

    function isTimeWrapped(a, b) {
        return a.startsWith('2') && b.startsWith('0')
    }

    function normalizeDate(d) {
        return d.replace(/(\-)|(:)|(.000)/g, '')
    }

    window.addToGoogleCalendar = async (fromStationTelecode, toStationTelecode, train, date, seat) => {
        const timetableUrl = `https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=${train}&from_station_telecode=${fromStationTelecode}&to_station_telecode=${toStationTelecode}&depart_date=${date}`
        const resp = await fetch(timetableUrl)
        const info = await resp.json()

        let origin, dest, prev
        let daysWrapped = 0
        for (let s of info.data.data) {
            if (origin) {
                if (prev && isTimeWrapped(prev.start_time, s.arrive_time)) {
                    daysWrapped++
                } else if (isTimeWrapped(s.arrive_time, s.start_time)) {
                    daysWrapped++
                }
            }
            if (!origin && s.isEnabled) {
                origin = s
            } else if (origin && !s.isEnabled) {
                dest = prev
                break
            }
            prev = s
        }
        if (!dest) {
            dest = prev
        }

        const eventSummary = `${info.data.data[0].station_train_code}: ${origin.station_name} - ${dest.station_name} @ ${seat}`
        const eventLocation = `${origin.station_name}火车站`
        const eventBeginTime = normalizeDate((new Date(`${date} ${origin.start_time}`)).toISOString())
        const eventEndTimeDate = new Date(`${date} ${dest.arrive_time}`)
        eventEndTimeDate.setDate(eventEndTimeDate.getDate() + daysWrapped)
        const eventEndTime = normalizeDate(eventEndTimeDate.toISOString())

        const eventUrl = encodeURI(`https://www.google.com/calendar/render?action=TEMPLATE&text=${eventSummary}&location=${eventLocation}&dates=${eventBeginTime}/${eventEndTime}`)
        window.open(eventUrl,'_blank')
    }

    const xhrOpen = XMLHttpRequest.prototype.open
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener('load', attachButton)
        xhrOpen.apply(this, arguments)
    }
})();