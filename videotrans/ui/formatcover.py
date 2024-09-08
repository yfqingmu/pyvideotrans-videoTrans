# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ott.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

from videotrans.configure import config


class Ui_formatcover(object):
    def setupUi(self, formatcover):
        self.videofiles = []
        self.has_done=False

        formatcover.setObjectName("formatcover")
        formatcover.setWindowModality(QtCore.Qt.NonModal)
        formatcover.resize(500, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(formatcover.sizePolicy().hasHeightForWidth())
        formatcover.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QVBoxLayout(formatcover)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.formLayout_2 = QtWidgets.QHBoxLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.formLayout_2.setAlignment(QtCore.Qt.AlignVCenter)

        self.selectbtn = QtWidgets.QPushButton(formatcover)
        self.selectbtn.setMinimumSize(QtCore.QSize(150, 35))
        self.selectbtn.setObjectName("selectbtn")
        self.selectbtn.setCursor(Qt.PointingHandCursor)

        self.pathdir = QtWidgets.QLineEdit(formatcover)
        self.pathdir.setMinimumSize(QtCore.QSize(0, 35))
        self.pathdir.setObjectName("pathdir")
        self.pathdir.setReadOnly(True)

        self.formLayout_2.addWidget(self.selectbtn)
        self.formLayout_2.addWidget(self.pathdir)
        self.gridLayout.addSpacing(10)

        self.gridLayout.addLayout(self.formLayout_2)

        # sk
        self.formLayout_3 = QtWidgets.QHBoxLayout()
        self.formLayout_3.setAlignment(QtCore.Qt.AlignVCenter)
        self.formLayout_3.setObjectName("formLayout_3")

        self.gridLayout.addSpacing(10)

        self.labelformat = QtWidgets.QLabel(formatcover)
        self.labelformat.setMinimumSize(QtCore.QSize(0, 35))
        self.labelformat.setObjectName("label")

        self.formatlist = QtWidgets.QComboBox(formatcover)
        self.formatlist.setFixedHeight(40)
        self.formatlist.setFixedWidth(320)
        self.formatlist.setObjectName("formatlist")
        self.formatlist.addItems(config.VIDEO_EXTS+config.AUDIO_EXITS)

        self.formLayout_3.addWidget(self.labelformat)
        self.formLayout_3.addStretch()
        self.formLayout_3.addWidget(self.formatlist)
        self.gridLayout.addLayout(self.formLayout_3)
        self.gridLayout.addSpacing(30)

        self.startbtn = QtWidgets.QPushButton(formatcover)
        self.startbtn.setMinimumSize(QtCore.QSize(200, 35))
        self.startbtn.setObjectName("startbtn")
        self.startbtn.setCursor(Qt.PointingHandCursor)

        self.opendir = QtWidgets.QPushButton(formatcover)
        self.opendir.setMinimumSize(QtCore.QSize(0, 35))
        self.opendir.setStyleSheet('''background-color:transparent''')
        self.opendir.setObjectName("opendir")
        self.opendir.setCursor(Qt.PointingHandCursor)

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.setObjectName("layout_btn")
        self.layout_btn.addStretch()
        self.layout_btn.addWidget(self.startbtn)
        self.layout_btn.addStretch()

        self.layout_opendir = QtWidgets.QHBoxLayout()
        self.layout_opendir.setObjectName("layout_opendir")
        self.layout_opendir.addStretch()
        self.layout_opendir.addWidget(self.opendir)
        self.layout_opendir.addStretch()

        self.gridLayout.addLayout(self.layout_btn)
        self.gridLayout.addSpacing(50)
        self.gridLayout.addLayout(self.layout_opendir)

        self.retranslateUi(formatcover)
        QtCore.QMetaObject.connectSlotsByName(formatcover)

    def retranslateUi(self, formatcover):
        formatcover.setWindowTitle('音视频格式转换' if config.defaulelang == 'zh' else 'Audio /Video conver')

        self.selectbtn.setText(
            '选择要转换的文件/可多选' if config.defaulelang == 'zh' else 'Select files to be converted/multiple selections possible')

        self.labelformat.setText('要转换到的目标格式' if config.defaulelang == 'zh' else 'Target format')

        self.pathdir.setPlaceholderText(
            '选择要转换的文件/可多选' if config.defaulelang == 'zh' else 'Select files to be converted/multiple selections possible')

        self.startbtn.setText('开始转换' if config.defaulelang == 'zh' else 'Start')
        self.opendir.setText('打开结果目录' if config.defaulelang == 'zh' else 'Open the results catalog')
