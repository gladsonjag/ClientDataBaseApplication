import pandas as pd
import customtkinter as ctk
import pickle as pkl
from Classes import MainClientWindow

#This Program is a proof of concept for small business owners that would need a simple user interface/application to store customer data
#Note the "ClientDataBase.csv" is used for showing the importing functionality and the data storage is in the pickel file.
#the Main file is just used to start the program and its where the pkl file loads the client data and after the application is done, updates the pikle file

def MAIN():
    #Loads up the data stored on the pkl file creates the Clientlist that we delete, append, edit that is used for our spreadsheet.
    infile = open("Clients.pkl", "rb")
    try:
        ClientList = pkl.load(infile)
    except EOFError:
        ClientList = []
    try:
        while True:
            ClientList.append(pkl.load(infile))
    except EOFError:
        pass
    infile.close()
    
    #Varibles for window
    TITLE = "Client DataBase"
    WINDOWSIZE = "1280x720"
    FONT = ("Arial", 18)
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme("dark-blue")
    #Creates the main interactable window that the user will use to add clients delete them, import etc.
    root = ctk.CTk()
    MainWindow = MainClientWindow(root=root, title=TITLE, font=FONT, windowsize=WINDOWSIZE, ClientList=ClientList, )
    


    #End of Program saves the client list to the pkl file.
    outfile = open("Clients.pkl", "wb")
    pkl.dump(MainWindow.ClientList, outfile)
    outfile.close()
    return


MAIN()