import tkinter as tk
from tkinter import filedialog as fd
from tkinter import Grid
from tkinter import messagebox
from zipfile import is_zipfile
from updateablezipfile import UpdateableZipFile
import os.path
import configparser
from xml.dom import minidom

# consider this one day for SAT to step https://github.com/jmplonka/InventorLoader/blob/master/Acis2Step.py

gui = tk.Tk()
gui.title('DSM Tools')
gui.minsize(800, 100)
gui.eval('tk::PlaceWindow . center')
Grid.grid_columnconfigure(gui, 1, weight=1)


def open_file_dialog():
    # retrieve last directory used
    initial_path = '/'
    if os.path.isdir(rsdocfile.get()):
        initial_path = os.path.dirname(os.path.abspath(rsdocfile.get()))
        print(initial_path)

    # open file dialog
    filename = fd.askopenfilename(initialdir=initial_path,
                                  title='Select Design Spark Mechanical Document',
                                  filetypes=(('RSDoc', '*.rsdoc'), ('all files', '*.*')))
    if filename:
        rsdocfile.set(filename)  # update the entry box
        # write to most recent files
        config = configparser.ConfigParser()
        if os.path.isfile('config.ini'):
            config.read('config.ini')
        config['Common'] = {'recentFile': rsdocfile.get()}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)


def unlock_solids():
    if not os.path.isfile(rsdocfile.get()):
        messagebox.showerror('File not found', 'The file "{}" is not available'.format(rsdocfile.get()))
        return
    if messagebox.askokcancel('Confirmation', 'Are you sure you want to proceed? Using the DSTools script is at your '
                                              'own risk and you claim no responsibility or liability on the part of the'
                                              ' author for any loss of damages from using this script.'
                                              '') == messagebox.CANCEL:
        return
    if not is_zipfile(rsdocfile.get()):
        messagebox.showerror('The file selected is not a valid rsdoc file')
        return

    with UpdateableZipFile(rsdocfile.get(), 'a') as rsdoc:
        # first remove the overrides
        content_types = minidom.parseString(rsdoc.read('[Content_Types].xml').decode(encoding='utf-8', errors='ignore'))
        for override in content_types.getElementsByTagName('Override'):
            parent = override.parentNode
            parent.removeChild(override)

        # secondly remove the RsLocked text from modificationLock element
        document = minidom.parseString(rsdoc.read('SpaceClaim/document.xml').decode(encoding='utf-8', errors='ignore'))
        for modificationlock in document.getElementsByTagName('modificationLock'):
            if modificationlock.firstChild.nodeValue == 'RSLocked':
                modificationlock.firstChild.nodeValue = 'None'

        # if the xml changes were successful, write it all back to the zip file
        rsdoc.writestr('[Content_Types].xml', content_types.toxml('utf-8'))
        rsdoc.writestr('SpaceClaim/document.xml', document.toxml('utf-8'))

    print('Unlocking of solids completed successfully')


rsdocfile = tk.StringVar()
lblFile = tk.Label(gui, text='RSDoc Filename')
lblFile.grid(row=0, column=0)
edtFile = tk.Entry(gui, textvariable=rsdocfile)
edtFile.grid(row=0, column=1, columnspan=1, sticky='ew')

if os.path.isfile('config.ini'):
    config = configparser.ConfigParser(strict=False)
    config.read('config.ini')
    rsdocfile.set(config.get('Common', 'recentFile', fallback=''))

btnFile = tk.Button(gui, text='...', command=open_file_dialog)
btnFile.grid(row=0, column=3)
btnUnlockSolids = tk.Button(gui, text='Unlock Solids', command=unlock_solids)
btnUnlockSolids.grid(row=1, column=0)

gui.mainloop()

