# -*- coding: utf-8 -*-
import sys
import random
import time
import os
from PIL import Image
import base64

if sys.version_info.major != 3:
    print('Please run under Python3')
    exit(1)
try:
    from common import debug, config, screenshot, UnicodeStreamFilter
    from common.auto_adb import auto_adb
    from common import apiutil
    from common import apiutilFACEPP
    from common.compression import resize_image
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(1)

VERSION = "0.0.1"

#源图
source_image_data="D:/compare.jpg"

DEBUG_SWITCH = True
FACE_PATH = 'face/'

adb = auto_adb()
adb.test_device()
config = config.open_accordant_config()

def yes_or_no():
    """
    检查是否已经为启动程序做好了准备
    """
    while True:
        yes_or_no = str(input('请确保手机打开了 ADB 并连接了电脑，'
                              '然后打开手机软件，确定开始？[y/n]:'))
        if yes_or_no == 'y':
            break
        elif yes_or_no == 'n':
            print('谢谢使用', end='')
            exit(0)
        else:
            print('请重新输入')


def _random_bias(num):
    """
    random bias
    :param num:
    :return:
    """
    print('num = ', num)
    return random.randint(-num, num)


def next_page():
    """
    翻到下一页
    :return:
    """
    cmd = 'shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=config['center_point']['x'],
        y1=config['center_point']['y']+config['center_point']['ry'],
        x2=config['center_point']['x'],
        y2=config['center_point']['y'],
        duration=200
    )
    adb.run(cmd)
    time.sleep(1.5)



def follow_user():
    """
    关注用户
    :return:
    """
    cmd = 'shell input tap {x} {y}'.format(
        x=config['follow_bottom']['x'] + _random_bias(10),
        y=config['follow_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)

def source_image(image_path):
   
    f=open(image_path,'rb')
    image_data=f.read()
    image=base64.b64encode(image_data)
    f.close()
    return image
    

def FacePPRun():
    global source_image_data
    while True:
        next_page()

        #time.sleep(1)
        screenshot.pull_screenshot()

        resize_image('autojump.png', 'optimized.png', 1024*1024)
      
       

        with open('optimized.png', 'rb') as bin_data:
            image_data = bin_data.read()
            
        
     
        AppID='kyvvWu38YdLNSElYJ474dZeqaxuom2pe'
        AppKey='gBivbqKgUVZOKKMYbfCWSIpBfOnqR8W0'
        ai_obj = apiutilFACEPP.AiPlatFACEPP(AppID, AppKey)
        im_s=source_image(source_image_data)
        confidence = ai_obj.compare_body(im_s,image_data)
        print('相似度：'+str(confidence))
        

        if  confidence>75:
            print("发现高度相似，已关注")
            follow_user()

def main():
    """
    main
    :return:
    """
    print('程序版本号：{}'.format(VERSION))
    print('激活窗口并按 CONTROL + C 组合键退出')
    debug.dump_device_info()
    screenshot.check_screenshot()

    #TencentRun()
    FacePPRun()


if __name__ == '__main__':
    try:
        # yes_or_no()
       
        
        main()
    except KeyboardInterrupt:
        adb.run('kill-server')
        print('谢谢使用')
        exit(0)
