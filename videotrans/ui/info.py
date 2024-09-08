# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'info.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QDesktopServices

from videotrans.configure import config

from . import mp,alipay,wx

class Ui_infoform(object):
    def setupUi(self, infoform):
        infoform.setObjectName("infoform")
        infoform.setWindowModality(QtCore.Qt.NonModal)
        infoform.resize(800, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(infoform.sizePolicy().hasHeightForWidth())
        infoform.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(infoform)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser = QtWidgets.QTextBrowser(infoform)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.anchorClicked.connect(self.openExternalLink)
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 1)
        if config.defaulelang == 'zh':
            self.retranslateUi(infoform)
        else:
            self.retranslateUi_en(infoform)
        QtCore.QMetaObject.connectSlotsByName(infoform)

    def openExternalLink(self, url):
        QDesktopServices.openUrl(url)

    def retranslateUi(self, infoform):
        _mp,_alipay,_wx=mp,alipay,wx
        _translate = QtCore.QCoreApplication.translate
        infoform.setWindowTitle(_translate("infoform", "捐助该软件以帮助持续维护"))
        self.textBrowser.setHtml(_translate("infoform", """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }a{text-decoration:none}
</style></head><body style="font-size:14px; font-weight:400; font-style:normal;">
<h1 style=" margin-top:18px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:xx-large; font-weight:600;">捐助该软件以帮助开发者持续维护</span></h1>

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">本项目基于兴趣创建，无商业和收费计划，你可以一直免费使用，或者fork后自己修改(开源协议GPL-v3)。所有代码均开源可审查。</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">至于维护问题呢，开源嘛都是用爱发电，闲时就多花些精力在这上面，忙时可能就一段时间顾不上。当然了，如果觉得该项目对你有价值，并希望该项目能一直稳定持续维护，也欢迎小额捐助。</p>

<hr />

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Email:jianchang512@gmail.com</p>

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">网站:pyvideotrans.com</p>

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">微信公众号/教程发布:pyvideotrans</p>

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a style="color:#fff" href="https://juejin.cn/user/4441682704623992/posts">掘金博客/教程发布: juejin.cn/user/4441682704623992</a></p>

<hr />

<h2 style="margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:x-large; font-weight:600;">如何捐助</span></h2>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">你可以向微信或支付宝二维码付款，备注你的github名称</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
    <img src=":/png/wx.png" width="240" />
    <img src=":/png/alipay.png" width="240" style="margin-left:8px" />
    <img src=":/png/mp.jpg" width="200" /></p>
<hr />

<h2 style=" margin-top:16px; margin-bottom:30px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a style=" font-size:x-large; font-weight:600;color:#ff0" href="https://pyvideotrans.com/about">
感谢所有捐助者，本项目的每一点改善都离不开您的帮助,点击查看捐赠名单</a></h2>
<hr />
<h2>免责声明：</h2>

在您下载或使用 "pyVideoTrans视频翻译配音" 软件（以下简称"本软件"）前，请仔细阅读并充分理解本免责声明中的各项条款。您的下载、安装或使用行为将被视为对本免责声明的接受，并同意按照本声明内容约束自己的行为。如果您不同意本声明的任何条款，请不要下载、安装或使用本软件。<br><br>

本软件所有源码均在 https://github.com/jianchang512/pyvideotrans 上开放。<br><br>

1. 本软件是由独立开发者使用开源语音识别模型并结合第三方翻译API和第三方配音API开发的免费工具，旨在提供视频翻译和配音功能。开发者保证在软件运行过程中不会获取或存储用户数据。<br><br>

2. 本软件中集成的语音识别功能（openai和faster模式）完全在本地环境下运行，不涉及将任何数据发送到开发者的服务器。当使用第三方翻译API和配音API时，相关数据将由用户的计算机直接传输至第三方服务器，未经开发者服务器处理。本软件无需用户注册或登录，不收集或存储任何个人信息。<br><br>

3. 本软件纯属个人爱好项目，开发者无营利目的，未制定任何盈利计划，并不提供付费技术支持或其他付费服务。<br><br>

4. 本软件不提供视频内容转移的功能，也不鼓励或支持任何形式的视频内容搬运行为。本软件仅旨在降低观赏外语视频时的语言障碍。<br><br>

5. 用户在使用本软件时，须自觉遵守当地法律以及中华人民共和国的法律法规，敬重并维护他人版权和知识产权。<br><br>

6. 用户因违反法律法规或侵犯他人权利而造成的任何后果，由用户本人承担，本软件开发者不承担任何连带责任。<br><br>

7. 鉴于开发者从本软件中未获利，对于本软件的使用引发的任何问题或损失，开发者不负责任。<br><br>

8. 本软件采用GPL-v3开源协议。任何基于本软件的二次开发或分支版本，需遵循GPL-v3协议规定，遵守相应义务和约束。<br>

本软件的所有解释权均属于开发者。谨请用户在理解、同意、遵守本免责声明的前提下使用本软件。<br>


</body></html>
"""))

    def retranslateUi_en(self, infoform):
        _translate = QtCore.QCoreApplication.translate
        infoform.setWindowTitle(_translate("infoform", "Donate to this software"))
        self.textBrowser.setHtml(_translate("infoform", """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }a{text-decoration:none}
</style></head><body style="font-size:14px; font-weight:400; font-style:normal;">
<h1 style=" margin-top:18px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:xx-large; font-weight:600;">Donate to this software to help the developers maintain it</span></h1>

<hr />
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">This project is created based on interest, with no commercial or charging plans. You can always use it for free, or fork it and modify it yourself (open source agreement GPL-v3). All codes are open source and can be reviewed.</p>
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">As for maintenance, open source is all about love. When you are free, you can spend more time on it. When you are busy, you may not be able to take care of it for a while. Of course, if you think the project is valuable to you and hope that the project can be maintained stably and continuously, small donations are also welcome.</p>

<hr />

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Email:jianchang512@gmail.com</p>

<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Documents:pyvideotrans.com</p>


<hr />

<h2 style="margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:x-large; font-weight:600;">How to Donate</span></h2>
<p><a style="font-size:18px;color:#4caf50" href="https://ko-fi.com/jianchang512"> 👑 Donate to this project and support at https://ko-fi.com/jianchang512 </a></p>

<h2 style=" margin-top:16px; margin-bottom:30px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a style=" font-size:x-large; font-weight:600;color:#ff0" href="https://pyvideotrans.com/about">
Thank you to all of our donors, every improvement in this program is made possible with your help, click here to see all donors!</a></h2>
<hr />
<h2>Disclaimer</h2>
Before you download or use the "pyVideoTrans video translation and dubbing" software (hereinafter referred to as "this software"), please read carefully and fully understand the terms in this disclaimer. Your download, installation or use will be deemed as acceptance of this disclaimer and agreement to constrain your behavior in accordance with the content of this statement. If you do not agree to any of the terms in this statement, please do not download, install or use this software. <br><br>

All source code of this software is open at https://github.com/jianchang512/pyvideotrans. <br><br>

1. This software is a free tool developed by independent developers using open source speech recognition models and combining third-party translation APIs and third-party dubbing APIs to provide video translation and dubbing functions. The developer guarantees that user data will not be obtained or stored during the operation of the software. <br><br>

2. The speech recognition function integrated in this software (openai and faster mode) runs completely in a local environment and does not involve sending any data to the developer's server. When using third-party translation APIs and dubbing APIs, the relevant data will be transmitted directly from the user's computer to the third-party server without being processed by the developer's server. This software does not require user registration or login, and does not collect or store any personal information. <br><br>

3. This software is purely a personal hobby project. The developer has no profit purpose, has not formulated any profit plan, and does not provide paid technical support or other paid services. <br><br>

4. This software does not provide the function of video content transfer, nor does it encourage or support any form of video content transfer. This software is only intended to reduce the language barrier when watching foreign language videos. <br><br>

5. When using this software, users must consciously abide by local laws and the laws and regulations of the People's Republic of China, respect and protect the copyrights and intellectual property rights of others. <br><br>

6. Any consequences caused by the user's violation of laws and regulations or infringement of the rights of others shall be borne by the user himself, and the developer of this software shall not bear any joint and several liability. <br><br>

7. In view of the fact that the developer has not made any profit from this software, the developer is not responsible for any problems or losses caused by the use of this software. <br><br>

8. This software adopts the GPL-v3 open source agreement. Any secondary development or branch version based on this software must comply with the provisions of the GPL-v3 agreement and comply with the corresponding obligations and constraints. <br>

All rights of interpretation of this software belong to the developer. Please use this software on the premise of understanding, agreeing to and complying with this disclaimer.<br>


</body></html>
"""))
