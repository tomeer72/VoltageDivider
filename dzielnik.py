#!/usr/bin/python3

# Its set resistor value for voltage divider using value series
# U1 - napiecie wejsciowe
# U2 - napiecie wyjsciowe
# U1 on result is when U2 is correct
# U2 on result is when U1 is correct 

import argparse
import re
import os
import locale
# from decimal import Decimal

TGREEN = '\033[32m'  # Green Text
TRED = '\033[31m'  # Red Text
TEND = '\033[0m'  # Reset

parser = argparse.ArgumentParser(description='Voltage divider')
parser.add_argument('-u1', metavar='U1', type=float, nargs='?', default=0, help="Voltage U1")
parser.add_argument('-u2', metavar='U2', type=float, nargs='?', default=0, help="Voltage U2")
parser.add_argument('-e96', action='store_true', help="Series E96 - 1%%")
parser.add_argument('-t', metavar='T', type=float, nargs='?', default=2.0, help="Tolerance")
parser.add_argument('-c', metavar='C', type=int, nargs='?', default=10, help="Number of results")
parser.add_argument('-f', metavar='%s', nargs='?', default="null", help="File with resistor series")

args = parser.parse_args()

loc=locale.getlocale(locale.LC_NUMERIC)
locale.setlocale(locale.LC_NUMERIC,"en_US")
u1 = float(args.u1)
u2 = float(args.u2)

print("U1={}, U2={}".format(u1, u2))

print("Top R1; Bottom R2")
print("  | U1")
print("  _")
print(" | | ")
print(" | | R1")
print(" |_|")
print("  | U2")
print("  _")
print(" | |")
print(" | | R2")
print(" |_|")
print("  |")
print(" ---\n")


def checkZero(e):
    if(e <= 0):
        print(TRED + "Seriously...? Value must be > 0" + TEND)
        quit()


def takeValue(e, text):
    if(e == 0):
        e = input("Set value for " + text + ":")
        if(e == ''):
            print(TRED + "You not set value" + TEND)
            quit()    
        e = float(e)
        checkZero(e)
        return e
    else:
        return e

    
u1 = takeValue(u1, "input voltage U1")
u2 = takeValue(u2, "output voltage U2")    

if(u1 <= u2):
    print(TRED + "Let's think... Voltage U1 must be greater than U2" + TEND)
    quit()

E24 = [ 10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91 ]
E96 = [100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150, 154, 158,
        162, 165, 169, 174, 178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255,
        261, 267, 274, 287, 294, 301, 309, 316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412, 422,
        432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549, 562, 576, 590, 604, 619, 634, 649, 665, 681,
        698, 715, 732, 750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976]
multipler = [  1, 10, 100, 1000, 10000, 100000 ]
multipler2 = [0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1]

resultList = []

if(u2 > u1 / 2):
    multipler = multipler2

if(args.f != "null"):
    f = open(args.f, "r")
    ETable = re.findall(r"(\d+)[,-]", f.read())
    
    print("Using file {} for resistor series".format(args.f))
    # print("TableRange:{}".format(len(ETable)))
    # print(ETable)
else:    
    if(args.e96):
        ETable = E96
        print("Using Table E96")
    else:
        ETable = E24
        print("Using Table E24")

print("Divider Tolerance: {}%".format(args.t))
   
for index in range(len(ETable)):
    try:
        r2 = float(ETable[ index ])

    except:
        continue
    r1 = r2 * (u1 - u2) / u2
    for y in range(len(multipler)):
        for items in range(len(ETable)):
            rr1 = r1
            rr2 = r2
            try:
                Ritems = float(ETable[items])
            except:
                continue;
            value = Ritems * multipler[ y ]
            while(value < 10):
                value *= 10
                rr2 *= 10
                rr1 *= 10            
            res = {'error':float((rr1 - value) / rr1), 'r1':value, 'r2':rr2}
            resultList.append(res)   


def compare(e):
    return abs(e['error'])

      
resultList.sort(key=compare)


def surfix(v):
    if(v > 1e6):
        v /= 1e6
        s = 'M'
    elif(v > 1e3):
        v /= 1e3
        s = 'k'
    else:
        s = ''
    result = "{:g} {}\u03A9"
    return result.format(v, s)


for number in range(args.c):
        
    if(len(resultList) - 1 < number):
        break
    
    res = resultList[ number ]
    error = res['error'] * 100
   
    print("Pos=%d:" % number, end=' ')

    if(abs(error) > float(args.t)):
        print(TRED, end='')
    else:
        print(TGREEN, end='')
    
    result = "R1 = {:.2g}, Error = {:.2f} %, U1 = {:.2f}({:.2f}%), U2 = {:.2f}({:.2f}%)"
    r1f = res['r2'] * (u1 - u2) / u2  # ideal R1
    u1f = u2 * (res['r1'] + res['r2']) / res['r2']  # real U1 if U2=u2
    u1error = (u1 - u1f) / u1 * 100
    u2f = u1 * res['r2'] / (res['r1'] + res['r2'])  # real U2 if U1=u1
    u2error = float((u2 - u2f) / u2) * 100
    print(result.format(r1f, error, u1f, u1error, u2f, u2error) + TEND)
    
    test = True
    
    r1 = res['r1']
    r2 = res['r2']
    
    while(test):
        print("\tR1 = {}; R2 = {}".format(surfix(r1), surfix(r2)))
        r1 *= 10
        r2 *= 10
        if(r1 > 10e6 or r2 > 10e6):
            break
       
    print(TEND)
locale.setlocale(locale.LC_NUMERIC, loc)
