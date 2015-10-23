from sftp_sync import SyncServer
if __name__ == '__main__':
    SERVER = '127.0.0.1'
    PRIVATE_KEY = 'C:\\Users\\Administrator\\.ssh\\id_rsa'
    USERNAME = 'user'
    
    LOCAL = 'D:\\sync_dir\\'
    REMOTE = '/home/user/sync_dir/'
    ALLOWS = [r'\.py$']
    
    server = SyncServer(SERVER,
                        username=USERNAME,
                        private_key=PRIVATE_KEY,
                        )

    server.allow(ALLOWS)
    server.run(LOCAL,REMOTE)