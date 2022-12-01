import mesa_reader as mr
import utils
import os
from moviepy.editor import ImageSequenceClip
import time
import argparse
import multiprocessing as mp
from multiprocessing import Pool

start = time.time()

# TODO: add argparse for history file, number of cores, and view of the first n number of lines of the history file
parser = argparse.ArgumentParser(description='Create MESA animation.')
parser.add_argument('--file', help='name of history file')
parser.add_argument('--numworkers', help='number of processors to use')
parser.add_argument('--head', help='use the first n number of lines for the history file')
args = parser.parse_args()


# to truncate history: head -10000 history.data > history_trunc.data
# initialize history and profile
file = args.file
h1 = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file +'/LOGS1/history.data')
h2 = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file + '/LOGS2/history.data')
b = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file + '/binary_history.data')
print('Initialized history and binary files...')

# getting system variables
movie_length = 30 # in seconds
fastest_feature = 1
fps = 24
n_frames = int(movie_length*fps)
t_uniform, M1, M2, R1, R2, T1, T2, a = utils.get_SysVars(h1, h2, b, n_frames=n_frames)
print('Obtained system variables...')

# create separate ../mesa/PNGS directory for each run
try:
    os.makedirs('/Users/sean/Documents/Ricker_Research/' + file + '/PNGS/')
    print('Created PNGS directory...')
except OSError as error:
    print(error)

# creating snapshots
timeout = 10
timeout_start = time.time()
# TODO: make parallel here; potentially move snapshot code to main function
while time.time() < timeout_start - timeout:
    utils.create_Snapshot(M1, M2, R1, R2, T1, T2, a, t_uniform, file, n_frames)
plot_names = utils.create_SnapshotTitles(n_frames)

# compiling animation
clip = ImageSequenceClip(['/Users/sean/Documents/Ricker_Research/' + file + '/PNGS/' + name for name in plot_names], fps=fps)
clip.write_videofile('/Users/sean/Documents/Ricker_Research/animations/' + file +'.mp4', fps=24, codec='libx264')

end = time.time()
execution_time = end - start
print('Execution time in seconds: ' + str(execution_time))

# TODO: Create snapshots in parallel:
# Can split the history data into batches based on the number of workers.
numworkers = args.numworkers
numtasks = len(t_uniform)
# TODO: handle the case when the number of frames is not divisible by the number of workers
# code from meeting:
def create(nw, nt):
    div = nt // nw
    rem = nt % nw
    istart = [0] * nw
    iend = [div-1] * nw
    for i in range(1, nw):
        istart[i] = iend[i-1] + 1
        if i < nw-rem:
            iend[i] = istart[i] + iend[i]
        else:
            iend[i] = istart[i] + iend[i] + 1
    return istart, iend
istart, iend = create(numworkers, numtasks)

with Pool(numworkers) as p:
    p.map(utils.create_Snapshot(), )
