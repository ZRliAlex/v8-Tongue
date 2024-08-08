import os.path
from segment import Segment


def inference(source):
    model = Segment()
    model.inference(source)
    model.output(source)


if __name__ == "__main__":
    inference(r"/home/medcv/tongue/tongue_server_v8s_24_06_25/uploads/tmp")


