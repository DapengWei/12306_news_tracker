#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import smtplib
from email.mime.text import MIMEText
from urlparse import urljoin

import requests
from lxml import html

news_url = "http://www.12306.cn/mormhweb/zxdt/"
news_page = "index_zxdt.html"
rule_url = "<your json file store the news>"
mailto_list = ["<mail address>"]


def get_latest_news(error_msg):
    try:
        r = requests.get(urljoin(news_url, news_page), timeout=10)
    except Exception, e:
        error_msg.append("download 12306 webpage error:" + str(type(e)))
        return False
    r.encoding = "utf-8"
    try:
        root = html.document_fromstring(r.content)
        news_list = root.get_element_by_id("newList")
        latest_news = news_list.xpath("//span/a")[0]
    except Exception, e:
        error_msg.append("parse 12306 webpage error" + str(type(e)))
        return False
    latest_news = {
        "title": latest_news.get("title"),
        "url": urljoin(news_url, latest_news.get("href")).decode("utf-8")}
    return latest_news


def get_online_news(error_msg):
    try:
        r = requests.get(rule_url, timeout=10)
    except Exception, e:
        error_msg.append("download json error:" + str(type(e)))
        return False
    r.encoding = "utf-8"
    try:
        json_file = r.json()
        current_news = {
            "title": json_file[u"announce_title"],
            "url": json_file[u"announce_link"]}
    except Exception, e:
        error_msg.append("parse json error" + str(type(e)))
        return False
    return current_news


def send_mail_local(send_subject, send_msg):
    mail_sender = "<send mail address>"
    mail_msg = MIMEText(send_msg, _subtype='plain', _charset='utf-8')
    mail_msg['Subject'] = send_subject
    mail_msg['From'] = mail_sender
    mail_msg['To'] = ",".join(mailto_list)
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(mail_sender, mailto_list, mail_msg.as_string())
        s.close()
        return True
    except Exception, e:
        print type(e)
        return False


def main():
    msg = []
    should_send = False
    msg_mail = {"subject": "", "content": ""}
    latest_announce = get_latest_news(msg)
    current_announce = get_online_news(msg)
    if latest_announce and current_announce:
        if latest_announce == current_announce:
            pass
        else:
            should_send = True
            msg_mail["subject"] = "Some updates for 12306 news"
            msg_mail["content"] = "new title: %s\nnew url: %s" % (latest_announce["title"], latest_announce["url"])
    else:
        should_send = True
        msg_mail["subject"] = "12306 update error!"
        msg_mail["content"] = str(msg)
    if should_send:
        send_mail_local(msg_mail["subject"], msg_mail["content"])
        print "should mail:\nlatest:%s \ncurrent:%s" % (str(latest_announce), str(current_announce))
    else:
        print "no update:\nlatest:%s \ncurrent:%s" % (str(latest_announce), str(current_announce))
if __name__ == '__main__':
    main()
