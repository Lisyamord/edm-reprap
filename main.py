  
from PIL import Image, ImageDraw
#import math


projname = '34063' #название файла без разширения, картинка PNG
 

dpi = 300 #пикселей на дюйм
cap = 3 #0 - отключен, 1 - 220 мкф, 2 - 2200 мкф, 3 - 2420 мкф

pixonstep = 1 #пикселей на один шаг парсера
zdownup = 0.45 #миллиетров поднятие-опускание электрода
g92zcor = 5 #новая аблосютная координата высоты

butthurt = [0, 0.08/1000, 0.15/1000, 0.2/1000] #подгорание электрода, миллиметров на 1000 точек
capdelay = ["0", "50", "400", "450"]
repeat = [1, 2, 1, 1] #повторов прожига на точку
dwire = [0, 0.12, 0.3, 0.4]
xcor = 24 #смещение сопла относительно электрода по X
ycor = 1 #смещение сопла относительно электрода по Y
backlash = 0.05 #добавление хода электрода для неровностей текстолита

step = 25.4 * pixonstep / dpi #миллиметров на пиксель
mpi = 1 / step #пикселей на миллиметр

image = Image.open(projname + '.png')
draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
width = image.size[0]  # Определяем ширину
height = image.size[1] # Определяем высоту
pix = image.load()  # Выгружаем значения пикселей

for x in range(width): #парсинг и приведение к 255 - 0 исходного файла
    for y in range(height):
        r = pix[x, y][0] #красный пиксель
        g = pix[x, y][1] #зелёный
        b = pix[x, y][2] #синий
        sr = (r + g + b)  #среднее значение
        if sr <= 250*3: # если не совсем белый - то чёрнный
            sr = 0
        else:
            sr = 255
        draw.point((x, y), (sr, sr, sr)) #рисуем пиксель
image.save("result" + projname + '.png') #сохранить картинку-результат
image.close()
  
wrad = int(0.5*dwire[cap]*mpi) #радиус пятна пикселей относительно центра электрода
image = Image.open("result" + projname + '.png') #
draw = ImageDraw.Draw(image)  # создаем инструмент для рисования


newimage = [0] * width #новый массив значений для функции компенсации диаметра пятна
for i in range(width):
    newimage[i] = [0] * height

for k in range(0, wrad, 1): #уомпансация толщины электрода на границу
    pix = image.load() 
    for x in range(width):
        for y in range(height):
            if(x>=1 and x<width-1 and y>=1 and y<height-1): #если не граица картинки
                i = ppix[x, y][1] + ix[x, y+1][1] + pix[x, y-1][1] #складываем значения соседних пикселей
                i = i + pix[x+1, y][1] + pix[x-1, y][1]
                i = i + pix[x+1, y+1][1] + pix[x-1, y-1][1] + pix[x+1, y-1][1] + pix[x-1, y+1][1]
                if(i <255*9): #если хоть один чёрный
                    newimage[x][y] = 0 #то и исходный пиксель будет чёрный
                else:
                    newimage[x][y] = 255 #иначе белый

    for x in range(width): #запись новых значений в картинку-результат
        for y in range(height):
            draw.point((x, y), (newimage[x][y], newimage[x][y], newimage[x][y]))
    
    image.save("result" + projname + '.png') #сохранить

