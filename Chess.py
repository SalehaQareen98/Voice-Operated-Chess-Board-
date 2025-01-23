import chess
import numpy as np
from subprocess import call
from Cell import Cell  #importing the class cell for storing the arm cordinates
import serial
import time

#setting default value of player as first turn is of white player
player = "white"
No_of_moves = 1

def InitializeBoard(board,cells):
# reading all the x,y cordinates form file
# declaring i,j cordinates 
    i,j,counter=0,0,0
    try:
        f = open('ArmCordinates.txt','r')
    except IOError:
         call(["espeak","-s140 -ven+18 -z","Board is not initialized."])
         
    for line in f: # reading all the cordinates from the file line by line
        for num in line.split(' '): #spliting the line integer wise 
            if counter%2==0: #to read x degree of robotic arm
                x=int(num)
                counter=1
            else: #to read y degree of robotic arm
                y=int(num)
                counter=0
                cells[i,j]=Cell(x,y)
                j+=1
        i+=1
        j=0
        
    f.close()
    call(["espeak","-s140 -ven+18 -z","Board is turned on and initialized succcessfully."])

def validCell(str):
    if str[0] >='a' and str[0] <='h':
        if str[1] >= '1' and str[1] <= '8':
            return True
        else:
            return False
    else:
        return False

def CheckCommandValidity(inputstring):
    var=inputstring.split(' ')
    if var[0]=="move":
        if var[1]== "from":
            source=var[2]
            if not validCell(source):
                call(["espeak","-s140 -ven+18 -z","invalid command!"])
                return False
            if var[3]=="to":
                destination = var[4]
                if not validCell(destination):
                    call(["espeak","-s140 -ven+18 -z","invalid command!"])
                else:
                    return True
            else:
               call(["espeak","-s140 -ven+18 -z","Give command again."])
        else:
            call(["espeak","-s140 -ven+18 -z","invalid command!"])
    else:
        call(["espeak","-s140 -ven+18 -z","invalid command!"])
    return False
    
def GiveCommand(player):
    ser1 = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser1.flush()
    IsCommandValid = False
    systemResponse = "Player " + player + " give command"
    call(["espeak","-s140 -ven+18 -z",systemResponse])
    while IsCommandValid == False:
        #systemResponse = "Player " + player + " give command"
        #call(["espeak","-s140 -ven+18 -z",systemResponse])
        #time.sleep(5)
        if ser1.in_waiting > 0:
            inputstring = ser1.readline().decode('utf-8').rstrip()
            inputstring = inputstring.lower()
            print(inputstring)
        #inputstring= str(input())
        #inputstring = inputstring.lower()
            if CheckCommandValidity(inputstring):
                IsCommandValid = True
                var=inputstring.split(' ')
                source=var[2]
                destination=var[4]
    return inputstring,source,destination

def mappingcolumns (s):
    switcher={
                'a':1,
                'b':2,
                'c':3,
                'd':4,
                'e':5,
                'f':6,
                'g':7,
                'h':8 
             }
    return switcher.get(s,"Invalid")

def PickPiece(row,col,cells,ser, No_of_moves):
    if No_of_moves == 1:
        d = str(cells[row-1][col-1].x) + ' ' + str(cells[row-1][col-1].y) + ' ' + '1' + ' ' + '1' + '\n';
        ser.write(d.encode('utf-8'));
        line = ser.readline().decode('utf-8').rstrip()
        time.sleep(1)

    d = str(cells[row-1][col-1].x) + ' ' + str(cells[row-1][col-1].y) + ' ' + '1' + ' ' + '1' + '\n';
    ser.write(d.encode('utf-8'));
    line = ser.readline().decode('utf-8').rstrip()
    time.sleep(7)
    if line != "":
        return True

def DropPiece(row,col,cells,ser):
    d = str(cells[row-1][col-1].x) + ' ' + str(cells[row-1][col-1].y) + ' ' + '1' + ' ' + '0' + '\n';
    ser.write(d.encode('utf-8'));
    line = ser.readline().decode('utf-8').rstrip()
    time.sleep(5)
    
def DropKilledPiece(x,y,ser):
    print("hello")
    d = x + ' ' + y + ' ' + '1' + '0' + '\n'
    ser.write(d.encode('utf-8'));
    line = ser.readline().decode('utf-8').rstrip()
    time.sleep(5) 
    
def MovePiece(source,destination,Pieces,cells,No_of_moves):
    while True:
        command= source+destination
        if(chess.Move.from_uci(command) in board.legal_moves):
            inputmove = chess.Move.from_uci(command)
            board.push(inputmove)  # Make the move    
            s_col,d_col = (mappingcolumns(source[0])),(mappingcolumns(destination[0]))
            s_row,d_row = int(source[1]),int(destination[1])
            ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            ser.flush()
            #if Pieces[d_row-1][d_col-1] != '.':
             #   if PickPiece(d_row,d_col,cells,ser,No_of_moves):
              #      DropKilledPiece('15','155',ser)
            
            if PickPiece(s_row,s_col,cells,ser,No_of_moves):
                DropPiece(d_row,d_col,cells,ser)
            Pieces[s_row-1][s_col-1], Pieces[d_row-1][d_col-1] = Pieces[d_row-1][d_col-1], Pieces[s_row-1][s_col-1]
            No_of_moves += 1
            break
        else:
            call(["espeak","-s140 -ven+18 -z", "invalid move"])
            inputstring,source,destination = GiveCommand(player)
            
        
if __name__=="__main__":
   
    cells = np.empty((8,8), dtype = object)
    board = chess.Board();
    InitializeBoard(board,cells)
    Pieces = [ ['R', 'N','B','Q','K','B','N','R'], ['P','P','P','P','P','P','P','P'],
              ['.','.','.','.','.','.','.','.'],['.','.','.','.','.','.','.','.'],
              ['.','.','.','.','.','.','.','.'] ,['.','.','.','.','.','.','.','.'],
              ['p','p','p','p','p','p','p','p'],['r', 'n','b','q','k','b','n','r']]
    while not (board.is_checkmate() or board.is_stalemate()):
        inputstring,source,destination = GiveCommand(player)
        MovePiece (source,destination,Pieces,cells,No_of_moves)
        #print(Pieces)
        if player == "white":
            player = "black"
        else:
            player = "white"
