#define reset_timer() ticks = millis()
#define get_timer() (millis() - ticks)

#define VALVULA_OPEN 12
#define VALVULA_CLOSE 13
#define OPEN 1
#define CLOSE 0

#define FASTADC 1

// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif
// Declaracao das variaveis
//----------------------------------------------------------
static uint32_t ticks = 0;
static uint32_t time_liberacao_ms = 0;    // Tempo de liberacao recebido pelo terminal
static uint32_t time_recuperacao_ms = 0;  // Tempo de recuperacao recebido pelo terminal
static uint32_t ciclos = 0;               // Numero de ciclos recebido pelo terminal
int desativado = 0;
int count = 0;                            // Contagem de ciclos

float valor_sensor1 = 0;                   // Valor recebido do sensor
float valor_sensor2 = 0;
float valor_sensor3 = 0;
float valor_sensor4 = 0;
float valor_sensor5 = 0;                   // Valor recebido do sensor
float valor_sensor6 = 0;
float valor_sensor7 = 0;
float valor_sensor8 = 0;
float valor_sensor9 = 0;                   // Valor recebido do sensor


float pinSensor1 = A1;                     // Pino do sensor de gas
float pinSensor2 = A2;
float pinSensor3 = A3;
float pinSensor4 = A4;
float pinSensor5 = A5;
float pinSensor6 = A6;
float pinSensor7 = A7;
float pinSensor8 = A8;
float pinSensor9 = A9;


float valor_sensor_voltage1 = 0.0;         // Valor do sensor em Volts
float valor_sensor_voltage2 = 0.0;
float valor_sensor_voltage3 = 0.0;
float valor_sensor_voltage4 = 0.0;
float valor_sensor_voltage5 = 0.0;
float valor_sensor_voltage6 = 0.0;
float valor_sensor_voltage7 = 0.0;
float valor_sensor_voltage8 = 0.0;
float valor_sensor_voltage9 = 0.0;

bool libera = true;                       // Verdadeiro se estiver liberando gas e false se estiver nao estiver liberando gas
bool recupera = false;                    // 
bool start_command = false;               // Verdadeiro se comecar a leitura do sensor

float valor_ppm1 = 0;                     // Valor da leitura do sensor de gas em PPM
float valor_ppm2 = 0;
float valor_ppm3 = 0;
float valor_ppm4 = 0;
float valor_ppm5 = 0;
float valor_ppm6 = 0;
float valor_ppm7 = 0;
float valor_ppm8 = 0;
float valor_ppm9 = 0;

//----------------------------------------------------------

// Seta os pinos e a leitura serial
//--------------------------------------------------------------------------------------
void setup() {
  // set prescale to 16
  sbi(ADCSRA,ADPS2) ;
  cbi(ADCSRA,ADPS1) ;
  cbi(ADCSRA,ADPS0) ;

  Serial.begin(115200);                    // Baund Rate da leitura serial
  pinMode(12, OUTPUT);                   // Seta o pino 12 como output
  pinMode(13, OUTPUT);                   // Seta o pino 13 como output
  digitalWrite(VALVULA_CLOSE, OPEN);    // Comeca com a valvula do pino 12 fechada
  digitalWrite(VALVULA_OPEN, CLOSE);      // Comeca com a valvula do pino 13 aberta
}
//--------------------------------------------------------------------------------------

