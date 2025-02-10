from django.shortcuts import render, get_object_or_404

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.utils.safestring import mark_safe
from django.middleware.csrf import get_token

from .models import Content, AppUser, Collect, Comment, Message

from util.retcode import RETCODE
from util.dateformat import dateformat, timenow

import requests, re

from test_dj import settings

# Create your views here.

DEBUG = settings.CODESHARE_DEBUG


 
def token(request):
    token=get_token(request)
    return JsonResponse({'token':token})

# /codesharex/get-openid?code=xxx
def get_openid(request):
    code = request.GET.get('code')
    openid = get_openid_(code)
    if openid:
        return JsonResponse({'code': 200, 'msg': 'ok', 'openid': openid})
    else:
        return JsonResponse({'code': 400, 'msg': 'wrong code!'})
        

def get_openid_(code):
    # appi与secret,可以将其存入数据库中获取
    appid = 'wx56ad1f38634fab4c'
    secret = 'a1d614a9618a449945e4127bf395486f'
    grant_type = 'authorization_code'
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}' \
            f'&secret={secret}&js_code={code}&grant_type={grant_type}'
    try:
        res = requests.get(url).json()
        openid = res['openid']
        
    except:
        print("openid 请求失败")
        return None
    
    return openid


# /codesharex/get-user?openid=xxx
def get_user(request):
    openid = request.GET.get('openid')
    
    if openid is not None:
        try:
            obj = AppUser.objects.get(openid=openid)
        except AppUser.DoesNotExist:
            return JsonResponse({
                'code': 400, 
                'msg': '获取用户信息失败，openid=' + openid
            })
            
        
        return JsonResponse({
            'code': 200, 
            'msg':'ok', 
            'nickName': obj.nick_name,
            'avatarURL':obj.avatar.url if obj.avatar else settings.BLANK_AVATAR
        })
    return JsonResponse({
        'code': 400, 
        'msg': '获取用户信息失败，openid=' + openid
    })


def create_user(request):
    if request.method != 'POST': 
        return HttpResponseBadRequest()
    
    code = request.POST.get('code')
    openid = get_openid_(code)
    print(request.POST)
    if not openid or not re.match(r'^[_A-Za-z0-9\-]{20,40}$', openid):
        return HttpResponseBadRequest()
    
    obj = AppUser(openid=openid, nick_name=f"微信用户{openid[-5:]}")
    obj.save()

    return JsonResponse({
        'code': 200, 
        'msg':'ok', 
        'openid': openid,
        'nickName': obj.nick_name,
        'avatarURL':obj.avatar.url if obj.avatar else settings.BLANK_AVATAR
    })

# /codesharex/update-user?openid=xxx&nickName=xxx
def update_user(request):
    openid = request.POST.get('openid')
    nick_name = mark_safe(request.POST.get('nickName'))

    if (all([openid, nick_name])):
        try:
            obj = AppUser.objects.get(openid=openid)
            obj.nick_name = nick_name
            obj.save()
        except AppUser.DoesNotExist:
            return JsonResponse({'code': 400, 'msg': f'获取用户信息失败，openid={openid}'})
        return JsonResponse({'code': 200, 'msg':'ok'})
    return JsonResponse({'code': 400, 'msg': '获取用户信息失败，openid={openid}'})


def upload_avatar(request):
    avatar = request.FILES.get('file')
    openid = request.POST.get('openid')
    try:
        # 将图片保存在media文件夹中
        user = AppUser.objects.get(openid=openid)
        user.avatar = avatar
        user.save()
        return HttpResponse(
            user.avatar.url
        )
    except AppUser.DoesNotExist:
        JsonResponse({'code': 400, 'msg': '获取用户信息失败，openid=' + openid})
    



