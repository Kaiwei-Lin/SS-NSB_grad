import argparse, os
from importlib import import_module

from src.util.config_parse import ConfigParser
from src.trainer import get_trainer_class

def main():
    # parsing configuration
    args = argparse.ArgumentParser()
    args.add_argument('-gr', '--group_name', default=None,  type=str)
    args.add_argument('-s', '--session_name', default=None,  type=str)
    args.add_argument('-c', '--config',       default='SSBSN_SIDD',  type=str)
    args.add_argument('-r', '--resume',       action='store_true')
    args.add_argument('-g', '--gpu',          default='0',  type=str)
    args.add_argument(      '--thread',       default=4,     type=int)

    args = args.parse_args()

    assert args.config is not None, 'config file path is needed'
    if args.session_name is None:
        args.session_name = args.config # set session name to config file name

    cfg = ConfigParser(args)

    # intialize trainer
    trainer = get_trainer_class(cfg['trainer'])(cfg)
    trainer.set_device(args.gpu)
    trainer.train()


if __name__ == '__main__':
    main()
