import socket;
import MySQLdb;
import urlparse;
import sys;
import smtplib;


#Connect to the database and pull the needed information
def appsportal_db_connect():

        #Create the datbase connection to find the IP address
        db = MySQLdb.connect(host="<<DATABASE SERVER>>", port=<<DB PORT>>, user="<<DABASTE USER>>", passwd="<<DATABASE PASSWORD>>", db="<<DATABASE>>")
        cursor = db.cursor()

        #Run the SQL statement
        cursor.execute("SELECT link_name,link_url FROM ops_links" )
        link = cursor.fetchall()

        #clode the coonnection to the database
        db.close()

        #return the links back to main.
        return link


#take the returned links and parse them in to a hostname and port(s) to check
def parse_link(word):

                #import the urlparse libary
                from urlparse import urlparse
                parsed = urlparse(word[1])

                #use the port from the database querry, otherwise assime the default of 443
                link_port = parsed.port or 443


                try:
                        #set a error handling varriable
                        unexpected_result = ""

                        #open a network connection to the host and port grabbed from above
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((parsed.hostname,link_port))

                        if result == 0:
                                #if the result comes back 0 then the network port is open.
                                result_443="Port 443 is Open"
                        else:
                                #if the result comes back anything else assum the port is closed.
                                result_443="Port 443 is not Open"

                        #open a network connection to the host and ssh
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((parsed.hostname,22))
                        if result == 0:
                                #if the result comes back 0 then the network port is open.
                                result_22="Port 22 is Open\n"
                        else:
                                #if the result comes back anything else assum the port is closed.
                                result_22="Port 22 is not Open\n"

                except:
                        #if anything goes wrong, then hard code the ports to null and report back and error.
                        result_443='Null'
                        result_22='Null'
                        unexpected_result = "!!Unable to test the network connection!!\n"

                #return the results back to main.
                return [parsed.hostname, result_443, result_22, unexpected_result]

def email_output(email_results1, email_results2):

        #import the email libary.
        from email.mime.text import MIMEText

        msg = ("Bad Results \n"
        "-------------------\n" +
        email_results1 + "\n"
        "-------------------\n " +
        "Good Results \n " +
        "-------------------\n" +
        email_results2 + "\n" +
        "-------------------")

        payload = MIMEText(msg)

        payload['Subject'] = 'Port Checker Script for Apps Portal'
        payload['From'] = '<ADD FROM ADDRESS>'
        payload['To'] = '<ADD TO ADDRESS>'

        s = smtplib.SMTP('smtp.cul.am.sony.com')
        s.sendmail('<ADD FROM ADDRESS>', '<ADD TO ADDRESS>', payload.as_string())
        s.quit()

#execute the db_connect def and capture the returned links
link=appsportal_db_connect()


#main section
bad_results=""
good_results=""

for word in link:

        #for each link returned run the link parser and test the network connection.
        result=parse_link(word)

        #Sees if the host has any ports unaccessable then add them bad_list
        if result[1] == 'Port 443 is not Open' or result[2] == 'Port 22 is not Open' or result[3] == '!!Unable to test the network connection!!':
                if result[3] != "":
                        bad_results += "Investigate host: " + result[0] + ", port: " + result[1] + ", or: " + result[2] + ", or: " + result[3]
                else:
                        bad_results += "Investigate host: " + result[0] + ", port: " + result[1] + ", or: " + result[2]
        #else
        else:
                good_results += "Host: " + result[0] + " is accessable"

#after sorting, send the output out for email
email_output(bad_results, good_results)
                                                                            
