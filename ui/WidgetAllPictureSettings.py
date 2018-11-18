from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QApplication, QWidget
import os
import sys

from watch_out_lib import Config

TEMP_SETTINGS = 0
BACKUP_SETTINGS = 1

_PIC_STYLE_DISABLED_MAP = {Config.PARAM_PICTURE_TYPE_TEMP: Config.BLUE_STYLE_BG,
                  Config.PARAM_PICTURE_TYPE_BACKUP: Config.YELLOW_STYLE_BG}

_PIC_STYLE_ENABLED_MAP = {Config.PARAM_PICTURE_TYPE_TEMP: Config.GRADIENT_GREEN_BLUE_BG,
                  Config.PARAM_PICTURE_TYPE_BACKUP: Config.GRADIENT_GREEN_YELLOW_BG}

PICTURE_UPLOAD_SETTINGS_TITLE_FORMAT = \
    "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600; color:#009311;\">{:s}</span></p></body></html>"
HTML_LINE_BREAK = "<br />"


def set_size_policy(widget):
    size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    widget.setSizePolicy(size_policy)


class QWidgetPictureSettings(QWidget):
    def __init__(self, pic_type, parent=None):
        self._pic_type = pic_type
        # noinspection PyArgumentList
        QWidget.__init__(self, parent=parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "QWidgetPictureSettings.ui"), self)
        self.set_style(False)
        set_size_policy(self)
        self.groupBoxUploadSettings.setTitle(pic_type.replace('_', ' '))

    def set_style(self, upload_enable):
        if upload_enable:
            self.setStyleSheet(_PIC_STYLE_ENABLED_MAP[self._pic_type])
        else:
            self.setStyleSheet(_PIC_STYLE_DISABLED_MAP[self._pic_type])


