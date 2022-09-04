from textwrap import TextWrapper
import requests
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageFilter
from random import randint
import io

def prem_overlay(js):
    r = requests.get(js["avatar"])
    avatar = Image.open(io.BytesIO(r.content)).resize((500, 500))

    r = requests.get(js["overlay"])
    overlay = Image.open(io.BytesIO(r.content)).resize((500, 500))

    avatar.paste(overlay,(0, 0), overlay)
    
    a = randint(0, 50)
    avatar.save(f"./trash/{a}.png")
    return a

def prem_balance(js):
    r = requests.get(js["avatar"])
    avatar = Image.open(io.BytesIO(r.content)).resize((280, 280))

    r = requests.get(js["background"])
    background = Image.open(io.BytesIO(r.content)).resize((1024,538))
    truebackground = Image.open("./assets/backcurve.png").resize((1024,538))
    background = background.filter(ImageFilter.GaussianBlur(10))

    total = 300
    a = Image.new("RGBA", (301, 301))
    draw = ImageDraw.Draw(a)
    draw.ellipse((0, 0 , total, total), fill=(255, 255, 255))
    a.paste(avatar, (10,10), Image.open("./assets/mask_circle.jpg").convert("L").resize((280, 280)))
    background.paste(a, (50, 20), a)

    r = requests.get(js["background"])

    aaa = 140
    ajaja = 50
    r = requests.get(js["balanceimage"])
    coinIcon = Image.open(io.BytesIO(r.content)).resize((100, 100))
    background.paste(coinIcon, (380+125-ajaja, 51), coinIcon)
    
    r = requests.get(js["bankimage"])
    coinIcon = Image.open(io.BytesIO(r.content)).resize((100, 100))
    background.paste(coinIcon, (380+125-ajaja, 70+aaa), coinIcon)
    
    r = requests.get(js["totalimage"])
    coinIcon = Image.open(io.BytesIO(r.content)).resize((100, 100))
    background.paste(coinIcon, (380+125-ajaja, 231+aaa), coinIcon)

    draw = ImageDraw.Draw(background)
    fontstyle = ImageFont.truetype("./assets/VarelaRound-Regular.ttf", 45)
    draw.text((50, 350), "username", font=fontstyle, fill="white")
    draw.text((500+125-ajaja, 50), str(js["balancetext"]), font=fontstyle, fill="white")
    draw.text((500+125-ajaja, 70+aaa), str(js["banktext"]), font=fontstyle, fill="white")
    draw.text((500+125-ajaja, 225+aaa), str(js["totaltext"]), font=fontstyle, fill="white")

    fontstyle = ImageFont.truetype("./assets/VarelaRound-Regular.ttf", 60)
    draw.text((50, 390), js["username"], font=fontstyle, fill="white")
    draw.text((500+125-ajaja, 90), str(js["balance"]), font=fontstyle, fill="white")
    draw.text((500+125-ajaja, 110+aaa), str(js["bank"]), font=fontstyle, fill="white")
    draw.text((500+125-ajaja, 265+aaa), str(js["total"]), font=fontstyle, fill="white")

    bg = Image.new("RGBA", (1024,538))
    bg.paste(background, (0,0), truebackground.convert("L"))
    a = randint(0,50)
    bg.save(f"./trash/{a}.png")
    return a

