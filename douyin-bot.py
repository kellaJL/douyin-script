# -*- coding: utf-8 -*-
import sys
import random
import time
import os
import base64
from PIL import Image


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




DEBUG_SWITCH = True
FACE_PATH = 'face/'

adb = auto_adb()
adb.test_device()
config = config.open_accordant_config()

# 审美标准
BEAUTY_THRESHOLD = 80

# 最小年龄
GIRL_MIN_AGE = 12

#源图
source_image_data="D:/compare.jpg"

#断点续存
ts=0
if not os.path.isdir('screenshot_backups'):
    os.mkdir('screenshot_backups')
if not os.path.exists('screenshot_backups/ts.txt'):
    f=open('screenshot_backups/ts.txt','w')
    f.write('0')
    f.close()
with open('screenshot_backups/ts.txt','r') as f:
    ts=int(f.readline())
f.close()

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


def thumbs_up():
    """
    点赞
    :return:
    """
    cmd = 'shell input tap {x} {y}'.format(
        x=config['star_bottom']['x'] + _random_bias(10),
        y=config['star_bottom']['y'] + _random_bias(10)
    )
    adb.run(cmd)
    time.sleep(0.5)

def source_image(image_path):
   
    f=open(image_path,'rb')
    image_data=f.read()
    image=base64.b64encode(image_data)
    f.close()
    return image

def TencentRun():
    global ts
    while True:
        next_page()

        time.sleep(1)
        screenshot.pull_screenshot()

        resize_image('autojump.png', 'optimized.png', 1024*1024)
      
       

        with open('optimized.png', 'rb') as bin_data:
            image_data = bin_data.read()
            
        
        #存储图片
        # 申请地址 http://ai.qq.com
        AppID='2108770140'
        AppKey='JWZYO7SuPcsURp04'
        ai_obj = apiutil.AiPlat(AppID, AppKey)
        rsp = ai_obj.face_detectface(image_data, 0)

        major_total = 0
        minor_total = 0

        if rsp['ret'] == 0:
            beauty = 0
            for face in rsp['data']['face_list']:
                print(face)
                face_area = (face['x'], face['y'], face['x']+face['width'], face['y']+face['height'])
                print(face_area)
                img = Image.open("optimized.png")
                cropped_img = img.crop(face_area).convert('RGB')
                cropped_img.save(FACE_PATH + face['face_id'] + '.png')
                # 性别判断
                if face['beauty'] > beauty and face['gender'] < 50:
                    beauty = face['beauty']

                if face['age'] > GIRL_MIN_AGE:
                    major_total += 1
                else:
                    minor_total += 1

            # 是个美人儿~关注点赞走一波
            if beauty > BEAUTY_THRESHOLD and major_total > minor_total:
                print('发现漂亮妹子！！！')
                thumbs_up()
                follow_user()
                #存储截图
                debug.save_debug_screenshot_font(ts,face['age'],face['beauty'])
                ts+=1

        else:
            print(rsp)
            continue


def FacePPRun():
    global ts
    global source_image_data
    while True:
        next_page()

        #time.sleep(1)
        screenshot.pull_screenshot()

        resize_image('autojump.png', 'optimized.png', 1024*1024)
      
       

        with open('optimized.png', 'rb') as bin_data:
            image_data = bin_data.read()
            
        bin_data.close()
     
        AppID='kyvvWu38YdLNSElYJ474dZeqaxuom2pe'
        AppKey='gBivbqKgUVZOKKMYbfCWSIpBfOnqR8W0'
        ai_obj = apiutilFACEPP.AiPlatFACEPP(AppID, AppKey)
        rsp = ai_obj.face_detectfacePP(image_data, 1)
        print(rsp)
        im_s=source_image(source_image_data)
        confidence = ai_obj.compare_body(im_s,image_data)

        print('相似度：'+str(confidence))
        

        if  ('female_score' in rsp.keys()) and ('male_score' in rsp.keys()) and ('age' in rsp.keys()) and ('gender' in rsp.keys()):
            
            
            # 是个美人儿~关注点赞走一波

            if rsp['female_score'] > BEAUTY_THRESHOLD and rsp['male_score'] > BEAUTY_THRESHOLD and rsp['age']>GIRL_MIN_AGE and rsp['gender']=='Female':
                print('发现漂亮妹子！！！')
                thumbs_up()
                follow_user()
                #存储截图
                rspk=ai_obj.body_segment(image_data)
                if  confidence>75:
                   print("发现高度相似，已抠像")
                   with open(os.path.join('screenshot_backups','#segment-'+str(ts)+'.png'),'wb') as bin_data:
                      bin_data.write(rspk)
                   bin_data.close()
                debug.save_debug_screenshot_font(ts,rsp['age'],rsp['male_score'])
                ts+=1

        else:
            print(rsp)
            continue

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