# /codesharex/get-content?id=x
def get_content(request):
    id = int(request.GET.get('id'))

    if id is None or id <= 0:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    
    try:
        obj =  Content.objects.get(pk=id) # get_object_or_404(Content, id=id)
        return JsonResponse({
            'code': RETCODE.OK.code,
            'msg': 'ok',
            'content': obj.content,
            
            'lang': obj.lang,
            'posterInfo': {
                'nickName': obj.poster.nick_name,
                'openid': obj.poster.openid,
                'avatarUrl': obj.poster.avatar.url if obj.poster.avatar else settings.BLANK_AVATAR,
                'short': obj.short,
                'postTime': dateformat(obj.post_time),
                'destTime': "无" if obj.never_destory else dateformat(obj.destory_time)
            },
            'neverDestory': obj.never_destory,
            'destoryTime': obj.destory_time,
            'postTime': obj.post_time,
            'password': obj.password
        }, safe=False)
    
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    

def update_content(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    openid = request.POST.get('openid')
    contentid = request.POST.get('contentid')
    content = request.POST.get('content')
    short = request.POST.get('short')

    try:
        cont = Content.objects.get(pk=int(contentid))
        if cont.poster.openid == openid:
            cont.content = content
            cont.short = short
            cont.save()
            return JsonResponse({
                'code': 200, 
                'msg': 'ok'
            })
        else:
            return JsonResponse({
                'code': 401,
                'msg': '不允许的操作'
            })
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })


def delete_content(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    
    openid = request.POST.get('openid')
    contentid = request.POST.get('contentid')

    try:
        content = Content.objects.get(pk=int(contentid))

        if content.poster.openid == openid:
            content.delete()
            return JsonResponse({
                'code': 200, 
                'msg': 'ok'
            })
        else:
            return JsonResponse({
                'code': 401,
                'msg': '不允许的操作'
            })
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })


# /codesharex/get-share?openid=xxx
def get_share(request):
    openid = request.GET.get('openid')

    try:
        app_user = AppUser.objects.get(openid=openid)
        contents = Content.objects.filter(poster=app_user)

        share_list = []
        for s in contents:
            share_list.append(s.pk)

        return JsonResponse({
            'code': 200, 
            'msg':'ok', 
            'list': share_list
        })

    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })


# /codesharex/add-content?id=x
def add_content(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    
    content = request.POST.get('content')
    short = request.POST.get('short')
    openid = request.POST.get('openid')
    lang = request.POST.get('lang')
    never_destory = request.POST.get('neverDestory')
    destory_time = request.POST.get('destoryTime')
    post_time = request.POST.get('postTime')
    password = request.POST.get('password')

    if (all([content, short, openid, lang, never_destory,
             destory_time, post_time])):
        
        never_destory = False if int(never_destory) == 0 else True
        destory_time = int(destory_time)
        post_time = int(post_time)
        
        poster = AppUser.objects.get(openid=openid)

        obj = Content(content=content,
                    short=short,
                    lang=lang,
                    never_destory=never_destory,
                    destory_time=destory_time,
                    post_time=post_time,
                    password=password,
                    poster=poster
                    )
        obj.save()
        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'contentid': obj.pk
        })
    return JsonResponse({
        'code': 400,
        'msg': '请求参数错误'
    })


# /codesharex/get_collect?openid=xx
def get_collect(request):
    openid = request.GET.get('openid')
    try:
        app_user = AppUser.objects.filter(openid=openid)
        collects = Collect.objects.filter(app_user__in=app_user)

        collect_list = []
        for col in collects:
            collect_list.append(col.content.pk)

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'list': collect_list
        })
    except:
        return JsonResponse({
        'code': 400,
        'msg': '请求参数错误'
    })


# /codesharex/set_collect?openid=xxx&contentid=xx&collect=0/1
def set_collect(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    
    openid = request.POST.get('openid')
    contentid = request.POST.get('contentid')
    collect = request.POST.get('collect')
    
    try:
        contentid = int(contentid)
        collect = int(collect)
        app_user = AppUser.objects.get(openid=openid)
        content = Content.objects.get(pk=contentid)
        
        if collect:
            col = Collect(app_user=app_user, content=content)
            col.save()

            # 如果不是自己的，则发送消息
            if openid != content.poster.openid or DEBUG:
                

                msg = Message(sender_openid=openid,
                              sender_name=app_user.nick_name,
                              app_user=content.poster, 
                              belongs=content,
                              content="收藏了你的代码", 
                              time=timenow())
                msg.save()
        else:
            
            col = Collect.objects.get(app_user=app_user, content=content)
            col.delete()
            

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
        })
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    