def welcomer(a):
    background,avatar,username,message, text = a.values()
    r = requests.get(avatar)
    avatar = Image.open(io.BytesIO(r.content)).resize((150,150))
    del r
    r = requests.get(background)
    background = Image.open(io.BytesIO(r.content))
    background = background.resize((720,327))
    W, H = background.size

    myFont = ImageFont.truetype("./assets/VarelaRound-Regular.ttf",40)
    xmas = 270
    draw = ImageDraw.Draw(background)
    draw.ellipse((xmas, 0 , 440, 168), fill=(255, 255, 255), outline=(255,255,255))
    msg = username

    w,h = draw.textsize(msg, font=myFont)
    draw.text(((W-w)/2,(327/2)+15), msg,font=myFont, fill="white",stroke_width=2,stroke_fill=(0,0,0))

    msg = message

    myFont = ImageFont.truetype("./assets/VarelaRound-Regular.ttf",40)
    w,h = draw.textsize(msg, font=myFont)
    draw.text(((W-w)/2,(327/2)+55), msg,font=myFont, fill="white",stroke_width=2,stroke_fill=(0,0,0))

    myFont = ImageFont.truetype("./assets/VarelaRound-Regular.ttf",25)
    w,h = draw.textsize(text, font=myFont)
    draw.text(((W-w)/2,(327/2)+110), text,font=myFont, fill="white",stroke_width=2,stroke_fill=(0,0,0))

    mask_im = Image.open("./assets/mask_circle.jpg").convert('L').resize((150,150))
    background.paste(avatar, (280, 10), mask_im)
    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    del background,avatar,mask_im,myFont,draw,r
    return a

