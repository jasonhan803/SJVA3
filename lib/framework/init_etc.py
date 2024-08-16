# -*- coding: utf-8 -*-
import os, traceback, sys

from datetime  import datetime, timedelta
from flask import request, abort
from functools import wraps
from flask import request

def check_api(original_function):
    @wraps(original_function)
    def wrapper_function(*args, **kwargs):  #1
        from framework import logger
        #logger.debug('CHECK API... {} '.format(original_function.__module__))
        #logger.warning(request.url)
        #logger.warning(request.form)
        try:
            from system import ModelSetting as SystemModelSetting
            if SystemModelSetting.get_bool('auth_use_apikey'):
                if request.method == 'POST':
                    apikey = request.form['apikey']
                else:
                    apikey = request.args.get('apikey')
                #apikey = request.args.get('apikey')
                if apikey is None or apikey != SystemModelSetting.get('auth_apikey'):
                    logger.debug('CHECK API : ABORT no match ({})'.format(apikey))
                    logger.debug(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
                    abort(403)
                    return 
        except Exception as exception: 
            print('Exception:%s', exception)
            print(traceback.format_exc())
            logger.debug('CHECK API : ABORT exception')
            abort(403)
            return 
        return original_function(*args, **kwargs)  #2
    return wrapper_function


def make_default_dir(path_data):
    try:
        if not os.path.exists(path_data):
            os.mkdir(path_data)
        tmp = os.path.join(path_data, 'tmp')
        try:
            import shutil
            if os.path.exists(tmp):
                shutil.rmtree(tmp)
        except:
            pass
        sub = ['db', 'log', 'download', 'command', 'custom', 'output', 'tmp']
        for item in sub:
            tmp = os.path.join(path_data, item)
            if not os.path.exists(tmp):
                os.mkdir(tmp)
    except Exception as exception: 
        print('Exception:%s', exception)
        print(traceback.format_exc())
        


def pip_install():
    from framework import app
    try:
        import discord_webhook
    except:
        try: os.system("{} install discord-webhook".format(app.config['config']['pip']))
        except: pass

    try:
        from flaskext.markdown import Markdown
    except:
        try: os.system("{} install Flask-Markdown".format(app.config['config']['pip']))
        except: pass

        
                    

def get_ip():
    headers_list = request.headers.getlist("X-Forwarded-For")
    return headers_list[0] if headers_list else request.remote_addr


def config_initialize(action):
    from . import logger, app

    if action == 'start':
        init_define()
        

        app.config['config']['run_by_real'] = True if sys.argv[0] == 'sjva.py' or sys.argv[0] == 'sjva3.py' else False
        #app.config['config']['run_by_migration'] = True if sys.argv[-2] == 'db' else False
        app.config['config']['run_by_worker'] = True if sys.argv[0].find('celery') != -1 else False
        app.config['config']['run_by_init_db'] = True if sys.argv[-1] == 'init_db' else False
        if sys.version_info[0] == 2: 
            app.config['config']['pip'] = 'pip'
            app.config['config']['is_py2'] = True
            app.config['config']['is_py3'] = False
        else: 
            app.config['config']['is_py2'] = False
            app.config['config']['is_py3'] = True
            app.config['config']['pip'] = 'pip3'
        
        app.config['config']['is_debug'] = False
        app.config['config']['repeat'] = -1

        if app.config['config']['run_by_real']:
            try:
                if len(sys.argv) > 2:
                    app.config['config']['repeat'] = int(sys.argv[2])
            except:
                app.config['config']['repeat'] = 0
        if len(sys.argv) > 3:
            try:
                app.config['config']['is_debug'] = (sys.argv[-1] == 'debug')
            except:
                app.config['config']['is_debug'] = False
        app.config['config']['use_celery'] = True
        for tmp in sys.argv:
            if tmp == 'no_celery':
                app.config['config']['use_celery'] = False
                break
        #logger.debug('use_celery : %s', app.config['config']['use_celery'])
        logger.debug('======================================')
    elif action == 'auth':
        from system.logic_auth import SystemLogicAuth
        # 2021-08-11 로딩시 인증 실행 여부 
        #SystemLogicAuth.do_auth()
        
        tmp = SystemLogicAuth.get_auth_status()
        app.config['config']['auth_status'] = tmp['ret']
        app.config['config']['auth_desc'] = tmp['desc']
        app.config['config']['level'] = tmp['level']
        app.config['config']['point'] = tmp['point']
        #app.config['config']['auth_status'] = True
    
    elif action == 'system_loading_after':
        from . import SystemModelSetting
        try: app.config['config']['is_server'] = (SystemModelSetting.get('ddns') == app.config['DEFINE']['MAIN_SERVER_URL'])
        except: app.config['config']['is_server'] = False
        
        if app.config['config']['is_server'] or app.config['config']['is_debug']:
            app.config['config']['server'] = True
            app.config['config']['is_admin'] = True
        else:
            app.config['config']['server'] = False
            app.config['config']['is_admin'] = False
        app.config['config']['running_type'] = 'native'
        if 'SJVA_RUNNING_TYPE' in os.environ:
            app.config['config']['running_type'] = os.environ['SJVA_RUNNING_TYPE']
        else:
            import platform
            if platform.system() == 'Windows':
                app.config['config']['running_type'] = 'windows'


def init_define():
    from . import logger, app
    app.config['DEFINE'] = {}
    # 이건 필요 없음
    app.config['DEFINE']['MAIN_SERVER_URL'] = 'https://server.sjva.me'

    app.config['DEFINE']['METADATA_SERVER_URL'] = 'https://meta.sjva.me'
    
    app.config['DEFINE']['WEB_DIRECT_URL'] = 'https://sjva.me'


    app.config['DEFINE']['RSS_SUBTITLE_UPLOAD_WEBHOOK'] = 'https://discordapp.com/api/webhooks/689800985887113329/GBTUBpP9L0dOegqL4sH-u1fwpssPKq0gBOGPb50JQjim22gUqskYCtj-wnup6BsY3vvc'

    from support.base.discord import webhook_list
    app.config['DEFINE']['WEBHOOK_LIST_FOR_IMAGE_PROXY'] = webhook_list
    
    #2020-05-27 23번방부터 32번방 삭제
    #2020-08-31 29, 30, 31번 삭제
    app.config['DEFINE']['SJVA_BOT_CHANNEL_CHAT_ID'] = [       
        '-1001424350090',
        '-1001290967798', '-1001428878939', '-1001478260118', '-1001276582768', '-1001287732044', 
        '-1001185127926', '-1001236433271', '-1001241700529', '-1001231080344', '-1001176084443', 
        '-1001338380585', '-1001107581425', '-1001374760690', '-1001195790611', '-1001239823262', 
        '-1001300536937', '-1001417416651', '-1001411726438', '-1001312832402', '-1001473554220',
        '-1001214198736', '-1001366983815', '-1001336003806', '-1001229313654', '-1001403657137', 
        #'-1001368328507', '-1001197617982', #'-1001480443355', '-1001479557293', ,  
        #'-1001322329802', # 31번방 - 중복봇
        #'-1001256559181', # 32번방 - 대답안하는것들
        '-1001202840141']

    # 방송하는 봇
    app.config['DEFINE']['SUPER_BOT_TOKEN'] = 'gyGqcYaMYfKNqutj6uETk2WHdjt3EiltpvCs9aC45upbx/UV1lTfmeH2a9nIDRin/ogO106xDJvpYjhmuDeW3Q=='

    # 참석방 찾아주는 봇
    app.config['DEFINE']['ADMIN_BOT_TOKEN'] = 'AemiErWy5XT2Q08WAH78qpP0B0NHPGSRiwyANuruFaxGTnTavdtN2QP6ZqV0LUV6Sb0TouMZcyHXAqa5HUFr/w=='
