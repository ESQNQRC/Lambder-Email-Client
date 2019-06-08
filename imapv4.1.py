import email, getpass, imaplib, os, time, threading, configparser, string, sys


########################################################################################################################
#               Team: Lambder                                                                                          #
#                   Cesar Salazar                                                                                      #
#                   Daniel Berbesi                                                                                     #
#                   Saul Ugueto                                                                                        #
#                   Valentina Contreras                                                                                #
# Script to get unseen emails from a email account                                                                     #
# Information Extracted from:                                                                                          #
#                                                                                                                      #
# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/                                        #
# https://www.tutorialspoint.com/python/python_imap.how-to-read-email-from-gmail-using-python                          #
# https://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail?lq=1            #
# https://stackoverflow.com/questions/13210737/get-only-new-emails-imaplib-and-python                                  #
# https://codehandbook.org/how-to-read-email-from-gmail-using-python/                                                  #
# https://gist.github.com/robulouski/7441883                                                                           #
# http://web.archive.org/web/20131017130434/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/#
#                                                                                                                      #
########################################################################################################################
    


 # user data
userConfig = {
    "database.user": "",
    "database.password": ""}


 # load userConfig
def loadConfig(file):

    #returns a dictionary with keys of the form
    #<section>.<option> and the corresponding values
    cp = configparser.ConfigParser(  )
    cp.read(file)
    for sec in cp.sections(  ):
        name = str.lower(sec)
        for opt in cp.options(sec):
            userConfig[name + "." + str.lower(opt)] = str.strip(
                cp.get(sec, opt))
    return userConfig


def analizerMail():


    loadConfig("config.ini")
    # get user from userConfig
    user = userConfig["database.user"]
    # get password from userConfig
    pwd = userConfig["database.password"]

    # connecting to the gmail imap server
    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")
    # Login
    imapMail.login(user,pwd)
    
    ################################################
    # Makes a list of mails id (to show only new unseen ones)
    listOfShowedEmailsID = []
    listOfEmailsID = []
    allowedToShow = False

    try: 

        #Idle Loop
        while True:

            # makes a list of email
            imapMail.list()

            imapMail.select('Inbox') # here you a can choose a mail box like INBOX instead

            print("Checking inbox")

            (resp, data) = imapMail.uid('search',None, '(UNSEEN)') # filter unseen mails

            data = data[0].split() # getting the mails id


            # Now for every unseen email
            for emailid in data:

                print(emailid)
    

                #####################################################################
                # Check if email id is in the list of last emails shown
                try:
                # If exception doesn't comes up then item is in the last showed emails list, so we dont show it
                    listOfShowedEmailsID.index(emailid)
                    allowedToShow = False
                    print("Try, item already showed")
                except: 
                # Except, so id isnt in the list, we need to show it
                    allowedToShow = True
                    print("Except, item wasnt showed")

                ######################################################################
                if allowedToShow:
                    (resp, data) = imapMail.uid('fetch',emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
        
                    email_info = data[0][1] # getting the mail content
        
                    mail = email.message_from_bytes(email_info) # parsing the mail content to get a mail object
        
                    (resp, data) = imapMail.uid('store',emailid, '-FLAGS', '\\Seen') # Mark email as unseen again (bc fetching brings body of email too)

                    #Check if any attachments at all
                    if mail.get_content_maintype() != 'multipart':
                        continue

                    ###################################################################
                    # Add the current emailID to listOfEmailsID, to save new IDs, then show them
                    # and clear the lastOfEmailsId

                    listOfEmailsID.append(emailid)

                    #############################################################

                    print ("["+mail["From"]+"] :" + mail["Subject"] + "\n")

            print (listOfShowedEmailsID)
            print (listOfEmailsID)

            if listOfEmailsID:
                listOfShowedEmailsID.extend(listOfEmailsID)
                listOfEmailsID.clear()

            print (listOfShowedEmailsID)
            print (listOfEmailsID)

            time.sleep(10)

    finally:        

        imapMail.logout()


#####################################################   MAIN  #############################################

try:
    
    threadFunction = threading.Thread(target=analizerMail)

    threadFunction.setDaemon(True)

    threadFunction.start()

    threadFunction.join()

except:

    print("\nProgram stopped")
