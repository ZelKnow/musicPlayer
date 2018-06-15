import enum

@enum.unique
class PlayMode(enum.Enum):
    '''播放模式：随机、单曲循环、列表循环'''
    RANDOM = 1
    REPEAT = 2
    LOOP = 3