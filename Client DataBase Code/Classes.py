import pickle as pkl
import re
import itertools as it
import pandas as pd
import numpy as np
import customtkinter as ctk
from tkinter.messagebox import askyesno
from tkinter.filedialog import askopenfilename
from pandastable import Table, TableModel

#These Classes are the main workings of this Client data storage application-
#Note that i have a couple classes for adding and deleting clients,-
#this is mainly due to me wanting to have a seperate window from the main window,-
#that i think increases the User expirence in using the application.

class Client():
    #This is the Client Class that is used to store each clients information name, number, address
    #Also note the account number system. if you have no clients it will generate up as you add them in the UI
    #if you already have clients in, it was start from the last Client and continue generating account # from there
    #if you are importing clients from a csv, you can still keep the account numbers associated to that client, -
    #and future clients added will generate from the last imported ones.
    counter = it.count()
    Name:str
    PhoneNumber:str
    Address:str

    def __init__(self, ClientList, Name, PhoneNumber, Address, AccountNumber=0):
        BaseAccountNumber = 1000000
        if len(ClientList) > 0 and AccountNumber == 0:
            BaseAccountNumber = ClientList[-1].AccountNumber
            self.AccountNumber = BaseAccountNumber + 1
        elif AccountNumber > 0:
            self.AccountNumber = AccountNumber
        else:
            self.AccountNumber = BaseAccountNumber + next(self.counter)
        self.Name = Name
        #this allows for 10 digit entry, but will display with "-" and are code "()" for user friendlyness
        if len(PhoneNumber) == 10: 
            self.PhoneNumber = "(" + PhoneNumber[0:3] + ")" + "-" + PhoneNumber[3:6] + "-" + PhoneNumber[6:10]
        else:
            self.PhoneNumber = PhoneNumber
        self.Address = Address
        return

    def to_dict(self):
        #used to turn our client list into pandas dataframe which is used for displaying to a table in the MainClientWindow
        return {
            "Account #" : self.AccountNumber,
            "Name" : self.Name,
            "Phone #" : self.PhoneNumber,
            "Address" : self.Address
        }


