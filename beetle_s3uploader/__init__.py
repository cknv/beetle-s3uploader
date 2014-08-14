from boto.s3.connection import S3Connection, Key
# from boto.s3 import Key
from boto.exception import S3ResponseError
import mimetypes
from StringIO import StringIO
from gzip import GzipFile
import zlib
import os

class Uploader:
    def __init__(self, config, beetle_config):
        self.folder = beetle_config.folders['output']
        self.bucket_name = beetle_config.site['domain']
        self.gzip = config.get('gzip', False)
        self.cache = config.get('cache', 3600)
        # Using environment variables
        self.connection = S3Connection()
        self.bucket = self.get_bucket()
        self.headers = config.get('headers', [])

    def get_bucket(self):
        try:
            return self.connection.get_bucket(self.bucket_name)
        except S3ResponseError as err:
            return self.connection.create_bucket(self.bucket_name)

    def list_files(self):
        for folder, __, file_names in os.walk(self.folder):
            for file_name in file_names:
                yield os.path.join(folder, file_name)

    def read_files(self):
        for page_path in self.list_files():
            destination = os.path.relpath(page_path, self.folder)
            content_type, content_encoding = mimetypes.guess_type(destination)
            prefix, suffix = content_type.split('/')
            with open(page_path) as file_in:
                # Check if we are gzipping.
                # And if the file will actually benefit from being compressed.
                if self.gzip and prefix not in {'image'}:
                    # Build a compressor, it's a bit magic.
                    compressor = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
                    compressed = compressor.compress(file_in.read()) + compressor.flush()
                    yield destination, compressed, content_type, True
                else:
                    yield destination, file_in.read(), content_type, False          

    def upload(self):
        for destination, data, content_type, compressed in self.read_files():
            key = Key(self.bucket)
            key.content_type = content_type
            if compressed:
                key.set_metadata('content-encoding', 'gzip')

            for header, value in self.headers:
                key.set_metadata(header, value)
            key.key = destination
            key.set_contents_from_string(data)

    def clean(self):
        for key in self.bucket.get_all_keys():
            key.delete()


def register(plugin_config, config, commander, builder, content_renderer):
    uploader = Uploader(plugin_config, config)
    commander.add('s3upload', uploader.upload)
    commander.add('s3clean', uploader.clean)
