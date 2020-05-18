from tkinter import *
import tkinter as tk
import time  # importa biblioteca Time
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import mypackage.Serial_acquire as serial_acquire
import flask
from flask import request, render_template
import numpy as np
import matplotlib.ticker as ticker

app = flask.Flask(__name__)

app.config["DEBUG"] = True

plt.style.use("seaborn-ticks")

def main():
    # Codigo do usuario
    # ------------------
    baudRate = 115200 # BaundRate do codigo em arduino
    dataNumBytes = 4  # Number de bytes de 1 ponto de dado
    # ------------------

    # Entaradas do usuario sao armazenadas nas variaveis tempo_exposicao, tempo_recuperacao e ciclos
    # --------------------------------------------------
    print("Com o crtl apertado entre nesse link http://127.0.0.1:5000/Nariz_Eletronico")
    @app.route('/', methods=['GET'])
    def get_input():
        return render_template('homepage.html')

    # @app.route('/', methods=['POST'])
    # def simulation():   
    #     portName = request.form['portName']
    #     tempo_exposicao = request.form['tempo_exposicao']
    #     tempo_recuperacao = request.form['tempo_recuperacao']
    #     ciclos = request.form['ciclos']
    #     intervalPlot = request.form['intervalPlot']
    #     filename = request.form['filename']
    #     # sensores_desativados = self.sensores_desativados.get()
    #     numPlots = 9
    #     option = request.form['filename']

    #     # if (erro_handler(self,tempo_exposicao,tempo_recuperacao,ciclos,intervalPlot,portName,)== False):
    #     tempo_exposicao = int(tempo_exposicao)
    #     tempo_recuperacao = int(tempo_recuperacao)
    #     ciclos = int(ciclos)
    #     intervalPlot = int(intervalPlot)
    #     tempo_total = (tempo_exposicao + tempo_recuperacao) * ciclos
    #     day = tempo_total//86400
    #     hour = tempo_total%86400//3600
    #     minutes = ((tempo_total%86400)%3600)//60
    #     seconds = (((tempo_total%86400)%3600)%60)
    #     return render_template('sumlationpage.html', output = "Tempo total do ensaio: %d:%d:%d:%d s" % (day, hour, minutes, seconds))

    @app.route('/', methods=['POST'])
    def start():
        portName = request.form['portName']
        tempo_exposicao = request.form['tempo_exposicao']
        tempo_recuperacao = request.form['tempo_recuperacao']
        ciclos = request.form['ciclos']
        intervalPlot = request.form['intervalPlot']
        filename = request.form['filename']
        option = request.form['expressar tempo']
        # sensores_desativados = self.sensores_desativados.get()
        numPlots = 9

    #   if (erro_handler(self,tempo_exposicao,tempo_recuperacao,ciclos,intervalPlot,portName,sensores_desativados,)== False and (option == 1 or option == 2)):
        tempo_exposicao = int(tempo_exposicao)#segundos
        tempo_recuperacao = int(tempo_recuperacao)#segundos
        ciclos = int(ciclos)
        # sensores_desativados = int(sensores_desativados)
        intervalPlot = int(intervalPlot)
        option = int(option)

        nframes = int((((tempo_exposicao + tempo_recuperacao)*(ciclos)*1000)+10000)//intervalPlot)
        maxPlotLength = nframes + 1  # Maximo valor do eixo x do grafico (tempo) em segundos

        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        s = serial_acquire.serialPlot(
            portName,
            baudRate,
            maxPlotLength,
            dataNumBytes,
            numPlots,
            # sensores_desativados,
            tempo_exposicao,
            tempo_recuperacao,
            ciclos,
            filename,
            option,)

        s.readSerialStart()  # Comeca o backgroundThread

        # Comeca a plotar no grafico
        # ----------------------------------------------------------------------
        xmin = 0  # Valor minimo do X do grafico
        xmax = maxPlotLength  # Valor maximo do X do grafico
        ymin = 200 # Valor minimo do y do grafico
        ymax = 1000  # Valor maximo do y do grafico
        fig,ax = plt.subplots(facecolor=(.18, .31, .31),figsize=(17,5))
        ax = plt.axes()
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)


        ax.set_title("Projeto IC",color='peachpuff')  # Titulo do grafico
        ax.set_xlabel("Numero de plots",color='peachpuff')  # Titulo do eixo x
        ax.set_ylabel("Valor em PPM",color='peachpuff')  # Titulo do eixo y
        ax.set_facecolor('#eafff5')
        ax.grid(True)
        
        #ReScale x label
        x = np.linspace(xmin,xmax)
        scale_x = 1000/(intervalPlot)
        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_x))
        ax.xaxis.set_major_formatter(ticks_x)
        ax.set_xticks(np.arange(xmin,xmax))


        lineLabel = ["Sensor1","Sensor2","Sensor3","Sensor4","Sensor5","Sensor6","Sensor7","Sensor8","Sensor9",]
        style = ["r-","c-","b-","g-","y-","m-","k-","s-","p-",]  # linestyles for the different plots
        timeText = ax.text(0.50, 0.95, "", transform=ax.transAxes)
        lines = []
        lineValueText = []
        for i in range(numPlots):
            lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
            lineValueText.append(ax.text(0.70, 0.90 - i * 0.05, "", transform=ax.transAxes))
        anim = animation.FuncAnimation(fig,s.getSerialData,fargs=(lines, lineValueText, lineLabel, timeText),interval = intervalPlot,frames = nframes,repeat = False)  # Envia as variaveis para plotar o grafico

        plt.legend(loc="upper left")  # Local da legenda no graafico
        plt.show()
        # ----------------------------------------------------------------------

        s.close()  # Para de plotar o grafico
        return render_template('backpage.html')
    app.run()

if __name__ == "__main__":
    main()
# def erro_handler(self,tempo_exposicao="",tempo_recuperacao="",ciclos="",intervalPlot="",portName="",numPlots="",):
#     if (tempo_exposicao == ""or tempo_recuperacao == ""or ciclos == ""or intervalPlot == ""or portName == ""or numPlots == "" ):
#         erro = Label(self,text="É preciso completar todos os espaços em branco",fg="black",font=("arial", 10, "bold"),)
#         erro.grid(row=6, column=3)
#         return True
#     else:
#         erro = Label(self,text="Completar todos os espaços em branco",fg="black",font=("arial", 10, "bold"),)
#         erro.grid(row=5, column=3)
#         erro.grid_remove()
#         return False
