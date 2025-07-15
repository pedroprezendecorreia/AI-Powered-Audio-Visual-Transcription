"""
Batch processing list component for the transcription application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal

class BatchList(QWidget):
    """
    Widget for managing the list of files for batch processing.
    """
    # Signals
    batch_process_requested = Signal(list)
    item_removed = Signal(int)
    folder_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("Files for Batch Processing")
        self.layout.addWidget(title_label)
        
        # Add buttons
        add_layout = QHBoxLayout()
        
        self.add_folder_button = QPushButton("Add Folder")
        self.add_folder_button.clicked.connect(self.on_add_folder_clicked)
        add_layout.addWidget(self.add_folder_button)
        
        add_layout.addStretch()
        
        self.layout.addLayout(add_layout)
        
        # File list
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.process_all_button = QPushButton("Process All")
        self.process_all_button.clicked.connect(self.on_process_all_clicked)
        button_layout.addWidget(self.process_all_button)
        
        self.remove_selected_button = QPushButton("Remove Selected")
        self.remove_selected_button.clicked.connect(self.on_remove_selected_clicked)
        button_layout.addWidget(self.remove_selected_button)
        
        self.clear_all_button = QPushButton("Clear List")
        self.clear_all_button.clicked.connect(self.on_clear_all_clicked)
        button_layout.addWidget(self.clear_all_button)
        
        self.layout.addLayout(button_layout)
        
        # Update button states
        self._update_button_states()
    
    def add_item(self, path):
        """
        Adds an item to the batch list.
        
        Args:
            path (str): File path or YouTube URL
        """
        # Check if the item already exists in the list
        for i in range(self.file_list.count()):
            if self.file_list.item(i).text() == path:
                QMessageBox.information(
                    self,
                    "Duplicate Item",
                    "This item is already in the processing list."
                )
                return
        
        # Add new item
        item = QListWidgetItem(path)
        self.file_list.addItem(item)
        
        # Update button states
        self._update_button_states()
    
    def on_add_folder_clicked(self):
        """
        Handler for the add folder button click.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Audio/Video Files",
            ""
        )
        
        if folder_path:
            self.folder_selected.emit(folder_path)
    
    def on_process_all_clicked(self):
        """
        Handler for the process all button click.
        """
        if self.file_list.count() > 0:
            items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            self.batch_process_requested.emit(items)
    
    def on_remove_selected_clicked(self):
        """
        Handler for the remove selected button click.
        """
        selected_items = self.file_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.file_list.row(item)
                self.file_list.takeItem(row)
                self.item_removed.emit(row)
            
            # Update button states
            self._update_button_states()
    
    def on_clear_all_clicked(self):
        """
        Handler for the clear list button click.
        """
        if self.file_list.count() > 0:
            confirm = QMessageBox.question(
                self,
                "Confirm Clear",
                "Are you sure you want to clear the entire list?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.file_list.clear()
                # Update button states
                self._update_button_states()
    
    def _update_button_states(self):
        """
        Updates the state of buttons based on the list content.
        """
        has_items = self.file_list.count() > 0
        self.process_all_button.setEnabled(has_items)
        self.clear_all_button.setEnabled(has_items)
        
        has_selection = len(self.file_list.selectedItems()) > 0
        self.remove_selected_button.setEnabled(has_selection)
    
    def get_all_items(self):
        """
        Returns all items in the list.
        
        Returns:
            list: List of file paths/URLs
        """
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]


