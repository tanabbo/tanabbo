# TANABBO Installation Guide

## Overview
This guide provides step-by-step instructions for installing TANABBO on Windows 10. Administrative rights are required for the installation process.

## Prerequisites
- Windows 10 with administrative rights.
- [Visual Studio Code (VSCode)](https://code.visualstudio.com/) or any preferred IDE for editing XML files.

## Installation Steps

### 1. Download GRASS GIS
- Visit the official [GRASS GIS website](https://grass.osgeo.org/download/windows/) and download the latest version for Windows.

### 2. Install GRASS GIS
- Run the downloaded installer to install GRASS GIS.

### 3. Download Necessary Data
- Download the required data from [this link](https://drive.google.com/file/d/1F1tsXt-pZh9tBPM5QIJ8hWPOaxACiGJW/view?usp=sharing).

### 4. Unzip and Copy Data
- Unzip the downloaded file.
- Copy the contents to the corresponding folders in the GRASS GIS directory (`C:\Program Files\GRASS GIS 8.2`), except for the `gui` folder.

### 5. Edit XML File
- Navigate to `\bbo1_27\gui\wxpython\xml` in the unzipped folder.
- Right-click on the `menudata` file and choose “Edit”.

### 6. Locate TANABBO Entry
- In WordPad, press `CTRL-F` to find the first mention of “TANABBO”.

### 7. Copy Required Text
- Select and copy the text as instructed in the guide.

### 8. Edit Original Menu Data
- Open the original `menudata` file in the GRASS GIS directory with VSCode.

### 9. Modify and Save File
- Delete the last two lines (`</menubar>`, `</menudata>`) and paste the copied text.
- Save the file and choose “Retry as Admin…” if a warning appears.

### 10. Install Python Libraries
- Open Command Prompt and install necessary Python libraries:
pip install pandas
pip install numpy
pip install scipy
pip install scikit-learn

- If you encounter SSL problems, refer to [this guide](https://www.youtube.com/watch?v=mN8SLBsvSCU).

### 11. Verify Installation
- Open GRASS GIS to ensure it's working correctly.

## Additional Notes
- This guide uses VSCode for XML editing, but you're free to use any IDE of your choice.

