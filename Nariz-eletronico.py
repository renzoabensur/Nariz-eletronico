from tkinter import *
import tkinter as tk
import time  # importa biblioteca Time
import matplotlib.pyplot as plt  # importa biblioteca matplotlib
import matplotlib.animation as animation
import mypackage.Serial_acquire as serial_acquire

plt.style.use("seaborn-ticks")

def main():
    # Codigo do usuario
    # ------------------
    baudRate = 115200 # BaundRate do codigo em arduino
    dataNumBytes = 4  # Number de bytes de 1 ponto de dado
    # ------------------

    # Entaradas do usuario sao armazenadas nas variaveis tempo_exposicao, tempo_recuperacao e ciclos
    # --------------------------------------------------
    class GUI_interface(Frame):
        def __init__(self, master):
            Frame.__init__(self, master)
            self.grid()
            self.create_widgets()

        def create_widgets(self):
            self.option = tk.IntVar()
            self.instruction = Label(self,text="Qual porta:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=0, column=0)

            self.instruction = Label(self,text="Expressar tempo em:",fg="black",font=("arial", 10, "bold"),padx=30,pady=10,bd=1,)
            self.instruction.grid(row=1, column=0)

            self.instruction = Radiobutton(self,text="Segundos",padx = 5,variable= self.option,value = 1)
            self.instruction.grid(row=1, column=1)

            self.instruction = Radiobutton(self,text="Milisegundos",padx = 5,variable= self.option,value = 2)
            self.instruction.grid(row=1, column=2)

            self.instruction = Label(self,text="Tempo exposição (s):",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=2, column=0)

            self.instruction = Label(self,text="Tempo recuperção (s):",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=3, column=0)

            self.instruction = Label(self,text="Numero de ciclos:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=4, column=0)

            self.instruction = Label(self,text="Numero de leituras/ciclo:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=5, column=0)

            # self.instruction = Label(self,text="Sensores desativados:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            # self.instruction.grid(row=6, column=0)

            self.instruction = Label(self,text="Nome do arquivo txt:",fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=6, column=0)

            self.portName = Entry(self)
            self.portName.grid(row=0, column=1, sticky=W)

            self.Tempo_exposicao = Entry(self)
            self.Tempo_exposicao.grid(row=2, column=1, sticky=W)

            self.Tempo_recuperacao = Entry(self)
            self.Tempo_recuperacao.grid(row=3, column=1, sticky=W)

            self.ciclos = Entry(self)
            self.ciclos.grid(row=4, column=1, sticky=W)

            self.numero_amostragem = Entry(self)
            self.numero_amostragem.grid(row=5, column=1, sticky=W)

            # self.sensores_desativados = Entry(self)
            # self.sensores_desativados.grid(row=6, column=1, sticky=W)

            self.filename = Entry(self)
            self.filename.grid(row=6, column=1, sticky=W)

            self.simulation_button = Button(self,text="Tempo total",command=self.simulation,fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.simulation_button.grid(row=7, column=2, sticky=W)

            self.start_button = Button(self,text="Start",command=self.start,fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.start_button.grid(row=7, column=1, sticky=W)

        def simulation(self):
            tempo_exposicao = self.Tempo_exposicao.get()
            tempo_recuperacao = self.Tempo_recuperacao.get()
            ciclos = self.ciclos.get()
            numero_amostragem = self.numero_amostragem.get()
            portName = self.portName.get()
            filename = self.filename.get()
            # sensores_desativados = self.sensores_desativados.get()
            numPlots = 9
            option = self.option.get()

            # if (erro_handler(self,tempo_exposicao,tempo_recuperacao,ciclos,numero_amostragem,portName,)== False):
            tempo_exposicao = int(tempo_exposicao)
            tempo_recuperacao = int(tempo_recuperacao)
            ciclos = int(ciclos)
            numero_amostragem = int(numero_amostragem)
            tempo_total = (tempo_exposicao + tempo_recuperacao) * ciclos
            maxPlotLength = int(((tempo_exposicao + tempo_recuperacao) * ciclos) + 1)  # Maximo valor do eixo x do grafico (tempo) em segundos
            day = tempo_total//86400
            hour = tempo_total%86400//3600
            minutes = ((tempo_total%86400)%3600)//60
            seconds = (((tempo_total%86400)%3600)%60)
            self.instruction = Label(self,text= "Tempo total do ensaio: %d:%d:%d:%d s" % (day, hour, minutes, seconds) ,fg="black",font=("arial", 10, "bold"),padx=50,pady=10,bd=1,)
            self.instruction.grid(row=6, column=3)

        def start(self):
            tempo_exposicao = self.Tempo_exposicao.get()
            tempo_recuperacao = self.Tempo_recuperacao.get()
            ciclos = self.ciclos.get()
            numero_amostragem = self.numero_amostragem.get()
            portName = self.portName.get()
            filename = self.filename.get()
            # sensores_desativados = self.sensores_desativados.get()
            numPlots = 9
            option = self.option.get()

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
                filename,option,)

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

    root = Tk()
    root.title("IC")
    root.geometry("1100x400")
    app = GUI_interface(root)

    root.mainloop()

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
