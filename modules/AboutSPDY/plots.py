#
# Alcides Viamontes Esquivel
#  Zunzun AB
#  www.zunzun.se
#
#  Copyright 2015
#
#  Distribution of this file is subject
#  to the accompanying licence in this 
#  project. 
#
from collections import defaultdict
import pandas as pd
import numpy as np

import sys
import pandas as pd

import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

test_record = np.array([(393.0, 637.0, 186565), (680.0, 789.0, 1566358),
       (1019.0, 1019.0, 1577), (1152.0, 1152.0, 1577),
       (684.0, 684.0, 1577), (829.0, 846.0, 583492), (1315.0, 1315.0, 402),
       (1324.0, 1348.0, 583403), (1466.0, 1467.0, 8675),
       (1686.0, 2085.0, 171987)],
      dtype=[('starts', '<f8'), ('ends', '<f8'), ('bytes', '<i8')])


def discretize_load_distribution(load_entries, time_delta_size, bytes_horizon):
    bytes_scale = 1 # Not needed anymore...
    time_unit_to_bytes = defaultdict(int)
    for (start_time, end_time, bytes_downloaded) in load_entries:
        time_unit_starts_index = int( start_time // time_delta_size )
        time_unit_ends_index = int( end_time // time_delta_size )

        if end_time == start_time :
            time_unit_to_bytes [ time_unit_starts_index ] += bytes_downloaded / bytes_scale
            continue

        if time_unit_starts_index == time_unit_ends_index:
            time_unit_to_bytes[ time_unit_starts_index ] += bytes_downloaded / bytes_scale
            continue

        distributed = 0
        bytes_per_time_unit =  bytes_downloaded / float(end_time - start_time)
        bytes_per_time_delta = bytes_per_time_unit * time_delta_size

        # Account correctly for the two ends...
        bytes_at_start = bytes_per_time_unit * (time_delta_size - ( start_time - time_unit_starts_index*time_delta_size ) )
        assert bytes_at_start >= 0
        distributed += bytes_at_start
        bytes_at_end = bytes_per_time_unit * ( end_time - time_unit_ends_index*time_delta_size )
        distributed += bytes_at_end
        assert bytes_at_end >= 0

        time_unit_to_bytes[time_unit_starts_index] += bytes_at_start/bytes_scale
        time_unit_to_bytes[time_unit_ends_index] += bytes_at_end/bytes_scale

        ratio = bytes_per_time_delta/bytes_scale
        for i in range(time_unit_starts_index+1, time_unit_ends_index):
            time_unit_to_bytes[i] += ratio
            distributed += bytes_per_time_delta

        assert( abs(distributed-bytes_downloaded) < 1)


    new_dict = defaultdict()
    weight_cursor = 0.0
    top = max(time_unit_to_bytes.keys())
    for i in range(top):
        time_point = i
        weight = time_unit_to_bytes[time_point]
        new_dict[time_point] = weight_cursor
        weight_cursor += weight/bytes_horizon


    return pd.Series(new_dict)


milliseconds=30
bytes_unit = 1
def plot_bandwith_on_load(f, horizon_bytes, label_on_top):

    starts = f['started_date_time'][0]
    start_series = (f['started_date_time'] - starts)/np.timedelta64(1, 'ms') + \
                  f['tm_dns'] + f['tm_connect'] + f['tm_send'] + f['tm_wait']
    end_series = start_series + f['tm_receive']
    load_distrib_frame = pd.DataFrame({
        'starts': start_series,
        'ends'  : end_series,
        'bytes' : f['sz_response_body']+f['sz_response_headers']
    }, columns=['starts', 'ends', 'bytes'])
    records = load_distrib_frame.to_records(index=False)

    spaces_per_second = 1000.0/milliseconds
    load_distrib_quant = discretize_load_distribution( records, milliseconds, horizon_bytes )
    fig = plt.figure(figsize=(16,6))
    ax = fig.add_subplot(111);
    #ax.bar(left=load_distrib_quant.index/spaces_per_second, height=load_distrib_quant, width=milliseconds/1000.);
    ax.plot(load_distrib_quant.index/spaces_per_second, load_distrib_quant)
    ax.set_xlabel('time')
    ax.set_ylabel('fraction of {0} bytes loaded'.format(horizon_bytes))
    ax.set_xlim((0.0, 5.0))
    ax.set_ylim((0.0, 1.0))
    ax.set_title(label_on_top)
    return ax


def _main():
    print( discretize_load_distribution(test_record, 10, 50) )


if __name__ == '__main__':
    _main()
