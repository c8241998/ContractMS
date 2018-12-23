import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

    
def mail(my_receiver,mail_content):
    sender_name = '合同管理系统'
    receiver_name = '尊敬的用户'
    theme = '合同管理系统温馨提示'

    my_sender='185873016@qq.com'    # 发件人邮箱账号
    my_pass = 'wpibkvwjtfohbiab'              # 发件人邮箱密码(当时申请smtp给的口令)
    # my_receiver='569362884@qq.com'      # 收件人邮箱账号，我这边发送给自己
    ret=True
    try:
        msg=MIMEText(mail_content,'plain','utf-8')
        msg['From']=formataddr([sender_name,my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To']=formataddr([receiver_name,my_receiver])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject']=theme               # 邮件的主题，也可以说是标题

        server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender,[my_receiver,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()# 关闭连接
    except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret=False
    # if ret:
    #     print("邮件发送成功")
    # else:
    #     print("邮件发送失败")
