from threading import Thread
import serial  # importa biblioteca Serial
import time  # importa biblioteca Time
import collections
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import struct
import copy
import pandas as pd
import csv
from tkinter import *

plt.style.use("seaborn-ticks")  # Seleciona o estilo do grafico
# ['seaborn-ticks', 'ggplot', 'dark_background', 'bmh', 'seaborn-poster','seaborn-muted', '_classic_test',
# 'seaborn-notebook', 'fast', 'seaborn', 'classic', 'Solarize_Light2', 'seaborn-dark', 'seaborn-pastel',
# 'seaborn-paper', 'seaborn-colorblind', 'seaborn-bright', 'seaborn-talk', 'seaborn-dark-palette', 'tableau-colorblind10',
# 'seaborn-whitegrid', 'fivethirtyeight', 'grayscale', 'seaborn-white', 'seaborn-deep', 'seaborn-darkgrid']

class serialPlot:  # define classe serialPlot
    def __init__(self,serialPort="COM12",serialBaud=9600,plotLength=100,dataNumBytes=2,numPlots=1,tempo_exposicao=0,tempo_recuperacao=0,ciclos=0,numero_amostragem=0):
        # variaveis definidas para a classe serialPlot
        # ----------------------
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        self.rawData = bytearray(numPlots * dataNumBytes)
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = "h"  # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = "f"  # 4 byte float
        self.data = []
        for i in range(numPlots):  # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0] * plotLength, maxlen=plotLength))
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.tempo_exposicao = tempo_exposicao
        self.tempo_recuperacao = tempo_recuperacao
        self.ciclos = ciclos
        self.numero_amostragem = numero_amostragem
        self.csvData = []
        self.tempo = 0
        self.i = 0
        # ----------------------

        # Comeca a comunicacao serial com o arduino
        print("Trying to connect to: "+ str(serialPort)+ " at "+ str(serialBaud)+ " BAUD.")
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print(
                "Connected to " + str(serialPort) + " at " + str(serialBaud) + " BAUD.")
        except:
            print("Failed to connect with "+ str(serialPort)+ " at "+ str(serialBaud)+ " BAUD.")

    def readSerialStart(self):
        # Envia para o arduino as entradas de tempo_exposicao, tempo_recuperacao e ciclos
        # ---------------------------------------------------------------------------
        time.sleep(1)
        self.serialConnection.write(f"i;l;{self.tempo_exposicao:05d};f\n".encode())
        self.serialConnection.write(f"i;r;{self.tempo_recuperacao:05d};f\n".encode())
        self.serialConnection.write(f"i;c;{self.ciclos:05d};f\n".encode())
        self.serialConnection.write(f"i;a;{self.numero_amostragem:05d};f\n".encode())
        # ---------------------------------------------------------------------------

        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            while self.isReceiving != True:  # Fica no loop ate comecar a receber dados
                time.sleep(0.1)

    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText):
        # Plota no grafico o tempo e os dados recebidos dos sensores
        # --------------------------------------------------------------
        x = 0
        while x != self.numero_amostragem:
            self.serialConnection.write(b"i;s;00000;f\n")  # Inicia a leitura do sensor analogico no arduino
            currentTimer = time.perf_counter()
            self.plotTimer = int((currentTimer - self.previousTimer) * 1000)  # the first reading will be erroneous
            if self.i == 0:
                self.tempo = 0
                self.plotTimer = 0
                self.i = 1
            else:
                self.tempo = round(self.tempo + self.plotTimer / 1000, 1)
            if x == self.numero_amostragem - 1:
                self.csvData.append(self.tempo)
            self.previousTimer = currentTimer
            self.finish_time = round(((self.tempo_exposicao + self.tempo_recuperacao)*self.ciclos)-self.tempo,2)
            timeText.set_text("Tempo = " + str(self.tempo) + "s, Restante = " + str(self.finish_time) + "s, Intevalo = " + str(self.numero_amostragem) + "s")
            privateData = copy.deepcopy(self.rawData[:])  # so that the 3 values in our plots will be synchronized to the same sample time
            for i in range(self.numPlots):
                data = privateData[(i * self.dataNumBytes) : (self.dataNumBytes + i * self.dataNumBytes)]
                value, = struct.unpack(self.dataType, data)
                self.data[i].append(value)  # we get the latest data point and append it to our array
                lines[i].set_data(range(self.plotMaxLength), self.data[i])
                lineValueText[i].set_text("[" + lineLabel[i] + "] = " + str(value))
                if x == self.numero_amostragem - 1:
                    self.csvData.append(value)
            if x == self.numero_amostragem - 1:
                self.csvData.append("\n")
            x = x+1
        # --------------------------------------------------------------

    def backgroundThread(self):  # Recupera `data`
        time.sleep(1.0)  # Da um tempo para o buffer armazenar os dados
        self.serialConnection.reset_input_buffer()
        while self.isRun:
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print("Disconnected...")
        with open("IC.csv", "w", newline="") as f:
            thewriter = csv.writer(f)
            thewriter.writerow(self.csvData)
        f.close()

