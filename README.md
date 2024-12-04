# Data Filler GUI

This Python script creates a simple graphical user interface (GUI) to fill in specific data values for computational chemistry input files. The user can provide information for molecular calculations such as the SCF type, multiplicity, and charge, as well as select a file to extract data from. The filled template is then saved to a `.txt` file. Additionally, the saved text file can be converted into an HTML format.

## Features
- **SCF Type Selection**: Allows the user to choose between different SCF types (e.g., RHF, UHF) from a dropdown.
- **Multiplicity and Charge Input**: Provides input fields to specify multiplicity and charge, with buttons to increment and decrement values.
- **File Selection**: Users can select a `.xyz` file, from which the content will be extracted and used to populate a template.
- **Data Saving**: The filled template is saved to a `data.txt` file.
- **HTML Conversion**: The `data.txt` file can be converted into an HTML file using a predefined function.

## Components
1. **SCF Type**: A dropdown menu with two options: RHF and UHF.
2. **Multiplicity**: A text input field with buttons to increase or decrease the value.
3. **Charge**: A text input field with buttons to increase or decrease the value.
4. **File Selector**: A button to open a file dialog to choose an `.xyz` file.
5. **Save Button**: Saves the filled data to `data.txt`.
6. **Convert to HTML Button**: Converts the saved `data.txt` file to an HTML format.

## Requirements
- `tkinter` for creating the GUI.
- `text_to_html_file` module for converting the text file to HTML.

## How to Use
1. Launch the GUI.
2. Select a file using the "Select a File" button.
3. Input values for SCF type, multiplicity, and charge.
4. Click "Save" to save the data into a `data.txt` file.
5. Optionally, click "Convert to HTML" to generate an HTML version of the file.

