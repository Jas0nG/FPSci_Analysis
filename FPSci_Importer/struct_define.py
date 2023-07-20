from datetime import datetime
import math
IN_LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

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
    if cos_angle < 1e-6:
        return 0.0
    if cos_angle > 1.0:
        cos_angle = 1.0
    # 通过反余弦函数获取夹角的弧度值
    angle_rad = math.acos(cos_angle)
    # 将弧度转换为度数
    angle_deg = math.degrees(angle_rad)
    return angle_deg

class Trial:
    def __init__(self, sessionId, blockId, tastId, tastIndex, trialId, trialIndex, startTime, endTime, duaration, taskExecTime, destroyedTargets, totalTargets, index=-1):
        self.sessionId = sessionId
        self.blockId = blockId
        self.tastId = tastId
        self.tastIdx = tastIndex
        self.trialId = trialId
        self.trialIdx = trialIndex
        self.startTime = startTime
        self.endTime = endTime
        self.duaration = duaration
        self.taskExecTime = taskExecTime
        self.destroyedTargets = destroyedTargets
        self.totalTargets = totalTargets
        self.index = index


class PlayerAction:
    def __init__(self, t, pos_az, pos_el, pos_x, pos_y, pos_z, event, state, targetId=None):
        self.time = datetime.strptime(t, IN_LOG_TIME_FORMAT)
        self.view_az = float(pos_az)
        self.view_el = float(pos_el)
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.pos_z = float(pos_z)
        self.event = event
        self.state = state
        self.targetId = targetId


class Target:
    def __init__(self, targetId, trialId, tType, tParams, model):
        self.id = targetId
        self.trial = trialId
        self.type = tType
        self.params = tParams
        self.model = model

#JasonG: 由数据库中的Targets表重构的类
class Targets:
    def __init__(self, targetId, targetType, spawnTime, size, ecc_h, ecc_v):
        self.id = targetId
        self.type = targetType
        self.spawn_time = spawnTime
        self.size = size
        self.spawn_ecc_h = ecc_h
        self.spawn_ecc_v = ecc_v

#JasonG: 由数据库中的TargetTrajectory表重构的类
class TargetTrajectory:
    def __init__(self, t, targetId, state, pos_x, pos_y, pos_z):
        self.time = datetime.strptime(t, IN_LOG_TIME_FORMAT)
        self.Id = targetId
        self.state = state
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.pos_z = float(pos_z)


class QuestionResponse:
    def __init__(self, sessionId, question, response):
        self.sessId = sessionId
        self.question = question
        self.response = response

class FrameInfo:
    def __init__(self, time, sdt):
        self.time = time
        self.sdt = float(sdt)

class Event:
    def __init__(self, time, eventType):
        self.time = time
        self.type = eventType

class Click:
    def __init__(self, time, azim, elev, hit, clicktophoton):
        self.time = time
        self.azim = azim
        self.elev = elev
        self.hit = hit
        self.clicktophoton = clicktophoton

class Users:
    def __init__(self,subject_id,session_id,time,cmp360,mouse_deg_per_mm,mouse_dpi,reticle_index,min_reticle_scale,max_reticle_scale,min_reticle_color,max_reticle_color,reticle_change_time,user_turn_scale_x,user_turn_scale_y,sess_turn_scale_x,sess_turn_scale_y,sensitivity_x,sensitivity_y):
        self.subject_id = subject_id
        self.session_id = session_id
        self.time = time
        self.cmp360 = cmp360
        self.mouse_deg_per_mm = mouse_deg_per_mm
        self.mouse_dpi = mouse_dpi
        self.reticle_index = reticle_index
        self.min_reticle_scale = min_reticle_scale
        self.max_reticle_scale = max_reticle_scale
        self.min_reticle_color = min_reticle_color
        self.max_reticle_color = max_reticle_color
        self.reticle_change_time = reticle_change_time
        self.user_turn_scale_x = user_turn_scale_x
        self.user_turn_scale_y = user_turn_scale_y
        self.sess_turn_scale_x = sess_turn_scale_x
        self.sess_turn_scale_y = sess_turn_scale_y
        self.sensitivity_x = sensitivity_x
        self.sensitivity_y = sensitivity_y

class Bearing:
    def __init__(self):
        self.azimuth = 0
        self.elevation = 0

    def __init__(self, azimuth=0, elevation=0):
        self.azimuth = azimuth
        self.elevation = elevation

    def __sub__(self,other) ->float:
        return polarAngle(other.azimuth, other.elevation, self.azimuth, self.elevation)

    def Angle(self)->float:
        return polarAngle(0, 0, self.azimuth, self.elevation)
    
