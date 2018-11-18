# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/CameraProtocol.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FormCameraProtocol(object):
    def setupUi(self, FormCameraProtocol):
        FormCameraProtocol.setObjectName("FormCameraProtocol")
        FormCameraProtocol.resize(507, 170)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FormCameraProtocol.sizePolicy().hasHeightForWidth())
        FormCameraProtocol.setSizePolicy(sizePolicy)
        self.verticalLayoutForm = QtWidgets.QVBoxLayout(FormCameraProtocol)
        self.verticalLayoutForm.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutForm.setObjectName("verticalLayoutForm")
        self.frameCameraProtocol = QtWidgets.QFrame(FormCameraProtocol)
        self.frameCameraProtocol.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameCameraProtocol.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCameraProtocol.setObjectName("frameCameraProtocol")
        self.verticalLayoutFrameCameraProtocol = QtWidgets.QVBoxLayout(self.frameCameraProtocol)
        self.verticalLayoutFrameCameraProtocol.setContentsMargins(9, -1, -1, -1)
        self.verticalLayoutFrameCameraProtocol.setObjectName("verticalLayoutFrameCameraProtocol")
        self.horizontalLayoutCameraProtocol = QtWidgets.QHBoxLayout()
        self.horizontalLayoutCameraProtocol.setObjectName("horizontalLayoutCameraProtocol")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutCameraProtocol.addItem(spacerItem)
        self.labelCameraProtocol = QtWidgets.QLabel(self.frameCameraProtocol)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCameraProtocol.sizePolicy().hasHeightForWidth())
        self.labelCameraProtocol.setSizePolicy(sizePolicy)
        self.labelCameraProtocol.setObjectName("labelCameraProtocol")
        self.horizontalLayoutCameraProtocol.addWidget(self.labelCameraProtocol)
        self.radioButtonCameraProtocolUDP = QtWidgets.QRadioButton(self.frameCameraProtocol)
        self.radioButtonCameraProtocolUDP.setChecked(True)
        self.radioButtonCameraProtocolUDP.setObjectName("radioButtonCameraProtocolUDP")
        self.horizontalLayoutCameraProtocol.addWidget(self.radioButtonCameraProtocolUDP)
        self.radioButtonCameraProtocolTCP = QtWidgets.QRadioButton(self.frameCameraProtocol)
        self.radioButtonCameraProtocolTCP.setObjectName("radioButtonCameraProtocolTCP")
        self.horizontalLayoutCameraProtocol.addWidget(self.radioButtonCameraProtocolTCP)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutCameraProtocol.addItem(spacerItem1)
        self.verticalLayoutFrameCameraProtocol.addLayout(self.horizontalLayoutCameraProtocol)
        self.verticalLayoutForm.addWidget(self.frameCameraProtocol)

        self.retranslateUi(FormCameraProtocol)
        QtCore.QMetaObject.connectSlotsByName(FormCameraProtocol)

    def retranslateUi(self, FormCameraProtocol):
        _translate = QtCore.QCoreApplication.translate
        FormCameraProtocol.setWindowTitle(_translate("FormCameraProtocol", "Form"))
        self.labelCameraProtocol.setText(_translate("FormCameraProtocol", "Camera Protocol"))
        self.radioButtonCameraProtocolUDP.setText(_translate("FormCameraProtocol", "UDP"))
        self.radioButtonCameraProtocolTCP.setText(_translate("FormCameraProtocol", "TCP"))

