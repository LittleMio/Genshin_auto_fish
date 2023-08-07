#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.

import os
import argparse
import random
import time
import torch
import keyboard
import winsound
import win32gui

from loguru import logger
from yolox.exp import get_exp
from yolox.utils import fuse_model, get_model_info
from yolox.data.datasets.voc_classes import VOC_CLASSES

from utils.config import config
from fisher.predictor import Predictor
from fisher.environment import FishFind
from fisher.fish import Window, Check

def make_parser():
    parser = argparse.ArgumentParser("YOLOX Demo!")
    parser.add_argument("-demo", default="image", help="demo type, eg. image, video and webcam")
    parser.add_argument("-expn", "--experiment-name", type=str, default=None)
    parser.add_argument("-n", "--name", type=str, default=None, help="model name")
    parser.add_argument("--path", default="./assets/dog.jpg", help="path to images or video")

    # exp file
    parser.add_argument(
        "-f",
        "--exp_file",
        default="yolox/exp/yolox_tiny_fish.py",
        type=str,
        help="pls input your experiment description file",
    )
    parser.add_argument("-c", "--ckpt", default="weights/best_tiny3.pth", type=str, help="ckpt for eval")
    parser.add_argument(
        "--device",
        default="cpu",
        type=str,
        help="device to run our model, can either be cpu or gpu",
    )
    parser.add_argument("--conf", default=0.25, type=float, help="test conf")
    parser.add_argument("--nms", default=0.45, type=float, help="test nms threshold")
    parser.add_argument("--tsize", default=640, type=int, help="test img size")
    parser.add_argument(
        "--fp16",
        dest="fp16",
        default=False,
        action="store_true",
        help="Adopting mix precision evaluating.",
    )
    parser.add_argument(
        "--legacy",
        dest="legacy",
        default=False,
        action="store_true",
        help="To be compatible with older versions",
    )
    parser.add_argument(
        "--fuse",
        dest="fuse",
        default=False,
        action="store_true",
        help="Fuse conv and bn for testing.",
    )
    parser.add_argument(
        "--trt",
        dest="trt",
        default=False,
        action="store_true",
        help="Using TensorRT model for testing.",
    )
    return parser


def main(exp, args):
    if not args.experiment_name:
        args.experiment_name = exp.exp_name

    if args.trt:
        args.device = "gpu"

    if config.is_debug:
        logger.info("Args: {}".format(args))

    if args.conf is not None:
        exp.test_conf = args.conf
    if args.nms is not None:
        exp.nmsthre = args.nms
    if args.tsize is not None:
        exp.test_size = (args.tsize, args.tsize)

    model = exp.get_model()

    if config.is_debug:
        logger.info("Model Summary: {}".format(get_model_info(model, exp.test_size)))

    if args.device == "gpu":
        model.cuda()
        if args.fp16:
            model.half()  # to FP16
    model.eval()

    if not args.trt:
        if args.ckpt is None:
            ckpt_file = os.path.join(file_name, "best_ckpt.pth")
        else:
            ckpt_file = args.ckpt
        if config.is_debug:
            logger.info("loading checkpoint")
        ckpt = torch.load(ckpt_file, map_location="cpu")
        # load the model state dict
        model.load_state_dict(ckpt["model"])
        if config.is_debug:
            logger.info("loaded checkpoint done.")

    if args.fuse:
        logger.info("\tFusing model...")
        model = fuse_model(model)

    if args.trt:
        assert not args.fuse, "TensorRT model is not support model fusing!"
        if args.ckpt is None:
            trt_file = os.path.join(file_name, "model_trt.pth")
        else:
            trt_file = args.ckpt
        assert os.path.exists(
            trt_file
        ), "TensorRT model is not found!\n Run python3 tools/trt.py first!"
        model.head.decode_in_inference = False
        decoder = model.head.decode_outputs
        logger.info("Using TensorRT to inference")
    else:
        trt_file = None
        decoder = None

    predictor = Predictor(model, exp, VOC_CLASSES, trt_file, decoder, args.device, args.fp16, args.legacy)

    print('INIT OK')
    while True:
        print('Waiting for "r" to perform fishing')
        winsound.Beep(500, 500)
        keyboard.wait('r')
        winsound.Beep(500, 500)
        if args.demo == "image":
            start_fishing(predictor, config.time_out)


def start_fishing(predictor, TIME_OUT):
    ff = FishFind(predictor)
    window = Window(config.window_name, 'UnityWndClass')
    Check.setup(window.capture, config.ready_rect, config.pos_dect)

    do_fish_count = 0
    while True:
        if do_fish_count > 4:
            winsound.Beep(500, 1000)
            time.sleep(0.5)
            winsound.Beep(500, 1000)
            time.sleep(0.5)
            winsound.Beep(500, 1000)
            do_fish_count = 0
            break
        result: bool = ff.do_fish()

        # continue if no fish found
        if not result:
            do_fish_count += 1
            continue

        do_fish_count = 0
        winsound.Beep(700, 500)
        while result is True:
            start_time = time.time()
            while win32gui.GetForegroundWindow() != window.hWnd or not Check().isReady():
                time.sleep(.05)
                if round(time.time() - start_time, 1) > TIME_OUT:
                    window.click(.08 + random.random()*.2)
                    break
                assert win32gui.IsWindow(window.hWnd)
            time.sleep(.2 + random.random()*.9)
            window.click(.8)
            while True:
                pos = Check().getPos()
                if pos is None:
                    break
                cur, front, back = pos
                if config.show_cur:
                    buf = list(f'[{window.width:8}x{window.height:<9}{window.width:9}x{window.height:<8}]')
                    buf[front // 10 + 2: back // 10 + 5] = f' <{"":{back // 10 - front // 10 - 1}}> '
                    buf[cur // 10 + 2: cur // 10 + 5] = f'{"<" if buf[cur // 10 + 2] == "<" else " "}|{">"if buf[cur // 10 + 4]==">" else " "}'
                    print(''.join(buf), end='\r')
                if cur + 10 < (front + back) // 2:
                    window.click(.08 + random.random() * .2)
                else:
                    time.sleep(random.random() * .2)
            time.sleep(3)
            break
    winsound.Beep(900, 500)
    time.sleep(3)


# python fishing.py image -f yolox/exp/yolox_tiny_fish.py -c weights/best_tiny3.pth --conf 0.25 --nms 0.45 --tsize 640 --device gpu
if __name__ == "__main__":
    args = make_parser().parse_args()
    exp = get_exp(args.exp_file, args.name)
    main(exp, args)
