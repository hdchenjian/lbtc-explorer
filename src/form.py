#!/usr/bin/python3
# -*- coding: utf-8 -*-

from wtforms.form import Form
from wtforms.fields import StringField, PasswordField, BooleanField, \
    FileField, SelectField
from wtforms.validators import InputRequired


class Login(Form):
    email_address = StringField(u"", [InputRequired()])
    password = PasswordField(u'', [InputRequired()])
    remmeber_me = BooleanField(u'记住我')


class UploadFileForm(Form):
    device_type = SelectField(u"设备类型", choices=[
        ("0", u"CHIGO"), ("1", u"晓客"), ("2", u"店计"), ("3", u"店计v4")])
    package_type = SelectField(
        u"包类型", choices=[("firm", u"固件"), ("alg", u"算法"), ("fpga", u"FPGA")])
    version = StringField(u'版本', [InputRequired()])
    md5 = StringField(u'md5值', [InputRequired()])
    file_name = FileField(u'请选择包(tar.gz或.pkg格式)')


class AddDeviceType(Form):
    name = StringField(u"升级脚本中的appname,用来区别设备类型", [InputRequired()])
    device_name = StringField(u'设备名', [InputRequired()])
