import matplotlib.pyplot as plt
from FPSci_Importer.Importer import Importer
from FPSci_Importer.struct_define import *
import sys
import numpy as np
import pandas as pd
import math

def reactionAnalysis(aimAngleTimeline):
    sorted(aimAngleTimeline)
    for i in range(len(list(aimAngleTimeline.values()))):
        if list(aimAngleTimeline.values())[i] > 0.5:
            return list(aimAngleTimeline.keys())[i]
    return 0


def visualizeTimeline(timeline_1, title_1, ylable_1, timeline_2=None, title_2=None, ylable_2=None):
    plt.style.use("seaborn")
    if timeline_2 is not None and title_2 is not None and ylable_2 is not None:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        axes[0].plot(list(timeline_1.keys()), list(timeline_1.values()))
        axes[0].set_ylabel(ylable_1)
        axes[0].set_title(title_1)
        axes[1].plot(list(timeline_2.keys()), list(timeline_2.values()))
        axes[1].set_ylabel(ylable_2)
        axes[1].set_title(title_2)
    else:
        plt.plot(list(timeline_1.keys()), list(timeline_1.values()))
        plt.xlabel("Time(ms)")
        plt.ylabel(ylable_1)
        plt.title(title_1)
    plt.show()

def find_relative_minima(arr):
    minima_indices = []
    winSize = 20

    for i in range(winSize, len(arr) - winSize):
        if arr[i] < min(arr[i-winSize:i]) or arr[i] < min(arr[i+1:i+winSize+1]):
            minima_indices.append(i)

    return minima_indices


if len(sys.argv) < 2:
    raise Exception("Provide db filename as input!")


def main():
    #                      Parameters                            #
    doOutlierDetection = False
    visualize_Vel_Ang = False
    #############################################################

    # Get the database
    db = Importer(sys.argv[1])
    trials = db.getTrials()

    score = []
    recognitionTime = []
    # JasonG: Get the user information, mainly for sensitivity
    query_User = "SELECT * FROM Users"
    user = Users(*db.queryDb(query_User)[len(db.queryDb(query_User)) - 1])
    # JasonG: mapX, mapY表示鼠标每移动1cm，视角水平和垂直方向的变化角度
    mapX = 360 / user.sensitivity_x
    mapY = 360 / user.sensitivity_y
    max_speed = 30  # 100 cm/s
    max_angular_speed_x = max_speed * mapX  # degree/s
    max_angular_speed_y = max_speed * mapY  # degree/s
    print(
        "max_angular_speed_x:",
        max_angular_speed_x,
        "max_angular_speed_y:",
        max_angular_speed_y,
    )

    # JasonG: Process each trial
    for trial in trials:
        query_Target = "SELECT * FROM Targets WHERE [spawn_time] <= '{0}' AND [spawn_time] >= '{1}'".format(
            trial.endTime, trial.startTime
        )
        # JasonG: Get the target information
        target = Targets(*db.queryDb(query_Target)[0])
        if target.type == "warm-up":
            continue
        query_Traget_Traj = (
            "SELECT * FROM Target_Trajectory WHERE [target_id] == '{0}'".format(
                target.id
            )
        )
        # JasonG: Trajectory of the target stays the same within a trial in our implementation
        traj = TargetTrajectory(*db.queryDb(query_Traget_Traj)[0])
        # print(
        #     "====Trial:",
        #     trial.index,
        #     "Uses:",
        #     float(trial.taskExecTime) * 1000,
        #     "ms====",
        # )
        query_destory = "SELECT * FROM Player_Action WHERE [time] <= '{0}' AND [time] >= '{1}'  AND [event] == 'destroy'".format(
            trial.endTime, trial.startTime
        )
        query_aim = "SELECT * FROM Player_Action WHERE [time] <= '{0}' AND [time] >= '{1}' ".format(
            trial.endTime, trial.startTime
        )
        action_destory = PlayerAction(*db.queryDb(query_destory)[0])
        action_start_aim = PlayerAction(*db.queryDb(query_aim)[0])
        target_bearing = Bearing(action_destory)
        aim_start_bearing = Bearing(action_start_aim)
        last_bearing = Bearing()
        aim_angle_Timeline, aim_vel_Timeline = {}, {}
        last_timeStamp = 0

        total_angle = target_bearing - aim_start_bearing
        recognition = 0
        for row in db.queryDb(query_aim):
            action = PlayerAction(*row)
            timeStamp = (
                action.time - action_start_aim.time
            ).total_seconds() * 1e3  # JasonG: 从action开始的时间戳 ms
            aim_moving_bearing = Bearing(action)
            # JasonG: skip 1st frame
            if last_timeStamp == 0:
                last_bearing = aim_moving_bearing
                last_timeStamp = timeStamp
                continue
            # JasonG: 角速度 = (当前方位角 - 上一帧方位角) / (当前时间戳 - 上一帧时间戳)
            ang_vel = (
                (aim_moving_bearing - last_bearing) / (timeStamp - last_timeStamp) * 1e3
            )  # degree/s
            if not doOutlierDetection:
                aim_vel_Timeline[timeStamp] = ang_vel
                aim_angle_Timeline[timeStamp] = aim_moving_bearing - aim_start_bearing
                # minima_indiaces = find_relative_minima(list(aim_vel_Timeline.values()))
            else:
                if ang_vel < max_angular_speed_x:
                    aim_vel_Timeline[timeStamp] = ang_vel
                    aim_angle_Timeline[timeStamp] = (
                        aim_moving_bearing - aim_start_bearing
                    )
                else:
                    # JasonG: Outlier detected
                    print("detected OD")
                    continue
        series_velocity = pd.Series(aim_vel_Timeline)
        series_angle    = pd.Series(aim_angle_Timeline)
        print(series_velocity)
        print(series_velocity.describe())
        input()

        if aim_moving_bearing - aim_start_bearing > total_angle * 0.05 and recognition == 0:
            recognition = 1
            recognitionTime.append(timeStamp)
            # if timeStamp < 80:
            #     visualizeTimeline(
            #         aim_vel_Timeline,
            #         "Angular Velocity",
            #         "Angular Velocity(degree/s)",
            #         aim_angle_Timeline,
            #         "Aim Angle",
            #         "Aim Angle(degree)",
            #     )
            last_bearing = aim_moving_bearing
            last_timeStamp = timeStamp
        if visualize_Vel_Ang or True:
            visualizeTimeline(
                aim_vel_Timeline,
                "Angular Velocity",
                "Angular Velocity(degree/s)",
                aim_angle_Timeline,
                "Aim Angle",
                "Aim Angle(degree)"
            )
        # recTime = reactionAnalysis(aim_angle_Timeline)
        # if 80 < recTime < 400:
            # recognitionTime.append(recTime)
    # end for trial in trials

    # Plot Reaction time
    plt.figure(sys.argv[1])
    plt.style.use("seaborn")
    plt.hist(recognitionTime, bins=20, edgecolor="black", linewidth=1.2)
    plt.xlabel("Recognition Time(ms)")
    plt.ylabel("Frequency")
    plt.title("Recognition Time Distribution")
    plt.show()


if __name__ == "__main__":
    main()