class WidgetAllPictureSettings(QWidget):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        QWidget.__init__(self, parent=parent)

        self.pic_settings_widgets = {
            Config.PARAM_PICTURE_TYPE_TEMP: QWidgetPictureSettings(Config.PARAM_PICTURE_TYPE_TEMP, parent=self),
            Config.PARAM_PICTURE_TYPE_BACKUP: QWidgetPictureSettings(Config.PARAM_PICTURE_TYPE_BACKUP, parent=self),
        }
        for pic_settings in Config.PARAM_PICTURE_TYPE_LIST:
            setattr(self, pic_settings, self.pic_settings_widgets[pic_settings])
        self.setObjectName("WidgetAllPictureSettings")
        self.resize(800, 588)
        self.setMaximumSize(QtCore.QSize(800, 588))

        set_size_policy(self)

        self.setContentsMargins(0,0,0,0)
        self.setWindowTitle("Watch Out!")

        self.pic_settings_widgets[Config.PARAM_PICTURE_TYPE_TEMP].framePictureExpiry.hide()

        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(Config.APP_COLOR_BG)

        # Widget layout
        self.verticalLayoutWidget = QtWidgets.QVBoxLayout(self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setContentsMargins(0,0,0,0)
        self.verticalLayoutWidget.setSpacing(0)

        self.verticalLayoutPictureUploadSettings = QtWidgets.QVBoxLayout()
        self.verticalLayoutPictureUploadSettings.setObjectName("verticalLayoutPictureUploadSettings")
        self.verticalLayoutPictureUploadSettings.setContentsMargins(0,0,0,0)
        self.verticalLayoutPictureUploadSettings.setSpacing(0)

        # noinspection PyArgumentList
        self.framePictureUploadSettings = QtWidgets.QFrame(self)
        set_size_policy(self.framePictureUploadSettings)
        self.framePictureUploadSettings.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.framePictureUploadSettings.setFrameShadow(QtWidgets.QFrame.Raised)
        self.framePictureUploadSettings.setObjectName("framePictureUploadSettings")
        self.framePictureUploadSettings.setFrameShape(QtWidgets.QFrame.Panel)
        self.framePictureUploadSettings.setLineWidth(2)
        self.framePictureUploadSettings.setLayout(self.verticalLayoutPictureUploadSettings)

        self.verticalLayoutInsideFrame = QtWidgets.QVBoxLayout()
        self.verticalLayoutInsideFrame.setObjectName("verticalLayoutInsideFrame")
        self.verticalLayoutInsideFrame.setContentsMargins(0,0,0,0)
        self.verticalLayoutInsideFrame.setSpacing(0)

        ################################
        # add Widget header
        self.verticalLayoutHeader = QtWidgets.QVBoxLayout()
        self.verticalLayoutHeader.setObjectName("verticalLayoutInsideFrame")
        self.verticalLayoutHeader.setContentsMargins(0,0,0,10)
        self.verticalLayoutHeader.setSpacing(0)

        self.labelHeaderPictureUploadSettings = QtWidgets.QLabel(self.framePictureUploadSettings)
        self.labelHeaderPictureUploadSettings.setAlignment(QtCore.Qt.AlignCenter)
        self.labelHeaderPictureUploadSettings.setObjectName("labelHeaderPictureUploadSettings")
        # noinspection PyArgumentList
        self.verticalLayoutHeader.addWidget(self.labelHeaderPictureUploadSettings)
        self.verticalLayoutInsideFrame.addLayout(self.verticalLayoutHeader)

        ################################
        # Line Edits Frame
        self.verticalLayoutLineEdits = QtWidgets.QVBoxLayout()
        self.verticalLayoutLineEdits.setObjectName("verticalLayoutLineEdits")
        self.verticalLayoutLineEdits.setContentsMargins(0,0,0,0)
        self.verticalLayoutLineEdits.setSpacing(3)

        self.frameLineEdits = QtWidgets.QFrame(self)
        set_size_policy(self.frameLineEdits)
        self.frameLineEdits.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameLineEdits.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameLineEdits.setContentsMargins(9,3,9,3)
        self.frameLineEdits.setLayout(self.verticalLayoutLineEdits)

        self.verticalLayoutInsideLineEditsFrame = QtWidgets.QVBoxLayout()
        self.verticalLayoutInsideLineEditsFrame.setObjectName("verticalLayoutInsideLineEditsFrame")
        self.verticalLayoutInsideLineEditsFrame.setContentsMargins(0,0,0,0)
        self.verticalLayoutInsideLineEditsFrame.setSpacing(0)

        ################################
        # Add camera description
        self.horizontalLayoutDescription = QtWidgets.QHBoxLayout()
        self.horizontalLayoutDescription.setObjectName("horizontalLayoutDescription")
        self.horizontalLayoutDescription.setContentsMargins(9,0,9,0)
        self.horizontalLayoutDescription.setSpacing(9)

        self.frameDescription = QtWidgets.QFrame(self.frameLineEdits)
        self.frameDescription.setStyleSheet(Config.LIGHT_BROWN_STYLE_BG)
        set_size_policy(self.frameDescription)
        self.frameDescription.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameDescription.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameDescription.setContentsMargins(9,3,9,3)
        self.frameDescription.setLayout(self.horizontalLayoutDescription)

        self.labelCameraDescription = QtWidgets.QLabel()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.labelCameraDescription.setSizePolicy(size_policy)
        self.labelCameraDescription.setObjectName("labelCameraDescription")
        self.labelCameraDescription.setText("Short Camera Description")
        # noinspection PyArgumentList
        self.horizontalLayoutDescription.addWidget(self.labelCameraDescription)

        self.lineEditCameraDescription = QtWidgets.QLineEdit()
        set_size_policy(self.lineEditCameraDescription)
        self.lineEditCameraDescription.setObjectName("lineEditCameraDescription")
        str_format = "<html><head/><body><p><span style=\"font-size:8pt; font-family:'Courier New'; font-weight:400; color:#009311;\">{:s}</span></p></body></html>"
        tip = str_format.format("You may only use alpha numeric, space, '_' characters<br />")
        self.lineEditCameraDescription.setToolTip(tip)

        # noinspection PyArgumentList
        self.horizontalLayoutDescription.addWidget(self.lineEditCameraDescription)

        self.verticalLayoutInsideLineEditsFrame.addWidget(self.frameDescription)


        ################################
        # Add camera URL
        self.horizontalLayoutCameraUrl = QtWidgets.QHBoxLayout()
        self.horizontalLayoutCameraUrl.setObjectName("horizontalLayoutCameraUrl")
        self.horizontalLayoutCameraUrl.setContentsMargins(9,0,9,0)
        self.horizontalLayoutCameraUrl.setSpacing(9)

        self.frameCameraUrl = QtWidgets.QFrame(self.frameLineEdits)
        self.frameCameraUrl.setStyleSheet(Config.LIGHT_BROWN_STYLE_BG)
        set_size_policy(self.frameCameraUrl)
        self.frameCameraUrl.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameCameraUrl.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCameraUrl.setContentsMargins(9,3,9,3)
        self.frameCameraUrl.setLayout(self.horizontalLayoutCameraUrl)

        self.labelCameraUrl = QtWidgets.QLabel()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.labelCameraUrl.setSizePolicy(size_policy)
        self.labelCameraUrl.setObjectName("labelCameraUrl")
        self.labelCameraUrl.setText("Camera URL\n(hover mouse cursor over line for tip)")
        self.horizontalLayoutCameraUrl.addWidget(self.labelCameraUrl)

        self.lineEditCameraUrl = QtWidgets.QLineEdit()
        set_size_policy(self.lineEditCameraUrl)
        self.lineEditCameraUrl.setObjectName("lineEditCameraUrl")
        str_format = "<html><head/><body><p><span style=\"font-size:8pt; font-family:'Courier New'; font-weight:400; color:#009311;\">{:s}</span></p></body></html>"
        tip = str_format.format("Your URL may contain the following fields, literally:<br />"
                                "&nbsp;&nbsp;&nbsp;Camera password:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{password:s}<br />"
                                "&nbsp;&nbsp;&nbsp;Camera's index:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{camera_index:d}<br /><br />"
                                "Examples:<br />"
                                "rtsp://admin:{password:s}@192.168.1.10:554/ch0{camera_index:d}/0<br /><br />"
                                "rtsp://192.168.1.10:554/ch0<br /><br />"
                                "See your camera system manual for details.")
        self.lineEditCameraUrl.setToolTip(tip)

        self.horizontalLayoutCameraUrl.addWidget(self.lineEditCameraUrl)

        self.verticalLayoutInsideLineEditsFrame.addWidget(self.frameCameraUrl)

        ################################
        # Camera protocol
        self.verticalLayoutFrameCameraProtocol = QtWidgets.QVBoxLayout()
        self.verticalLayoutFrameCameraProtocol.setContentsMargins(9, -1, -1, -1)
        self.verticalLayoutFrameCameraProtocol.setObjectName("verticalLayoutFrameCameraProtocol")

        self.frameCameraProtocol = QtWidgets.QFrame()
        self.frameCameraProtocol.setFrameShape(QtWidgets.QFrame.Panel)
        self.frameCameraProtocol.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCameraProtocol.setObjectName("frameCameraProtocol")
        self.frameCameraProtocol.setLayout(self.verticalLayoutFrameCameraProtocol)
        self.frameCameraProtocol.setStyleSheet(Config.LIGHT_BROWN_STYLE_BG)

        self.horizontalLayoutCameraProtocol = QtWidgets.QHBoxLayout()
        self.horizontalLayoutCameraProtocol.setObjectName("horizontalLayoutCameraProtocol")
        self.labelCameraProtocol = QtWidgets.QLabel(self.frameCameraProtocol)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.labelCameraProtocol.sizePolicy().hasHeightForWidth())
        self.labelCameraProtocol.setSizePolicy(size_policy)
        self.labelCameraProtocol.setText("Camera Protocol")
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutCameraProtocol.addItem(spacer_item)
        self.labelCameraProtocol.setObjectName("labelCameraProtocol")
        self.horizontalLayoutCameraProtocol.addWidget(self.labelCameraProtocol)
        self.radioButtonCameraProtocolUDP = QtWidgets.QRadioButton(self.frameCameraProtocol)
        self.radioButtonCameraProtocolUDP.setText("UDP")
        self.radioButtonCameraProtocolUDP.setChecked(True)
        self.radioButtonCameraProtocolUDP.setObjectName("radioButtonCameraProtocolUDP")
        self.horizontalLayoutCameraProtocol.addWidget(self.radioButtonCameraProtocolUDP)
        self.radioButtonCameraProtocolTCP = QtWidgets.QRadioButton(self.frameCameraProtocol)
        self.radioButtonCameraProtocolTCP.setText("TCP")
        self.radioButtonCameraProtocolTCP.setObjectName("radioButtonCameraProtocolTCP")
        self.horizontalLayoutCameraProtocol.addWidget(self.radioButtonCameraProtocolTCP)
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutCameraProtocol.addItem(spacer_item)
        self.verticalLayoutFrameCameraProtocol.addLayout(self.horizontalLayoutCameraProtocol)

        self.verticalLayoutInsideLineEditsFrame.addWidget(self.frameCameraProtocol)

        self.verticalLayoutLineEdits.addLayout(self.verticalLayoutInsideLineEditsFrame)

        self.verticalLayoutInsideFrame.addWidget(self.frameLineEdits)

        ################################
        # Add Picture Settings Widgets
        # noinspection PyArgumentList
        self.verticalLayoutInsideFrame.addWidget(self.pic_settings_widgets[Config.PARAM_PICTURE_TYPE_TEMP])
        # noinspection PyArgumentList
        self.verticalLayoutInsideFrame.addWidget(self.pic_settings_widgets[Config.PARAM_PICTURE_TYPE_BACKUP])

        # Ok/Cancel
        self.horizontalLayoutConfirmOkCancel = QtWidgets.QHBoxLayout()
        self.horizontalLayoutConfirmOkCancel.setContentsMargins(0,0,0,0)
        self.horizontalLayoutConfirmOkCancel.setContentsMargins(9,0,9,0)

        self.horizontalLayoutConfirmOkCancel.setObjectName("horizontalLayoutConfirmOkCancel")
        spacer_item_buttons = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutConfirmOkCancel.addItem(spacer_item_buttons)
        self.pushButtonOk = QtWidgets.QPushButton(self.framePictureUploadSettings)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.pushButtonOk.setText("Ok")
        self.pushButtonOk.setStyleSheet("background-color: rgb(200, 200, 200);")

        # noinspection PyArgumentList
        self.horizontalLayoutConfirmOkCancel.addWidget(self.pushButtonOk)
        self.pushButtonCancel = QtWidgets.QPushButton(self.framePictureUploadSettings)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.pushButtonCancel.setText("Cancel")
        self.pushButtonCancel.setStyleSheet("background-color: rgb(200, 200, 200);")
        # noinspection PyArgumentList
        self.horizontalLayoutConfirmOkCancel.addWidget(self.pushButtonCancel)
        self.verticalLayoutInsideFrame.addLayout(self.horizontalLayoutConfirmOkCancel)

        self.verticalLayoutPictureUploadSettings.addLayout(self.verticalLayoutInsideFrame)

        # Add everything under Widget's layout
        # noinspection PyArgumentList
        self.verticalLayoutWidget.addWidget(self.framePictureUploadSettings)

    def set_title(self, cam_description_array):
        cameras = HTML_LINE_BREAK.join(cam_description_array)
        title = PICTURE_UPLOAD_SETTINGS_TITLE_FORMAT.format(cameras)
        self.labelHeaderPictureUploadSettings.setText(title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = WidgetAllPictureSettings()
    ui.set_title(["UI DEMO!"])
    ui.temp_picture_settings.checkBoxGrayscale.setChecked(True)
    ui.show()
    sys.exit(app.exec_())

