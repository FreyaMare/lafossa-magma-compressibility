"""The About window."""
import os
import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QFrame

from . import __version__

AUTHOR = "Freya Mohammadian"
EMAIL = "freya.mohammadian@gmail.com"
GITHUB = "https://github.com/FreyaMare"
LINKEDIN = "https://www.linkedin.com/in/freya-mohammadian-14614a135"
APP_NAME = "Magma Compressibility and Surface Uplift"


def _resource(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, rel)


def _rule():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color:#cdd6e0")
    return line


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedWidth(600)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 22, 24, 18)
        lay.setSpacing(10)

        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QPixmap(_resource(os.path.join("assets", "app.png"))).scaled(
            72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setFixedSize(80, 80)
        head.addWidget(icon, 0, Qt.AlignTop)
        title = QLabel(f"<div style='font-size:16pt;font-weight:600;color:#1F4E79'>{APP_NAME}</div>"
                       f"<div style='color:#5b6b7b;margin-top:2px'>Version {__version__} · Windows desktop edition</div>"
                       "<div style='margin-top:8px;color:#1b2631'>From the chemistry of a magma to the uplift of the "
                       "ground: how much of an injected magma volume is taken up by compressing the magma already "
                       "stored in a reservoir, and how much lifts the surface — for any volcano.</div>")
        title.setWordWrap(True)
        head.addWidget(title, 1)
        lay.addLayout(head)
        lay.addWidget(_rule())

        dev = QLabel(
            "<div style='font-weight:600;color:#1F4E79;font-size:11pt'>Developer</div>"
            f"<div style='margin-top:4px'>This application was developed by <b>{AUTHOR}</b>.</div>"
            "<table cellspacing='0' cellpadding='3' style='margin-top:6px'>"
            f"<tr><td style='color:#5b6b7b'>E-mail</td><td><a href='mailto:{EMAIL}'>{EMAIL}</a></td></tr>"
            f"<tr><td style='color:#5b6b7b'>GitHub</td><td><a href='{GITHUB}'>github.com/FreyaMare</a></td></tr>"
            f"<tr><td style='color:#5b6b7b'>LinkedIn&nbsp;&nbsp;</td><td><a href='{LINKEDIN}'>"
            "linkedin.com/in/freya-mohammadian-14614a135</a></td></tr></table>")
        dev.setOpenExternalLinks(True)
        dev.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lay.addWidget(dev)
        lay.addWidget(_rule())

        credits = QLabel(
            "<div style='font-weight:600;color:#1F4E79;font-size:11pt'>Built on</div>"
            "<ul style='margin-left:-20px;margin-top:4px'>"
            "<li><b>EVo</b> 1.1.0 — thermodynamic degassing model (P. Liggins, O. Shorttle, P. B. Rimmer; "
            "<a href='https://github.com/pipliggins/EVo'>github.com/pipliggins/EVo</a>), GPL-3.0</li>"
            "<li><b>dMODELS</b> — analytical deformation sources (M. Battaglia, P. F. Cervelli, J. R. Murray, USGS), "
            "Python port dmodelspy 0.2 by W. Crawford, GPL-3.0</li>"
            "<li>Qt for Python (PySide6), NumPy, SciPy, pandas, pydantic and Matplotlib</li></ul>")
        credits.setOpenExternalLinks(True)
        credits.setWordWrap(True)
        credits.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lay.addWidget(credits)
        lay.addWidget(_rule())

        lic = QLabel(f"<div style='color:#5b6b7b;font-size:9pt'>© 2026 {AUTHOR}. Free software under the GNU General "
                     "Public License, version 3 or later. It is provided without any warranty; see the licence for "
                     "details.</div>")
        lic.setWordWrap(True)
        lay.addWidget(lic)

        buttons = QHBoxLayout()
        b_lic = QPushButton("Licence…")
        b_lic.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(_resource("LICENSE.txt"))))
        b_close = QPushButton("Close")
        b_close.setDefault(True)
        b_close.clicked.connect(self.accept)
        buttons.addWidget(b_lic)
        buttons.addStretch(1)
        buttons.addWidget(b_close)
        lay.addLayout(buttons)