// Comeca o loop da funcao principal
//----------------------------------------------------------------------------------------------------------------
void loop() {
  if (Serial.available()) {                                                    // Caso a serial estiver diponivel chamar a funcao `parse_serial()
      parse_serial();
  }

  if(start_command){                                                           // Entra no `if` caso o `start_command` for `True`
      reset_timer();                                                           // Reseta o timer     
      while ( ciclos >= count ) {                                               // Inicia os ciclos de liberacao e recuperacao de gas
        if(get_timer() > time_liberacao_ms*1000 && libera){
            liberacao();                                                       // Chama a funcao liberacao
            libera = false;                                                    // Fecha a valvula de liberacao do gas
            recupera = true;              
            reset_timer();                                                     // Reseta o timer
          }
          if(get_timer() > time_recuperacao_ms*1000 && recupera){
            recuperacao();                                                     // Chama a funcao recuperacao
            recupera = false;                                                  // Abre a valvula para a liberacao de gas
            libera = true;
            count++;                                                           // Aumenta a contagem de ciclos em 1
            reset_timer();                                                     // Reseta o timer
          }
        
        valor_sensor1 = analogRead(pinSensor1);                                  // Leitura analogica do sensor de gas
        valor_sensor_voltage1 = valor_sensor1 / 1024 * 5.0;                      // Conversao da leitura analogica para Volts
        valor_ppm1 = map(valor_sensor_voltage1 * 100, 0, 500, 200, 1000);        // Regra de tres para conversao da leitura em Volts para PPM
       
        valor_sensor2 = analogRead(pinSensor2);                                 
        valor_sensor_voltage2 = valor_sensor2 / 1024 * 5.0;                      
        valor_ppm2 = map(valor_sensor_voltage2 * 100, 0, 500, 200, 1000);        

        valor_sensor3 = analogRead(pinSensor3);
        valor_sensor_voltage3 = valor_sensor3 / 1024 * 5.0;                      
        valor_ppm3 = map(valor_sensor_voltage3 * 100, 0, 500, 200, 1000);  
        
        valor_sensor4 = analogRead(pinSensor4);
        valor_sensor_voltage4 = valor_sensor4 / 1024 * 5.0;                      
        valor_ppm4 = map(valor_sensor_voltage4 * 100, 0, 500, 200, 1000);          

        valor_sensor5 = analogRead(pinSensor5);
        valor_sensor_voltage5 = valor_sensor5 / 1024 * 5.0;                      
        valor_ppm5 = map(valor_sensor_voltage5 * 100, 0, 500, 200, 1000);   

        valor_sensor6 = analogRead(pinSensor6);
        valor_sensor_voltage6 = valor_sensor6 / 1024 * 5.0;                      
        valor_ppm6 = map(valor_sensor_voltage6 * 100, 0, 500, 200, 1000);

        valor_sensor7 = analogRead(pinSensor7);
        valor_sensor_voltage7 = valor_sensor7 / 1024 * 5.0;                      
        valor_ppm7 = map(valor_sensor_voltage7 * 100, 0, 500, 200, 1000);  
        
        valor_sensor8 = analogRead(pinSensor8);
        valor_sensor_voltage8 = valor_sensor8 / 1024 * 5.0;                      
        valor_ppm8 = map(valor_sensor_voltage8 * 100, 0, 500, 200, 1000);          

        valor_sensor9 = analogRead(pinSensor9);
        valor_sensor_voltage9 = valor_sensor9 / 1024 * 5.0;                      
        valor_ppm9 = map(valor_sensor_voltage9 * 100, 0, 500, 200, 1000);   

  

        sendToPython(&valor_ppm1,&valor_ppm2,&valor_ppm3,&valor_ppm4,&valor_ppm5,&valor_ppm6,&valor_ppm7,&valor_ppm8,&valor_ppm9,desativado);                       // Envia o valor em PPM para a funcao `sendToPython`
    
    }   
  }
}
//----------------------------------------------------------------------------------------------------------------


