import matplotlib.pyplot as plt
from FPSci_Importer.Importer import Importer
from FPSci_Importer.struct_define import *
import sys
import numpy as np
import math
import matplotlib.pyplot as plt


def polarAngle(theta1_d, phi1_d, theta2_d, phi2_d):
    # 转换为弧度
    theta1 = math.radians(theta1_d)
    phi1 = math.radians(phi1_d)
    theta2 = math.radians(theta2_d)
    phi2 = math.radians(phi2_d)
    # 计算夹角的余弦值
    cos_angle = math.sin(theta1) * math.sin(theta2) * math.cos(phi1 - phi2) + math.cos(
        theta1
    ) * math.cos(theta2)
    # 通过反余弦函数获取夹角的弧度值
    angle_rad = math.acos(cos_angle)
    # 将弧度转换为度数
    angle_deg = math.degrees(angle_rad)
    return angle_deg


if len(sys.argv) < 2:
    raise Exception("Provide db filename as input!")


def main():
    showDebugInfo = False
    # Get the database
    db = Importer(sys.argv[1])
    trials = db.getTrials()

    # JasonG: Process each trial
    score = []
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
        if showDebugInfo:
            print(
                "====Trial:",
                trial.index,
                "Uses:",
                float(trial.taskExecTime) * 1000,
                "ms====",
            )
            print("Start Time:  ", trial.startTime)
            print("End Time:    ", trial.endTime)
            # JasonG: Target spawn after 7us(0.007ms) after trial start, this duration could be ignored
            print("Target Spwan:", target.spawn_time)
        query_destory = "SELECT * FROM Player_Action WHERE [time] <= '{0}' AND [time] >= '{1}'  AND [event] == 'destroy'".format(
            trial.endTime, trial.startTime
        )
        query_start_aim = "SELECT * FROM Player_Action WHERE [time] <= '{0}' AND [time] >= '{1}'  AND [event] == 'aim'".format(
            trial.endTime, trial.startTime
        )
        action_destory = PlayerAction(*db.queryDb(query_destory)[0])
        action_start_aim = PlayerAction(*db.queryDb(query_start_aim)[0])
        if showDebugInfo:
            print("Destory Time:", action_destory.time)
            print("Start Aim Time:", action_start_aim.time)
            print("Start Bearing:", action_start_aim.view_az, action_start_aim.view_el)
            print("Destory Bearing:", action_destory.view_az, action_destory.view_el)
        angle = polarAngle(
            action_start_aim.view_az,
            action_start_aim.view_el,
            action_destory.view_az,
            action_destory.view_el,
        )
        # Lower the better
        score.append(trial.taskExecTime / angle)

    print("Ave Result:", sum(score) / len(score), "s/deg")

    x = range(len(score))
    plt.title(sys.argv[1])
    plt.plot(x, score)
    plt.xlabel("Trial Index")
    plt.ylabel("Uses Time per Degree(lower the better)")
    plt.show()


if __name__ == "__main__":
    main()
