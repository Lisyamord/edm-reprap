  
from PIL import Image, ImageDraw

#import math


projname = '34063.png' #название файла без разширения, картинка PNG
 


cap = 1 #0 - отключен, 1 - 220 мкф, 2 - 2200 мкф, 3 - 2420 мкф

pixonstep = 1 #пикселей на один шаг парсера
zdownup = 0.8 #миллиетров поднятие-опускание электрода
g92zcor = 5 #новая аблосютная координата высоты


dpidefault = 300 # dpi картинки по умолчанию
butthurt = [0, 0.65/1000, 0.55/1000, 0.6/1000] #подгорание электрода, миллиметров на 1000 точек
butthurtnummin = 600 #не проводить компенсацию, если менше стольки точек
butthurtmmmin = 0.1 #не проводить компенсацию, если меньше стольки миллиметров расхода
capdelay = ["0", "50", "400", "450"]
repeat = [0, 1, 1, 1] #повторов прожига на точку
dwire = [0, 0.35, 0.35, 0.55]
xcor = 1 #смещение сопла относительно электрода по X
ycor = 5 #смещение сопла относительно электрода по Y
backlash = 0.25 #добавление хода электрода для неровностей текстолита

image = Image.open(projname)
draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
width = image.size[0]  # Определяем ширину
height = image.size[1] # Определяем высоту

dpi = dpidefault


pix = image.load()  # Выгружаем значения пикселей

step = 25.4 * pixonstep / dpi #миллиметров на пиксель
mpi = 1 / step #пикселей на миллиметр

print ('plate ' + projname)
print(format(int(dpi)) + ' dpi')



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
image.save("result" + projname) #сохранить картинку-результат
image.close()
  
wrad = int(0.5*dwire[cap]*mpi) #радиус пятна пикселей относительно центра электрода
image = Image.open("result" + projname) #
draw = ImageDraw.Draw(image)  # создаем инструмент для рисования


newimage = [0] * width #новый массив значений для функции компенсации диаметра пятна
for i in range(width):
    newimage[i] = [0] * height

for k in range(0, wrad, 1): #уомпансация толщины электрода на границу
    pix = image.load() 
    for x in range(width):
        for y in range(height):
            if(x>=1 and x<width-1 and y>=1 and y<height-1): #если не граица картинки
                i = pix[x, y][1] + pix[x, y+1][1] + pix[x, y-1][1] #складываем значения соседних пикселей
                i = i + pix[x+1, y][1] + pix[x-1, y][1]
                i = i + pix[x+1, y+1][1] + pix[x-1, y-1][1] + pix[x+1, y-1][1] + pix[x-1, y+1][1]
                if(i <255*9): #если хоть один чёрный
                    newimage[x][y] = 0 #то и исходный пиксель будет чёрный
                else:
                    newimage[x][y] = 255 #иначе белый

    for x in range(width): #запись новых значений в картинку-результат
        for y in range(height):
            draw.point((x, y), (newimage[x][y], newimage[x][y], newimage[x][y]))
    
    image.save("result" + projname) #сохранить

