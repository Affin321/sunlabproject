import sys
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, \
    QTableWidget, QHeaderView, QTableWidgetItem, QHBoxLayout, QSplitter
import firebase_admin
from firebase_admin import credentials, firestore

# This part gets the primary generated key from the firebase database from the service key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
Cloudfirestore = firestore.client()


# The Main window that shows 3 different buttons which are Access, Users, and Admin and has a textbox field
class AccessWindowPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("The Main panel")
        self.setGeometry(300, 200, 300, 200)
        self.Text_Access = QVBoxLayout(self)
        self.Text_Accessfield = QLabel("Enter your Access ID for the access panel")
        self.Text_Access.addWidget(self.Text_Accessfield)
        self.AccessIdforPSU = QLineEdit()
        self.Text_Access.addWidget(self.AccessIdforPSU)
        self.ButtonAccess = QPushButton("Enter")
        self.ButtonAccess.clicked.connect(self.Valid_ACCESSPIN)
        self.Text_Access.addWidget(self.ButtonAccess)

    #  checks if the entered id is the same as the one from the firebase
    def Valid_ACCESSPIN(self):
        Valid_Pin = self.AccessIdforPSU.text().strip()

        if self._Access_Is_Correct(Valid_Pin):
            entry_input = self._get_the_logsfromusers(Valid_Pin)
            if self._Access_Is_Correct(Valid_Pin):
                entry_forUsers = self._logfromACCESS_(Valid_Pin)
                if entry_input:
                    self._New_timestamp(entry_forUsers)
                    QMessageBox.information(self, "These logs were able to be put within the database", "Next")
                else:
                    self._Put_in_new_logs_ACCESS(Valid_Pin, entry_forUsers)
                    QMessageBox.information(self, "Success, These logs were able to be put within the database",
                                            "Next")
            else:
                QMessageBox.warning(self, "Not able to access the database", "Please put a new correct ID")

    # returns true if the acces pin is 9 digits and there are no letters
    def _Access_Is_Correct(self, Firebase_pin):
        return Firebase_pin.isdigit() and len(Firebase_pin) == 9

    @staticmethod
    def _get_the_logsfromusers(Firebase_pin):
        infofrom_Users = Cloudfirestore.collection('USERS').document(Firebase_pin).get()
        return infofrom_Users.to_dict() if infofrom_Users.exists else None

    def _get_the_logsfromAccess(self, Firebase_pin):
        Accesslogs = Cloudfirestore.collection('ACCESS').where("ID", "=", Firebase_pin).where.limit(1).stream()
        return next((log for log in Accesslogs if log.to_dict()['ID'] == Firebase_pin), None)

    def _running_time(self, appear_show):
        Time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _Put_New_logs_on_main(self, Firebase_pin, Entry_input):
        Shows_table = Cloudfirestore.collection('ACCESS').where("ID", "==", Firebase_pin).stream()
        iteration_entry = sum(1 for _ in Shows_table)
        Table_multiple_PIN = f"Log #{iteration_entry + 1}"
        Time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Cloudfirestore.collection('ACCESS').document(Table_multiple_PIN).set({
            "ID": Firebase_pin,
            "Name": Entry_input.get("Name"),
            "EntryTimeStamp": Time_now,
            "ExitTimeStamp": "N/A"
        })



# This is the admin window pannel that asks for the admin pin
class AdminWindowPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.Newwindow = None
        self.setWindowTitle("Admin")
        self.setGeometry(500, 200, 300, 200)
        self.Admin_Box = QVBoxLayout(self)
        self.setLayout(self.Admin_Box)
        self.Admin_Label = QLabel("Please Enter The Admin ID")
        self.Admin_Box.addWidget(self.Admin_Label)
        self.ADMINID = QLineEdit()
        self.Admin_Box.addWidget(self.ADMINID)
        self.Admin_Button = QPushButton("Sign IN")
        self.Admin_Button.clicked.connect(self.ACCESS_PIN)
        self.Admin_Box.addWidget(self.Admin_Button)

    # checks if the admin pin is the same as the admin pin
    def ACCESS_PIN(self):
        Faculty_Pass = self.ADMINID.text()
        findadmin = Cloudfirestore.collection('USERS').where('Name', '==', 'admin').stream()
        Find_Logs = False
        for admin_user in findadmin:
            admin_data = admin_user.to_dict()
            if 'ID' in admin_data and admin_data['ID'] == Faculty_Pass:
                Find_Logs = True
                break
        if Find_Logs:
            self.BrandWindow = admintables()

            self.BrandWindow.show()

        else:
            QMessageBox.warning(self, "Wrong Admin", "Enter a correct ID")

