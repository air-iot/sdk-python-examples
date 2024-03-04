from airiot_python_sdk.algorithm.startup import Startup
from algorithm.my_algorithm import MyAlgorithmApp

if __name__ == "__main__":
    startup = Startup()
    startup.run(MyAlgorithmApp())