pix = image.load()  #выгружаем значения пикселей
with open(projname + ".gcode", "w") as gout: #новый файл g-кода
    print(projname + ".gcode")
    print(";" + projname + " plate", file = gout)
    print("M42 I P11 M1 S0 ; отключение конденсатора C1 2200 мкф", file = gout)
    print("M42 I P6 M1 S0 ; отключение конденсатора C2 220 мкф", file = gout)
    print("M42 I P5 M0 ; датчик напряжения на вход", file = gout)
    print("G28 X Y ; Home X, Y", file = gout)
    print("G28 Z ; Home Z on X0 Y0", file = gout)
    print("G1 Z35 F500 ; Up Z to 35 mm", file = gout) #поднятие для перехода через край ванны
    xtostring = format(float(xcor), '.2f') #перевод координаты в строку с 2 знаками после точки
    ytostring = format(float(ycor), '.2f')
    
    print("G1 X" + xtostring + " Y" + ytostring + " F1500", file = gout) #перемещение электрода в нулевую точку платы
    
    wireleight = 0 #расход проволоки
    dotnum = 0 #счётчик точек
    butthurtnum = 0 #счётчик количества компенсаций подгораний с последней корректировки
    butthurtmm = 0 #счётик миллиметров расхода с последней корректировки
    xtostring = format(float(xcor), '.2f')
    ytostring = format(float(ycor), '.2f')
    print("G1 X" +xtostring + " Y" + ytostring + " F1000", file = gout)
    print("M42 I P9 M1 S0", file = gout)
    print("G28 Z ; Home Z", file = gout)
    print("G92 Z5 ; ", file = gout) #новая абсолютная координата в начале столбца
    print("G1 Z5.5 ; ", file = gout)
    zcorup = g92zcor + zdownup #начальная координата Z поднятия электрода
    zcordown = g92zcor - backlash #координата Z опускания электроа

    for x in range(0, width, pixonstep): #цикл по горизонтали
        ycor = 0
        xtostring = format(float(xcor), '.2f')
        

        if butthurtnum >= butthurtnummin or butthurtmm >= butthurtmmmin: #если столбец был не пустым, то новая Z-проба в начале столбца
            print("M42 I P9 M1 S255", file = gout)
            ytostring = format(float(ycor), '.2f')
            print("G1 X" +xtostring + " Y" + ytostring + " F1000", file = gout)
            print("M42 I P9 M1 S0", file = gout)
            print("G28 Z", file = gout)
            print("G92 Z5", file = gout) #новая абсолютная координата в начале столбца
            print("G1 Z5.5", file = gout)
            butthurtnum = 0
            butthurtmm = 0
            zcorup = g92zcor + zdownup #начальная координата Z поднятия электрода
            zcordown = g92zcor - backlash #координата Z опускания электроа
            print("M42 I P9 M1 S255", file = gout) #включить соленоид
            
        if (cap == 1): #подключение нового конденсатора к зарядке
            print("M42 I P6 M1 S255 ; ", file = gout) #подключение конденсатора C2 220 мкф
        elif (cap == 2):
            print("M42 I P11 M1 S255 ; ", file = gout) #подключение конденсатора C2 2200 мкф
        elif (cap == 3):
            print("M42 I P6 M1 S255 ; ", file = gout)
            print("M42 I P11 M1 S255 ; ", file = gout)
        print("M226 P5 S1 ; ", file = gout) #ожидание зарядки
        ycor = 1 #координата на 1 миллиметре вверх
        
        
        for y in range(0, height, pixonstep):  #проверка, что пиксель в столбце не чёрный
            if pix[x, (height - y - 1)][1] > 0:
                for rep in range(repeat[cap]): #счётчик повторов прожигов на пиксель
                    ytostring = format(float(ycor), '.2f')
                    xtostring = format(float(xcor), '.2f')
                    zuptostring = format(float(zcorup), '.2f')
                    zdowntostring = format(float(zcordown), '.2f')
                    
                    print("G1 X" + xtostring + " Y" + ytostring + " F1000", file = gout) #перемещение на координату пикселя
                    print("G1 Z" + zdowntostring + " F300", file = gout) #опускание электрода
                    print("M226 P5 S1", file = gout) #ожидание зарядки конденсатора
                    
                    print("M42 I P9 M1 S0", file = gout) #отключить соленоид
                    print("G4 P150", file = gout) #пауза для опускания электрода пружиной
                    print("M226 P5 S1", file = gout) #ожидание зарядки конденсатора
                    print("M42 I P9 M1 S255", file = gout) #включить соленоид
                    #print("G4 P200", file = gout) #небольшая подзарядка конденсатора
                    
                    #print("G1 Z" + zuptostring, file = gout) #поднятие
                    
                    zcorup -= butthurt[cap] #вычитание подгорания из Z координат
                    zcordown -= butthurt[cap]
                    wireleight += butthurt[cap] #длина израсходованной проволоки
                    dotnum += 1 #счётчик точек
                    butthurtnum += 1
                    butthurtmm += butthurt[cap]
                if pix[x, (height - y - 2)][1] == 0 or y + 1 == height: #поднять, если следующий пиксель равен нулю или достигнут край платы
                    print("G1 Z" + zuptostring, file = gout) #поднятие
            ycor += step #следующая Y координата
                    
        print("M42 I P11 M1 S0 ; ", file = gout) #отключение конденсатора C1 2200 мкф
        print("M42 I P6 M1 S0 ; ", file = gout) #отключение конденсатора C2 220 мкф
        if butthurtnum >= butthurtnummin or butthurtmm >= butthurtmmmin: #если столбец был не пустым
            print("G1 Z" + zuptostring, file = gout) #поднятие
            ycor += 1 #перемещение на миллиметр выше границы платы
            zcordown -= 0.1 #опускание электрода до гарантированного касания и разрядки конденсатора
            ytostring = format(float(ycor), '.2f')
            zuptostring = format(float(zcorup), '.2f')
            zdowntostring = format(float(zcordown), '.2f')
            print("G1 X" + xtostring + " Y" + ytostring + " F1000", file = gout)
            print("G1 Z" + zdowntostring + " F300", file = gout)
            
            print("M42 I P9 M1 S0", file = gout)
            print("G4 P200", file = gout)
            print("M42 I P9 M1 S255", file = gout)
            
            print("G1 Z" + zuptostring, file = gout)
                    
            wireleight += butthurt[cap]
       
        print("M42 I P9 M1 S255", file = gout)
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

    
    

