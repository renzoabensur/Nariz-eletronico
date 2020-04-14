from tkinter import *
import tkinter as tk
import time  # importa biblioteca Time
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import mypackage.Serial_acquire as serial_acquire
import flask
from flask import request, render_template

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
    print("Aperte nesse link com o crtl http://127.0.0.1:5000/")
    @app.route('/', methods=['GET'])
    def get_input():
        return render_template('homepage.html')

    # @app.route('/', methods=['POST'])
    # def simulation():   
    #     portName = request.form['portName']
    #     tempo_exposicao = request.form['tempo_exposicao']
    #     tempo_recuperacao = request.form['tempo_recuperacao']
    #     ciclos = request.form['ciclos']
    #     numero_amostragem = request.form['numero_amostragem']
    #     filename = request.form['filename']
    #     # sensores_desativados = self.sensores_desativados.get()
    #     numPlots = 9
    #     option = request.form['filename']

    #     # if (erro_handler(self,tempo_exposicao,tempo_recuperacao,ciclos,numero_amostragem,portName,)== False):
    #     tempo_exposicao = int(tempo_exposicao)
    #     tempo_recuperacao = int(tempo_recuperacao)
    #     ciclos = int(ciclos)
    #     numero_amostragem = int(numero_amostragem)
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
        numero_amostragem = request.form['numero_amostragem']
        filename = request.form['filename']
        option = request.form['expressar tempo']

        if option == 'Segundos':
            option = 1
        else:
            option = 2
            
        # sensores_desativados = self.sensores_desativados.get()
        numPlots = 9

    #   if (erro_handler(self,tempo_exposicao,tempo_recuperacao,ciclos,numero_amostragem,portName,sensores_desativados,)== False and (option == 1 or option == 2)):
        tempo_exposicao = int(tempo_exposicao)#segundos
        tempo_recuperacao = int(tempo_recuperacao)#segundos
        ciclos = int(ciclos)
        # sensores_desativados = int(sensores_desativados)
        numero_amostragem = int(numero_amostragem)
        pltInterval = int(((tempo_exposicao + tempo_recuperacao)*1000//numero_amostragem))  # Tempo em que e atualizado cada Plot do grafico

        nframes = int((((tempo_exposicao + tempo_recuperacao)*(ciclos)*1000)+10000)//pltInterval)
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
            ciclos,pltInterval,
            filename,option)

        s.readSerialStart()  # Comeca o backgroundThread

        # Comeca a plotar no grafico
        # ----------------------------------------------------------------------
        xmin = 0  # Valor minimo do X do grafico
        xmax = maxPlotLength  # Valor maximo do X do grafico
        ymin = 200  # Valor minimo do y do grafico
        ymax = 1000  # Valor maximo do y do grafico
        fig = plt.figure()
        ax = plt.axes(xlim=(xmin, xmax), ylim=(ymin, ymax))
        ax.set_title("Projeto IC")  # Titulo do grafico
        ax.set_xlabel("Numero de plots")  # Titulo do eixo x
        ax.set_ylabel("Valor em PPM")  # Titulo do eixo y

        lineLabel = ["Sensor1","Sensor2","Sensor3","Sensor4","Sensor5","Sensor6","Sensor7","Sensor8","Sensor9",]
        style = ["r-","c-","b-","g-","y-","m-","k-","s-","p-",]  # linestyles for the different plots
        timeText = ax.text(0.50, 0.95, "", transform=ax.transAxes)
        lines = []
        lineValueText = []
        for i in range(numPlots):
            lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
            lineValueText.append(ax.text(0.70, 0.90 - i * 0.05, "", transform=ax.transAxes))
        anim = animation.FuncAnimation(fig,s.getSerialData,fargs=(lines, lineValueText, lineLabel, timeText),interval = pltInterval,frames = nframes,repeat = False)  # Envia as variaveis para plotar o grafico

        plt.legend(loc="upper left")  # Local da legenda no graafico
        plt.show()
        # ----------------------------------------------------------------------

        s.close()  # Para de plotar o grafico
        return render_template('backpage.html')
    app.run()

if __name__ == "__main__":
    main()
# def erro_handler(self,tempo_exposicao="",tempo_recuperacao="",ciclos="",numero_amostragem="",portName="",numPlots="",):
#     if (tempo_exposicao == ""or tempo_recuperacao == ""or ciclos == ""or numero_amostragem == ""or portName == ""or numPlots == "" ):
#         erro = Label(self,text="É preciso completar todos os espaços em branco",fg="black",font=("arial", 10, "bold"),)
#         erro.grid(row=6, column=3)
#         return True
#     else:
#         erro = Label(self,text="Completar todos os espaços em branco",fg="black",font=("arial", 10, "bold"),)
#         erro.grid(row=5, column=3)
#         erro.grid_remove()
#         return False
