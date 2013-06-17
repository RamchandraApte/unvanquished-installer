__license__ = '''
Unvanquished Installer, an installer for Unvanquished (http://unvanquished.net).
Copyright (C) 2012-2013  Ramchandra Apte

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
# TODO BUG: "connecting..." doesn"t show
freeze = True
import sys
import traceback
from PyQt4 import QtCore, QtGui, QtNetwork

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import argparse
        import os
        import stat
        import glob
        import itertools
        parser = argparse.ArgumentParser()
        parser.add_argument("installdir")
        parser.add_argument("uid")
        args = parser.parse_args()
        base_dir = os.path.join(args.installdir, "base")
        try:
            os.makedirs(base_dir)
        except FileExistsError:
            pass  # called when downloads have finished
            # stat.S_IWUSR|stat.S_IXUSR) # rx for owner; none for everybody else

        def recursivechown(dir_, *args, **kwargs):
            for path in itertools.chain((dir_,),
                                        (glob.iglob(os.path.join(dir_, "**")))):
                os.chown(path, *args, **kwargs)
        recursivechown(args.installdir, int(args.uid), -1)
        print("started")
        line = input()
        if line == "chown_root":
            recursivechown(args.installdir, 0, -1)
        elif line == "quit":
            pass
        else:
            raise AssertionError("child process gave incorrect output \"{}\"".format(line))
        sys.exit()

app = QtGui.QApplication(sys.argv)
app.setStyle(QtGui.QStyleFactory.create("oxygen"))
translator = QtCore.QTranslator()
translator.load("hellotr_la")
app.installTranslator(translator)
error_dialog_open = False


def excepthook(exctype, value, tb):
    global error_dialog_open
    if error_dialog_open is False: # To ensure that cases where an error occurs in the error handler, infinite dialogs won't popup.
        error_dialog_open = True
        error_dialog = QtGui.QMessageBox(
            QtGui.QMessageBox.Critical, "Internal Error",
            "Sorry, an internal error has occured. The Unvanquished Installer"
            " can't continue. Please <a href=\"https://github.com/Unvanquished"
            "/Unvanquished/issues\">file a bug report</a> with the diagnostic "
            "information below.")

        error_dialog.setInformativeText("".join(
            traceback.format_exception(exctype, value, tb)))
        error_dialog.exec()
        app.exit()

if __name__=="__main__": sys.excepthook = excepthook
import shutil
import subprocess
from urllib.request import urlopen
import glob
import datetime
import ui_installer
import csv
import io
import os
import time
import tempfile
import math
import itertools
import shutil
import stat
import traceback

authAutomaticNext = False
refs = []
keep_ref = refs.append
#download_dir_url = "http://127.0.0.1:8080/installer/"
download_dir_url = "http://downloads.sourceforge.net/project/unvanquished/Assets/"

UNVANQUISHED_VERSION = "0.16"
STAGES = ("Alpha", "Beta", "RC")
stages_index = {stage[0].lower(): stage for stage in STAGES}

class NoWaitDestructorProcess(QtCore.QProcess):
    def __del__(self):
        self.write("quit\n")
        self.waitForFinished()
    
class FileDownloader:
    completeFilesSize = 0
    average_speed = None
    index = -1
    manager = QtNetwork.QNetworkAccessManager()

    def __init__(self, file_infos):
        self.file_infos = file_infos
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_info)
        self.base_dir = os.path.join(installdir, "base")
        self.install_proc = self.install()

    def install(self):
        # TODO in production installer.py should be removed
        if not freeze:
            proc = popen_root((sys.executable, os.path.abspath("installer.py"),
                          os.path.abspath(installdir), str(os.getuid())),)
        if freeze:
            proc = popen_root((sys.executable,
                               os.path.abspath(installdir), str(os.getuid())),)
        wizard.setEnabled(False)
        wizard.back()
        proc.readyRead.connect(self.readyRead)
        proc.finished.connect(lambda:wizard.setEnabled(True))
        return proc

    def readyRead(self):
        global authAutomaticNext
        if self.install_proc.canReadLine():
            line = self.install_proc.readLine()
            if line == b"": # User cancelled dialog
                wizard.restart()
            else:
                assert line == b"started\n", "Child process gave incorrect output {}".format(line)
                authAutomaticNext = True
                wizard.next()
                authAutomaticNext = False
                self.start_next_download()
            wizard.setEnabled(True)
    
    def connected(self, bytes_received, total_bytes):
        self.total_bytes = total_bytes
        self.lasttime = time.monotonic()
        self.last_bytes_received = bytes_received
        size = int(self.file_infos[self.index]["size"])
        # ui.downloadProgressTableWidget.setItem(self.index, 3,
        # QtGui.QTableWidgetItem(size))
        ui.currentFileProgressBar.setMaximum(size)
        self.download_progress(bytes_received, size)
        self.currentreply.downloadProgress.disconnect()
        self.currentreply.downloadProgress.connect(
            ui.currentFileProgressBar.setValue)
        self.currentreply.downloadProgress.connect(self.download_progress)
        self.currentreply.readyRead.connect(self.write_data)
        self.currentreply.finished.connect(self.start_next_download)

    @property
    def totalDownloaded(self):
        return self.completeFilesSize + self.bytes_received

    @staticmethod
    def eta(total, downloaded, speed):
        try:
            seconds = (total - downloaded) / speed
        except ZeroDivisionError:
            return "∞ (Infinity, will take forever)"
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        if seconds < 1:seconds = 1
        locals_ = locals()
        magnitudes_str = ("{n} {magnitude}".format(n=int(locals_[magnitude]), magnitude=magnitude)
                          for magnitude in ("days", "hours", "minutes", "seconds") if locals_[magnitude])
        eta_str = ", ".join(magnitudes_str)
        return eta_str

    def update_info(self):
        eta_str = self.eta(
            self.total_bytes, self.bytes_received, self.average_speed)
        ui.currentFileETA.setText(eta_str)
        text = "Current download speed: {}/s".format(
            human_readable_size(self.average_speed))
        ui.currentDownloadSpeedLabel.setText(text)
        ui.totalETA.setText(self.eta(
            totalSize, self.totalDownloaded, self.average_speed))

    def download_progress(self, bytes_received, total_bytes):
        if self.timer.isActive() == False:
            self.timer.start(500)
        self.bytes_received = bytes_received
        # print(self.bytes_received)
        current_time = time.perf_counter()
        ui.currentFileDownloadProgress.setText("{} / {}".format(human_readable_size(
            self.bytes_received), human_readable_size(int(self.file_infos[self.index]["size"]))))
        ui.totalDownloadProgress.setText("{} / {}".format(human_readable_size(
            self.totalDownloaded), human_readable_size(totalSize)))
        SMOOTHING_FACTOR = 0.003
        # print(current_time,self.lasttime)
        self.current_speed = (bytes_received - self.last_bytes_received) / \
            (current_time - self.lasttime)
        # print(current_time - self.lasttime, bytes_received -
        # self.last_bytes_received, self.current_speed)
        if self.average_speed is not None:
            self.average_speed = SMOOTHING_FACTOR * \
                self.current_speed + (1 -
                                      SMOOTHING_FACTOR) * self.average_speed
        elif self.current_speed != 0:
            self.average_speed = self.current_speed

        self.lasttime = current_time
        self.last_bytes_received = bytes_received
        ui.totalProgressBar.setValue(
            self.totalDownloaded /
            totalSize *
            2 ** 31 -
            1)

    def write_data(self):
        self.fp.write(self.currentreply.readAll())

    def start_next_download(self):
        self.timer.stop()
        if self.index >= 0:
            shutil.move(self.fp.name, self.filename)
            self.fp.close()
        self.completeFilesSize += int(self.file_infos[self.index]["size"])
        self.index += 1
        try:
            self.filename = self.file_infos[self.index]["filename"]
        except IndexError:
            self.install_proc.write.write(b"chown_root\n")
            wizard.next()
            return
        filename = self.file_infos[self.index]["filename"]
        ui.currentFileName.setText(str(self.file_infos[self.index]["name"] if ismap(filename) else self.file_infos[self.index]["filename"]))
        ui.totalFileProgress.setText("{} out of {}".format(
            self.index, len(self.file_infos)))
        oldSelectionMode = ui.fileInfoTableWidget.selectionMode()
        ui.fileInfoTableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        ui.fileInfoTableWidget.selectRow(self.index)
        ui.fileInfoTableWidget.setSelectionMode(oldSelectionMode)
        self.currentreply = self.manager.get(
            QtNetwork.QNetworkRequest(QtCore.QUrl(download_dir_url + self.filename)))
        self.fp = open(os.path.join(
            self.base_dir, "{}.tmp".format(self.filename)), "ab")
        # if self.fp.tell() ==
        self.currentreply.downloadProgress.connect(self.connected)

wizard = QtGui.QWizard()
ui = ui_installer.Ui_Wizard()
ui.setupUi(wizard)
wizard.page(1).setCommitPage(True)
wizard.setButtonText(wizard.CommitButton, "Install")
#wizard.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(
#    "/home/ramchandra/Pictures/picture_1.png")) # TODO:Replace with Unvanquished banner.
install_dirs = {"posix": "test"}
ui.directoryToInstallInLineEdit.setText(install_dirs[os.name])
browseIcon = QtGui.QIcon.fromTheme(
    "folder-open", QtGui.QIcon("folder-open.png"))
ui.browseButton.setIcon(browseIcon)


def get_dir_and_update_text():
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
    if dialog.exec():
        dir_ = dialog.selectedFiles()[0]
        ui.directoryToInstallInLineEdit.setText(dir_)
ui.browseButton.clicked.connect(get_dir_and_update_text)


def stateChanged(checked):
    if checked == QtCore.Qt.Checked:
        ui.mapsToIncludeTableWidget.selectAll()
    elif checked == QtCore.Qt.Unchecked:
        ui.mapsToIncludeTableWidget.clearSelection()
ui.allCheckBox.stateChanged.connect(stateChanged)
ui.fileInfoCheckBox.stateChanged.connect(ui.fileInfoTableWidget.setVisible)
ui.fileInfoTableWidget.hide()
mirror = "auto"
"&use_mirror={mirror}"
#    subprocess.Popen(path+cmd_args+*args)


def linux_gui_sudo():
    exe = shutil.which("pkexec")
    if exe: return exe
    exes = list(filter(None, map(shutil.which, (
        "kdesudo", "kdesu", "gksudo", "gksu"))))
    if len(exes) == 1:
        return exes[0]
    # Detect the DE and execute gksudo/kdesudo (portions from
    # http://stackoverflow.com/a/2035666)
    desktop_environment = None
    if os.environ.get("KDE_FULL_SESSION") == "true":
        desktop_environment = "kde"
    elif os.environ.get("GNOME_DESKTOP_SESSION_ID"):
        desktop_environment = "gnome"
    else:
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session:
            if "kde" in desktop_session:
                desktop_environment = "kde"
            elif "gnome" in desktop_session or desktop_session == "ubuntu":
                desktop_environment = "gnome"
    if desktop_environment == "kde":
        names = "kdesudo", "kdesu"
    elif desktop_environment == "gnome":
        names = "gksudo", "gksu"
    else:
        names = ()
    exes = list(filter(None, map(shutil.which, names)))
    if exes:
        exe = exes[0]
        return exe

def popen_root(cmd_args, *args, **kwargs):
    # TODO windos
    if os.name == "posix":
        proc = NoWaitDestructorProcess()
        proc.start(linux_gui_sudo(), cmd_args, *args, **kwargs)
        return proc
    elif os.name == "win32":
        pass


def human_readable_size(size):
    MAGNITUDES = ("B", "KiB", "MiB", "GiB")
    assert size >= 0, "size ({}) should be a non-negative integer".format(size)
    if size == 0:
        fraction = 0
        integral = 0
    else:
        fraction, integral = math.modf(math.log(size, 1024))
    return "{n:.1f} {magnitude}".format(n=1024 ** fraction, magnitude=MAGNITUDES[int(integral)])


def ismap(filename):
    return filename.startswith("map-")


def map_info(filename, row_index):
    splitted = os.path.splitext(filename)[0].split("-")
    try:
        version = splitted[2]
    except IndexError:
        version = "Unknown"
    version_first_letter = version[0]
    try:
        versionstr = stages_index[version_first_letter]
    except KeyError:
        version = "Unknown"
    else:
        version = " ".join((versionstr, version[-1]))
    try:
        name = splitted[1].capitalize()
    except IndexError:
        name = filename
    size = file_info_csv[row_index]["size"]
    return name, version, human_readable_size(int(size))


def gen_table(tableWidget, file_info):
    tableWidget.setRowCount(1000)
    tableWidget.setColumnCount(1000)
    for row_index, row in enumerate(file_info):
        for column_index, value in enumerate(map_info(row["filename"], row_index)):
            if isinstance(value, str):
                tableWidget.setItem(
                    row_index, column_index, QtGui.QTableWidgetItem(value))
            else:
                tableWidget.setCellWidget(row_index, column_index, value)

    tableWidget.setRowCount(row_index + 1)
    tableWidget.setColumnCount(column_index + 1)

with urlopen(download_dir_url + "file_info.csv") as f:
    file_info = f.read().decode()
file_info_csv = tuple(csv.DictReader(
    file_info.splitlines(), ("filename", "name", "size", "TODO"), dialect="excel-tab"))
gen_table(ui.mapsToIncludeTableWidget, (
    x for x in file_info_csv if ismap(x["filename"])))


def start_file_downloader(id_):
    global _, totalSize, installdir, downloader
    if id_ == 1 and not authAutomaticNext:
        wizard.button(QtGui.QWizard.CommitButton).hide()
        selected_rows = tuple(file_info_csv[row] for row in set(
            range.row() for range in ui.mapsToIncludeTableWidget.selectedIndexes()))
        notmaps = tuple(row for row in file_info_csv if not ismap(row["filename"]))
        file_infos = selected_rows + notmaps
        gen_table(ui.fileInfoTableWidget, selected_rows + notmaps)
        totalSize = sum(int(row["size"]) for row in file_infos)
        ui.totalProgressBar.setMaximum(2 ** 31 - 1)  # max value of signed int
        installdir = ui.directoryToInstallInLineEdit.text()
        downloader = FileDownloader(file_infos)


def on_finish_button():
    # After the Finish button is clicked.
    
    if ui.displayUnvInAppMenu.isChecked():
        with open("unvanquished.in.desktop") as infp, open("unvanquished.desktop", "w") as outfp:
            outfp.write(infp.read().format(installdir=os.path.abspath(installdir)))
        failed_actions = []
        err_details = ""
        exists = shutil.which("xdg-desktop-menu")
        if exists:
            with subprocess.Popen(("xdg-desktop-menu", "install", "--novendor", outfp.name), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as proc:
                if proc.wait():
                    failed_actions.append("desktop menu entry")
                    err_details+="xdg-desktop-menu error output:\n"+proc.stderr.read().decode(errors="replace")

            with subprocess.Popen(("xdg-icon-resource", "install", "--novendor", "unvanquished.icon"), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as proc:
                    if proc.wait():
                        failed_actions.append("icon")
                        err_details+="xdg-icon-resource error output:\n"+proc.stderr.read().decode(errors="replace")
        else:
            failed_actions = ("desktop menu entry", "icon")
        if failed_actions:
            message_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Error", "Installing the {failed_actions} failed".format(failed_actions = " and ".join(failed_actions)) + ("." if exists else " because XDG utils was not found."))
            message_box.setInformativeText(err_details)
            message_box.exec()
    if ui.runUnvAfterFinish.isChecked():
        subprocess.Popen(os.path.join(installdir, "unvanquished.bin"))

wizard.button(wizard.FinishButton).clicked.connect(on_finish_button)

wizard.currentIdChanged.connect(start_file_downloader)
def main():
    wizard.show()
    app.exec()

if __name__ == "__main__":
    main()