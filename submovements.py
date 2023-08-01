import sys
import numpy as np
import matplotlib.pyplot as plt
from FPSci_Importer.Importer import Importer
from scipy import ndimage, signal

# 获取数据库
db = Importer(sys.argv[1])
# db = Importer('test.db')
trials = db.getTrials()

# 定义低通Butterworth滤波器
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.filtfilt(b, a, data)
    return y

# 分析每个trial
for trial in trials:
    
    actions = db.getTrialPlayerActions(trial)

    # 提取视角方位角和仰角的时间序列数据
    time = [action.time for action in actions]
    azimuth = [action.view_az for action in actions]
    elevation = [action.view_el for action in actions]

    # 提取每个tiral中的目标位置数据
    target_positions = db.getTrialTargetPositionsAzimElev(trial)
    target_times = list(target_positions.keys())
    target_azimuths = [pos[1] for pos in target_positions.values()]
    target_elevations = [pos[2] for pos in target_positions.values()]

    # 使用5阶7hz的Butterworth低通滤波器对方位角和仰角数据进行滤波
    azimuth_filtered = butter_lowpass_filter(azimuth, 7, 240)
    elevation_filtered = butter_lowpass_filter(elevation, 7, 240)

    # 计算角速度
    velocity_list = []
    velocity_filtered_list = []
    submovements = []
    in_submovement = False
    Vstart = 8
    Vend = 4
    Tmin = 80 / 1000  # convert from ms to s

    for i in range(1, len(time)):
        dt = (time[i] - time[i-1]).total_seconds() 
        d_azimuth = azimuth[i] - azimuth[i-1] 
        d_elevation = elevation[i] - elevation[i-1]
        d_azimuth_filtered = azimuth_filtered[i] - azimuth_filtered[i-1]
        d_elevation_filtered = elevation_filtered[i] - elevation_filtered[i-1]

        # 计算角速度
        velocity = np.sqrt((d_azimuth / dt)**2 + (d_elevation / dt)**2)
        velocity_list.append(velocity)
        
        # 如果当前角速度与上一帧的角速度的差值绝对值大于100，则将当前角速度设为上一帧的角速度
        if len(velocity_list) > 1 and abs(velocity_list[-1] - velocity_list[-2]) > 100:
            velocity_list[-1] = velocity_list[-2]
        
        # 计算滤波后的角速度
        velocity_filtered = np.sqrt((d_azimuth_filtered / dt)**2 + (d_elevation_filtered / dt)**2)
        # 如果当前角速度与上一帧的角速度的差值绝对值大于100，则将当前角速度设为上一帧的角速度
        if len(velocity_filtered_list) > 1 and abs(velocity_filtered - velocity_filtered_list[-1]) > 100:
            velocity_filtered = velocity_filtered_list[-1]
        velocity_filtered_list.append(velocity_filtered)

        

        # 另一种数据处理方法：对角速度数据进行高斯滤波处理
        sigma = 3
        velocity_Gaussian = ndimage.gaussian_filter1d(velocity_list, sigma)

        # 分割子动作
        if in_submovement:
            if velocity_filtered < Vend and (time[i] - tstart).total_seconds() > Tmin:
                submovements[-1]['end_time'] = time[i]
                submovements[-1]['end_azimuth'] = azimuth_filtered[i]
                submovements[-1]['end_elevation'] = elevation_filtered[i]
                in_submovement = False
        else:
            if velocity_filtered > Vstart:
                in_submovement = True
                tstart = time[i]
                submovements.append({'start_time': tstart, 
                                     'start_azimuth': azimuth_filtered[i-1], 
                                     'start_elevation': elevation_filtered[i-1], 
                                     'start_velocity': velocity_filtered})

    # Add end details for the last submovement if we end in a submovement
    if in_submovement:
        submovements[-1]['end_time'] = time[-1]
        submovements[-1]['end_azimuth'] = azimuth_filtered[-1]
        submovements[-1]['end_elevation'] = elevation_filtered[-1]

    # for submovement in submovements:
    #     end_time = submovement['end_time']
    #     player_azimuth = azimuth[time.index(end_time)]
    #     player_elevation = elevation[time.index(end_time)]
    #     target_index = target_times.index(min(target_times, key=lambda t: abs((t - end_time).total_seconds())))
    #     target_azimuth = target_azimuths[target_index]
    #     target_elevation = target_elevations[target_index]
        
    #     # Calculate the angle between the player's view direction and the target's direction
    #     angle = np.arccos(np.sin(player_elevation)*np.sin(target_elevation) +
    #                       np.cos(player_elevation)*np.cos(target_elevation)*np.cos(abs(player_azimuth - target_azimuth)))

    #     # Record the angle
    #     submovement['angle_to_target'] = angle

    print("{0} submovements.".format(len(submovements)))

    # Visualization
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(time[1:], velocity_list)
    ax[0].plot(time[1:], velocity_Gaussian)
    ax[0].set_ylabel('Angular velocity')
    ax[1].plot(time[1:], velocity_filtered_list)
    ax[1].scatter(time[1:], velocity_filtered_list, marker='o', s=3, label='Filtered Velocity')
    ax[1].set_ylabel('Filtered angular velocity')
    for submovement in submovements:
        plt.text(submovement['start_time'], submovement['start_velocity'] * 2 , round(submovement['start_velocity'],2))
        plt.axvline(x=submovement['start_time'], color='r', linestyle='--')
        plt.axvline(x=submovement['end_time'], color='b', linestyle='--')
    plt.show()