def add_comment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    
    openid = request.POST.get('openid')
    belongsid = request.POST.get('belongs')
    cnt = request.POST.get('content')
    time = request.POST.get('time')
    to = None

    if cnt:
        import re
        match = re.match("^&gt;&gt;(\d{6})\:((.)*)$", cnt)
        if match:
            to = int(match.group(1))
            cnt=match.group(2)

    try:
        app_user = AppUser.objects.get(openid=openid)
        belongs = Content.objects.get(pk=int(belongsid))

        if all([cnt, time]):
            com = Comment(app_user=app_user, to=to, belongs=belongs, comment=cnt, time=time)
            com.save()

            s = f"评论了你"
            reply_to = belongs.poster
            if to:
                s = "回复了你的评论"
                reply_to = Comment.objects.get(pk=to).app_user

            
            # 如果评论者不是本人则发送消息
            if openid != belongs.poster.openid or DEBUG:
                
                msg = Message(sender_openid=openid,
                              sender_name=app_user.nick_name,
                                app_user=reply_to,
                                belongs=belongs,
                                content=s, 
                                to_comment=com.pk,
                                time=int(time))
                msg.save()

            return JsonResponse({
                'code': 200,
                'msg': 'ok',
            })
        
        else:
            return JsonResponse({
                'code': 400,
                'msg': '请求参数错误'
            })

        
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    

def get_comment(request):
    belongsid = request.GET.get('belongs')

    try:
        comments = Comment.objects.filter(belongs=int(belongsid)).order_by('time').reverse()

        com_list = []
        for c in comments:
            piece = {
                'id': c.pk,
                'avatar': c.app_user.avatar.url if c.app_user.avatar else settings.BLANK_AVATAR,
                'nickName': c.app_user.nick_name,
                'time': dateformat(c.time),
                'comment': c.comment,
                'to': c.to
            }
            com_list.append(piece)

        return JsonResponse({
            'code': 200,
            'msg': 'ok',
            'list': com_list
        })
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    

def get_message(request):
    openid = request.GET.get('openid')
    
    message_list = []
    messages = []

    try:
        app_user = AppUser.objects.get(openid=openid)
        messages = Message.objects.filter(app_user=app_user).order_by('pk').reverse()
    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    
    for m in messages:
        piece = {
            'id': m.pk,
            'sender_openid': m.sender_openid,
            'sender_name': m.sender_name,
            'to': m.to_comment,
            'belongsid': m.belongs.pk,
            'content': m.content,
            'to_comment': m.to_comment,
            'time': dateformat(m.time),
            'is_read': m.is_read
        }
        message_list.append(piece)
    return JsonResponse({
        'code': 200,
        'msg': 'ok',
        'list': message_list
    })


def delete_message(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    
    openid = request.POST.get('openid')
    msgid = request.POST.get('msgid')

    try:
        app_user = AppUser.objects.get(openid=openid)
        messages = Message.objects.get(pk=msgid)

    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    
    if app_user.openid != messages.app_user.openid:
        return JsonResponse({
            'code': 401,
            'msg': '不允许的操作'
        })
    
    messages.delete()

    return JsonResponse({
        'code': 200,
        'msg': 'ok'
    })


def read_message(request):
    openid = request.GET.get('openid')
    msgid = request.GET.get('msgid')

    try:
        app_user = AppUser.objects.get(openid=openid)
        messages = Message.objects.get(pk=msgid)

    except:
        return JsonResponse({
            'code': 400,
            'msg': '请求参数错误'
        })
    
    if app_user.openid != messages.app_user.openid:
        return JsonResponse({
            'code': 401,
            'msg': '不允许的操作'
        })
    
    messages.is_read = True
    messages.save()

    return JsonResponse({
        'code': 200,
        'msg': 'ok'
    })