  
from PIL import Image, ImageDraw
#import math


projname = '/thisplate/'
 
image = Image.open(projname + '.png')
#image.show()

dpi = 300 #пикселей на дюйм
repeat = 1 #повторов прожига на точку

pixonstep = 1 #пикселей на один шаг парсера
zdownup = 0.4 #миллиетров поднятие-опускание электрода
g92zcor = 15 #новая аблосютная координата высоты
dspotс1 = 0.1 #диаметр каверны при прожиге первымм конденсатором 220 мкф
dspotс2 = 0.25 #диаметр каверны при прожиге вторым конденсатором 2200 мкф
cap = 3 #0 - отключен, 1 - 220 мкф, 2 - 2200 мкф, 3 - 2420 мкф
butthurt = [0, 0.1/1000, 0.25/1000, 0.35/1000] #подгорание электрода, миллиметров на 1000 точек
capdelay = ["0", "50", "400", "450"]
xcor = 24 #смещение сопла относительно электрода по X
ycor = 0 #смещение сопла относительно электрода по Y

step = 25.4 * pixonstep / dpi #миллиметров на пиксель

draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
width = image.size[0]  # Определяем ширину
height = image.size[1] # Определяем высоту
pix = image.load()  # Выгружаем значения пикселей

for x in range(width):
    for y in range(height):
        r = pix[x, y][0] #узнаём значение красного цвета пикселя
        g = pix[x, y][1] #зелёного
        b = pix[x, y][2] #синего
        sr = (r + g + b)  #среднее значение
        if sr <= 250*3:
            sr = 0
        else:
            sr = 255
        draw.point((x, y), (sr, sr, sr)) #рисуем пиксель
            
    
image.save("result" + projname + '.png') #не забываем сохранить изображение


with open(projname + ".gcode", "w") as gout:
    print(";" + projname + " plate", file = gout)
    print("M42 I P11 M1 S0 ; отключение конденсатора C1 2200 мкф", file = gout)
    print("M42 I P6 M1 S0 ; отключение конденсатора C2 220 мкф", file = gout)
    print("G28 X Y ; Home X, Y", file = gout)
    print("G28 Z ; Home Z on X0 Y0", file = gout)
    print("G1 Z25 F500 ; Up Z to 25 mm", file = gout) #поднятие для перехода через край ванны
    xtostring = format(float(xcor), '.2f')
    ytostring = format(float(ycor), '.2f')
    
    print("G1 X" + xtostring + " Y" + ytostring + " F1500", file = gout) #перемещение электрода в нулевую точку платы
    print("G28 Z ; Home Z", file = gout)
    print("G92 Z15 ; New absolute coordinate", file = gout)
    if (cap == 1):
        print("M42 I P6 M1 S255 ; подключение конденсатора C2 220 мкф", file = gout)
    elif (cap == 2):
        print("M42 I P11 M1 S255 ; подключение конденсатора C2 2200 мкф", file = gout)
    elif (cap == 3):
        print("M42 I P6 M1 S255 ; подключение конденсатора C2 220 мкф", file = gout)
        print("M42 I P11 M1 S255 ; подключение конденсатора C1 2200 мкф", file = gout)
    
    
    
    zcorup = g92zcor + zdownup
    zcordown = g92zcor
    
    wireleight = 0
    dotnum = 0
    
    for x in range(0, width, pixonstep):
        ycor = 0
        xtostring = format(float(xcor), '.2f')
        ytostring = format(float(ycor), '.2f')
        print("G1 X" +xtostring + " Y" + ytostring + " F1000", file = gout)
        for y in range(0, height, pixonstep):
            
            
            if pix[x, (height - y - 1)][1] > 0:
                ytostring = format(float(ycor), '.2f')
                zuptostring = format(float(zcorup), '.2f')
                zdowntostring = format(float(zcordown), '.2f')
                for rep in range(repeat):
                    print("G1 X" + xtostring + " Y" + ytostring + " F1000", file = gout)
                    print("G1 Z" + zdowntostring + " F200", file = gout)
                    print("G1 Z" + zuptostring, file = gout)
                    print("G4 P" + capdelay[cap], file = gout) #задержка для зарядки конденсатора
                    zcorup -= butthurt[cap]
                    zcordown -= butthurt[cap]
                    wireleight += butthurt[cap]
                    dotnum += 1
                ycor += step
            else:
                ycor += step
                continue
        xcor += step
        if zcordown <= 0:
            zcordownflag = 1
        else:
            zcordownflag = 0
    
    print(dotnum, " dots")
    print("; end of file", file = gout)
if zcordownflag == 1:
    print("ZCorDown <= 0, " + format(float(zcordown), '.2f'))
print("Wire leight = , " + format(float(wireleight), '.2f') + "mm")

    
    
