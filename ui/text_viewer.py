"""
Text viewer component for the transcription application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QClipboard, QGuiApplication

class TextView(QWidget):
    """
    Widget for viewing and exporting transcribed text.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("Transcription will appear here")
        self.layout.addWidget(self.text_edit, 1)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.on_copy_clicked)
        button_layout.addWidget(self.copy_button)
        
        self.save_button = QPushButton("Save as TXT")
        self.save_button.clicked.connect(self.on_save_clicked)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        button_layout.addWidget(self.clear_button)
        
        self.layout.addLayout(button_layout)
        
        # Update button states
        self._update_button_states()
    
    def set_text(self, text):
        """
        Sets the text to be displayed.
        
        Args:
            text (str): Transcribed text
        """
        self.text_edit.setPlainText(text)
        self._update_button_states()
    
    def get_text(self):
        """
        Returns the current text.
        
        Returns:
            str: Current text
        """
        return self.text_edit.toPlainText()
    
    def on_copy_clicked(self):
        """
        Handler for the copy button click.
        """
        text = self.text_edit.toPlainText()
        if text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(
                self,
                "Copied",
                "Text copied to clipboard."
            )
    
    def on_save_clicked(self):
        """
        Handler for the save button click.
        """
        text = self.text_edit.toPlainText()
        if text:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Transcription",
                "",
                "Text Files (*.txt)"
            )
            
            if file_path:
                # Add .txt extension if not present
                if not file_path.lower().endswith(".txt"):
                    file_path += ".txt"
                
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    
                    QMessageBox.information(
                        self,
                        "Saved",
                        f"Transcription saved to {file_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error saving file: {str(e)}"
                    )
    
    def on_clear_clicked(self):
        """
        Handler for the clear button click.
        """
        if self.text_edit.toPlainText():
            confirm = QMessageBox.question(
                self,
                "Confirm Clear",
                "Are you sure you want to clear the text?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.text_edit.clear()
                self._update_button_states()
    
    def _update_button_states(self):
        """
        Updates the state of buttons based on the text content.
        """
        has_text = bool(self.text_edit.toPlainText())
        self.copy_button.setEnabled(has_text)
        self.save_button.setEnabled(has_text)
        self.clear_button.setEnabled(has_text)