def main():
    # Codigo do usuario
    # ------------------
    baudRate = 9600  # BaundRate do codigo em arduino
    dataNumBytes = 4  # Number de bytes de 1 ponto de dado
     # number of plots in 1 graph
    # ------------------

    # Entaradas do usuario sao armazenadas nas variaveis tempo_exposicao, tempo_recuperacao e ciclos
    # --------------------------------------------------
    class Application(Frame) :
        def __init__(self,master):
            Frame.__init__(self,master)
            self.grid()
            self.create_widgets()
        def create_widgets(self):
            self.instruction = Label(self, text = "Port name:",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 0, column = 0)

            self.instruction = Label(self, text = "Tempo exposição (s):",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 1, column = 0)

            self.instruction = Label(self, text = "Tempo recuperção (s):",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 2, column = 0)

            self.instruction = Label(self, text = "Numero de ciclos:",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 3, column = 0)

            self.instruction = Label(self, text = "Numero de amostragem por ciclos:",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 4, column = 0)

            self.instruction = Label(self, text = "Numero de sensores(max = 10):",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 5, column = 0)

            self.portName = Entry(self)
            self.portName.grid(row = 0, column = 1, sticky = W)

            self.Tempo_liberacao = Entry(self)
            self.Tempo_liberacao.grid(row = 1, column = 1, sticky = W)

            self.Tempo_recuperacao = Entry(self)
            self.Tempo_recuperacao.grid(row = 2, column = 1, sticky = W)

            self.ciclos = Entry(self)
            self.ciclos.grid(row = 3, column = 1, sticky = W)

            self.numero_amostragem = Entry(self)
            self.numero_amostragem.grid(row = 4, column = 1, sticky = W)

            self.numPlots = Entry(self)
            self.numPlots.grid(row = 5, column = 1, sticky = W)

            self.simulation_button = Button(self, text = "Tempo total", command = self.simulation,fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.simulation_button.grid(row = 6, column = 2, sticky = W)

            self.start_button = Button(self, text = "Start", command = self.start,fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.start_button.grid(row = 6, column = 1, sticky = W)

        def simulation(self):
            tempo_exposicao = self.Tempo_liberacao.get()
            tempo_recuperacao = self.Tempo_recuperacao.get()
            ciclos = self.ciclos.get()
            numero_amostragem = self.numero_amostragem.get()
            portName = self.portName.get()
            numPlots = self.numPlots.get()
            tempo_total = (tempo_exposicao+tempo_recuperacao)*ciclos*1000

            self.instruction = Label(self, text = "Tempo total do ensaio:" + str(tempo_total) + "s",fg = "black", font =('arial',10,'bold'),padx = 50, pady = 10, bd = 1)
            self.instruction.grid(row = 7, column = 1)


        def start(self) :
            tempo_exposicao = self.Tempo_liberacao.get()
            tempo_recuperacao = self.Tempo_recuperacao.get()
            ciclos = self.ciclos.get()
            numero_amostragem = self.numero_amostragem.get()
            portName = self.portName.get()
            numPlots = self.numPlots.get()

            if erro_handler(self,tempo_exposicao,tempo_recuperacao,ciclos,numero_amostragem, portName, numPlots) == False:
                tempo_exposicao = int(tempo_exposicao)
                tempo_recuperacao = int(tempo_recuperacao)
                ciclos = int(ciclos)
                numero_amostragem = int(numero_amostragem)
                numPlots = int(numPlots)
                maxPlotLength = ((tempo_exposicao+tempo_recuperacao)*ciclos)+1 # Maximo valor do eixo x do grafico (tempo)
                # --------------------------------------------------

                s = serialPlot(portName,baudRate,maxPlotLength,dataNumBytes,numPlots,tempo_exposicao,tempo_recuperacao,ciclos,numero_amostragem)  # Inizializa todas as varivaeis necessarias para a 'classe serialPLot'
                s.readSerialStart()  # Comeca o backgroundThread

                # Comeca a plotar no grafico
                # ----------------------------------------------------------------------
                pltInterval = ((tempo_exposicao + tempo_recuperacao)/numero_amostragem)*1000  # Tempo em que e atualizado cada Plot do grafico
                xmin = 0  # Valor minimo do X do grafico
                xmax = maxPlotLength  # Valor maximo do X do grafico
                ymin = 200  # Valor minimo do y do grafico
                ymax = 1000  # Valor maximo do y do grafico
                fig = plt.figure()
                ax = plt.axes(xlim=(xmin, xmax), ylim=(ymin, ymax))
                ax.set_title("Projeto IC")  # Titulo do grafico
                ax.set_xlabel("Tempo")  # Titulo do eixo x
                ax.set_ylabel("Valor em PPM")  # Titulo do eixo y
                nframes = (tempo_exposicao + tempo_recuperacao)*ciclos//pltInterval

                lineLabel = ["Sensor1", "Sensor2", "Sensor3", "Sensor4","Sensor5", "Sensor6", "Sensor7", "Sensor8","Sensor9", "Sensor10"]
                style = ["r-", "c-", "b-", "g-","y-", "m-", "k-", "w-","p-", "s-"]  # linestyles for the different plots
                timeText = ax.text(0.50, 0.95, "", transform=ax.transAxes)
                lines = []
                lineValueText = []
                for i in range(numPlots):
                    lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
                    lineValueText.append(ax.text(0.70, 0.90 - i * 0.05, "", transform=ax.transAxes))

                anim = animation.FuncAnimation(fig,s.getSerialData, fargs=(lines, lineValueText, lineLabel, timeText), interval = pltInterval, frames = nframes, repeat = False)  # Envia as variaveis para plotar o grafico

                plt.legend(loc="upper left")  # Local da legenda no graafico
                plt.show()
                # ----------------------------------------------------------------------

                s.close()  # Para de plotar o grafico

    root = Tk()
    root.title("IC")
    root.geometry("800x300")
    app = Application(root)

    root.mainloop()

def erro_handler(self,tempo_exposicao = "", tempo_recuperacao = "", ciclos = "", numero_amostragem = "", portName = "", numPlots = ""):
    if tempo_exposicao == ""  or tempo_recuperacao == "" or ciclos == "" or numero_amostragem == "" or portName == "" or numPlots == "":
        erro = Label(self,text = "É preciso completar todos os espaços em branco", fg = "black", font =('arial',10,'bold'))
        erro.grid(row = 6, column = 3)
        return True
    elif int(numPlots) > 10:
        erro = Label(self,text = "Passou o numero máximo de sensores", fg = "black", font =('arial',10,'bold'))
        erro.grid(row = 5, column = 3)
        return True
    else:
        erro = Label(self,text = "Completar todos os espaços em branco", fg = "black", font =('arial',10,'bold'))
        erro.grid(row = 5, column = 3)
        erro.grid_remove()
        return False

if __name__ == "__main__":
    main()
