from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QObject

from watch_out_lib.Config import *
from ui.PictureSettingsConfigUiInterface import PictureSettingsConfigUiInterface
from ui.MainWindow import *

from watch_out_lib.MyLogger import logger
import watch_out_lib.MyLogger

from math import floor
import sys
from threading import Thread
import time


class Configurator(Ui_MainWindow, QObject):

    def __init__(self, verbosity):
        super(Configurator, self).__init__()
        self._main_window = None
        self._data_usage_style = None
        self._config = Config()
        self._disable_bandwidth_usage_update = False
        self._pic_settings_config_ui_interface = PictureSettingsConfigUiInterface(self._config,
                                                                                  self.pic_settings_cancel_slot,
                                                                                  self.pic_settings_ok_slot)
        self._camera_selection_checkbox = {}

        watch_out_lib.MyLogger.MyLogger.set_default_class_level(verbosity)

    def setupUi(self, main_window):
        super(Configurator, self).setupUi(main_window)
        self._main_window = main_window
        self._pic_settings_config_ui_interface.setup_ui()
        for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            self._camera_selection_checkbox[i] = getattr(self, "checkBoxCam%d" % i)
        setattr(self._main_window, 'closeEvent', self.closeEvent)
        self._main_window.setStyleSheet(APP_COLOR_BG)

    # noinspection PyTypeChecker
    def setup(self):
        self._pic_settings_config_ui_interface.set_ui_from_config([i for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1)])
        self.pushButtonClose.clicked.connect(self._terminate_program)
        self.pushButtonApply.clicked.connect(self._write_config)
        self.horizontalScrollBar_day_of_month_data_cap_reset.valueChanged.connect(self._update_day_data_cap_reset)

        self.pushButton_reset_data_usage.clicked.connect(self._reset_data_usage)
        self.pushButton_reload_config_file.clicked.connect(self._init_gui_with_config_value)
        self.pushButtonConfigureCameras.clicked.connect(self._configure_cameras)

        self._data_usage_style = self.label_data_usage_value.styleSheet()

        self._update_camera_checkbox_description()
        self._update_camera_style()

        # update ui from config on startup
        self._init_gui_with_config_value()

        # noinspection PyCallByClass
        QTimer.singleShot(1000, self._update_data_usage)

    def _configure_cameras(self):
        logger.debug("########################################")
        logger.debug("_configure_cameras")
        logger.debug("########################################")
        cam_index_array = []
        for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            if self._camera_selection_checkbox[i].isChecked():
                cam_index_array.append(i)
        if len(cam_index_array) == 0:
            return
        self._pic_settings_config_ui_interface.set_ui_from_config(cam_index_array)
        self._pic_settings_config_ui_interface.update()
        self._pic_settings_config_ui_interface.show()
        self._main_window.setDisabled(True)

    def _write_config(self):
        allowance = self.spinBox_data_allowance_gb_x_100.value() * 100 + \
                    self.spinBox_data_allowance_gb_x_10.value() * 10 + \
                    self.spinBox_data_allowance_gb_x_1.value()
        self._config.set(OPTION_MONTHLY_DATA_ALLOWANCE_GB, str(allowance))

        timeout = self.spinBox_ffmpeg_timeout_s.value()
        self._config.set(OPTION_FFMPEG_TIMEOUT, str(timeout))

        self._config.set(OPTION_DAY_OF_MONTH_DATA_CAP_RESET,
                         self.horizontalScrollBar_day_of_month_data_cap_reset.value())

        if self._disable_bandwidth_usage_update:
            self._disable_bandwidth_usage_update = False
            self.label_data_usage_value.setStyleSheet(self._data_usage_style)
            self.label_data_usage_value.setText("0")
            self._config.set(OPTION_CURRENT_MONTH_DATA_USAGE_KB, 0)
            # noinspection PyCallByClass,PyTypeChecker
            QTimer.singleShot(1000, self._update_data_usage)
        else:
            v = int(self.label_data_usage_value.text())
            self._config.set(OPTION_CURRENT_MONTH_DATA_USAGE_KB, v)

        margin = self.spinBox_upload_stop_margin_MB.value()
        margin = int(margin / 32) * 32
        if margin == 0:
            margin = 32
        if margin > 512:
            margin = 512
        self._config.set(OPTION_UPLOAD_STOP_MARGIN_MB, margin)

        self._config.write()

        self.pushButtonApply.setStyleSheet("background-color: green")
        self.pushButtonApply.update()

        t = Thread(target=self._push_button_apply_back_to_gray)
        t.start()

    def _init_gui_with_config_value(self):
        self._pic_settings_config_ui_interface.set_ui_from_config([i for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1)])

        allowance = int(self._config.get(OPTION_MONTHLY_DATA_ALLOWANCE_GB))
        all_100s = int(floor(allowance / 100))
        all_10s = int(floor(allowance - all_100s * 100) / 10)
        all_1s = allowance - all_100s * 100 - all_10s * 10
        self.spinBox_data_allowance_gb_x_100.setValue(all_100s)
        self.spinBox_data_allowance_gb_x_10.setValue(all_10s)
        self.spinBox_data_allowance_gb_x_1.setValue(all_1s)

        timeout = int(self._config.get(OPTION_FFMPEG_TIMEOUT))
        self.spinBox_ffmpeg_timeout_s.setValue(timeout)

        day = int(self._config.get(OPTION_DAY_OF_MONTH_DATA_CAP_RESET))
        self.horizontalScrollBar_day_of_month_data_cap_reset.setValue(day)

        bandwidth_usage_kb = self._config.get(OPTION_CURRENT_MONTH_DATA_USAGE_KB)
        self.label_data_usage_value.setText(str(bandwidth_usage_kb))

        margin = int(self._config.get(OPTION_UPLOAD_STOP_MARGIN_MB))
        self.spinBox_upload_stop_margin_MB.setValue(margin)

    def _reset_data_usage(self):
        self._disable_bandwidth_usage_update = True
        self.label_data_usage_value.setText('0')
        self._config.set(OPTION_CURRENT_MONTH_DATA_USAGE_KB, 0)

    def _push_button_apply_back_to_gray(self):
        time.sleep(1)
        self.pushButtonApply.setStyleSheet("background-color: lightgray")

    def _update_day_data_cap_reset(self):
        v = self.horizontalScrollBar_day_of_month_data_cap_reset.value()
        self.label_day_of_month_data_cap_reset_live_value.setText(str(v))

    def _update_data_usage(self):
        if self._disable_bandwidth_usage_update:
            self.label_data_usage_value.setStyleSheet("background-color: yellow")
            self.label_data_usage_value.setText("Apply Config to reset data usage,\nread config or exit to undo!")
        else:
            v = self._config.read(OPTION_CURRENT_MONTH_DATA_USAGE_KB)
            # v = self._config.get()
            self.label_data_usage_value.setText(str(v))
            # noinspection PyCallByClass,PyTypeChecker
            QTimer.singleShot(1000, self._update_data_usage)

    def _terminate_program(self):
        self._main_window.destroy()
        sys.exit(0)

    def _update_camera_style(self):
        for cam_index in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            temp_en = self._config.get(OPTION_PICTURE_UPLOAD_ENABLE,
                                       picture_type=PARAM_PICTURE_TYPE_TEMP,
                                       cam_index=cam_index)
            backup_en = self._config.get(OPTION_PICTURE_UPLOAD_ENABLE,
                                         picture_type=PARAM_PICTURE_TYPE_BACKUP,
                                         cam_index=cam_index)

            cam_widget_checkbox_main_ui = self._camera_selection_checkbox[cam_index]

            if temp_en and backup_en:
                cam_widget_checkbox_main_ui.setStyleSheet(GREEN_STYLE_BG)
            elif temp_en:
                cam_widget_checkbox_main_ui.setStyleSheet(BLUE_STYLE_BG)
            elif backup_en:
                cam_widget_checkbox_main_ui.setStyleSheet(YELLOW_STYLE_BG)
            else:
                cam_widget_checkbox_main_ui.setStyleSheet(RED_STYLE_BG)

            cam_widget_checkbox_main_ui.update()

    def _update_camera_checkbox_description(self):
        for cam_index in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            cam_widget_checkbox_main_ui = self._camera_selection_checkbox[cam_index]
            config_camera_description = self._config.get(OPTION_CAMERA_DESCRIPTION,
                                                         picture_type=PARAM_PICTURE_TYPE_TEMP,
                                                         cam_index=cam_index)
            cam_widget_checkbox_main_ui.setText("Camera %d: %s" % (cam_index, config_camera_description))

    # noinspection PyPep8Naming
    def closeEvent(self, QCloseEvent=None):
        sys.exit(0)

    ############################################
    # Picture Upload Settings Ui Slots
    ############################################
    def pic_settings_cancel_slot(self):
        logger.debug("pic_settings_cancel_slot")
        self._pic_settings_config_ui_interface.destroy()
        self._main_window.setDisabled(False)

    def pic_settings_ok_slot(self):
        logger.debug("pic_settings_ok_slot")
        self._main_window.setDisabled(False)
        for cam_index in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            cam_widget_checkbox_main_ui = self._camera_selection_checkbox[cam_index]
            if not cam_widget_checkbox_main_ui.isChecked():
                continue
            self._pic_settings_config_ui_interface.set_config_from_ui(cam_index)
        self._pic_settings_config_ui_interface.destroy()
        self._update_camera_style()
        # Update MainWindow camera checkbox description
        self._update_camera_checkbox_description()
        self._pic_settings_config_ui_interface.reset_multiple_cameras_selection_config_update()


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Watch Out! Configurator')
    parser.add_argument('-v',
                        action='count',
                        dest='verbosity',
                        default=0,
                        help='Output Debugging Information, can be specified multiple times.')

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    app = QApplication(sys.argv)
    # noinspection PyArgumentList
    main_window = QMainWindow()

    ui = Configurator(args.verbosity)
    ui.setupUi(main_window)
    ui.setup()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