pix = image.load()  #выгружаем значения пикселей
with open(projname + ".gcode", "w") as gout: #новый файл g-кода
    print(";" + projname + " plate", file = gout)
    print("M42 I P11 M1 S0 ; отключение конденсатора C1 2200 мкф", file = gout)
    print("M42 I P6 M1 S0 ; отключение конденсатора C2 220 мкф", file = gout)
    print("M42 I P5 M0 ; датчик напряжения на вход", file = gout)
    print("G28 X Y ; Home X, Y", file = gout)
    print("G28 Z ; Home Z on X0 Y0", file = gout)
    print("G1 Z25 F500 ; Up Z to 25 mm", file = gout) #поднятие для перехода через край ванны
    xtostring = format(float(xcor), '.2f') #перевод координаты в строку с 2 знаками после точки
    ytostring = format(float(ycor), '.2f')
    
    print("G1 X" + xtostring + " Y" + ytostring + " F1500", file = gout) #перемещение электрода в нулевую точку платы
    
    wireleight = 0 #расход проволоки
    dotnum = 0 #счётчик точек
    
    for x in range(0, width, pixonstep): #цикл по горизонтали
        ycor = 0
        freeflag = 0 #признак того, что столбец пустой
        
        for ys in range(0, height): #проверка того, что столбец пустой
            if pix[x, (height - ys - 1)][1] > 0:
                freeflag = 1
                break
        if freeflag == 1: #если не пустой, то новая Z-проба в начале столбца
            xtostring = format(float(xcor), '.2f')
            ytostring = format(float(ycor), '.2f')
            print("G1 X" +xtostring + " Y" + ytostring + " F1000", file = gout)
            print("G28 Z ; Home Z", file = gout)
            print("G92 Z5 ; ", file = gout) #новая абсолютная координата в начале столбца
            print("G1 Z5.5 ; ", file = gout)      
            
        if (cap == 1): #подключение нового конденсатора к зарядке
            print("M42 I P6 M1 S255 ; ", file = gout) #подключение конденсатора C2 220 мкф
        elif (cap == 2):
            print("M42 I P11 M1 S255 ; ", file = gout) #подключение конденсатора C2 2200 мкф
        elif (cap == 3):
            print("M42 I P6 M1 S255 ; ", file = gout)
            print("M42 I P11 M1 S255 ; ", file = gout)
        print("M226 P5 S1 ; ", file = gout) #ожидание зарядки
        ycor = 1 #координата на 1 миллиметре вверх
        zcorup = g92zcor + zdownup #начальная координата Z поднятия электрода
        zcordown = g92zcor - backlash #координата Z опускания электроа
        
        for y in range(0, height, pixonstep):  #проверка, что пиксель в столбце не чёрный
            if pix[x, (height - y - 1)][1] > 0:
                for rep in range(repeat[cap]): #счётчик повторов прожигов на пиксель
                    ytostring = format(float(ycor), '.2f')
                    zuptostring = format(float(zcorup), '.2f')
                    zdowntostring = format(float(zcordown), '.2f')
                    print("G1 X" + xtostring + " Y" + ytostring + " F1000", file = gout) #перемещение на координату пикселя
                    print("M226 P5 S1 ; ", file = gout) #ожидание зарядки конденсатора
                    print("G1 Z" + zdowntostring + " F300", file = gout) #опускание электрода
                    print("G1 Z" + zuptostring, file = gout) #поднятие 
                    zcorup -= butthurt[cap] #вычитание подгорания из Z координат
                    zcordown -= butthurt[cap]
                    wireleight += butthurt[cap] #длина израсходованной проволоки
                    dotnum += 1 #счётчик точек
                ycor += step #следующая Y координата
            else:
                ycor += step
                continue
        if freeflag == 1: #если столбец был не пустым
            print("M42 I P11 M1 S0 ; ", file = gout) #отключение конденсатора C1 2200 мкф
            print("M42 I P6 M1 S0 ; ", file = gout) #отключение конденсатора C2 220 мкф
            ycor += 1 #перемещение на миллиметр выше границы платы
            zcordown -= 0.1 #опускание электрода до гарантированного касания и разрядки конденсатора
            ytostring = format(float(ycor), '.2f')
            zuptostring = format(float(zcorup), '.2f')
            zdowntostring = format(float(zcordown), '.2f')
            print("G1 X" + xtostring + " Y" + ytostring + " F1000", file = gout)
            print("G1 Z" + zdowntostring + " F300", file = gout)
            print("G1 Z" + zuptostring, file = gout)
            wireleight += butthurt[cap]
        xcor += step
        if zcordown <= 0: #признак того, что запас хода по Z недостаточный
            zcordownflag = 1
        else:
            zcordownflag = 0
    
    
    print(dotnum, " dots")
    print("; end of file", file = gout)
if zcordownflag == 1:
    print("ZCorDown <= 0, " + format(float(zcordown), '.2f'))
print("Wire leight = , " + format(float(wireleight), '.2f') + "mm")
