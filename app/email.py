# coding: utf-8
from flask.ext.mail import Message
from flask import current_app, render_template
from . import mail


def send_email(to, subject, template, **kwargs):  # 为同步发邮件方式 TODO 后面要改为异步发送邮件的方式
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
