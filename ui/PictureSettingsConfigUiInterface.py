from watch_out_lib.Config import *
from ui.WidgetAllPictureSettings import (WidgetAllPictureSettings,
                                         PICTURE_UPLOAD_SETTINGS_TITLE_FORMAT,
                                         HTML_LINE_BREAK)
from watch_out_lib.MyLogger import logger

from math import floor
import re


class PictureSettingsConfigUiInterface(WidgetAllPictureSettings):
    def __init__(self,
                 config,
                 main_window_on_destroy,
                 main_window_on_ok):
        super(PictureSettingsConfigUiInterface, self).__init__()
        self.config = config
        self.main_window_pic_settings_cancel_slot = main_window_on_destroy
        self.main_window_pic_settings_ok_slot = main_window_on_ok

        self._line_edit_re = re.compile(r"^(?:[a-zA-Z0-9_])+(?:[a-zA-Z0-9_]|\s)*$")
        self.lineEditCameraDescription.editingFinished.connect(self.line_edit_finished)
        self.lineEditCameraDescription.textChanged.connect(self.line_edit_change)

        # Flag used to prevent updating all camera's description when multiple cameras selected.
        self._multiple_cameras_selected = False

        self.widgets = {}
        widget_str_list = ["spinBoxDailyUploadStartHour",
                           "spinBoxDailyUploadStartMinute",
                           "spinBoxDailyUploadStopHour",
                           "spinBoxDailyUploadStopMinute",
                           "comboBoxResolution",
                           "comboBoxPictureFormat",
                           "checkBoxGrayscale",
                           "spinBoxUploadIntervalMinutes",
                           "spinBoxUploadIntervalSeconds",
                           'spinBoxPictureQuality',
                           'spinBoxExpiryWeeks',
                           'spinBoxExpiryDays',
                           "checkBoxUploadEnable",]

        for pic_type in PARAM_PICTURE_TYPE_LIST:
            self.widgets[pic_type] = {}
            for widget_str in widget_str_list:
                self.widgets[pic_type][widget_str] = getattr(self.pic_settings_widgets[pic_type], widget_str)

    def setup_ui(self):
        for pic_type in [PARAM_PICTURE_TYPE_TEMP, PARAM_PICTURE_TYPE_BACKUP]:
            r = self.widgets[pic_type]['comboBoxResolution']
            for res in RESOLUTION_LIST:
                r.addItem(res)
                r.setCurrentIndex(0)

            f = self.widgets[pic_type]['comboBoxPictureFormat']
            for comboBoxPictureFormat in FORMAT_LIST:
                f.addItem(comboBoxPictureFormat)
                f.setCurrentIndex(0)

            self.widgets[pic_type]['checkBoxUploadEnable'].released.connect(self._set_picture_type_upload_style)

        self.pushButtonOk.clicked.connect(self.main_window_pic_settings_ok_slot)
        self.pushButtonCancel.clicked.connect(self.main_window_pic_settings_cancel_slot)

    def _set_picture_type_upload_style(self):
        for pic_type in PARAM_PICTURE_TYPE_LIST:
            is_checked = self.pic_settings_widgets[pic_type].checkBoxUploadEnable.isChecked()
            self.pic_settings_widgets[pic_type].set_style(is_checked)

    def line_edit_finished(self):
        text = self.lineEditCameraDescription.text()
        m = self._line_edit_re.match(text)
        if not m:
            self.lineEditCameraDescription.setText("INVALID")

    def line_edit_change(self):
        text = self.lineEditCameraDescription.text()
        m = self._line_edit_re.match(text)
        if not m:
            self.lineEditCameraDescription.setText(text[0:-1])

    @staticmethod
    def set_combo_box_index(widget, value):
        index = widget.findText(value)
        if index != -1:
            widget.setCurrentIndex(index)
        else:
            widget.setCurrentIndex(widget.findText(DEFAULT_PICTURE_RESOLUTION))

    def set_ui_defaults(self):
        logger.debug("set_ui_defaults")
        for pic_type in PARAM_PICTURE_TYPE_LIST:
            self.widgets[pic_type]['spinBoxDailyUploadStartHour'].setValue(DEFAULT_PICTURE_UPLOAD_START.hour)
            self.widgets[pic_type]['spinBoxDailyUploadStartMinute'].setValue(DEFAULT_PICTURE_UPLOAD_START.minute)
            self.widgets[pic_type]['spinBoxDailyUploadStopHour'].setValue(DEFAULT_PICTURE_UPLOAD_STOP.hour)
            self.widgets[pic_type]['spinBoxDailyUploadStopMinute'].setValue(DEFAULT_PICTURE_UPLOAD_STOP.minute)
            self.set_combo_box_index(self.widgets[pic_type]['comboBoxResolution'], DEFAULT_PICTURE_RESOLUTION)
            self.set_combo_box_index(self.widgets[pic_type]['comboBoxPictureFormat'], DEFAULT_PICTURE_FORMAT)
            self.widgets[pic_type]['checkBoxGrayscale'].setChecked(DEFAULT_PICTURE_GRAYSCALE)
            self.widgets[pic_type]['spinBoxUploadIntervalMinutes'].setValue(int(DEFAULT_PICTURE_UPLOAD_INTERVAL_TIME_DELTA.seconds/60))
            self.widgets[pic_type]['spinBoxUploadIntervalSeconds'].setValue(DEFAULT_PICTURE_UPLOAD_INTERVAL_TIME_DELTA.seconds)
            self.widgets[pic_type]['spinBoxPictureQuality'].setValue(DEFAULT_PICTURE_QUALITY)
            self.widgets[pic_type]['checkBoxUploadEnable'].setChecked(DEFAULT_PICTURE_UPLOAD_ENABLE)
            self.pic_settings_widgets[pic_type].set_style(DEFAULT_PICTURE_UPLOAD_ENABLE)

            t_delta = DEFAULT_BACKUP_PICTURE_EXPIRY_TIME_DELTA
            weeks = int(floor(t_delta.days/7))
            days = t_delta.days - weeks * 7
            self.widgets[pic_type]['spinBoxExpiryWeeks'].setValue(weeks)
            self.widgets[pic_type]['spinBoxExpiryDays'].setValue(days)

        if DEFAULT_CAMERA_PROTOCOL == PROTOCOL_UDP:
            self.radioButtonCameraProtocolUDP.setChecked(True)
        elif DEFAULT_CAMERA_PROTOCOL == PROTOCOL_TCP:
            self.radioButtonCameraProtocolTCP.setChecked(True)
        self.lineEditCameraUrl.setText(DEFAULT_CAMERA_URL)


    def set_ui_multiple_camera_selection(self, cam_index_array):
        logger.debug("set_ui_multiple_camera_selection")
        cam_selection = ["Camera %d" % i for i in cam_index_array]
        cam_selection = HTML_LINE_BREAK.join(cam_selection)
        title = HTML_LINE_BREAK.join(["Multiple Selection Settings", cam_selection])
        self.labelHeaderPictureUploadSettings.setText(PICTURE_UPLOAD_SETTINGS_TITLE_FORMAT.format(title))

        self.lineEditCameraDescription.setText("Multiple Camera Selection (all values set to default, review all before applying)")
        self.lineEditCameraDescription.setDisabled(True)

        self.set_ui_defaults()

    def set_ui_from_config(self, cam_index_array):
        logger.debug("set_ui_from_config: %s" % ["%s" % i for i in cam_index_array])
        if len(cam_index_array) == 1:
            self._set_ui_from_config(cam_index_array[0])
            self._multiple_cameras_selected = False
        else:
            self._multiple_cameras_selected = True
            self.set_ui_multiple_camera_selection(cam_index_array)

    def _set_ui_from_config(self, cam_index):
        logger.debug("_set_ui_from_config: %d" % cam_index)
        camera_description = self.config.get(OPTION_CAMERA_DESCRIPTION,
                                             picture_type=PARAM_PICTURE_TYPE_LIST[0],
                                             cam_index=cam_index)

        title = "Camera Index: %d%s%s" % (cam_index, HTML_LINE_BREAK, camera_description)
        self.labelHeaderPictureUploadSettings.setText(PICTURE_UPLOAD_SETTINGS_TITLE_FORMAT.format(title))

        self.lineEditCameraDescription.setDisabled(False)
        self.lineEditCameraDescription.setText(camera_description)

        v = self.config.get(OPTION_CAMERA_URL, picture_type=PARAM_PICTURE_TYPE_LIST[0], cam_index=cam_index)
        self.lineEditCameraUrl.setText(v)

        v = self.config.get(OPTION_CAMERA_PROTOCOL, picture_type=PARAM_PICTURE_TYPE_LIST[0], cam_index=cam_index)
        if v == PROTOCOL_UDP:
            self.radioButtonCameraProtocolUDP.setChecked(True)
        elif v == PROTOCOL_TCP:
            self.radioButtonCameraProtocolTCP.setChecked(True)

        for pic_type in PARAM_PICTURE_TYPE_LIST:
            v =  self.config.get(OPTION_PICTURE_UPLOAD_START_TIME, picture_type=pic_type, cam_index=cam_index)
            self.widgets[pic_type]['spinBoxDailyUploadStartHour'].setValue(v.hour)
            self.widgets[pic_type]['spinBoxDailyUploadStartMinute'].setValue(v.minute)

            v =  self.config.get(OPTION_PICTURE_UPLOAD_STOP_TIME, picture_type=pic_type, cam_index=cam_index)
            self.widgets[pic_type]['spinBoxDailyUploadStopHour'].setValue(v.hour)
            self.widgets[pic_type]['spinBoxDailyUploadStopMinute'].setValue(v.minute)

            v =  self.config.get(OPTION_PICTURE_RESOLUTION, picture_type=pic_type, cam_index=cam_index)
            self.set_combo_box_index(self.widgets[pic_type]['comboBoxResolution'], v)

            v =  self.config.get(OPTION_PICTURE_FORMAT, picture_type=pic_type, cam_index=cam_index)
            self.set_combo_box_index(self.widgets[pic_type]['comboBoxPictureFormat'], v)

            v =  self.config.get(OPTION_PICTURE_GRAYSCALE, picture_type=pic_type, cam_index=cam_index)
            self.widgets[pic_type]['checkBoxGrayscale'].setChecked(v)

            v =  self.config.get(OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA, picture_type=pic_type, cam_index=cam_index)
            minutes = int(floor(v.seconds/60))
            self.widgets[pic_type]['spinBoxUploadIntervalMinutes'].setValue(minutes)
            self.widgets[pic_type]['spinBoxUploadIntervalSeconds'].setValue(v.seconds - minutes*60)

            v = self.config.get(OPTION_PICTURE_QUALITY, picture_type=pic_type, cam_index=cam_index)
            self.widgets[pic_type]['spinBoxPictureQuality'].setValue(v)

            t_delta = self.config.get(OPTION_PICTURE_EXPIRY_TIME_DELTA, picture_type=pic_type, cam_index=cam_index)
            weeks = int(floor(t_delta.days/7))
            days = t_delta.days - weeks * 7
            self.widgets[pic_type]['spinBoxExpiryWeeks'].setValue(weeks)
            self.widgets[pic_type]['spinBoxExpiryDays'].setValue(days)
            logger.debug(str(t_delta))

            v = self.config.get(OPTION_PICTURE_UPLOAD_ENABLE, picture_type=pic_type, cam_index=cam_index)
            self.widgets[pic_type]['checkBoxUploadEnable'].setChecked(v)

        self._set_picture_type_upload_style()

    def set_config_from_ui(self, cam_index):
        for pic_type in PARAM_PICTURE_TYPE_LIST:
            if not self._multiple_cameras_selected:
                self.config.set(OPTION_CAMERA_DESCRIPTION,
                                self.lineEditCameraDescription.text().strip(),
                                picture_type=pic_type,
                                cam_index=cam_index)

            self.config.set(OPTION_CAMERA_URL,
                            self.lineEditCameraUrl.text(),
                            picture_type=pic_type,
                            cam_index=cam_index)

            if self.radioButtonCameraProtocolUDP.isChecked():
                protocol = PROTOCOL_UDP
            elif self.radioButtonCameraProtocolTCP.isChecked():
                protocol = PROTOCOL_TCP
            else:
                raise Exception("UI BUG: Unknown protocol!")
            self.config.set(OPTION_CAMERA_PROTOCOL, protocol, picture_type=pic_type, cam_index=cam_index)

            hour = self.widgets[pic_type]['spinBoxDailyUploadStartHour'].value()
            minute = self.widgets[pic_type]['spinBoxDailyUploadStartMinute'].value()
            v = datetime.time(hour=hour, minute=minute)
            self.config.set(OPTION_PICTURE_UPLOAD_START_TIME, v, picture_type=pic_type, cam_index=cam_index)

            hour = self.widgets[pic_type]['spinBoxDailyUploadStopHour'].value()
            minute = self.widgets[pic_type]['spinBoxDailyUploadStopMinute'].value()
            v = datetime.time(hour=hour, minute=minute)
            self.config.set(OPTION_PICTURE_UPLOAD_STOP_TIME, v, picture_type=pic_type, cam_index=cam_index)

            v = self.widgets[pic_type]['comboBoxResolution'].currentText()
            self.config.set(OPTION_PICTURE_RESOLUTION, v, picture_type=pic_type, cam_index=cam_index)

            v = self.widgets[pic_type]['comboBoxPictureFormat'].currentText()
            self.config.set(OPTION_PICTURE_FORMAT, v, picture_type=pic_type, cam_index=cam_index)

            v = self.widgets[pic_type]['checkBoxGrayscale'].isChecked()
            self.config.set(OPTION_PICTURE_GRAYSCALE, v, picture_type=pic_type, cam_index=cam_index)

            minute = self.widgets[pic_type]['spinBoxUploadIntervalMinutes'].value()
            second = self.widgets[pic_type]['spinBoxUploadIntervalSeconds'].value()
            v = datetime.timedelta(minutes=minute, seconds=second)
            self.config.set(OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA, v, picture_type=pic_type, cam_index=cam_index)

            v = self.widgets[pic_type]['spinBoxPictureQuality'].value()
            self.config.set(OPTION_PICTURE_QUALITY, v, picture_type=pic_type, cam_index=cam_index)

            v = self.widgets[pic_type]['spinBoxExpiryWeeks'].value() * 7
            v += self.widgets[pic_type]['spinBoxExpiryDays'].value()
            v = datetime.timedelta(days=v)
            self.config.set(OPTION_PICTURE_EXPIRY_TIME_DELTA, v, picture_type=pic_type, cam_index=cam_index)
            logger.debug(str(v))

            v = self.widgets[pic_type]['checkBoxUploadEnable'].isChecked()
            self.config.set(OPTION_PICTURE_UPLOAD_ENABLE, v, picture_type=pic_type, cam_index=cam_index)

    def reset_multiple_cameras_selection_config_update(self):
        self._multiple_cameras_selected = False

    # noinspection PyPep8Naming
    def closeEvent(self, QCloseEvent=None):
        self.main_window_pic_settings_cancel_slot()
