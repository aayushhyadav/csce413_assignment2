import paramiko
import logging

# Fake SSH server implementation
class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.logger = logging.getLogger("Honeypot")
        self.event = None

    def check_auth_password(self, username, password):
        self.logger.info(
            f"Login attempt from {self.client_ip} | user={username} password={password}"
        )

        # ACCEPT login (honeypot behavior)
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.logger.info(f"Shell opened from {self.client_ip}")
        return True
    
    # handles PTY request
    # ensuring the fake shell looks legitimate
    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        self.logger.info(
            f"PTY requested from {self.client_ip} | term={term} {width}x{height}"
        )
        return True

