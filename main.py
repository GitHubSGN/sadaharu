#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：sadaharu 
@File ：main.py
@Author ：dongzhen
@Date ：2023/6/22 14:35 
'''
import logging
import os
import random
from datetime import datetime
from enum import Enum

from tools.dir_util import project_dir, dir_mk_clr
from tools.process_time_util import timer

EXP_NUM = 1000
NTile = 4
MAX_ADD_NUM = 500
DROP_PROB = 0.00

USE_LOG = True
if USE_LOG:
    log_dir = os.path.join( project_dir(), "log" )
    dir_mk_clr(log_dir)
    today_str = datetime.today().strftime("%Y%m%d_%H%M%S")
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S%p"
    logging.basicConfig(filename=os.path.join( log_dir, f"example{today_str}.log"),
                        level=logging.DEBUG,
                        format=LOG_FORMAT,
                        datefmt=DATE_FORMAT,
                        filemode='w')
    print = logging.getLogger().info
else:
    print = print

def initialize():
    card_seq = []
    for i in range(4):
        cur_seq = list(range(1, 11))
        card_seq.extend(cur_seq)
    random.shuffle(card_seq)

    return card_seq

class TileStatus(Enum):
    ALIVE = 1
    EMPTY = 2
    SADAHARU = 3

class Tile:
    def __init__(self):
        self.seq = []
        self.status = TileStatus.ALIVE

    def add_card(self, card: int):
        if card<1 or card>10:
            raise ValueError("Card should be int between 1 &. 10.")
        self.seq.append(card)
        self.status = TileStatus.ALIVE

    def __pass__(self, a, b, c):
        if a+b+c in [9, 19, 29]:
            return True
        else:
            return False

    def review_once(self):
        return_seq = []
        if len(self.seq) >= 3:
            process_choices = []
            if self.__pass__(self.seq[1], self.seq[0], self.seq[-1]):
                process_choices.append(0)
            if self.__pass__(self.seq[0], self.seq[-1], self.seq[-2]):
                process_choices.append(1)
            if self.__pass__(self.seq[-1], self.seq[-2], self.seq[-3]):
                process_choices.append(2)
            process_choice = random.choice(process_choices) if len(process_choices)>0 else -1
            # process_choice = process_choices[0] if len(process_choices) > 0 else -1

            # manually error to miss the picking
            process_choice = -1 if random.random() < DROP_PROB else process_choice

            if process_choice==0:
                return_seq = [self.seq[1], self.seq[0], self.seq[-1]]
                self.seq = self.seq[2:-1]
            elif process_choice==1:
                return_seq = [self.seq[0], self.seq[-1], self.seq[-2]]
                self.seq = self.seq[1:-2]
            elif process_choice==2:
                return_seq = [self.seq[-1], self.seq[-2], self.seq[-3]]
                self.seq = self.seq[:-3]
        return return_seq

    def review(self):
        return_seq = []
        while True:
            return_seq_once = self.review_once()
            if len(return_seq_once)==0:
                break
            else:
                return_seq.extend(return_seq_once)
        if len(self.seq)==0:
            self.status = TileStatus.EMPTY
        elif self.seq == [3]:
            self.status = TileStatus.SADAHARU
        return return_seq


def sadaharu_once():
    card_seq = initialize()
    init_card_seq = card_seq
    # card_seq = [7, 8, 10, 6, 5, 4, 1, 9, 6, 5, 1, 6, 7, 4, 3, 10, 6, 8, 10, 9, 8, 9, 9, 1, 4, 3, 7, 1, 2, 3, 5, 3, 7, 5, 2, 10, 2, 2, 8, 4]
    print(f"Card Shuffle: {card_seq}")
    tile_seq = [Tile() for i in range(NTile)]

    def status_stats(tile_seq):
        stats = [0,0,0]
        for tile in tile_seq:
            if tile.status == TileStatus.ALIVE:
                stats[0] += 1
            elif tile.status == TileStatus.EMPTY:
                stats[1] += 1
            elif tile.status == TileStatus.SADAHARU:
                stats[2] += 1
            else:
                raise ValueError(f"tile status should not be {tile.status}")
        return stats

    add_num = 0
    while True:
        for (i_tile,tile) in enumerate(tile_seq):
            if tile.status != TileStatus.EMPTY:
                tile.add_card(card_seq[0])
                add_num += 1
                card_seq = card_seq[1:]
                return_seq = tile.review()
                card_seq.extend(return_seq)
            print(f"{i_tile} Tile: {tile.seq} ({len(tile.seq)}, {tile.status})")
            print(f"Hand Card: {card_seq}")
            if len(card_seq) + sum([len(tile.seq) for tile in tile_seq]) !=40:
                print("Error Occurs: Need Debug.")
            if status_stats(tile_seq) == [0, NTile - 1, 1] or status_stats(tile_seq) == [0, NTile, 0] or status_stats(tile_seq) == [1, NTile-1, 0]:
                return True, add_num, init_card_seq
            if len(card_seq) == 0 or add_num==MAX_ADD_NUM:
                return False, add_num, init_card_seq

def sadaharu_multiple():
    success_num = 0
    add_nums = []
    inits = []

    # multiple sadaharu exps
    for i in range(EXP_NUM):
        print(f"{i} exp: \n")
        with timer(f"{i} exp:"):
            success, add_num, init_card_seq = sadaharu_once()
            add_nums.append(add_num)
            if add_num >= MAX_ADD_NUM:
                inits.append(init_card_seq)
            if success:
                success_num += 1
            print(success)
    # stat
    print(f"{success_num} success of {EXP_NUM} exps, thus win rate is {success_num / EXP_NUM * 100}%")
    with_max = sum(1 for add_num in add_nums if add_num>=MAX_ADD_NUM)
    print(f"{with_max} achieves MAX_ADD_NUM of {EXP_NUM} exps, thus percent ratio is {with_max / EXP_NUM * 100}%")
    print(f"They are: ({len(inits)})")
    print(inits)

if __name__ == '__main__':
    sadaharu_multiple()

