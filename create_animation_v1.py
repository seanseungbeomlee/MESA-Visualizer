import mesa_reader as mr
import utils
import os
from moviepy.editor import ImageSequenceClip

# head -10000 history.data > history_trunc.data

# initialize history and profile
file = input('Enter MESA file name: ')
# h1 = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file +'/LOGS1/history.data')
# h2 = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file + '/LOGS2/history.data')
# b = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file + '/binary_history.data')
h1 = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file +'/history_trunc/history1_trunc.data')
h2 = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file + '/history_trunc/history2_trunc.data')
b = mr.MesaData('/Users/sean/Documents/Ricker_Research/' + file + '/history_trunc/binary_history_trunc.data')
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
utils.create_Snapshot(M1, M2, R1, R2, T1, T2, a, t_uniform, file, n_frames)
plot_names = utils.create_SnapshotTitles(n_frames)

# compiling animation
clip = ImageSequenceClip(['/Users/sean/Documents/Ricker_Research/' + file + '/PNGS/' + name for name in plot_names], fps=fps)
clip.write_videofile('/Users/sean/Documents/Ricker_Research/animations/' + file +'.mp4', fps=24, codec='libx264')
