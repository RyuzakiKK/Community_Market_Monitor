#!/usr/bin/python3

import configparser
import time
import urllib3
from gi.repository import Notify

notification_sent = []


def get_site(url):
    urllib3.disable_warnings()
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    return r.data.decode("utf-8")


def check_url(url, price, index_url):
    page = get_site(url + "/render?start=0&currency=3&language=english")
    query = 'price_with_fee'
    offset = 31
    index = page.find(query)
    while index != -1 and page[index + offset:index + offset + 5] == "Sold!":
        shifted = page[index + offset:].find(query)
        index = -1 if shifted == -1 else index + offset + shifted
    if index != -1:
        decimal_point_index = page[index + offset:].find(",")
        actual_price = page[index + offset:index + offset + decimal_point_index + 3]
        print(actual_price)
        actual_price = actual_price[:decimal_point_index] + "." + actual_price[-2:]
        if actual_price[-2:] == "--":
            actual_price = actual_price[:-2] + "00"
        print(actual_price)
        global notification_sent
        if not notification_sent[index_url] and float(actual_price) <= price:
            notification_sent[index_url] = True
            Notify.Notification.new("Price matched",
                                    "Desired price {0}, actual price <b>{1}</b>.\n\n{2}".format(price, actual_price,
                                                                                                url),
                                    "dialog-information").show()


def main():
    Notify.init("Market Monitor")
    config = configparser.RawConfigParser()
    config.read('Settings.cfg')
    link_items = config.items("Links")
    price_items = config.items("Prices")
    try:
        sleep_time = config.getint("Misc", "sleep_time")
    except (configparser.NoOptionError, configparser.NoSectionError):
        sleep_time = 15
    global notification_sent
    notification_sent = [False] * len(link_items)
    if len(link_items) < 1:
        Notify.Notification.new("Configuration error", "At least one link is needed in the config file",
                                "dialog-error").show()
    elif len(link_items) != len(price_items):
        Notify.Notification.new("Configuration error", "The number of prices need to match the links",
                                "dialog-error").show()
    else:
        while True:
            for index, item in enumerate(link_items):
                check_url(item[1], float(price_items[index][1]), index)
            time.sleep(sleep_time)


if __name__ == '__main__':
    main()
