import multiprocessing
import socket
import os

import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark import SparkConf
from pyspark.sql.functions import col

from settings import SPARK_DISTRIBUTED_FILE_SYSTEM


class ThesisSparkClass:

    def __init__(self,
                 project_name: str,
                 file_a: str,
                 file_b: str,
                 logger):

        self.logger = logger
        self.project_name = project_name
        self.file_a = file_a
        self.file_b = file_b

        self.dataframe = None
        self.matched_data = None
        self.metrics_dict = None
        self.df_1 = None
        self.df_2 = None
        self.matching_field = ''
        self.df_columns = []
        self.numPartitions = 1_000

        spark_driver_host = socket.gethostname()
        self.spark_conf = SparkConf() \
            .setAll([
            ('spark.master', f'spark://spark-master:7077'),
            ('spark.driver.bindAddress', '0.0.0.0'),
            ('spark.driver.host', spark_driver_host),
            ('spark.app.name', self.project_name),
            ('spark.submit.deployMode', 'client'),
            ('spark.ui.showConsoleProgress', 'true'),
            ('spark.eventLog.enabled', 'false'),
            ('spark.logConf', 'false'),
            ('spark.cores.max', "4"),
            ("spark.executor.memory", "1g"),
            ('spark.driver.memory', '15g'),
        ])
        self.spark = SparkSession.builder \
                                 .config(conf=self.spark_conf)\
                                 .enableHiveSupport() \
                                 .getOrCreate()
        self.spark.sparkContext.accumulator(0)

    def set_matching_field(self):
        import re

        self.df_columns = [name for name, value in self.df_1.take(1)[0].asDict().items()]
        self.df_columns.remove("_c0")

        matching_field = [name for name, value in self.df_1.take(1)[0].asDict().items() if not re.match("[0-9a-f]{64}", value)]
        matching_field.remove("_c0")
        self.matching_field = str(matching_field[0])

    def get_matching_field(self):
        return self.matching_field

    def read_csv(self, file_name: str) -> DataFrame:
        return self.spark.read.csv(path=f"{SPARK_DISTRIBUTED_FILE_SYSTEM}/{file_name}", sep=",", header=True)

    def extract_data(self):
        self.logger.logger.info(f"started extracting data")
        self.df_1 = self.read_csv(file_name=f'pretransformed_data/alice_{self.file_a}').coalesce(numPartitions=self.numPartitions)
        self.df_2 = self.read_csv(file_name=f'pretransformed_data/bob_{self.file_b}').coalesce(numPartitions=self.numPartitions)
        #
        self.logger.logger.info(f"finished extracting data")

    def transform_data(self):
        self.logger.logger.info(f"started transforming data")
        self.set_matching_field()

        condition = self.df_1.columns
        condition.remove(self.matching_field)
        condition.remove('_c0')

        self.df_1 = self.df_1.withColumnRenamed(self.matching_field, "MatchingFieldDF1")
        self.df_2 = self.df_2.withColumnRenamed(self.matching_field, "MatchingFieldDF2")

        self.matched_data = self.df_1.join(other=self.df_2, on=condition, how='inner').select('*')

        self.matched_data = self.matched_data.drop(col("MatchingFieldDF2"))
        self.matched_data = self.matched_data.withColumnRenamed("MatchingFieldDF1", self.matching_field)
        self.matched_data = self.matched_data.drop(*(colms for colms in self.matched_data.columns if colms not in self.df_columns))
        self.logger.logger.info(f"finished transforming data")

    def load_data(self):
        self.logger.logger.info(f"started loading data")

        directory = os.path.join(SPARK_DISTRIBUTED_FILE_SYSTEM, f'{self.project_name.lower()}')
        if not os.path.exists(directory):
            os.mkdir(directory)
        path = os.path.join(directory, 'results.csv')

        # with multiprocessing.Pool() as pool:
        #     pandas_dfs = pool.map(self.matched_data.toPandas(), [self.matched_data])
        #     pool.starmap(self.matched_data.to_csv(path, index=False), [(pandas_df, "output.csv") for pandas_df in pandas_dfs])

        # self.matched_data.coalesce(numPartitions=1).toPandas().to_csv(path, index=False)

        self.matched_data.coalesce(numPartitions=self.numPartitions).write.csv(directory, header=True, mode='overwrite')
        self.logger.logger.info(f"finished loading data")

    def start_etl(self):
        self.extract_data()
        self.transform_data()
        self.load_data()
        self.spark.stop()
