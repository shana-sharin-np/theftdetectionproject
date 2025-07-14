import json

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from myapp.models import *
from django.contrib import auth
import datetime
# Create your views here.


import cv2
face_cascade = cv2.CascadeClassifier(r'C:\Users\shana\Desktop\theft detection\Theft_Detection\myapp\haarcascade_frontalface_default.xml')


def logout(request):
    auth.logout(request)
    return render(request,'index.html')


def login(request):
    return render(request,'index.html')


def loginpost(request):
    uname=request.POST["textfield"]
    password=request.POST["textfield2"]
    ob=login_table.objects.filter(username=uname,password=password)
    if ob.exists():
        p=login_table.objects.get(username=uname,password=password)
        request.session['lid'] = p.id

        if p.type=='admin':
            ob1 = auth.authenticate(username="admin", password="admin")
            if p is not None:
                auth.login(request, ob1)
            request.session['lid'] = p.id
            return HttpResponse('''<script>alert('logined');window.location='/home'</script>''')
    else:
        return HttpResponse('''<script>alert('invalid username or password');window.location='/'</script>''')


def home(request):
    return render(request, 'admin/index.html')




@login_required(login_url='/')
def complaint(request):
    a = Complaint.objects.all()
    return render(request,'admin/complaint.html',{'data':a})


@login_required(login_url='/')
def feedback(request):
    a =Feedback.objects.all()
    return render(request,'admin/feedback.html',{'data':a})



@login_required(login_url='/')
def reply_send_get(request,id):
    request.session['rid']=id
    a=Complaint.objects.get(id=id)
    return render(request,'admin/reply.html')




@login_required(login_url='/')
def reply_send(request):
    reply=request.POST['textarea']
    ob=Complaint.objects.get(id=request.session["rid"])
    ob.replay=reply
    ob.save()
    return HttpResponse('''<script>alert('sended');window.location='/complaint'</script>''')


@login_required(login_url='/')
def users(request):
    a=user_table.objects.all()
    return render(request,'admin/users.html',{'data':a})


@login_required(login_url='/')
def block_users(request,id):
    ob=login_table.objects.get(id=id)
    ob.type='blocked'
    ob.save()
    return HttpResponse('''<script>alert('blocked');window.location='/users'</script>''')

@login_required(login_url='/')
def unblock_users(request,id):
    ob=login_table.objects.get(id=id)
    ob.type='user'
    ob.save()
    return HttpResponse('''<script>alert('unblocked');window.location='/users'</script>''')


@login_required(login_url='/')
def viewtheft(request):
    a = theftinfo_table.objects.all()
    return render(request,'admin/viewtheft.html',{'data':a})


@login_required(login_url='/')
def cyberbullying(request):
    a = Comment.objects.filter (type="bullying")
    return render(request, 'admin/cyberbullying.html',{'data':a})

def block_user(request):
    if request.method == "POST":
        lid = request.POST.get('lid')
        try:
            a = login_table.objects.get(id=lid)
            a.type = 'block'
            a.save()
            return JsonResponse({"status": "ok"})
        except login_table.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def unblock_user(request):
    if request.method == "POST":
        lid = request.POST.get('lid')
        try:
            a =login_table.objects.get(id=lid)
            a.type = 'user'  # Assuming 'active' is the default type for unblocked users
            a.save()
            return JsonResponse({"status": "ok"})
        except login_table.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




##############android#######################



def and_login(request):
    username=request.POST['username']
    password=request.POST['password']
    a=login_table.objects.filter(username=username,password=password)
    if a.exists():
        b = login_table.objects.get(username=username, password=password)
        if b.type=='user':
            return JsonResponse({"task":"valid","lid":b.id,'type':'user'})
        if b.type=='blocked':
            return JsonResponse({"task":"valid","lid":b.id,'type':'blocked'})
        else:
            return JsonResponse({"task":"invalid"})
    else:
        return JsonResponse({"task": "invalid"})

