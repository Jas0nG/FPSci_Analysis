import matplotlib.pyplot as plt
from FPSci_Importer.Importer import Importer
import sys
import numpy as np

if len(sys.argv) < 2: raise Exception("Provide db filename as input!")

# Get the database
db = Importer(sys.argv[1])
# db = Importer('test.db')
trials = db.getTrials()


# Analyze each trial in the results
for trial in trials:
    # Get target trajectory and player actions from the db
    trajectories = db.getTrialTargetPositionsAzimElev(trial)  # This is now a dictionary
    actions = db.getTrialPlayerActions(trial)
    # print(trial.index)

    # 提取视角方位角和仰角的时间序列数据
    time = [action.time for action in actions]
    azimuth = [action.view_az for action in actions]
    elevation = [action.view_el for action in actions]

    # 计算合成角速度
    angular_velocity = []
    for i in range(1, len(time)):
        dt = (time[i] - time[i-1]).total_seconds()  # 计算时间间隔（单位：秒）
        d_azimuth = azimuth[i] - azimuth[i-1]  # 方位角变化量
        d_elevation = elevation[i] - elevation[i-1]  # 仰角变化量
        # 计算角速度（合成角速度）
        velocity = np.sqrt((d_azimuth / dt)**2 + (d_elevation / dt)**2)
        angular_velocity.append(velocity)

    # 绘制合成角速度-时间曲线
    plt.plot(time[1:], angular_velocity)
    plt.xlabel('Time')
    plt.ylabel('Angular Velocity')
    plt.title('Player View Angular Velocity')
    plt.show()