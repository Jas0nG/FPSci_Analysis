from datetime import datetime
IN_LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

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