class MainClientWindow():

    def __init__(self, root, title, font, windowsize, ClientList):
        self.root = root
        self.root.title(title)
        self.root.geometry(windowsize)
        self.font = font
        self.ClientList = ClientList

        #Creates all the buttons in a frame used to exec other methods in the class for the user interface
        self.frameButton = ctk.CTkFrame(master=self.root)
        self.frameButton.pack_configure(fill="both", expand=False)
        addClientButton = ctk.CTkButton(master=self.frameButton, text="Add Client Data", font=font,command=self.AddClientData)
        deleteClientButton = ctk.CTkButton(master=self.frameButton, text="Delete Client", font=font,command=self.DeleteClient)
        editClientButton = ctk.CTkButton(master=self.frameButton, text="Edit Client", font=font,command=self.EditClient)
        importButton = ctk.CTkButton(master=self.frameButton, text="Import File", font=font,command=self.ImportFile)
        exportButton = ctk.CTkButton(master=self.frameButton, text="Export File", font=font,command=self.ExportFile)
        addClientButton.grid_configure(row=0, column=0, padx=5)
        deleteClientButton.grid_configure(row=0, column=1, padx=5)
        editClientButton.grid_configure(row=0, column=2, padx=5)
        importButton.grid_configure(row=0, column=3, padx=5)
        exportButton.grid_configure(row=0, column=4, padx=5)
        
        #Displaying the table using a dataframe from the Client object list of the clients
        self.frameTable = ctk.CTkFrame(master=self.root)
        self.frameTable.pack_configure(fill="both",expand=True)
        self.dataframe = pd.DataFrame.from_records([client.to_dict() for client in self.ClientList])

        self.table = Table(self.frameTable, dataframe=self.dataframe, showtoolbar=False, showstatusbar=True)
        #Visual variables
        self.table.autoResizeColumns()
        self.table.textcolor = 'black'
        self.table.cellbackgr = 'light gray'
        self.table.boxoutlinecolor = 'white'

        self.table.show()
        #this is the mainloop of the tkinter module that runs the UI for the user to use, once out of mainloop, you are out of window
        self.root.mainloop() 
        return 
    
    def AddClientData(self):
        #Creates a new window to add individual clients to Client DataBase
        root = ctk.CTk()
        AddClientDataWindow(root=root, title="Add Clients Data", windowsize="600x300", MainWindow=self)
        return
    
    def DeleteClient(self):
        #takes the selected row in the UI and uses that index to find the index of the client in the client list to delete
        #also displays a nice confimation box for deleting clients
        row = self.table.getSelectedRow()
        if askyesno(title="Confirmation", message="Are you sure you want to delete Client: '" + str(self.ClientList[row].Name) + "'") == True:
            del self.ClientList[row]
            self.TableUpdate()
        return
    
    def EditClient(self):
        #method that launches a new window to change current selected clients information
        root = ctk.CTk()
        row = self.table.getSelectedRow()
        EditClientDataWindow(root=root, title="Client Data", windowsize="600x300", MainWindow=self, ClientIndex=row)
        return
    
    def ImportFile(self):
        #this takes the file path of a selected csv file and imports the data into the table
        #most importantly this is appending the clients into the clientlist which is the varible that is stored in the pkl file
        try:
            filePath = askopenfilename(initialdir='C:/', title='Select a File', filetype=(("CSV", ".csv"), ("All Files", "*.*")))
            clientDataFrame = pd.read_csv(filePath)
            #Create Clients and append into our Client List
            for client in clientDataFrame.to_numpy():
                newClient = Client(self.ClientList, str(client[1]), str(client[2]), str(client[3]), client[0])
                self.ClientList.append(newClient)
            self.TableUpdate()
        except FileNotFoundError: #just for clearing the error of closing out of the window
            pass
        return

    def ExportFile(self):
        #this takes the client list and turns it into a dataframe that pandas easily can write to a file of the users choosing
        self.dataframe = pd.DataFrame.from_records([client.to_dict() for client in self.ClientList])
        try:
            filePath = askopenfilename(initialdir='C:/', title='Select a File', filetype=(("CSV", ".csv"), ("All Files", "*.*")))
            self.dataframe.to_csv(filePath, index=False)
        except FileNotFoundError: #just for clearing the error of closing out of the window
            pass
        return
    
    def TableUpdate(self):
        #this is the main updater of the datatable shown on screen
        #the table.redraw() being most import that updates any changes to client(s) and/or their data to update and be shown on screen
        self.dataframe = pd.DataFrame.from_records([client.to_dict() for client in self.ClientList])
        self.table.model.df = self.dataframe
        self.table.autoResizeColumns()
        self.table.redraw()
        return

class AddClientDataWindow():
    #This window is just for adding clients to the table, which will also be data stored in the pkl file to be reloaded for future use

    def __init__(self, root, title, windowsize, MainWindow):
        self.root = root
        self.root.title(title)
        self.root.geometry(windowsize)
        self.font = MainWindow.font
        self.MainWindow = MainWindow
        
        #This creates all the Labels and entry boxes and organizes them nicely
        ctk.CTkLabel(self.root, text="Client's Name", font=self.font).grid(row=0, column=1, padx=5)
        self.clientName = ctk.CTkEntry(self.root, width=250, height=1)
        self.clientName.grid(row=0, column=2)
        ctk.CTkLabel(self.root, text="Client's Phone Number", font=self.font).grid(row=1, column=1, padx=5)
        self.clientPhoneNumber = ctk.CTkEntry(self.root, width=250, height=1)
        self.clientPhoneNumber.grid(row=1, column=2)
        ctk.CTkLabel(self.root, text="Client's Address", font=self.font).grid(row=2, column=1, padx=5)
        self.clientAddress = ctk.CTkEntry(self.root, width=250, height=1)
        self.clientAddress.grid(row=2, column=2)

        #most important button this executes the method to display and store the inputed information for the user
        ctk.CTkButton(self.root, text="Confirm Client Entry", font=self.font, command=self.CreateClient).grid(row=3, columnspan=3)

        self.root.mainloop()
        return
    
    def CreateClient(self):
        #This method is used to collect the string inputed into the entry boxes by the user and create client objects and shown in the table

        #This if statement is just a small restriction to the entered clients information, restricting the phone number to have to be 10 digits
        if len(str(self.clientPhoneNumber.get())) == 10:
            newClient = Client(self.MainWindow.ClientList, str(self.clientName.get()), str(self.clientPhoneNumber.get()), str(self.clientAddress.get()))
            #note these delete methods are just used to clear the text showing the information entered was added to the mainwindow table
            self.clientName.delete(0, 999)
            self.clientPhoneNumber.delete(0, 999)
            self.clientAddress.delete(0, 999)
            self.MainWindow.ClientList.append(newClient)
            self.MainWindow.TableUpdate()
        else:
            #this just displays the requirments for entering a new client.
            ctk.CTkLabel(self.root, text_color="Red3", font=self.font, text="Please enter Name whith just Alphebet characters,\n" \
                         "Please enter PHONE NUMBER as 10 digits [EX:'1234567891'] \n" \
                         "Please enter FULL address, [EX: '1234 NE Street, City, State, Apt']").grid(row=4, columnspan=4)
        return 

