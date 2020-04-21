from tkinter import * 
from tkinter.ttk import *

print("Enter file path")
handle = open(input(),"r")

arr = []

boardSize = 16

dataCollectionStart = False
dataCollectionStartRepeat = False
dataLengthCheck = False

gameRawData = []

print("reading data")

#count = 0

for line in handle:
    #count += 1
    
    if dataCollectionStart and dataCollectionStartRepeat:
        if len(line) == 113:
            dataLengthCheck = True

    if dataCollectionStart and dataCollectionStartRepeat and dataLengthCheck:
        #print(count)
        if line != "\n":
            #print(len(line))
            line = line.strip("\n")
            gameRawData[-1].append([line[i:i+7] for i in range(0, len(line), 7)])
        else:
            gameRawData.append([])
    if not dataCollectionStart and line == "\n":
        dataCollectionStart = True
        continue
    if dataCollectionStart and not dataCollectionStartRepeat and line == "\n":
        dataCollectionStartRepeat = True
        gameRawData.append([])


processedData = []

print("processing data")

for turn in gameRawData:
    processedData.append([])
    for row in range(len(turn)):
        arr = [0 for column in range(len(turn[row]))]
        for col in range(len(turn[row])):
            if "B" in turn[row][col]:
                arr[col] = 2
            if "W" in turn[row][col]:
                arr[col] = 1 
        processedData[-1].append(arr)

n = len(processedData[0])

print("showing data")


#Gui

root = Tk()

labelArr = []

for r in range(n):
    labelArr.append([])
    for c in range(n):
        label = Label(root,text="            ",padding="10",relief=RAISED)
        label.grid(row=r,column=c)
        labelArr[-1].append(label)

bluePawnLabel = Label(root,text="",padding="20",relief=RAISED)
bluePawnLabel.grid(row=n,column=n)
redPawnLabel = Label(root,text="",padding="20",relief=RAISED)
redPawnLabel.grid(row=n+1,column=n)



#print(len(processedData[0]))
#print(len(processedData[0][0]))

counter = -1



def refresh(event):
    global counter,processedData, labelArr, n, bluePawnLabel,redPawnLabel
    if counter >= len(processedData)-1:
        return
    print(counter)
    counter += 1
    blue = 0
    red = 0
    if counter >= len(processedData):
        return
    for r in range(n):
        for c in range(n):
            target = processedData[counter][r][c]
            if target == 0:
                labelArr[r][c].configure(background="WHITE")
                target = "       "
            if target == 1:
                target = gameRawData[counter][r][c]
                blue += 1
                labelArr[r][c].configure(background="BLUE")
            if target == 2:
                target = gameRawData[counter][r][c]
                red += 1
                labelArr[r][c].configure(background="RED")
            labelArr[r][c].configure(text=target)
    redPawnLabel.configure(text=str(red))
    bluePawnLabel.configure(text=str(blue))
    print("Refresh done")
    return

def refreshBack(event):
    global counter,processedData, labelArr, n
    blue = 0
    red = 0
    if counter == 0:
        return
    counter = max(0,counter-1)
    print(counter)
    if counter >= len(processedData):
        return
    for r in range(n):
        for c in range(n):
            target = processedData[counter][r][c]
            if target == 0:
                labelArr[r][c].configure(background="WHITE")
                target = "        "
            if target == 1:
                target = gameRawData[counter][r][c]
                labelArr[r][c].configure(background="BLUE")
                blue += 1
            if target == 2:
                target = gameRawData[counter][r][c]
                labelArr[r][c].configure(background="RED")
                red += 1
            labelArr[r][c].configure(text=target)
    redPawnLabel.configure(text=str(red))
    bluePawnLabel.configure(text=str(blue))
    print("Refresh done")
    return

root.bind('<Right>', refresh)
root.bind('<Left>', refreshBack)

root.mainloop()


    
