import sys
import os
from pathlib import Path
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.database.db_manager import init_db
from app.controllers.transaction_controller import TransactionController
from app.controllers.settings_controller import SettingsController
from app.controllers.dashboard_controller import DashboardController
from app.controllers.snapshot_controller import SnapshotController
from app.controllers.reports_controller import ReportsController

def main():
    # 1. Initialize DB
    init_db()

    # 2. Configure Qt application (QApplication is required by QtCharts)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
    
    app = QApplication(sys.argv)
    
    # Required by QML Settings module to save window geometry
    app.setOrganizationName("OpenSource")
    app.setApplicationName("OpenTradingTracker")
    
    # Set Application Icon
    icon_path = Path(__file__).parent / "assets" / "icon.svg"
    app.setWindowIcon(QIcon(os.fspath(icon_path)))

    # 3. Create engine and controllers
    engine = QQmlApplicationEngine()
    
    tx_controller = TransactionController()
    settings_controller = SettingsController()
    dashboard_controller = DashboardController()
    snapshot_controller = SnapshotController()
    reports_controller = ReportsController()
    
    # 4. Inject controllers
    engine.rootContext().setContextProperty("txController", tx_controller)
    engine.rootContext().setContextProperty("settingsController", settings_controller)
    engine.rootContext().setContextProperty("dashboardController", dashboard_controller)
    engine.rootContext().setContextProperty("snapshotController", snapshot_controller)
    engine.rootContext().setContextProperty("reportsController", reports_controller)
    
    # 5. Load main view (Main.qml)
    qml_file = Path(__file__).parent / "app" / "views" / "Main.qml"
    engine.load(os.fspath(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    # 6. Execute main loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
