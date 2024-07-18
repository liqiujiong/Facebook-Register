
import imaplib
import logging
import re
import threading
import time
import email as e_mail

class EmailMonitor:
    def __init__(self, server, port, username, password, folder, specified_sender, specified_receiver):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.folder = folder
        self.specified_sender = specified_sender
        self.specified_receiver = specified_receiver
        self.link_dict = dict()
        self.mail = None

        # 配置日志
        self.logger = logging.getLogger(self.__class__.__name__)

        # 线程
        self.thread = threading.Thread(target=self.check_new_mail, daemon=True)
        self.is_terminated = False

    def extract_link_from_mail(self, msg):
        # 实现从邮件内容提取链接的逻辑
        if msg.is_multipart():
            # Iterate over each part
            for part in msg.walk():
                # Check content type
                content_type = part.get_content_type()

                # Look for text/plain parts, but skip attachments
                if content_type == "text/html":
                    html_content = part.get_payload(decode=True).decode()

                    pattern = r'<a href="(.*?)".*?>[\s\S]*?Verify email address[\s\S]*?<\/a>'
                    result = re.search(pattern, html_content)
                    if result:
                        link = result.group(1)
                        self.logger.info(f'Account: {msg["To"]}')
                        self.logger.info(f'Found verify link: {link}')
                        return link
                    else:
                        self.logger.error('Verify link does not exist!')
                        return None
            else:
                self.logger.error(f'The text/html part not appears in this mail!')
                return None
        else:
            self.logger.error('The format of mail is wrong. Please check!')
            return None

    def check_new_mail(self):
        while not self.is_terminated:
            try:
                # 首次连接或重新连接
                if not self.mail:
                    self.mail = imaplib.IMAP4_SSL(self.server, self.port)
                    self.logger.info("Logging into Outlook mailbox...")
                    self.mail.login(self.username, self.password)
                    self.logger.info("Outlook successfully connected!")

                    # 列出所有文件夹
                    # status, folders = self.mail.list()
                    # if status == 'OK':
                    #     self.logger.info(f"Folders:")
                    #     for folder in folders:
                    #         self.logger.info('    ' + folder.decode())
                    # else:
                    #     self.logger.warning('列出所有Folders失败！')

                self.logger.info(f'Selecting folder: {self.folder}')
                self.mail.select(self.folder)

                # 搜索未读邮件
                self.logger.info(f'Searching for unseen mails...')
                # status, messages = self.mail.search(None, f'(UNSEEN FROM "{self.specified_sender}" TO "{self.specified_receiver}")')
                status, messages = self.mail.search(None, f'(FROM "{self.specified_sender}" TO "{self.specified_receiver}")')
                if status != 'OK':
                    self.logger.warning(f"Search failed，status: {status}")

                # Get the list of email IDs
                email_ids = messages[0].split()
                self.logger.info(f'Found {len(email_ids)} unseen mails from OpenAI.')

                # check if specific content appears
                for num in messages[0].split():
                    self.logger.info(f'Fetching unread mail -> {num.decode()}...')

                    # BUG: 使用 fetch RFC822 会将邮件标记为已读状态
                    status, data = self.mail.fetch(num, '(RFC822)')

                    if status == 'OK':
                        msg = e_mail.message_from_bytes(data[0][1])  # noqa

                        if msg['To'] == self.specified_receiver:
                            link = self.extract_link_from_mail(msg)
                            if link:
                                self.logger.info(f'[bold green]Got the verification mail for {self.specified_receiver}![/bold green]')
                                self.link_dict[msg['To']] = link

                                # 标记为已读
                                self.mail.store(num, '+FLAGS', '\\Seen')
                        else:
                            # 标记为未读
                            self.mail.store(num, '+FLAGS', '\\Unseen')
                            self.logger.info(f'Verification mail for {msg["To"]} discarded.')
                    else:
                        self.logger.error(f'Fetch failed for mail {num}!')

                self.logger.info("All emails have been checked.")
                time.sleep(2)

            except imaplib.IMAP4.error as e:
                self.logger.error(f"IMAP4错误: {e}")
                self.reset_connection()

            except Exception as e:
                self.logger.error(f"发生错误: {e}")
                self.reset_connection()

    def reset_connection(self):
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
        self.mail = None
        self.logger.info("邮箱连接已重置")

    def start_monitoring(self):
        self.thread.start()
        self.logger.info("开始监控邮箱")

    def end_monitoring(self):
        self.is_terminated = True
        self.logger.info("Waiting for monitoring thread to end...")
        self.thread.join()
        self.logger.info('Monitoring thread ended.')

    def get_link(self, account):
        present = self.link_dict.get(account, None)
        self.logger.info(f"检查认证链接是否存在: {account} - {'存在' if present else '不存在'}")
        return present

    def remove_link(self, account):
        if account in self.link_dict:
            self.link_dict.pop(account)
            self.logger.info(f"账号已移除: {account}")
        else:
            self.logger.error(f"要移除的账号不存在: {account}")