# window for the two tables for users and history logs
class admintables(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All the Logs")
        self.showMaximized()

        self.adminalayout = QHBoxLayout()

        self.middleDivider = QSplitter(Qt.Orientation.Horizontal)

        # makes the tbale on the left side for users
        self.userTables = QTableWidget()
        self.userTables.setColumnCount(4)
        self.userTables.setHorizontalHeaderLabels(["Name", "ID", "Status", "Action"])
        self.userTables.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # table for the access logs for history
        self.adminlogsTable = QTableWidget()
        self.adminlogsTable.setColumnCount(4)  # Increase column count to 4
        self.adminlogsTable.setHorizontalHeaderLabels(["Name", "ID", "ENTRY", "EXIT"])
        self.adminlogsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.middleDivider.addWidget(self.userTables)
        self.middleDivider.addWidget(self.adminlogsTable)

        self.adminalayout.addWidget(self.middleDivider)
        self.setLayout(self.adminalayout)

        self.loadusersfromFirebase()
        self.fillinAccesslogstable()

    def loadusersfromFirebase(self):
        user_docs = Cloudfirestore.collection('USERS').stream()
        self.userTables.setRowCount(0)

        # gets all the people from the USERS databse on firebase and inputs it into the table
        for i, doc in enumerate(user_docs):
            doc_dict = doc.to_dict()
            self.userTables.insertRow(i)

            # Add data
            self.userTables.setItem(i, 0, QTableWidgetItem(doc_dict.get('Name', 'N/A')))
            self.userTables.setItem(i, 1, QTableWidgetItem(doc_dict.get('ID', 'N/A')))
            self.userTables.setItem(i, 2, QTableWidgetItem(doc_dict.get('Status', 'N/A')))

            # adds button to the action colum, if they are suspended, it makes the button to 'activate'
            # if they are active, makes the button to 'ban'
            btn = QPushButton("Activate" if doc_dict.get('Status') == 'suspended' else "Ban")
            btn.clicked.connect(lambda checked, doc_id=doc.id: self.changeStatusinfirebase(doc_id))
            self.userTables.setCellWidget(i, 3, btn)

    def changeStatusinfirebase(self, doc_id):
        doc = Cloudfirestore.collection('USERS').document(doc_id).get().to_dict()
        new_status = 'active' if doc.get('Status') == 'suspended' else 'suspended'
        Cloudfirestore.collection('USERS').document(doc_id).update({"Status": new_status})
        self.loadusersfromFirebase()  # Refresh the table

    def fillinAccesslogstable(self):
        allacceslogsfromFirebase = Cloudfirestore.collection('ACCESS').stream()
        self.adminlogsTable.setRowCount(0)

        for i, doc in enumerate(allacceslogsfromFirebase):
            logsInfomation = doc.to_dict()
            self.adminlogsTable.insertRow(i)

            # populates the table from the databse or if it dosent exist, sets it to 'N/A'
            self.adminlogsTable.setItem(i, 0, QTableWidgetItem(logsInfomation.get('Name', 'N/A')))
            self.adminlogsTable.setItem(i, 1, QTableWidgetItem(logsInfomation.get('ID', 'N/A')))
            self.adminlogsTable.setItem(i, 2, QTableWidgetItem(logsInfomation.get('EntryTimestamp', 'N/A')))
            self.adminlogsTable.setItem(i, 3, QTableWidgetItem(logsInfomation.get('ExitTimestamp', 'N/A')))


class FirstPanelWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Access/Users")
        self.setGeometry(500, 200, 300, 200)
        self.MainPanelWindowLayout()

   #main window to open the sign in/out or admin window
    def MainPanelWindowLayout(self):
        AccessHorizantalbox = QVBoxLayout(self)
        MainPanel_Label = QLabel("Please select one of the following options:")
        AccessHorizantalbox.addWidget(MainPanel_Label)

        FirstAccess_Button = QPushButton("Access")
        FirstAccess_Button.clicked.connect(self.openFirstwindow)
        AccessHorizantalbox.addWidget(FirstAccess_Button)

        SecondButton = QPushButton("Admin")
        SecondButton.clicked.connect(self.DisplaylogsfromAdminpanel)
        AccessHorizantalbox.addWidget(SecondButton)

    # This definition shows the first window within the GUI to display the other buttons like Admin,Button, and Access
    def openFirstwindow(self):
        self.FirstAccessWindow = AccessWindowPanel()
        self.FirstAccessWindow.show()

    # This shows the admin panel whenever the admin button is pressed
    def DisplaylogsfromAdminpanel(self):
        self.AdminPanelWindow = AdminWindowPanel()
        self.AdminPanelWindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = FirstPanelWindow()
    main_window.show()
    sys.exit(app.exec())