class EditClientDataWindow():
    #this is the third seperate window class used to display the editing of clients information that is already in the mainwindow table
    def __init__(self, root, title, windowsize, MainWindow, ClientIndex):
        self.root = root
        self.root.title(title)
        self.root.geometry(windowsize)
        self.font = MainWindow.font
        self.MainWindow = MainWindow
        self.ClientIndex = ClientIndex
        
        #these are the labels and entry boxes same as the "AddClientDataWindow" Class, note the adding of pre inserting text to show the user-
        #which client they are changing and making it easier to change one parameter of all they need to do is update clients address.
        ctk.CTkLabel(self.root, text="Client's Name", font=self.font).grid(row=0, column=1, padx=5)
        self.clientName = ctk.CTkEntry(self.root, width=250, height=1)
        self.clientName.insert(0, self.MainWindow.ClientList[self.ClientIndex].Name)
        self.clientName.grid(row=0, column=2)
        ctk.CTkLabel(self.root, text="Client's Phone Number", font=self.font).grid(row=1, column=1, padx=5)
        self.clientPhoneNumber = ctk.CTkEntry(self.root, width=250, height=1)
        self.clientPhoneNumber.insert(0, re.sub("[()-]","",self.MainWindow.ClientList[self.ClientIndex].PhoneNumber))
        self.clientPhoneNumber.grid(row=1, column=2)
        ctk.CTkLabel(self.root, text="Client's Address", font=self.font).grid(row=2, column=1, padx=5)
        self.clientAddress = ctk.CTkEntry(self.root, width=250, height=1)
        self.clientAddress.insert(0, self.MainWindow.ClientList[self.ClientIndex].Address)
        self.clientAddress.grid(row=2, column=2)

        #Main confimation button the executes the method that handles the backend of the clients data
        ctk.CTkButton(self.root, text="Confirm Client Edit", font=self.font, command=self.EditClient).grid(row=3, columnspan=3)

        self.root.mainloop()
        return
    
    def EditClient(self):
        #used to confirm the same restriction of the 10 digit phone number length and gets the indexed client from the selected row-
        #and re assigns each attribute of the client obj, to the new entered values, updating in the mainwindow table
        if len(str(self.clientPhoneNumber.get())) == 10:
            PhoneNumber = str(self.clientPhoneNumber.get())
            self.MainWindow.ClientList[self.ClientIndex].Name = str(self.clientName.get())
            self.MainWindow.ClientList[self.ClientIndex].PhoneNumber = "(" + PhoneNumber[0:3] + ")" + "-" + PhoneNumber[3:6] + "-" + PhoneNumber[6:10]
            self.MainWindow.ClientList[self.ClientIndex].Address = str(self.clientAddress.get())
            self.MainWindow.TableUpdate()
        else:
            ctk.CTkLabel(self.root, text_color="Red3", font=self.font, text="Please enter Name whith just Alphebet characters,\n" \
                         "Please enter PHONE NUMBER as 10 digits [EX:'1234567891'] \n" \
                         "Please enter FULL address, [EX: '1234 NE Street, City, State, Apt']").grid(row=4, columnspan=3)
        return 