from .recognize_face import rec_face_image
from .encode_faces import enf
def and_user_reg(request):
    print(request.POST, "uuuki")
    name = request.POST['name']
    address = request.POST['address']
    email = request.POST['email']
    phone = request.POST['phone']
    # pin = request.POST['pin']
    image = request.FILES['image']
    password = request.POST['password']
    username = request.POST['username']

    fs = FileSystemStorage()
    fp = fs.save(image.name, image)
    image_name = image.name
    res=rec_face_image(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/"+image_name)
    if len(res)>0:
        fp = image_name
        theft_login = login_table(username=username, password=password, type='theft')
        theft_login.save()
        theft_user = user_table(
            uname=name,
            place=address,
            phone=phone,
            # pin=pin,
            email=email,
            image=fp,
            LOGIN=theft_login
        )
        theft_user.save()

        # Save theft alert with existing users
        matched_user = user_table.objects.get(id=res[0])

        # Create theft alert
        a = theft_alert_table()
        if matched_user:
            a.USER_id = matched_user.id  # The known user the image belongs to
        a.Theft_user_id = theft_user.id
        a.status = "pending"
        a.date = str(datetime.now())
        a.save()

        return JsonResponse({'status': 'error', 'message': 'Image already exists! Registered as theft.'})
    else:
        if login_table.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists!'})

        lob1 = login_table(username=username, password=password, type='user')
        lob1.save()

        # Save user info
        lob = user_table(
            uname=name,
            place=address,
            phone=phone,
            # pin=pin,
            email=email,
            image=fp,
            LOGIN=lob1
        )
        lob.save()

        enf([[lob.id,r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/"+image_name]])

        print("User saved:", lob)
        return JsonResponse({"status": "ok"})

#
# def and_user_reg(request):
#     print(request.POST, "uuuki")
#     name = request.POST['name']
#     address = request.POST['address']
#     email = request.POST['email']
#     phone = request.POST['phone']
#     pin = request.POST['pin']
#     image = request.FILES['image']
#
#     fs = FileSystemStorage()
#     image_name = image.name
#
#     if fs.exists(image_name):
#
#         return JsonResponse({'status': 'error', 'message': 'Image already exists!'})
#
#     # Save image
#     fp = fs.save(image_name, image)
#
#     password = request.POST['password']
#     username = request.POST['username']
#
#     # Check if username already exists
#     if login_table.objects.filter(username=username).exists():
#         return JsonResponse({'status': 'error', 'message': 'Username already exists!'})
#
#     # Save login info
#     lob1 = login_table()
#     lob1.username = username
#     lob1.password = password
#     lob1.type = 'user'
#     lob1.save()
#
#     # Save user info
#     lob = user_table()
#     lob.uname = name
#     lob.place = address
#     lob.phone = phone
#     lob.pin = pin
#     lob.email = email
#     lob.image = fp  # saved filename
#     lob.LOGIN = lob1
#     lob.save()
#
#     print("User saved:", lob)
#     return JsonResponse({"status": "ok"})




def view_profile(request):
    lid = request.POST['lid']
    ob = user_table.objects.filter(LOGIN__id=lid)
    result = []

    for i in ob:
        row = {
            "id": i.id,
            "name": i.uname,
            "phone": str(i.phone) if i.phone else "",  # Ensure phone is a string, or empty string if null
            "photo": request.build_absolute_uri(i.image.url[1:]),  # Check if photo exists, otherwise return an empty string
            "place": i.place if i.place else "",  # Check if place exists, otherwise return an empty string
            # "pin": i.pin if i.pin else "",  # Check if place exists, otherwise return an empty string
            "email": i.email if i.email else ""  # Check if email exists, otherwise return an empty string
        }
        result.append(row)
    print(result)

    return JsonResponse({"task": "ok", "data": result})


def viewprofile(request):
    lid=request.POST['lid']
    ob=user_table.objects.get(LOGIN_id=lid)
    return JsonResponse({"status":"ok","name":ob.uname,"image":ob.image.url,"place":ob.place,
                         # "pin":ob.pin,
                         "phone":ob.phone,"email":ob.email})



def update_profile(request):
    lid = request.POST['lid']
    name = request.POST['name']
    address = request.POST['place']
    email = request.POST['email']
    phone = request.POST['phone']
    lob = user_table.objects.get(LOGIN_id=lid)

    if 'photo' in request.FILES:
        image = request.FILES['photo']
        fs = FileSystemStorage()
        fp = fs.save(image.name, image)
        lob.image = fp
        lob.save()

    lob.uname = name
    lob.place = address
    lob.phone = phone
    lob.email = email
    lob.save()
    print("uuuuuuuuu", lob)
    return JsonResponse({'task': 'ok'})



def updateprofile(request):
    print(request.POST)
    lid=request.POST['lid']

    uname=request.POST['uname']
    place=request.POST['place']
    # pin=request.POST['pin']
    phone=request.POST['phone']
    email=request.POST['email']
    image= request.POST['file']
    fs=FileSystemStorage()
    fsave=fs.save(image.name,image)
    ob=user_table.objects.get(LOGIN__id=lid)
    ob.uname=uname
    ob.place=place
    # ob.pin=pin
    ob.phone=phone
    ob.email=email
    ob.image=fsave
    ob.save()

    return JsonResponse({"status":"profile updated successfully"})


def viewfriendrequest(request):
    lid=request.POST['lid']
    ob=Request.objects.filter(TO__LOGIN_id=lid)
    print(ob,"HHHHHHHHHHHHHHH")
    mdata=[]
    for i in ob:
        data={'name':i.FROM.uname,'uname':i.FROM.image.url,'id':i.id}
        mdata.append(data)
        print(mdata)
    return JsonResponse({"status":"ok","data":mdata})

def viewfriends(request):
    lid=request.POST['lid']
    ob=Request.objects.filter(TO__LOGIN_id=lid,status='accepted')
    print(ob,"HHHHHHHHHHHHHHH")
    mdata=[]
    for i in ob:
        data={'name':i.FROM.uname,'uname':i.FROM.image.url,'id':i.id}
        mdata.append(data)
        print(mdata)
    return JsonResponse({"status":"ok","data":mdata})


def acceptfriendrequest(request):
    req=request.POST['reqid']
    ob=Request.objects.get(id=req)
    ob.status="accepted"
    ob.save()
    return JsonResponse({'task': 'ok'})

def rejectfriendrequest(request):
    req = request.POST['reqid']
    ob = Request.objects.get(id=req)
    ob.status = "rejected"
    ob.save()
    return JsonResponse({'task': 'ok'})



def sendcomplaint(request):
    comp = request.POST['complaint']
    lid = request.POST['lid']
    lob = Complaint()
    lob.USER = user_table.objects.get(LOGIN__id=lid)
    lob.complaint = comp
    lob.complaintdate = datetime.datetime.now()
    lob.date = datetime.datetime.now()
    lob.reply='pending'
    lob.save()
    return JsonResponse({'task': 'ok'})



def viewcomplaintreply(request):
    ob=Complaint.objects.all()
    print(ob,"HHHHHHHHHHHHHHH")
    mdata=[]
    for i in ob:
        data={'reply':i.reply,'date':str(i.date),'complaint':i.complaint,'id':i.id}
        mdata.append(data)
        print(mdata)
    return JsonResponse({"status":"ok","data":mdata})




def sendfriendrequest(request):
    uid=request.POST['uid']
    lid=request.POST['lid']
    ob=Request()
    ob.FROM=user_table.objects.get(LOGIN_id=lid)
    ob.TO=user_table.objects.get(id=uid)
    ob.status="request"
    ob.date=datetime.datetime.today().now()
    ob.save()
    return JsonResponse({'task': 'ok'})

def cancelfriendrequest(request):
    req = request.POST['reqid']
    ob = Request.objects.get(id=req)
    ob.status = "canceled"
    ob.save()
    return JsonResponse({'task': 'ok'})

def viewotherspost(request):
    lid=request.POST['lid']
    ob=post_table.objects.get(LOGIN_id=lid)

    return JsonResponse({"status":"ok","user":ob.USER.uname,"image":ob.url,"description":ob.description,"date":ob.date,"location":ob.location})



def addpost(request):
    lid = request.POST['lid']
    image = request.FILES['file']
    dt=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+".jpg"

    fs = FileSystemStorage()
    fsave = fs.save(image.name, image)


    description=request.POST['description']
    location=request.POST['location']



    ob=post_table()
    ob.USER= user_table.objects.get(LOGIN_id=lid)
    ob.image =fsave
    ob.description=description
    ob.date = datetime.datetime.today().now()
    ob.location=location
    ob.save()
    return JsonResponse({'task': 'ok'})



def viewpost(request):
    lid=request.POST['lid']
    ob=post_table.objects.get(LOGIN_id=lid)
    return JsonResponse({"status":"ok","user":ob.USER.uname,"image":ob.url,"description":ob.description,"date":ob.date,"location":ob.location})


def commentotherpost(request):
    lid = request.POST['lid']
    uid = request.POST['uid']
    comment=request.POST['add_comment']
    type=request.POST['type']
    ob = Comment()
    ob.USER = user_table.objects.get(LOGIN_id=lid)
    ob.POST = post_table.objects.get(id=uid)
    ob.comment=comment
    ob.type=type
    ob.save()
    return JsonResponse({'task': 'ok'})


def likeotherspost(request):
    lid = request.POST['lid']
    uid = request.POST['uid']
    ob=Like()
    ob.USER = user_table.objects.get(LOGIN_id=lid)
    ob.POST = post_table.objects.get(id=uid)
    ob.save()
    return JsonResponse({'task': 'ok'})


from django.http import JsonResponse


def viewcomment(request):
    pid = request.POST['pid']
    print(request.POST)

    # Get comments that are not bullying for the given post ID
    ob = Comment.objects.filter(POSTID_id=pid, type='Not bullying')
    mdata = []

    for i in ob:
        data = {
            'comment': i.comment,
            'username': i.USERNAME.uname,
            'date': i.date,
            'photo':request.build_absolute_uri(i.USERNAME.image.url),
            # 'photo': i.USERNAME.image.url,  # Get the image URL if it exists
            'id': i.id
        }
        mdata.append(data)
        print('kkkkkkkkkkkk')

    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


# def viewcomment(request):
#     pid=request.POST['pid']
#     print(request.POST)
#     ob=Comment.objects.filter(POSTID_id=pid,type='Not bullying')
#     mdata=[]
#     for i in ob:
#         data={'comment':i.comment,
#               'date':i.date,
#               'username':i.USERNAME.uname,
#               'photo':i.USERNAME.image,
#               'id':i.id
#               }
#         mdata.append(data)
#         # print(mdata)
#         print('kkkkkkkkkkkk')
#     print(mdata)
#     return JsonResponse({"status":"ok","data":mdata})
def viewlike(request):
    lid = request.POST['lid']
    ob = Like.objects.get(LOGIN_id=lid)
    return JsonResponse({"status": "ok", "user": ob.USER.uname, "post": ob.POST.image.url})

def delete_post(request):
    pid=request.POST['post_id']
    ob=post_table.objects.get(id=pid)
    ob.delete()
    return JsonResponse({"task": "ok"})



def send_post(request):
    lid = request.POST['lid']
    image = request.POST['lid']
    fp=FileSystemStorage()
    fs=fp.save(image.name,image)

    a=post_table()
    a.image=fs
    a.date=datetime.datetime.today()
    a.USERNAME =user_table.objects.get(LOGIN_id=lid)
    a.save()


    uob=user_table.objects.get(LOGIN_id=lid)
    # ++++++++++++++++++++++++++++++++++++++




    oimg = cv2.imread(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/"+fp)
    cv2.imwrite(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media\original1/"+fp,oimg)
    print(oimg)
    print(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/"+fp,"++++++++++++++++++")
    gray_img = cv2.cvtColor(oimg, cv2.COLOR_BGR2GRAY)
    print(gray_img)
    faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)
    print(faces,"faces_rect")
    for (x, y, w, h) in faces:
        print("=================",x,y,w,h)
        print("=================",x,y,w,h)
        print("=================",x,y,w,h)

        cimg=oimg[y:y + h, x:x + w]
        from myapp.recognize_face import rec_face_image1
        res=rec_face_image1(cimg)
        if len(res)>0:



            if int(res[0])!=int(uob.id):
                blurImg = cv2.blur(cimg, (100, 100))
                oimg[y:y + h, x:x + w]=blurImg
                # cv2.rectangle(oimg, (x, y), (x + w, y + h), (0, 255, 0), thickness=-1)
                obn=Post_Alert()
                obn.USERNAME=user_table.objects.get(id=res[0])
                obn.date=datetime.today()
                obn.status="pending"
                obn.POSTID=a
                obn.save()
    cv2.imwrite(r"D:\identityOG\identity_theft\identity_theft\media/"+fp,oimg)






    return JsonResponse({"task":"ok"})



# old code

# def add_post(request):
#     lid=request.POST['lid']
#     image=request.FILES['file']
#     description = request.POST['description'] # safely getting description
#     location = request.POST['location']
#     fs=FileSystemStorage()
#     fp=fs.save(image.name,image)
#     uob=user_table.objects.get(LOGIN_id=lid)
#
#     ob=post_table()
#     ob.description=description
#     ob.location=location
#     ob.USER=user_table.objects.get(LOGIN_id=lid)
#     ob.image=fp
#     ob.image1=fp
#     ob.date=datetime.today().now()
#     ob.save()
#
#
#
#
#
#     import cv2
#     oimg = cv2.imread(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/" + fp)
#
#     cv2.imwrite(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media\post/" + str(ob.id)+".png", oimg)
#
#
#
#     gray_img = cv2.cvtColor(oimg, cv2.COLOR_BGR2GRAY)
#     print(gray_img)
#     faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)
#     print(faces, "faces_rect")
#     fn = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
#     print(fn)
#
#     for (x, y, w, h) in faces:
#         print("=================", x, y, w, h)
#         print("=================", x, y, w, h)
#         print("=================", x, y, w, h)
#
#         cimg = oimg[y:y + h, x:x + w]
#
#         from myapp.recognize_face import rec_face_image1
#         res = rec_face_image1(cimg)
#         if len(res) > 0:
#
#             if int(res[0]) != int(uob.id):
#
#                 for ii in res:
#                     try:
#                         if int(ii) != int(uob.id):
#
#                             obn = Post_Alert()
#                             obn.USERNAME = user_table.objects.get(id=ii)
#                             obn.date = datetime.today()
#                             obn.status = "pending"
#                             obn.POSTID = ob
#                             obn.save()
#                             print("detected")
#                             print(y, y + h, x, x + w)
#                             # ksize =  min(w, h)
#                             blurImg = cv2.medianBlur(cimg, 251)
#
#                             # # Blend overlay with original image
#                             # cv2.addWeighted(cimg, alpha, img, 1 - alpha, 0, img)
#                             oimg[y:y + h, x:x + w] = blurImg
#
#                     except Exception as e:
#
#                         print("erroooo")
#
#                         print(e,"=================")
#
#     cv2.imwrite(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/" + fp,oimg)
#
#
#     return JsonResponse({"task": "ok"})



# newode

def add_post(request):
    lid = request.POST['lid']
    image = request.FILES['file']
    description = request.POST['description']
    location = request.POST['location']
    fs = FileSystemStorage()
    fp = fs.save(image.name, image)
    uob = user_table.objects.get(LOGIN_id=lid)

    ob = post_table()
    ob.description = description
    ob.location = location
    ob.USER = user_table.objects.get(LOGIN_id=lid)
    ob.image = fp
    ob.image1 = fp
    ob.date = datetime.today().date()  # Use .date() to match DateField
    ob.save()

    import cv2
    oimg = cv2.imread(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/" + fp)
    cv2.imwrite(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media\post/" + str(ob.id) + ".png", oimg)

    gray_img = cv2.cvtColor(oimg, cv2.COLOR_BGR2GRAY)
    print(gray_img)
    faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)
    print(faces, "faces_rect")
    fn = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
    print(fn)

    for (x, y, w, h) in faces:
        print("=================", x, y, w, h)
        cimg = oimg[y:y + h, x:x + w]

        from myapp.recognize_face import rec_face_image1
        res = rec_face_image1(cimg)
        if len(res) > 0:
            if int(res[0]) != int(uob.id):
                for ii in res:
                    try:
                        if int(ii) != int(uob.id):
                            # Insert into Post_Alert
                            obn = Post_Alert()
                            obn.USERNAME = user_table.objects.get(id=ii)
                            obn.date = datetime.today().date()  # Use .date() to match DateField
                            obn.status = "pending"
                            obn.POSTID = ob
                            obn.save()
                            print("detected")
                            print(y, y + h, x, x + w)

                            # Insert into theft_alert_table
                            theft_alert = theft_alert_table()
                            theft_alert.USER = user_table.objects.get(LOGIN_id=lid)  # The user who posted
                            theft_alert.Theft_user = user_table.objects.get(id=ii)  # The detected user
                            theft_alert.status = "theft detected"
                            theft_alert.date = datetime.today().strftime("%Y-%m-%d")  # String format for CharField
                            theft_alert.save()

                            # Blur the detected face
                            blurImg = cv2.medianBlur(cimg, 251)
                            oimg[y:y + h, x:x + w] = blurImg

                            # Insert into theftinfo_table
                            bb = theftinfo_table()
                            bb.POST = ob
                            bb.USER = user_table.objects.get(LOGIN_id=lid)
                            bb.status = 'theft detect'
                            bb.save()

                    except Exception as e:
                        print("erroooo")
                        print(e, "=================")

    cv2.imwrite(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/" + fp, oimg)

    return JsonResponse({"task": "ok"})



def post_alert_action(request):
    id=request.POST["pid"]
    ob=Post_Alert.objects.get(id=id)
    ob.status="accepted"
    ob.save()

    pob=ob.POSTID
    uob=pob.USER

    oimg = cv2.imread(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media\post/" + str(pob.id)+".png")
    # print(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media\original1/" + str(pob.image))
    print(oimg)
    gray_img = cv2.cvtColor(oimg, cv2.COLOR_BGR2GRAY)
    print(gray_img)
    faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)
    print(faces, "faces_rect")


    for (x, y, w, h) in faces:
        print("=================", x, y, w, h)
        print("=================", x, y, w, h)
        print("=================", x, y, w, h)

        cimg = oimg[y:y + h, x:x + w]

        from myapp.recognize_face import rec_face_image1
        res = rec_face_image1(cimg)
        if len(res) > 0:

            if int(res[0]) != int(uob.id):
                obn = Post_Alert.objects.filter(USERNAME__id=res[0],POSTID__id=pob.id,status='accepted')

                if len(obn)==0:
                    print("detected")
                    print(y, y + h, x, x + w)
                    # ksize =  min(w, h)
                    blurImg = cv2.medianBlur(cimg, 501)

                    # # Blend overlay with original image
                    # cv2.addWeighted(cimg, alpha, img, 1 - alpha, 0, img)
                    oimg[y:y + h, x:x + w] = blurImg
                    cv2.imwrite("xx.png", oimg)

                    # try:
                    #
                    #     obn = Post_Alert()
                    #     obn.USERNAME = user_table.objects.get(id=res[0])
                    #     obn.date = datetime.today()
                    #     obn.status = "pending"
                    #     obn.POSTID = ob
                    #     obn.save()
                    # except Exception as e:
                    #
                    #     print("erroooo")

                        # print(e, "=================")
    fn=datetime.now().strftime("%Y%m%d%H%M%S")+".png"
    cv2.imwrite(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\media/" + str(fn), oimg)
    ob = Post_Alert.objects.get(id=id)
    ob.status = "accepted"

    ob.save()
    obp=ob.POSTID
    obp.image = fn
    obp.save()
    print(fn,"fn============")
    return JsonResponse({"task": "ok"})
def viewREQUEST(request):
    lid = request.POST['lid']
    ob = Request.objects.filter(toid_id=lid)
    mdata = []

    for i in ob:
        try:
            # Assuming i.fromid is a login/user object
            uu = user_table.objects.get(LOGIN=i.fromid)
            data = {
                'toid': i.fromid.username,
                'photo': request.build_absolute_uri(uu.image.url),
            # 'image': uu.image.url[1:] if uu.image else "",  # safely get image URL

                'status': i.status,
                'date': i.date,
                'id': i.id,
                'lid': str(i.fromid.id)
            }
            mdata.append(data)
            print(mdata,'mmmmmmmmmmmmmmmmmmmmmmmmm')
        except user_table.DoesNotExist:
            print(f"user_table does not exist for LOGIN: {i.fromid}")
            continue  # skip this record if user_table entry is missing

    return JsonResponse({"status": "ok", "data": mdata})

# def viewREQUEST(request):
#     lid=request.POST['lid']
#     ob=Request.objects.filter(toid_id=lid)
#     mdata=[]
#     for i in ob:
#
#         uu=user_table.objects.get(LOGIN=i.id).image
#         data={'toid':i.fromid.username,
#
#               'photo':uu.image,
#               'status':i.status,'date':i.date,'id':i.id,'lid':str(i.fromid.id)}
#         mdata.append(data)
#         print(mdata)
#     return JsonResponse({"status":"ok","data":mdata})


def accept_friendrequest(request):
    rid = request.POST['id']
    obf= Request.objects.get(id=rid)
    obf.status="accepted"
    obf.save()
    return JsonResponse({"task":"ok"})



def reject_friendrequest(request):
    rid = request.POST['id']
    obf = Request.objects.get(id=rid)
    obf.status = "rejected"
    obf.save()
    return JsonResponse({"task": "ok"})

def viewotheruser(request):
    lid = request.POST['lid']
    user_login = login_table.objects.get(id=lid)
    ob = user_table.objects.exclude(LOGIN_id=lid)
    mdata = []

    for i in ob:
        # Check for friend request in either direction
        from django.db.models import Q
        request_entry = Request.objects.filter(
            Q(fromid=user_login, toid=i.LOGIN) | Q(fromid=i.LOGIN, toid=user_login)
        ).first()
        status = "none"
        request_id = ""

        if request_entry:
            request_id = str(request_entry.id)
            if request_entry.status == "accepted":
                status = "accepted"
            elif request_entry.status == "rejected":
                status = "none"
            else:  # Pending request
                status = "pending"

        data = {
            'id': str(i.id),
            'lid': str(i.LOGIN.id),
            'name': i.uname,
            'phone': str(i.phone),
            'email': i.email,
            # 'gender': i.pin,
            'address': i.place,
            'image': str(i.image.url[1:]) if i.image else '',
            'request_status': status,
            'request_id': request_id
        }
        mdata.append(data)
        print(status,'status========')

    return JsonResponse({"status": "ok", "data": mdata})



# def send_friendrequest(request):
#     try:
#         lid = request.POST['lid']
#         toid = request.POST['id']
#         print("From:", lid)
#         print("To:", toid)
#
#         # If you're directly using login IDs from Flutter
#         to_login_id = toid
#
#         existing_request = Request.objects.filter(
#             Q(fromid_id=lid, toid_id=to_login_id) |
#             Q(fromid_id=to_login_id, toid_id=lid)
#         ).exclude(status='rejected').first()
#
#         if existing_request:
#             if existing_request.status == 'pending':
#                 return JsonResponse({"task": "exists", "message": "Friend request already pending"})
#             elif existing_request.status == 'accepted':
#                 return JsonResponse({"task": "exists", "message": "You are already friends"})
#         else:
#             obf = Request()
#             obf.fromid_id = lid
#             obf.toid_id = to_login_id
#             obf.date = datetime.today().now()
#             obf.status = "pending"
#             obf.save()
#             return JsonResponse({
#                 "task": "ok",
#                 "message": "Friend request sent",
#                 "request_id": str(obf.id)
#             })
#     except Exception as e:
#         return JsonResponse({"task": "not ok", "message": str(e)})
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime

def send_friendrequest(request):
    if request.method != "POST":
        return JsonResponse({"task": "not ok", "message": "Only POST method allowed"})

    try:
        lid = int(request.POST['lid'])
        toid = int(request.POST['id'])

        if lid == toid:
            return JsonResponse({"task": "not ok", "message": "Cannot send friend request to yourself"})

        existing_request = Request.objects.filter(
            Q(fromid_id=lid, toid_id=toid) |
            Q(fromid_id=toid, toid_id=lid)
        ).exclude(status='rejected').first()

        if existing_request:
            if existing_request.status == 'pending':
                return JsonResponse({"task": "exists", "message": "Friend request already pending"})
            elif existing_request.status == 'accepted':
                return JsonResponse({"task": "accepted", "message": "You are already friends"})
        else:
            obf = Request(
                fromid_id=lid,
                toid_id=toid,
                status="pending",
                date=datetime.now().today()
            )
            obf.save()
            return JsonResponse({
                "task": "ok",
                "message": "Friend request sent",
                "request_id": str(obf.id)
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"task": "not ok", "message": str(e)})


# def send_friendrequest(request):
#     try:
#         lid = request.POST['lid']
#         toid = request.POST['id']
#
#         # Check if a request already exists (either pending or accepted)
#         from django.db.models import Q
#         existing_request = Request.objects.filter(
#             Q(fromid_id=lid, toid_id=user_table.objects.get(id=toid).LOGIN.id) |
#             Q(fromid_id=user_table.objects.get(id=toid).LOGIN.id, toid_id=lid)
#         ).exclude(status='rejected').first()
#
#         if existing_request:
#             if existing_request.status == 'pending':
#                 return JsonResponse({"task": "exists", "message": "Friend request already pending"})
#             elif existing_request.status == 'accepted':
#                 return JsonResponse({"task": "exists", "message": "You are already friends"})
#         else:
#             obf = Request()
#             obf.fromid_id = lid
#             obf.toid_id = user_table.objects.get(id=toid).LOGIN.id
#             obf.date = datetime.datetime.today().now()
#             obf.status = "pending"
#             obf.save()
#             return JsonResponse({
#                 "task": "ok",
#                 "message": "Friend request sent",
#                 "request_id": str(obf.id)  # Add the request ID to the response
#             })
#     except Exception as e:
#         return JsonResponse({"task": "not ok", "message": str(e)})



def view_acceptedfriendlist(request):
    lid = request.POST['lid']
    print(request.POST)
    from django.db.models import Q
    obu = Request.objects.filter(toid_id=lid, status='accepted')
    obu1 = Request.objects.filter(fromid_id=lid, status='accepted')
    mdata = []
    for i in obu:
        uu = user_table.objects.get(LOGIN=i.fromid.id)
        l=i.fromid.id
        print(l,'login=====')
        print(uu,'userssss=====')
        data = {
            'toid': i.fromid.username,
            'uid': uu.id,
            'status': i.status,
            'date': str(i.date),
            'name': uu.uname,
            'image': uu.image.url[1:] if uu.image else "",  # safely get image URL
            'id': str(i.id),
            'LOGIN': str(l)
        }
        mdata.append(data)
    for i in obu1:
        uu = user_table.objects.get(LOGIN=i.toid.id)
        l=i.toid.id
        print(l,'login=====')
        print(uu,'userssss=====')
        data = {
            'toid': i.toid.username,
            'status': i.status,
            'date': str(i.date),
            'name': uu.uname,
            'image': uu.image.url[1:] if uu.image else "",  # safely get image URL
            'id': str(i.id),
            'LOGIN': str(l)
        }
        mdata.append(data)
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


# def view_acceptedfriendlist2(request):
#     lid = request.POST['lid']
#     print(request.POST)
#     from django.db.models import Q
#     obu = Request.objects.filter(Q(fromid_id=lid) | Q(toid_id=lid), status='accepted')
#     mdata = []
#     for i in obu:
#         uu = user_table.objects.get(LOGIN=i.fromid.id)
#         data = {
#             'toid': i.fromid.username,
#             'status': i.status,
#             'date': str(i.date),
#             'name': uu.uname,
#             'image': uu.image.url[1:] if uu.image else "",  # safely get image URL
#             'id': str(i.id),
#             'LOGIN': str(i.fromid.id)
#         }
#         mdata.append(data)
#         print(mdata)
#     return JsonResponse({"status": "ok", "data": mdata})







from django.http import JsonResponse
from django.db.models import Q

def view_acceptedfriend(request):
    lid = request.POST['lid']
    print(request.POST)

    obu = Request.objects.filter(Q(fromid_id=lid) | Q(toid_id=lid), status='accepted')

    mdata = []
    for i in obu:
        data = {
            'toid': i.fromid.username,
            'status': i.status,
            'date': str(i.date),
            'id': str(i.id),
            'LOGIN': str(i.fromid.id)
        }
        mdata.append(data)

    followers_count = Request.objects.filter(toid_id=lid, status='accepted').count()
    following_count = Request.objects.filter(fromid_id=lid, status='accepted').count()

    print(f"Followers: {followers_count}, Following: {following_count}")
    return JsonResponse({
        "status": "ok",
        "data": mdata,
        "followers": followers_count,
        "following": following_count
    })








def user_viewchat(request):
    fromid = request.POST["from_id"]
    toid = request.POST["to_id"]
    from django.db.models import Q
    res = Chat.objects.filter(Q(fromid_id=fromid, toid_id=toid) | Q(fromid_id=toid, toid_id=fromid)).order_by('id')
    l = []

    for i in res:
        l.append({"id": i.id, "msg": i.message, "from": i.fromid_id, "date": i.date, "to": i.toid_id})

    return JsonResponse({"status":"ok",'data':l})



def user_sendchat(request):
    fromid=request.POST['from_id']
    toid=request.POST['to_id']
    print(fromid)
    print(toid)
    msg=request.POST['message']

    from  datetime import datetime
    c=Chat()
    c.fromid_id=fromid
    c.toid_id=toid
    c.message=msg
    c.date=datetime.now()
    c.save()
    return JsonResponse({'status':"ok"})



#
#
# def view_my_post(request):
#     lid = request.POST['lid']  # Get the logged-in user ID (lid)
#     ob = post_table.objects.filter(USER__LOGIN_id=lid)
#     result = []
#     for i in ob:
#
#         row = {
#             "id": str(i.id),
#             "date": str(i.date),
#             "description": str(i.description),
#             "location": str(i.location),
#             'post': str(i.image.url),
#         }
#         result.append(row)
#     print(result)
#
#     return JsonResponse({"task": "ok", "data": result})


from django.http import JsonResponse
from .models import post_table

def view_my_post(request):
    lid = request.POST['lid']  # Get the logged-in user ID
    ob = post_table.objects.filter(USER__LOGIN_id=lid)
    result = []

    for i in ob:
        row = {
            "id": str(i.id),
            "date": str(i.date),
            "description": str(i.description),
            "location": str(i.location),
            "post": str(i.image.url),
        }
        result.append(row)

    post_count = ob.count()  # ✅ Get number of posts

    return JsonResponse({
        "task": "ok",
        "data": result,
        "post_count": post_count  # ✅ Include post count in response
    })


import  datetime
def sendfeedback(request):
    feedback = request.POST['feedback']
    rating = request.POST['rating']
    lid = request.POST['lid']
    lob = Feedback()
    lob.USERNAME =user_table.objects.get(LOGIN_id=lid)
    lob.feedback = feedback
    lob.rating = rating
    lob.date = datetime.today().now()
    lob.save()
    return JsonResponse({'task': 'ok'})

def sendcompalint(request):
    print(request.POST)
    comp = request.POST['com']
    lid = request.POST['lid']
    lob = Complaint()
    lob.USERNAME = user_table.objects.get(LOGIN_id=lid)
    lob.complaint = comp
    lob.replay = 'pending'
    lob.date = datetime.today().now()
    lob.save()
    return JsonResponse({'task': 'ok'})


def viewreply(request):
    lid=request.POST['lid']
    ob=Complaint.objects.filter(USERNAME__LOGIN_id=lid).order_by('-id')
    mdata=[]
    for i in ob:
        data={'complaint':i.complaint,'date':i.date,'reply':i.replay,'id':i.id}
        mdata.append(data)
        print(mdata)
    return JsonResponse({"status":"ok","data":mdata})

def delete_post(request):
    pid=request.POST['post_id']
    ob=post_table.objects.get(id=pid)
    ob.delete()
    return JsonResponse({"task": "ok"})


def view_likes(request):
    pid=request.POST['pid']
    print(request.POST)
    ob=Like.objects.filter(POSTID_id=pid)
    mdata=[]
    for i in ob:
        data={'date':i.date,'USER':i.USER.uname,
              'photo': i.USER.image.url[1:] if i.USER.image else "",  # safely get image URL
}
        mdata.append(data)
        print('kkkkkkkkkkkk')
    print(mdata)
    return JsonResponse({"status":"ok","data":mdata})

#
# def view_others_post(request):
#     lid = request.POST.get('lid')
#     print(request.POST)
#
#     if not lid:
#         return JsonResponse({"task": "error", "message": "Missing user ID"})
#
#     from django.db.models import Count
#     users = post_table.objects.exclude(USER__LOGIN_id=lid) \
#         .annotate(like_count=Count('like')) \
#         .order_by('-id')
#     result = []
#     for user in users:
#         row = {
#             "id": str(user.id),
#             "name": user.USER.uname,
#             "lid": user.USER.LOGIN.id,
#             "image": request.build_absolute_uri(user.image.url),
#             "description":user.description,
#             "location":user.location,
#             "likes": user.like_count,  # Pass the count of likes
#         }
#         result.append(row)
#     print(result)
#     return JsonResponse({"task": "ok", "data": result})




from django.http import JsonResponse
from django.db.models import Q, Count
from .models import post_table, Request, login_table

def view_others_post(request):
    lid = request.POST.get('lid')
    print(request.POST)

    if not lid:
        return JsonResponse({"task": "error", "message": "Missing user ID"})

    # Step 1: Find all accepted friendships for the given login ID
    accepted_friends = Request.objects.filter(
        Q(fromid__id=lid) | Q(toid__id=lid),
        status='accepted'
    )

    # Step 2: Extract the friend's LOGIN IDs
    friend_ids = set()
    for req in accepted_friends:
        if str(req.fromid.id) != lid:
            friend_ids.add(req.fromid.id)
        if str(req.toid.id) != lid:
            friend_ids.add(req.toid.id)

    # Step 3: Query posts made by these friends
    users = post_table.objects.filter(USER__LOGIN_id__in=friend_ids) \
        .annotate(like_count=Count('like')) \
        .order_by('-id')

    result = []
    for user in users:
        row = {
            "id": str(user.id),
            "name": user.USER.uname,
            "lid": user.USER.LOGIN.id,
            "image": request.build_absolute_uri(user.image.url),
            "description": user.description,
            "location": user.location,
            "likes": user.like_count,
        }
        result.append(row)

    print(result)
    return JsonResponse({"task": "ok", "data": result})

def add_like(request):
    pid = request.POST['pid']
    lid = request.POST['lid']
    likes = request.POST.get('likes', '1')  # Default to '1' if not provided

    # try:
    if True:
        user = user_table.objects.get(LOGIN_id=lid)
        post = post_table.objects.get(id=pid)

        # Check if the user already liked the post
        existing_like = Like.objects.filter(USER=user, POSTID=post).first()

        if existing_like:
            # If like exists, remove it (unlike)
            existing_like.delete()
            liked = False
        else:
            # If no like exists, add it (like)
            ob = Like()
            ob.USER = user
            ob.POSTID = post
            ob.likes = '1'  # Always set to '1' for a new like
            ob.date = datetime.today()  # Use timezone.now() instead of datetime.now()
            ob.save()
            liked = True

        # Calculate total likes for the post
        likes_count = Like.objects.filter(POSTID=post).count()

        return JsonResponse({
            "task": "ok",
            "liked": liked,  # True if liked, False if unliked
            "likes_count": likes_count
        })

    # except user_table.DoesNotExist:
    #     return JsonResponse({"task": "error", "message": "User not found"}, status=400)
    # except post_table.DoesNotExist:
    #     return JsonResponse({"task": "error", "message": "Post not found"}, status=400)
    # except Exception as e:
    #     return JsonResponse({"task": "error", "message": str(e)}, status=500)


# def add_comment(request):
#     from datetime import datetime
#     lid = request.POST['lid']
#     post_id = request.POST['pid']
#     comment = request.POST['comment']
#     post = post_table.objects.get(id=post_id)
#     user = user_table.objects.get(LOGIN=lid)
#     date = datetime.now().strftime("%Y-%m-%d")
#     #
#     from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
#     import pickle
#
#     msg = comment
#     msg = [msg]
#
#     print("Message=================")
#     print("Message=================")
#
#     # List of stopwords
#     my_file = open(
#         r"C:\Users\shana\Desktop\theft detection\Theft_Detection\static\stopwords2.txt",
#         "r")
#     content = my_file.read()
#     content_list = content.split("\n")
#     my_file.close()
#
#     tfidf_vector = TfidfVectorizer(stop_words=content_list, lowercase=True, vocabulary=pickle.load(
#         open(
#             r"C:\Users\shana\Desktop\theft detection\Theft_Detection\static\tfidf_vector_vocabulary2.pkl",
#             # r"C:\Users\USER\Desktop\THEFT ALERT\Theft_Detection\Theft_Detection\static\tfidf_vector_vocabulary.pkl",
#             "rb")))
#     data = tfidf_vector.fit_transform(msg)
#     print(data)
#     model = pickle.load(open(
#         # r"C:\Users\USER\Desktop\THEFT ALERT\Theft_Detection\Theft_Detection\static\LinearSVC.pkl",
#         r"C:\Users\shana\Desktop\theft detection\Theft_Detection\static\LinearSVC2.pkl",
#         'rb'))
#
#     pred = model.predict(data)
#     response = str(pred[0])
#     print(response)
#     response="0"
#     if str(response) == '0':
#         ob = Comment()
#         ob.USERNAME = user
#         ob.date = datetime.today()
#         ob.POSTID = post
#         ob.comment = comment
#         ob.type = "Not bullying"
#         ob.save()
#         return JsonResponse({"task": "ok"})
#     else:
#
#         ob = Comment()
#         ob.USERNAME = user
#         ob.date = datetime.today()
#         ob.POSTID = post
#         ob.comment = comment
#         ob.type = "bullying"
#         ob.save()
#
#         return JsonResponse({"status": "na"})
#
#     return JsonResponse({'status': 'ok'})


# import datetime
# def add_comment(request):
#     lid = request.POST['lid']
#     pid = request.POST['pid']
#
#     comments = request.POST['comment']
#     date = datetime.datetime.now().strftime("%Y-%m-%d")
#
#     from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
#     import pickle
#
#     msg = comments
#     msg = [msg]
#
#     # List of stopwords
#     my_file = open(
#         r"C:\\Users\\shana\\Desktop\\theft detection\\Theft_Detection\\static\\stopwords2.txt",
#         "r")
#     content = my_file.read()
#     content_list = content.split("\n")
#     my_file.close()
#
#     tfidf_vector = TfidfVectorizer(stop_words=content_list, lowercase=True, vocabulary=pickle.load(
#         open(
#             r"C:\\Users\\shana\\Desktop\\theft detection\\Theft_Detection\\static\\tfidf_vector_vocabulary2.pkl",
#             "rb")))
#     data = tfidf_vector.fit_transform(msg)
#     print(data)
#     model = pickle.load(open(
#         r"C:\\Users\\shana\\Desktop\\theft detection\\Theft_Detection\\static\\LinearSVC2.pkl",
#         'rb'))
#     pred = model.predict(data)
#     response = str(pred[0])
#     print(response)
#     if str(response) == '0':
#         obj = Comment()
#
#         obj.comment = comments
#         obj.date = date
#         obj.status = 'Not bullying'
#         obj.USERNAME = user_table.objects.get(LOGIN_id=lid)
#         obj.POSTID_id = pid
#         obj.save()
#         return JsonResponse({"status": "ok"})
#     else:
#         obj = Comment()
#         obj.comment = comments
#         obj.status = 'bullying'
#         obj.date = date
#         obj.USERNAME = user_table.objects.get(LOGIN_id=lid)
#         obj.POSTID_id = pid
#         obj.save()
#
#         # objj = bullying()
#         # objj.COMMENT_id = obj.id
#         # objj.save()
#         #
#         # u = User.objects.filter(LOGIN=lid)
#         # c = u[0].bullyingcount
#         # c = int(c) + 1
#         # u.update(bullyingcount=c)
#         return JsonResponse({"status": "ok"})
#



from django.http import JsonResponse
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from .models import Comment, post_table, user_table  # adjust import as per your models.py


def add_comment(request):
    if request.method == 'POST':
        try:
            lid = request.POST['lid']
            post_id = request.POST['pid']
            comment = request.POST['comment']

            post = post_table.objects.get(id=post_id)
            user = user_table.objects.get(LOGIN=lid)

            # Load stopwords from file
            with open(r"C:\Users\shana\Desktop\theft detection\Theft_Detection\static\stopwords2.txt", "r") as f:
                stopwords_list = f.read().split("\n")

            # Load vocabulary and TF-IDF vectorizer
            vocabulary_path = r"C:\Users\shana\Desktop\theft detection\Theft_Detection\static\tfidf_vector_vocabulary2.pkl"
            with open(vocabulary_path, "rb") as vocab_file:
                vocabulary = pickle.load(vocab_file)

            tfidf_vector = TfidfVectorizer(stop_words=stopwords_list, lowercase=True, vocabulary=vocabulary)
            tfidf_data = tfidf_vector.fit_transform([comment])

            # Load the trained model
            model_path = r"C:\Users\shana\Desktop\theft detection\Theft_Detection\static\LinearSVC2.pkl"
            with open(model_path, 'rb') as model_file:
                model = pickle.load(model_file)

            prediction = model.predict(tfidf_data)
            response = str(prediction[0])
            print("Prediction:", response)

            # Save comment based on prediction
            ob = Comment()
            ob.USERNAME = user
            ob.date = datetime.today()
            ob.POSTID = post
            ob.comment = comment

            if response == '0':
                ob.type = "Not bullying"
                ob.save()
                return JsonResponse({"task": "ok"})
            else:
                ob.type = "bullying"
                ob.save()
                return JsonResponse({"status": "na", "message": "Inappropriate comment detected"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({'status': 'invalid request'})


def remove_friend(request):
    try:
        fid = request.POST['fid']
        ob = Request.objects.get(id=fid)
        if ob.status == "accepted":
            ob.delete()
            return JsonResponse({'status': 'ok', 'message': 'Friend removed successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Not an accepted friend request'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



def userchangepass(request):
    current_password = request.POST['old']
    new_password = request.POST['new']
    confirm_password = request.POST['confirm']

    ob = login_table.objects.filter(password=current_password)
    if ob.exists():
        if new_password == confirm_password:
            ob1 = login_table.objects.filter(password=current_password).update(password=new_password)
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'not ok'})
    else:
        return JsonResponse({'status': 'not ok'})


def view_post_alert(request):
    pid = request.POST['lid']
    print(request.POST)
    ob = Post_Alert.objects.filter(USERNAME__LOGIN=pid, status="pending")
    mdata = []
    for i in ob:
        row = {
            "id": str(i.id),
            "date": str(i.date),
            'post': "/media/post/" + str(i.POSTID.id)+".png",
            'user': str(i.POSTID.USER.uname),
            'status': str(i.status),
            # Add liked_by_user status
        }
        mdata.append(row)

    print(mdata)
    return JsonResponse({"task": "ok", "data": mdata})


def rejectPostAlert(request):
    id = request.POST["id"]
    ob = Post_Alert.objects.get(id=id)
    ob.status = "rejected"
    ob.save()
    return JsonResponse({"task": "ok"})

def userviewtheft(request):
    pid=request.POST['lid']
    print(request.POST)
    ob=theft_alert_table.objects.filter(USER__LOGIN__id=pid,status='pending')
    mdata=[]
    for i in ob:
        data={'id':str(i.id),'name':i.Theft_user.uname,'img':i.Theft_user.image.url,'phno':str(i.Theft_user.phone),'address':i.Theft_user.place,}
        mdata.append(data)
        # print(mdata)
        print('kkkkkkkkkkkk')
    print(mdata)
    return JsonResponse({"status":"ok","data":mdata})

def theft_alert_action(request):
    id=request.POST["pid"]
    ob=theft_alert_table.objects.get(id=id)
    ob.status='accepted'
    ob.save()

    uob=ob.Theft_user
    lob=uob.LOGIN
    lob.type='user'
    lob.save()

    return JsonResponse({"task": "ok"})

def theft_alert_reject(request):
    id=request.POST["pid"]
    ob=theft_alert_table.objects.get(id=id)
    ob.status='accepted'
    ob.save()

    uob=ob.Theft_user
    lob=uob.LOGIN

    lob.delete()

    return JsonResponse({"task": "ok"})

def delete_friendrequest(request):
    fid=request.POST['fid']
    ob=Request.objects.get(id=fid)
    ob.delete()
    return JsonResponse({'status':'ok'})




# def eachuserpost(request):
#     uid=request.POST['LOGIN']
#     ob=post_table.objects.filter(USER__LOGIN_id=uid)
#     mdata = []
#     for i in ob:
#         data = {'id': str(i.id),
#                 'image':i.image.url,
#                  'description': i.description,
#                 }
#         mdata.append(data)
#         # print(mdata)
#         print('kkkkkkkkkkkk')
#     print(mdata)
#     return JsonResponse({"status": "ok", "data": mdata})


# def viewotheruserprofile(request):
#     userid = request.POST['userid']
#     try:
#         user = user_table.objects.get(LOGIN_id=userid)
#         data = {
#             "status": "ok",
#             "name": user.uname,
#             "bio": user.place,
#             "photo": user.image.url if user.image else "",
#             "id": str(user.LOGIN_id)
#         }
#     except user_table.DoesNotExist:
#         data = {"status": "not found"}
#     return JsonResponse(data)











def viewotheruserprofile(request):
    userid = request.POST.get('userid')
    try:
        user = user_table.objects.get(LOGIN_id=userid)
        data = {
            "status": "ok",
            "name": user.uname,
            "bio": user.place,
            "photo": user.image.url if user.image else "",
            "id": str(user.LOGIN_id)
        }
    except user_table.DoesNotExist:
        data = {"status": "not found"}
    return JsonResponse(data)

def eachuserpost(request):
    uid = request.POST.get('LOGIN')
    posts = post_table.objects.filter(USER__LOGIN_id=uid)
    mdata = [
        {
            'id': str(post.id),
            'image': post.image.url,
            'description': post.description
        }
        for post in posts
    ]
    return JsonResponse({"status": "ok", "data": mdata})

def otheruserview_acceptedfriend(request):
    userid = request.POST.get('userid')
    accepted = Request.objects.filter(Q(fromid_id=userid) | Q(toid_id=userid), status='accepted')

    mdata = [{

        'toid': i.fromid.username,
        'status': i.status,
        'date': str(i.date),
        'id': str(i.id),
        'LOGIN': str(i.fromid.id)
    } for i in accepted]

    followers_count = Request.objects.filter(toid_id=userid, status='accepted').count()
    following_count = Request.objects.filter(fromid_id=userid, status='accepted').count()

    return JsonResponse({
        "status": "ok",
        "data": mdata,
        "followers": followers_count,
        "following": following_count
    })


def view_followerslist(request):
    try:
        lid = request.POST['lid']
        print(f"Received lid: {lid}")  # Debugging line
        followers_qs = Request.objects.filter(toid_id=lid, status='accepted')

        data = []
        for req in followers_qs:
            try:
                user = user_table.objects.get(LOGIN=req.fromid.id)
                data.append({
                    'uid': user.id,
                    'rid': req.id,  # ✅ Use 'rid' instead of 'id'
                    'username': req.fromid.username,
                    'name': user.uname,
                    'image': user.image.url[1:] if user.image else "",
                    'date': str(req.date),
                    'status': req.status,
                    'login_id': str(req.fromid.id),
                })
            except user_table.DoesNotExist:
                continue

        return JsonResponse({'status': 'ok', 'data': data})
    except Exception as e:
        print(f"Error occurred: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def view_followinglist(request):
    lid = request.POST['lid']
    following_qs = Request.objects.filter(fromid_id=lid, status='accepted')
    data = []

    for req in following_qs:
        try:
            user = user_table.objects.get(LOGIN=req.toid.id)
            data.append({
                'uid': user.id,
                'username': req.toid.username,
                'name': user.uname,
                'image': user.image.url[1:] if user.image else "",
                'date': str(req.date),
                'status': req.status,
                'login_id': str(req.toid.id),
            })
        except user_table.DoesNotExist:
            continue

    return JsonResponse({'status': 'ok', 'data': data})


from django.http import JsonResponse
from .models import Request

def remove_followers_user(request):
    rid = request.POST.get('rid')

    if not rid:
        return JsonResponse({'status': 'error', 'message': 'Missing rid'})

    try:
        req_obj = Request.objects.get(id=rid)
        req_obj.delete()
        return JsonResponse({'status': 'ok'})
    except Request.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': f'Request with id {rid} does not exist'})
