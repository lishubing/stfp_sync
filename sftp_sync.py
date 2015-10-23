# -*- coding: utf-8 -*-
import os
import re
import time
import pysftp
import logging


class SyncServer(object):

    def __init__(self, server, **kw):
        '''Server initialization
        :param:See params of pysftp.Connection URL:http://pysftp.readthedocs.org/en/latest/pysftp.html
        '''
        self.logger = logging.getLogger('sftp_sync_logger')
        self.log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        self.log_handler.setFormatter(formatter)
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.INFO)
        try:
            self.conn = pysftp.Connection(server, **kw)
        except Exception as e:
            self.logger.error('Connect error! Message:{0}'.format(e))
            return

        self.local_dir = kw.get('local', os.getcwd())
        self.remote_dir = kw.get('remote', self.conn.getcwd())
        self.allows = set()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def is_allow(self, path):
        '''Check if the path is allowed.
        :param path: File path to be check
        :type path:str
        '''
        for pattern in self.allows:
            if re.search(pattern, path):
                return True
        else:
            return False

    def allow(self, *args):
        self.allows.update(*args)

    def sftp_upload(self, paths):
        '''Upload a list of files using sftp. 
        :param paths: The absolute paths of files need to be uploaded.
        :type paths:list
        :return:None
        '''
        if not len(paths):
            return

        for path in paths:
            if not path.startswith(self.local_dir):
                continue
            rel_path = path[len(self.local_dir):].replace('\\', '/')
            self.logger.info('Uploading file {0}'.format(path))
            try:
                self.conn.put(path, self.remote_dir + rel_path)
            except Exception as e:
                self.logger.error('Put file error! Message:{0}'.format(e))
                return
        self.logger.info('Upload done. File path:{0}'.format(rel_path))

    def run(self, local=None, remote=None):
        file_dict = {}
        self.local_dir = local or self.local_dir
        self.remote_dir = remote or self.remote_dir
        for path, dirs, files in os.walk(self.local_dir):
            for file in files:
                if not path.endswith('\\'):
                    path += '\\'
                file_path = path + file
                if self.is_allow(file_path):
                    status = os.stat(file_path)
                    file_dict[file_path] = status
                else:
                    continue

        self.logger.info('SFTP Sync is running...')
        self.logger.info('Current dir is ' + self.local_dir)

        while True:
            paths = []
            for file, status in file_dict.items():
                if not os.path.isfile(file):
                    del file_dict[file]
                    continue
                new_status = os.stat(file)
                if new_status != status:
                    paths.append(file)
                    file_dict[file] = new_status
            if len(paths):
                self.sftp_upload(paths)
            #time.sleep(0.5)