def rip_maker(avatar):
    r = requests.get(avatar,stream=True)
    avatar = Image.open(io.BytesIO(r.content)).resize((521//2,620//2))
    
    mask_im = Image.open("./assets/rip.png").convert('L').resize((521//2,620//2))
    background = Image.open("./assets/rip.png").resize((521//2,620//2))
    background.paste(avatar, (0, 0), mask_im)
    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    return a

def spongebobWAP(url):
    x = 140
    tuptup = (x,x)
    a = requests.get(url)

    avatar = Image.open(io.BytesIO(a.content)).resize(tuptup)
    background = Image.open("./assets/wap.jpg")
    mask = Image.open("./assets/wap_mask.png").convert("L").resize(tuptup)
    
    background.paste(avatar, (253, 10),mask)
    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    return a

def throwthechild(url):
    a = requests.get(url)

    avatar = Image.open(io.BytesIO(a.content)).resize((120,120))
    background = Image.open("./assets/throw.png")
    mask = Image.open("./assets/mask_circle.jpg").convert("L").resize((120,120))
    av1 = avatar.rotate(-150)
    background.paste(avatar, (50, 90),mask)
    background.paste(avatar, (600, 110),mask)
    background.paste(av1, (350, 590),mask)

    background.paste(av1.resize((45,45)), (912, 930),mask.resize((45,45)))

    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    return a

def burning(url):
    y=53
    x = 300
    a = requests.get(url)
    avatar = Image.open(io.BytesIO(a.content)).resize((x,x))
    background = Image.open("./assets/burn.png")
    mask = Image.open("./assets/burn_mask.png").convert("L").resize((x,x))
    mask2 = Image.open("./assets/burn_mask2.png").convert("L").resize((y,y))
    croped_avatar = avatar.crop((40,200,120,300)).resize((y,y)).rotate(45)

    background.paste(avatar, (12, 78),mask)
    background.paste(croped_avatar.transpose(Image.FLIP_LEFT_RIGHT), (99, 735),mask2.transpose(Image.FLIP_LEFT_RIGHT))

    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    return a

def tear(a):
    avatar1,avatar2 = a.values()
    y=140
    x = 186
    x1 = x +1
    
    aaa = 160
    b = (198,893)

    a = requests.get(avatar1)
    avatar = Image.open(io.BytesIO(a.content)).resize((x,x))
    avatar6 = Image.open(io.BytesIO(a.content)).resize((aaa,aaa))

    a = requests.get(avatar2)
    avatar1 = Image.open(io.BytesIO(a.content)).resize((x,x))

    a = (145,706)
    background = Image.open("./assets/spongetear.png")
    mask = Image.open("./assets/tear1.png").resize((x,x)).convert("L")
    mask2 = Image.open("./assets/tear2.png").resize((y,y)).convert("L")
    mask3 = Image.open("./assets/tear3.png").resize((y,y))
    mask4 = Image.open("./assets/tear4.png").resize((aaa,aaa)).convert("L")
    background.paste(avatar,(119,166),mask)
    background.paste(avatar1.resize((x1,x1)),((119,705)),mask.resize((x1,x1)))

    background.paste(avatar6.rotate(45),b,mask4)


    background.paste(avatar.resize((y,y)),a,mask2.resize((y,y)))
    background.paste(mask3.resize((y,y)),a,mask3.convert("L"))

    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    return a

def discordsays(a):
    avatar,username,message,color,time = a.values()
    r = requests.get(avatar)
    background = Image.open("./assets/discordsay.png")
    myFont = ImageFont.truetype("./assets/whitneymedium.otf",22)
    draw = ImageDraw.Draw(background)
    a = TextWrapper(width=45)
    aa = ""
    msg  = message
    for x in a.wrap(msg):
        aa+= x + "\n"

    draw.text((85,45),aa,"#c3c4c6",myFont)

    myFont = ImageFont.truetype("./assets/whitneymedium.otf",25)
    draw.text((85,14),username,fill=color,font=myFont)
    w , h = draw.textsize(username,myFont)
    myFont = ImageFont.truetype("./assets/whitneymedium.otf",18)
    draw.text((95+w,20),time,"#63676d",myFont)

    a = 54
    aaa = (a,a)

    mask_circle = Image.open("./assets/mask_circle.jpg").convert("L").resize(aaa)
    avatar = Image.open(io.BytesIO(r.content)).resize(aaa)

    background.paste(avatar,(10,17),mask_circle)

    a = randint(0,50)
    background.save(f"./trash/{a}.png", "PNG")
    return a

def trigger_maker(a):
    avatar, intensity = a.values()
    r = requests.get(avatar)
    images = []
    avatar = Image.open(io.BytesIO(r.content)).resize((500,500))
    banner = Image.open("./assets/triggered.jpg")
    avatar.paste(banner,(0,325))
    images.append(avatar.copy())

    a = intensity

    for x in range(3):
        images.append(ImageChops.offset(avatar, a, a))
        a = -1 * a


    a = randint(0,50)
    images[0].save(f"./trash/{a}.gif", save_all=True, append_images=images[1:], optimized=False, duration=40, loop=False)
    return a

def lover_me(a):
    avatar1, avatar2, percentage = a.values()
    love = percentage or randint(10,101)

    r = requests.get(avatar1)
    avatar1 = Image.open(io.BytesIO(r.content)).resize((175,175))
    r = requests.get(avatar2)
    avatar2 = Image.open(io.BytesIO(r.content)).resize((175,175))
    heart = Image.open("./assets/heart.png").resize((100,100))


    if love >= 100:
        background = Image.open("./assets/maxbackground.png")
    else:
        background = Image.open("./assets/background.png")
    background.paste(avatar1,(50,35))
    background.paste(heart,(255,80), heart)
    background.paste(avatar2,(385,35))

    love_percentage = int((love/100) * 510)

    draw = ImageDraw.Draw(background)
    myFont = ImageFont.truetype("./assets/VarelaRound-Regular.ttf",30)
    if love >=  100:
        draw.text((265,108),f"{love}%","white",myFont)
    else:
        draw.text((276,108),f"{love}%","white",myFont)
        
    if love > 100:
        im = Image.new("RGB", (5100, 51), (255, 255, 255))
        draw = ImageDraw.Draw(im, "RGBA")
        draw.rounded_rectangle((0, 0, 510, 50), 30, fill="#ffaec8")
        draw.rounded_rectangle((0, 0, love_percentage, 50), 30, fill="#ff0000")
    else:
        im = Image.new("RGB", (510, 51), (255, 255, 255))
        draw = ImageDraw.Draw(im, "RGBA")
        draw.rounded_rectangle((0, 0, 510, 50), 30, fill="#ffaec8")
        draw.rounded_rectangle((0, 0, love_percentage, 50), 30, fill="#ff0000")

    background.paste(im, (50, 235))
    a = randint(0,50)
    background.save(f"./trash/{a}.png")
    return a

def coat_maker(avatar):
    r = requests.get(avatar)
    background = Image.open("./assets/coat.png")

    mask = Image.open("./assets/coat_mask.png").convert("L")
    avatar = Image.open(io.BytesIO(r.content)).resize((350,350))

    background.paste(avatar,(327,60), mask)
    background = background.crop((125,25,750,650))

    a = randint(0,50)
    background.save(f"./trash/{a}.png")
    return a

def uwu_maker(avatar):
    r = requests.get(avatar)
    avatar = Image.open(io.BytesIO(r.content)).resize((500,500))
    uwu = Image.open("./assets/uwudiscord.png")
    back = Image.new("RGBA",(500,500))
    back.paste(avatar,(0,0), uwu.convert("L"))

    a = randint(0,50)
    back.save(f"./trash/{a}.png")
    return a

def leaderboardCreator(a):
    background,serverlogo,pos1,pos2,pos3,pos4,pos5,pos6,pos7,pos8,pos9,pos10 = a.values()

    r = requests.get(background)
    background = Image.open(io.BytesIO(r.content)).resize((1366, 768))
    # background = background.filter(ImageFilter.GaussianBlur(1))

    r = requests.get(serverlogo)
    serverLogo = Image.open(io.BytesIO(r.content)).resize((190,190))

    a = Image.new("RGBA", (200, 200))
    draw = ImageDraw.Draw(a)
    draw.ellipse((0, 0 , 200, 200), fill=(255, 255, 255))


    x = 180
    fontstyle = ImageFont.truetype("./assets/VarelaRound-Regular.ttf", 100)
    draw = ImageDraw.Draw(background)
    draw.text((530-x, 20), "LEADERBOARD", font=fontstyle, stroke_width=2, stroke_fill="white")

    a.paste(serverLogo, (5,5), Image.open("./assets/mask_circle.jpg").convert("L").resize((190,190)))
    a = a.resize((120, 120))
    background.paste(a, (400-x,20), a)

    def add_user(background, avatar, name, level, position):
        newmask = Image.open("./assets/maskcurvelevel.png")
        r = requests.get(avatar)
        avatar = Image.open(io.BytesIO(r.content)).resize((100, 100))
        new = Image.new("RGB", (500, 100))
        new.paste(background.filter(ImageFilter.GaussianBlur(15)), (-1 * position[0], -1 * position[1]))

        newww = Image.new("RGBA", avatar.size)
        try:
            newww.paste(avatar, mask=avatar.convert("RGBA").split()[3])
        except Exception as e:
            print(e)
            newww.paste(avatar, (0,0))

        new.paste(newww, (0, 0), newww)
        draw = ImageDraw.Draw(new)
        fontstyle = ImageFont.truetype("./assets/VarelaRound-Regular.ttf", 40)
        draw.text((120, 5), name, font=fontstyle)

        fontstyle = ImageFont.truetype("./assets/VarelaRound-Regular.ttf", 25)
        draw.text((120, 55), level, font=fontstyle)
        background.paste(new, position, newmask.convert("L"))
        return background
    
    if pos1 is not None:
        a = pos1.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (112, 150))
    
    if pos2 is not None:
        a = pos2.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (112, 260))
    
    if pos3 is not None:
        a = pos3.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (112, 420-50))
    
    if pos4 is not None:
        a = pos4.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (112, 530-50))
    
    if pos5 is not None:
        a = pos5.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (112, 640-50))

    if pos6 is not None:
        a = pos6.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (724, 150))
    
    if pos7 is not None:
        a = pos7.split("<sep>")
        background = add_user(background,a[0], a[1], a[2], (724, 260))
    
    if pos8 is not None:
        a = pos8.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (724, 420-50))
    
    if pos9 is not None:
        a = pos9.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (724, 530-50))
    
    if pos10 is not None:
        a = pos10.split("<sep>")
        background = add_user(background, a[0], a[1], a[2], (724, 640-50))

    new = Image.new("RGBA", background.size)
    new.paste(background,(0, 0), Image.open("./assets/backcurve.png").convert("L"))

    a = randint(0,50)
    new.save(f"./trash/{a}.png")
    return a

