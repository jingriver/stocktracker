def sendMail(host, addr, to, subject, content):
    import smtplib
    from email.MIMEText import MIMEText

    print "Sending mail from", addr, "to", to, "...",
    server = smtplib.SMTP(host)
    msg    = MIMEText(content)

    msg["Subject"] = subject
    msg["From"]    = addr
    msg["To"]      = to

    server.sendmail(addr, [to], msg.as_string())
    server.quit()
    print "done."

def display(host='', user='', passwd='', deletion = 0):
    import poplib, email
    #pop3 = poplib.POP3(host)
    pop3 = poplib.POP3_SSL('pop.gmail.com',995)
    pop3.user('jingriver@gmail.com')
    pop3.pass_('ycxm0531')

    num = len(pop3.list()[1])
    print user, "has", num, "messages"

    format = "%-3s %-15s %s"

    if num > 0:
        if deletion:
            print "Deleting", num, "messages",
            for i in range(1, num+1):
                pop3.dele(i)
                print ".",
            print " done."
        else:
            print format % ("Num", "From", "Subject")
            for i in range(1, num+1):
                str = string.join(pop3.top(i, 1)[1], "\n")
                msg = email.message_from_string(str)
                print format % (i, msg["From"], msg["Subject"])
    pop3.quit()
    
if __name__ == '__main__':
    display()