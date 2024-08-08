const int motorPUL = 9;
const int motorDIR = 11;
const int motorENA = 12;
const int fotoDiodo = 15;
const int stepsTo450nm = 150500;
const int moves[] = { 33000, 28500, 21500, 44000, 23500 };
const int Leds[] = { 45, 48, 47, 20, 19 };
int luzIncidente[] = { 205, 205, 205, 205, 205 };
int luzMedida[5];
int intensidadInicial[] = { 255, 174, 146, 110, 49 };  //205
//int intensidadInicial[] = { 95, 48, 40, 46, 24 };  //200
int flag = 0;
const int velocidadBase = 35;

void setup() {
  pinMode(motorPUL, OUTPUT);
  pinMode(motorDIR, OUTPUT);
  pinMode(motorENA, OUTPUT);
  pinMode(fotoDiodo, INPUT);
  for (int x = 0; x < 5; x++) {
    pinMode(Leds[x], OUTPUT);
  }
  Serial.begin(9600);
  delay(1500);
}

int valorRepetido() {
  int lista[20];
  for (int x = 0; x < 20; x++) {
    int valor = analogRead(fotoDiodo);
    valor = 255 - (valor / 16);
    lista[x] = valor;
    //Serial.print(valor);
    //Serial.print(" - ");
    delay(50);
  }
  //Serial.println();
  int elementoMasRepetido;
  int maximoContador = 0;

  for (int i = 0; i < 20; i++) {
    int contador = 1;  // Iniciar el contador para el elemento actual
    for (int j = i + 1; j < 20; j++) {
      if (lista[i] == lista[j]) {
        contador++;
      }
    }
    if (contador > maximoContador) {
      maximoContador = contador;
      elementoMasRepetido = lista[i];
    }
  }
  return elementoMasRepetido;
}
void regresoMotor() {
  for (int i = 0; i < stepsTo450nm; i++) {
    digitalWrite(motorDIR, HIGH);
    digitalWrite(motorPUL, HIGH);
    delayMicroseconds(velocidadBase);
    digitalWrite(motorPUL, LOW);
    delayMicroseconds(velocidadBase);
  }
}
void apagarLeds() {
  for (int x = 0; x < 5; x++) {
    analogWrite(Leds[x], 0);
  }
}
void moverMotor(int flag) {
  for (int x = 0; x < moves[flag]; x++) {
    digitalWrite(motorDIR, LOW);
    digitalWrite(motorPUL, HIGH);
    delayMicroseconds(45);
    digitalWrite(motorPUL, LOW);
    delayMicroseconds(45);
  }
}
void primeraLectura() {
  for (int i = 0; i < 5; i++) {
    analogWrite(Leds[i], intensidadInicial[i]);
    moverMotor(i);
    int dato = valorRepetido();
    delay(500);
    analogWrite(Leds[i], 0);
    luzIncidente[i] = dato;
  }
  apagarLeds();
  regresoMotor();
  for (int x = 0; x < 5; x++) {
    if (luzIncidente[x] >= 204 && luzIncidente[x] <= 206) {
      luzIncidente[x] = 205;
      Serial.println(luzIncidente[x]);
    } else {
      Serial.println(luzIncidente[x]);
    }
  }
}

void medicionSolucion() {
  // Apagado de todos los leds
  apagarLeds();
  // Movimiento del actuador
  for (int i = 0; i < 5; i++) {
    analogWrite(Leds[i], intensidadInicial[i]);
    moverMotor(i);
    delay(250);
    int dato = valorRepetido();
    analogWrite(Leds[i], 0);
    luzMedida[i] = dato;
  }
  apagarLeds();
  regresoMotor();
  absorbancia(luzIncidente, luzMedida);
}

void absorbancia(int* luzIncidente, int* luzMedida) {
  float datosMicro[5];
  for (int i = 0; i < 5; i++) {
    if (luzMedida[i] != 0 && luzIncidente[i] != 0) {
      float transmitancia = (float)luzMedida[i] / luzIncidente[i];
      float absorbancia = -log10(transmitancia);
      datosMicro[i] = absorbancia;
    } else {
      datosMicro[i] = 0;
    }
  }
  for (int i = 0; i < 5; i++) {
    if (datosMicro[i] > 0) {
      Serial.println(datosMicro[i], 3);
      //Serial.print(" - ");
      //Serial.print(luzIncidente[i]);
      //Serial.print(" - ");
      //Serial.print(luzMedida[i]);
      //Serial.println();  // Imprime una nueva línea después de cada valor
    } else {
      Serial.println(0);
    }
  }
}

void loop() {
  char dato = Serial.read();
  if (dato == '2') {
    regresoMotor();
  } else if (dato == '3') {
    medicionSolucion();

  } else if (dato == '4') {
    primeraLectura();
  }
}