def level_maker(a):
    background,level,avatar,username,current_exp,max_exp,bar_color, text_color = a.values()

    r = requests.get(avatar,stream=True)
    avatar = Image.open(io.BytesIO(r.content)).resize((170,170))
    # avatar = Image.open("./avgg.png").resize((170,170))

    r = requests.get(background,stream=True)
    overlay = Image.open("./assets/overlay1.png")
    background = Image.new("RGBA", overlay.size)
    backgroundover = Image.open(io.BytesIO(r.content)).resize((638,159))
    # backgroundover = Image.open("./assets/banme.jpg").resize((638,159))
    background.paste(backgroundover,(0,0))
    
    background = background.resize(overlay.size)
    background.paste(overlay,(0,0),overlay)

    myFont = ImageFont.truetype("./assets/welcomedont.otf",40)
    draw = ImageDraw.Draw(background)

    draw.text((205,(327/2)+20), username,font=myFont, fill=text_color,stroke_width=1,stroke_fill=(0, 0, 0))
    bar_exp = (current_exp/max_exp)*420
    if bar_exp <= 50:
        bar_exp = 50    

    try:
        if current_exp >= 1000000:
            current_exp = str(current_exp)[0] + "." + str(current_exp)[1] + "M"
    
        if max_exp >= 1000000:
            max_exp = str(max_exp)[0] + "." + str(max_exp)[1] + "M"
    except Exception:
        pass


    try:
        if current_exp >= 100000:
            current_exp = str(current_exp)[0:3] + "." + str(current_exp)[3] + "K"
    
        if max_exp >= 100000:
            max_exp = str(max_exp)[0:3] + "." + str(max_exp)[3] + "K"
    except Exception:
        pass
    
    
    try:
        if current_exp >= 10000:
            current_exp = str(current_exp)[0:2] + "." + str(current_exp)[2] + "K"
    
        if max_exp >= 10000:
            max_exp = str(max_exp)[0:2] + "." + str(max_exp)[2] + "K"
    except Exception:
        pass
    


    try:
        if current_exp >= 1000:
            current_exp = str(current_exp)[0]+"."+str(current_exp)[1]+"K"
    
        if max_exp >= 1000:
            max_exp = str(max_exp)[0]+"."+str(max_exp)[1]+"K"
    except Exception:
        pass

    

    myFont = ImageFont.truetype("./assets/welcomedont.otf",30)
    draw.text((197,(327/2)+125), f"LEVEL - {level}",font=myFont, fill=text_color,stroke_width=1,stroke_fill=(0, 0, 0))

    w,h = draw.textsize(f"{current_exp}/{max_exp}", font=myFont)
    draw.text((638-w-50,(327/2)+125), f"{current_exp}/{max_exp}",font=myFont, fill=text_color,stroke_width=1,stroke_fill=(0, 0, 0))

    mask_im = Image.open("./assets/mask_circle.jpg").convert('L').resize((170,170))
    new = Image.new("RGB", avatar.size, (0, 0, 0))
    try:
        new.paste(avatar, mask=avatar.convert("RGBA").split()[3])
    except Exception as e:
        print(e)
        new.paste(avatar, (0,0))
    background.paste(new, (13, 65), mask_im)

    im = Image.new("RGB", (490, 51), (0, 0, 0))
    draw = ImageDraw.Draw(im, "RGBA")
    draw.rounded_rectangle((0, 0, 420, 50), 30, fill=(255,255,255,50))
    draw.rounded_rectangle((0, 0, bar_exp, 50), 30, fill=bar_color)
    background.paste(im, (190, 235))
    a = randint(0,50)
    new = Image.new("RGBA", background.size)
    new.paste(background,(0, 0), Image.open("./assets/curvedoverlay.png").convert("L"))
    background = new.resize((505, 259))

    background.save(f"./trash/{a}.png", "PNG")
    return a