// Funcoes 
//---------------------------------------------------------------------------------------------------------------
// Recebe o valor em `data` e converte este valor em binario
void sendToPython(float* data1,float* data2,float* data3,float* data4,float* data5,float* data6,float* data7,float* data8,float* data9,float desativado){ // Adicionar mais sensores  `double* data2`               
  byte* byteData1 = (byte*)(data1);       // Sensor 1
  byte* byteData2 = (byte*)(data2);       // Sensor 1
  byte* byteData3 = (byte*)(data3);       // Sensor 1
  byte* byteData4 = (byte*)(data4);       // Sensor 1
  byte* byteData5 = (byte*)(data5);       // Sensor 1
  byte* byteData6 = (byte*)(data6);       // Sensor 1
  byte* byteData7 = (byte*)(data7);       // Sensor 1
  byte* byteData8 = (byte*)(data8);       // Sensor 1
  byte* byteData9 = (byte*)(data9);       // Sensor 1
  int sensor = 0;
  int bytenumber = 0; 
  
  while(sensor != 10){
    if(desativado == sensor){
         if(desativado == 1){
            while(bytenumber != 4){
              byteData1[bytenumber] = 0;
              bytenumber ++;           
            }
           }else if (desativado == 2){
            while(bytenumber != 4){
              byteData2[bytenumber] = 0;
              bytenumber ++;           
            }
          }else if(sensor == 3){
            while(bytenumber != 4){
              byteData3[bytenumber] = 0;
              bytenumber ++;           
            }
           }else if(sensor == 4){
            while(bytenumber != 4){
              byteData4[bytenumber] = 0;
              bytenumber ++;           
            }
           }else if(sensor == 5){
            while(bytenumber != 4){
              byteData5[bytenumber] = 0;
              bytenumber ++;           
            }
           }else if(sensor == 6){
            while(bytenumber != 4){
              byteData6[bytenumber] = 0;
              bytenumber ++;           
            }
          }else if(sensor == 7){
            while(bytenumber != 4){
              byteData7[bytenumber] = 0;
              bytenumber ++;           
            }
          }else if(sensor == 8){
            while(bytenumber != 4){
              byteData8[bytenumber] = 0;
              bytenumber ++;           
            }
          }else if(sensor == 9){
            while(bytenumber != 4){
              byteData9[bytenumber] = 0;
              bytenumber ++;           
            }
          }
      }
    sensor++;
   }

  

  byte buf[36] = {byteData1[0], byteData1[1], byteData1[2], byteData1[3],
                  byteData2[0], byteData2[1], byteData2[2], byteData2[3],
                  byteData3[0], byteData3[1], byteData3[2], byteData3[3],
                  byteData4[0], byteData4[1], byteData4[2], byteData4[3],
                  byteData5[0], byteData5[1], byteData5[2], byteData5[3],
                  byteData6[0], byteData6[1], byteData6[2], byteData6[3],
                  byteData7[0], byteData7[1], byteData7[2], byteData7[3],
                  byteData8[0], byteData8[1], byteData8[2], byteData8[3],
                  byteData9[0], byteData9[1], byteData9[2], byteData9[3]};
//
  Serial.write(buf, 36);      // Buffer de x = 4(bytes) * Numero de sensores
}

// Recebe os dados do Python
void parse_serial(){  
  if (Serial.available() < 11) {                        // Verifica se o valor e menor que 11 caracteres
    return;
  }
  
  String command = Serial.readStringUntil('\n');        // Faz a leitura seria recebida do Python
  command.trim();                                 
  
  uint32_t value = command.substring(4, 9).toInt();     // Armazena em value a substring entre 4,9 do valor recebido do python

  switch (command[2]) {                                 // Casos variados da string na posicao 2
    case 'l': {
      time_liberacao_ms = value;                
      break;
    }

    case 'r': {
      time_recuperacao_ms = value;
      break;
    }

    case 'c': {
      ciclos = value;
      break;
    }

    case 'n': {
      desativado = value;
      break;
    }
  
    case 's': {
      start_command = true;                           // Inicia a leitura PPM no loop principal
      break;
    }
  }
}

// Funcao para a liberacao de gas
void liberacao() {  
  digitalWrite(VALVULA_OPEN, OPEN);
  digitalWrite(VALVULA_CLOSE, CLOSE);
}

// Funcao para a recuperacao
void recuperacao() {
  digitalWrite(VALVULA_OPEN, CLOSE);
  digitalWrite(VALVULA_CLOSE, OPEN);
}
//---------------------------------------------------------------------------------------------------------------
