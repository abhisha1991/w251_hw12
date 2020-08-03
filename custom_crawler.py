import random
import threading
import time
import os
from os import listdir
from os.path import isfile, join
import random
import shutil
import lazynlp
from pybloom import BloomFilter

def process_files(path, id):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    for filename in files:
        file_path = os.path.join(path, filename)
        lazynlp.download_pages(file_path, "/gpfs/gpfsfpo/reddit", timeout=30, default_skip=True, extensions=[], domains=[])

if __name__ == "__main__":
    tick = time.time()
    threads = 3   # Number of threads to create

    jobs = []
    for i in range(1, threads+1):
        path = os.path.join(os.getcwd(), str(i))
        out_list = list()
        thread = threading.Thread(target=process_files(path, i))
        jobs.append(thread)

    # Start the threads
    for j in jobs:
        j.start()

    # Ensure all of the threads have finished
    for j in jobs:
        j.join()

    tock = time.time()
    print("Processing complete. Time taken ", tock-tick)

