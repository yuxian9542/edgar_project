from  johnsnowlabs import nlp
import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--driver-java-options "--add-opens java.base/java.nio=ALL-UNNAMED" pyspark-shell'
nlp.load('emotion').predict('Wow that easy!')