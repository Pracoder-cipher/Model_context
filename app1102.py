import sys
import re
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFrame, QLineEdit, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtGui import QPixmap

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)
        
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == "1111" and password == "1111":
            self.dashboard = DashboardApp()
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid Credentials. Try again.")

class DashboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard UI")
        self.setGeometry(100, 100, 800, 500)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Header Section
        header = QHBoxLayout()
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: black; color: white; padding: 10px;")
        
        title = QLabel("Hello User,")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        profile_icon = QLabel()
        profile_pixmap = QPixmap("profile.png").scaled(30, 30)
        profile_icon.setPixmap(profile_pixmap)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(profile_icon)
        header_frame.setLayout(header)
        main_layout.addWidget(header_frame)
        
        # Content Section
        content_layout = QHBoxLayout()
        
        sections = [
            ("Software Approval", "software.png", self.software_approval_action),
            ("Report Generation", "report.png", self.report_generation_action),
            ("Analysis Report", "analysis.png", self.analysis_report_action)
        ]
        
        for title, image, action in sections:
            section_layout = QVBoxLayout()
            
            label = QLabel(title)
            label.setStyleSheet("font-size: 14px; font-weight: bold; text-align: center;")
            
            img_label = QLabel()
            pixmap = QPixmap(image).scaled(100, 100)
            img_label.setPixmap(pixmap)
            img_label.setStyleSheet("margin: 10px auto;")
            
            button = QPushButton("Open")
            button.setStyleSheet("padding: 5px; background-color: #0078D7; color: white; border-radius: 5px;")
            button.clicked.connect(action)
            
            section_layout.addWidget(label)
            section_layout.addWidget(img_label)
            section_layout.addWidget(button)
            section_layout.addStretch()
            
            content_layout.addLayout(section_layout)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
    
    def software_approval_action(self):
        self.software_window = SoftwareApprovalScreen()
        self.software_window.show()
    
    def report_generation_action(self):
        self.report_window = ReportGenerationScreen()
        self.report_window.show()
    
    def analysis_report_action(self):
        self.analysis_window = AnalysisReportScreen()
        self.analysis_window.show()

class SoftwareApprovalScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Approval")
        self.setGeometry(150, 150, 600, 450)
        
        layout = QVBoxLayout()
        
        self.upload_button = QPushButton("Upload Excel File")
        self.upload_button.clicked.connect(self.upload_file)
        
        self.search_label = QLabel("Search Data:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_parameter)  # Live Search

        self.table = QTableWidget()
        
        layout.addWidget(self.upload_button)
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.data = None
    
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            self.data = pd.read_excel(file_path)
            QMessageBox.information(self, "Success", "File uploaded successfully!")
            self.display_data(self.data)  # Display full data after upload
    
    def display_data(self, df):
        """ Populate the QTableWidget with Excel data """
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        self.table.resizeColumnsToContents()

        # Enable live search    
    def search_parameter(self):
        if self.data is None:
            QMessageBox.warning(self, "Error", "Please upload an Excel file first.")
            return
    
        parameter = self.search_input.text().strip()
        if not parameter:
            QMessageBox.warning(self, "Error", "Please enter a search parameter.")
            return

        try:
            # Escape special characters in the parameter
            escaped_parameter = re.escape(parameter)

            # Apply filtering
            filtered_data = self.data[
                self.data.apply(lambda row: row.astype(str).str.contains(escaped_parameter, case=False, na=False).any(), axis=1)
            ]

            if filtered_data.empty:
                QMessageBox.warning(self, "No Results", "No matching parameter found.")
                return

            # Update table with search results
            self.table.setRowCount(filtered_data.shape[0])
            self.table.setColumnCount(filtered_data.shape[1])
            self.table.setHorizontalHeaderLabels(filtered_data.columns)

            for i, row in filtered_data.iterrows():
                for j, value in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

class ReportGenerationScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report Generation")
        self.setGeometry(150, 150, 500, 400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Report Generation Screen"))
        self.setLayout(layout)

class AnalysisReportScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analysis Report")
        self.setGeometry(150, 150, 500, 400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Analysis Report Screen"))
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec())
