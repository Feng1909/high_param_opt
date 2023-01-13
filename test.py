import yaml
from easydict import EasyDict as edict
from controller.control import MPC

if __name__ == '__main__':
    with open('config/bot.yaml') as yamlfile:
        cfgs = yaml.load(yamlfile, Loader=yaml.FullLoader)
        cfgs = edict(cfgs)
    mpc = MPC(cfgs)