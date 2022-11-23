import os

HOST = '0.0.0.0'
NAME_OF_CLUSTER = os.environ.get("NAME")
PORT = os.environ.get("PORT")
ENVIRONMENT_DEBUG = os.environ.get("DEBUG")
SPARK_DISTRIBUTED_FILE_SYSTEM = '/opt/workspace/'
ALLOWED_EXTENSIONS = {'csv'}
HDFS = 'http://hdfs:9500/'
URL_ALICE = os.environ.get("URL_ALICE")
URL_BOB = os.environ.get("URL_BOB")