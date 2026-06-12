from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("WordCount").getOrCreate()

df = spark.read.csv("s3a://zxy-spark-data/data/douban_movies.csv", header=True, inferSchema=True)
print("Schema:")
df.printSchema()
print("\n前5行数据:")
df.show(5)
print(f"\n总行数: {df.count()}")

spark.stop()