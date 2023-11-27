# TANABBO Installation Guide

## Overview
This guide provides step-by-step instructions for installing TANABBO on Windows 10.

## Prerequisites
- Windows 10 with administrative rights.
- [Visual Studio Code (VSCode)](https://code.visualstudio.com/) or any preferred IDE for editing XML files.

## Installation Steps

### 1. Download and Install GRASS GIS
- Visit the official [GRASS GIS website](https://grass.osgeo.org/download/windows/) and download the latest version for Windows and Run the downloaded installer to install GRASS GIS.

### 2. Download Necessary Data
- Download/Clone this repo with the necessary data.

### 3. Unzip and Copy Data
- Unzip the downloaded file.
- Copy the contents to the corresponding folders in the GRASS GIS directory (`C:\Program Files\GRASS GIS 8.2`), except for the `gui` folder.

### 4. Edit XML File
- Navigate to `\bbo1_27\gui\wxpython\xml` in the unzipped folder.
- Right-click on the `menudata` file and choose “Edit”.

### 5. Locate TANABBO Entry
- In WordPad, press `CTRL-F` to find the first mention of “TANABBO”.

### 6. Copy Required Text
- Select everything below and one line higher (containing “    <menu>”) of the line containing the “TANABBO” word, including this line.

### 7. Edit Original Menu Data
- Open the original `menudata` file in the GRASS GIS directory with VSCode.

### 8. Modify and Save File
- Delete the last two lines
   </menubar>
</menudata>
- Paste the copied text.
- Save the file and choose “Retry as Admin…” if a warning appears.

### 9. Install Python Libraries
- Open Command Prompt and install necessary Python libraries:
pip install pandas
pip install numpy
pip install scipy
pip install scikit-learn

If you encounter SSL problems, refer to [this guide](https://www.youtube.com/watch?v=mN8SLBsvSCU).
