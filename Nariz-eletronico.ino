#define reset_timer() ticks = millis()
#define get_timer() (millis() - ticks)

#define VALVULA_OPEN 12
#define VALVULA_CLOSE 13
#define OPEN 1
#define CLOSE 0
#define SENSOR_QUANTITY 9

#define FASTADC 1

// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif
// Declaracao das variaveis
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
static uint32_t ticks = 0;
static uint32_t time_liberacao_ms = 0;    // Tempo de liberacao recebido pelo terminal
static uint32_t time_recuperacao_ms = 0;  // Tempo de recuperacao recebido pelo terminal
static uint32_t time_liberacao = 0;       // Tempo de liberacao recebido pelo terminal
static uint32_t time_recuperacao = 0;     // Tempo de recuperacao recebido pelo terminal
static uint32_t ciclos = 0;               // Numero de ciclos recebido pelo terminal
int count = 0;                            // Contagem de ciclos
int option = 0;
bool start = false;

int desativado[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};

float sensor_value[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};

float pinSensor[9] = {A1, A2, A3, A4, A5, A6, A7, A8, A9};  // Pino do sensor de gas

float sensor_voltage_value[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};  // Valor do sensor em Volts

float ppm_value[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};  // Valor da leitura do sensor de gas em PPM

bool libera = true;          // Verdadeiro se estiver liberando gas e false se estiver nao estiver liberando gas
bool recupera = false;       //
bool start_command = false;  // Verdadeiro se comecar a leitura do sensor

//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// Seta os pinos e a leitura serial
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
void setup() {
    // set prescale to 16
    sbi(ADCSRA, ADPS2);
    cbi(ADCSRA, ADPS1);
    cbi(ADCSRA, ADPS0);

    Serial.begin(115200);                // Baund Rate da leitura serial
    pinMode(12, OUTPUT);                 // Seta o pino 12 como output
    pinMode(13, OUTPUT);                 // Seta o pino 13 como output
    digitalWrite(VALVULA_CLOSE, CLOSE);  // OPEN expondo CLOSE recuperacao
    digitalWrite(VALVULA_OPEN, OPEN);    // OPEN recuperacao CLOSE exposicao
}
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// Comeca o loop da funcao principal
//------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
void loop() {
    if (Serial.available()) {  // Caso a serial estiver diponivel chamar a funcao `parse_serial()
        parse_serial();
    }

    if (start_command) {  // Entra no `if` caso o `start_command` for `True`
        reset_timer();    // Reseta o timer
        if (option == 1) {
            time_recuperacao = time_recuperacao_ms;
            time_liberacao = time_liberacao_ms;
        } else if (option == 2) {
            time_recuperacao = time_recuperacao_ms * 1000;
            time_liberacao = time_liberacao_ms * 1000;
        }

        while (ciclos >= count) {  // Inicia os ciclos de liberacao e recuperacao de gas
          if(get_timer() > 10000 || start == true ){
            start == true;
            if (get_timer() > time_recuperacao && libera) {
                liberacao();     // Chama a funcao liberacao
                libera = false;  // Fecha a valvula de liberacao do gas
                recupera = true;
                reset_timer();  // Reseta o timer
            }
            if (get_timer() > time_liberacao && recupera) {
                recuperacao();     // Chama a funcao recuperacao
                recupera = false;  // Abre a valvula para a liberacao de gas
                libera = true;
                count++;        // Aumenta a contagem de ciclos em 1
                reset_timer();  // Reseta o timer
            }
          }

            for (int count_sensors = 0; count_sensors < SENSOR_QUANTITY; count_sensors++) {
                // Leitura analogica do sensor de gas
                sensor_value[count_sensors] = analogRead(pinSensor[count_sensors]);

                // Conversao da leitura analogica para Volts
                sensor_voltage_value[count_sensors] = (sensor_value[count_sensors] / 1024) * 5.0;

                // Regra de tres para conversao da leitura em Volts para PPM
                ppm_value[count_sensors] = map((sensor_voltage_value[count_sensors] * 100), 0, 500, 200, 1000);
            }

            sendToPython(ppm_value, desativado);  // Envia o valor em PPM para a funcao `sendToPython`
        }
    }
}
//----------------------------------------------------------------------------------------------------------------

// Funcoes
//---------------------------------------------------------------------------------------------------------------
// Recebe o valor em `data` e converte este valor em binario
void sendToPython(float data[SENSOR_QUANTITY], int desativados[SENSOR_QUANTITY]) {  // Adicionar mais sensores  `double* data2`
    typedef union data_to_be_sent {
      float float_data;
      uint8_t byte_data[4];
    } data_to_be_sent_t;

    data_to_be_sent_t aux_data[SENSOR_QUANTITY];

    for (int i = 0; i < SENSOR_QUANTITY; i++) {
      aux_data[i].float_data = data[i];
    }

    int sensor = 0;
    int bytenumber = 0;
    uint8_t buf[SENSOR_QUANTITY*4];

    for (int i = 0; i < SENSOR_QUANTITY; i++) {
        for (int j = 0; j < 4; j++) {
            buf[i*4 + j] = aux_data[i].byte_data[j];
        }
    }

    Serial.write(buf, SENSOR_QUANTITY*4);  // Buffer de x = 4(bytes) * Numero de sensores
}

// Recebe os dados do Python
void parse_serial() {
    if (Serial.available() < 11) {  // Verifica se o valor e menor que 11 caracteres
        return;
    }

    String command = Serial.readStringUntil('\n');  // Faz a leitura seria recebida do Python
    command.trim();

    uint32_t value =
        command.substring(4, 9).toInt();  // Armazena em value a substring entre 4,9 do valor recebido do python

    switch (command[2]) {  // Casos variados da string na posicao 2
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

        case 'o': {
            option = value;
            break;
        }

        // case 'd': {
        //     desativado[0] = value;
        //     break;
        // }

        case 's': {
            start_command = true;  // Inicia a leitura PPM no loop principal
            break;
        }
    }
}

// Funcao para a liberacao de gas
void liberacao() {
    digitalWrite(VALVULA_OPEN, CLOSE);
    digitalWrite(VALVULA_CLOSE, OPEN);
}

// Funcao para a recuperacao
void recuperacao() {
    digitalWrite(VALVULA_OPEN, OPEN);
    digitalWrite(VALVULA_CLOSE, CLOSE);
}
//---------------------------------------------------------------------------------------------------------------
