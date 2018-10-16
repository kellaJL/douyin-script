# -*-coding:utf8 -*-
import hashlib
import requests
import base64
import json
import time

url_preffix='https://api-cn.faceplusplus.com/facepp/'
def setParams(array,key,value):
    """
    设置参数数组
    """
    array[key]=value



class AiPlatFACEPP(object):
    def __init__(self,app_id,app_key):
        self.app_id=app_id
        self.app_key=app_key
        self.data={}
        self.url_data=''
        self.segment_url='https://api-cn.faceplusplus.com/humanbodypp/v2/segment'
        self.segment_data={}
    
    def invokeFacePP(self,params):
        """
        旷视科技
        """
        self.url_data=params
        attributes={}
        req=requests.post(self.url,data=(self.url_data))
        try:
            rsp=str(req.text)
            
            dict_rsp=json.loads(rsp)
            if 'error_message' in dict_rsp.keys():
                return attributes
            """
            情绪
            """
            # print(dict_rsp)
            emotion_att=dict_rsp['faces'][0]['attributes']['emotion']
            max_value=max(emotion_att.values())
            for key in emotion_att.keys():
                if emotion_att[key]==max_value:
                   attributes['emotion']=key
                   break
            
            """
            颜值评分
            """
            attributes['male_score']=dict_rsp['faces'][0]['attributes']['beauty']['male_score']
            attributes['female_score']=dict_rsp['faces'][0]['attributes']['beauty']['female_score']
            
            """
            性别
            """
            attributes['gender']=dict_rsp['faces'][0]['attributes']['gender']['value']

            """
            年龄
            """
            attributes['age']=dict_rsp['faces'][0]['attributes']['age']['value']

            """
            是否佩戴眼镜
            """
            attributes['galss']=dict_rsp['faces'][0]['attributes']['glass']['value']
            
            """
            人种
            """
            attributes['ethnicity']=dict_rsp['faces'][0]['attributes']['ethnicity']['value']


            return attributes
        except Exception as e:
            print(e)
            return {'ret':-1}
    
    def face_detectfacePP(self, image, mode):
        self.url = url_preffix + 'v3/detect'
        
      
        setParams(self.data, 'api_key', self.app_id)
        setParams(self.data, 'api_secret', self.app_key)
        image_data = base64.b64encode(image)
        setParams(self.data,'image_base64',image_data.decode("utf-8"))
        setParams(self.data,'return_landmark',mode)
        #....................................... 性别 年龄 微笑程度，眼镜 情绪     人种    颜值
        setParams(self.data,'return_attributes',"gender,age,smiling,eyestatus,emotion,ethnicity,beauty")
        return self.invokeFacePP(self.data)
    
    def save_segment_image(self,params):
        self.url_data=params
        attributes=''
        req=requests.post(self.segment_url,data=(self.url_data))
        try:
            rsp=str(req.text)
            
            dict_rsp=json.loads(rsp)
            if 'error_message' in dict_rsp.keys():
                return attributes
            attributes=base64.b64decode(dict_rsp['body_image'])
            return attributes
        except Exception as e:
            print(e)
            return {'ret':-1}


    def body_segment(self,image):
        setParams(self.segment_data,'api_key',self.app_id)
        setParams(self.segment_data,'api_secret',self.app_key)
        image_data=base64.b64encode(image)
        setParams(self.segment_data,'image_base64',image_data.decode("utf-8"))
        return self.save_segment_image(self.segment_data)   

    
    def compare_body(self,image1,image2):
        compare_url='https://api-cn.faceplusplus.com/facepp/v3/compare'
        compare_data={}
        setParams(compare_data,'api_key',self.app_id)
        setParams(compare_data,'api_secret',self.app_key)
        
        setParams(compare_data,'image_base64_1',image1.decode("utf-8"))
        image_data=base64.b64encode(image2)
        setParams(compare_data,'image_base64_2',image_data.decode("utf-8"))
        self.url_data=compare_data
        confidence=0
        req=requests.post(compare_url,data=(self.url_data))
        try:
            rsp=str(req.text)
            
            dict_rsp=json.loads(rsp)
            if 'error_message' in dict_rsp.keys():
                return -1
            confidence=dict_rsp['confidence']
            return confidence
        except Exception as e:
            print(e)
            return -1


if __name__ == "__main__":

    #矿视科技秘钥
    AppID='kyvvWu38YdLNSElYJ474dZeqaxuom2pe'
    AppKey='gBivbqKgUVZOKKMYbfCWSIpBfOnqR8W0'

   
    with open('D:/test.jpg', 'rb') as bin_data:
            image_data = bin_data.read()
    ai_obj=AiPlatFACEPP(AppID,AppKey)
    #旷视URL
    #rsp=ai_obj.face_detectfacePP(image_data,1)
    rsp=ai_obj.body_segment(image_data)
    with open('D:/t1.jpg','wb') as bin_data:
        bin_data.write(rsp)
    bin_data.close()
    #print(rsp)