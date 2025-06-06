# Detector de Gestos em Baixa Luminosidade

Este projeto implementa um sistema de **detecção de gestos em ambiente pouco iluminado** usando Python e MediaPipe. O objetivo é permitir que, em cenários de falta de energia (apagão), um usuário em ambiente escuro possa sinalizar gestos (por exemplo, “mão levantada” ou “punho fechado”) para enviar um alerta automático a um servidor.

## Integrantes
- Henrique Pontes Olliveira – RM 98036  
- Rafael Carvalho Mattos – RM 99874  
- Rafael Autieri Dos Anjos – RM 550885  

---

## Estrutura de Pastas


python_mediapipe_alert/
├─ gesture_detector.py        # Script principal
├─ requirements.txt           # Dependências Python
├─ test_videos/               # Vídeos de teste em baixa luminosidade
│    ├─ escuro_mao_levantada.mp4
│    └─ escuro_punho_fechado.mp4
├─ alert_log.txt              # Arquivo de log gerado em tempo de execução (gitignore)
└─ .gitignore                 # Ignora venv/, __pycache__/ e alert_log.txt


---

## Funcionalidades

1. **Ajuste de Baixa Luminosidade**  
   - Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) via OpenCV para realçar contraste e brilho em vídeos escuros.

2. **Detecção de Gestos**  
   - **Mão Levantada**: pontas dos dedos (landmarks 8, 12, 16, 20) acima do pulso (landmark 0).  
   - **Punho Fechado**: pontas dos dedos abaixo (ou muito próximas) do pulso.

3. **Geração de Alerta Sonoro**  
   - Se `playsound` estiver instalado e um arquivo `alert.mp3` existir, toca esse arquivo.  
   - Caso contrário, emite um beep simples no console.

4. **Envio de Alerta HTTP**  
   - POST JSON para `URL_ALERTA` (por padrão `http://localhost:6000/alerta/`).  
   - JSON enviado:
   
     {{
       "origem": "Camera_MediaPipe",
       "mensagem": "<TIPO_DE_GESTO> detectado",
       "gravidade": "Alta" ou "Normal"
     }}
 
   - Timeout de 5 segundos e tratamento de exceções em caso de falha de conexão ou status diferente de 200.

5. **Registro de Logs em Arquivo (`alert_log.txt`)**  
   - Cada alerta bem-sucedido grava uma linha no formato:
   
     YYYY-MM-DD HH:MM:SS | <TIPO_DE_GESTO> | <DESCRIÇÃO_DO_GESTO>
   

6. **Modo “Webcam” ou “Vídeo de Teste”**  
   - Permite ler de câmera ao vivo (índice configurável) ou processar um arquivo de vídeo de teste em `test_videos/`.

7. **Tratamento de Erros Robusto**  
   - Verifica se a câmera ou vídeo está acessível.  
   - Captura exceções do MediaPipe e do módulo HTTP.  
   - Notifica no console em caso de falhas.

---

## Pré-requisitos

- **Python 3.8+ (até 3.9)**  
- **pip** (gerenciador de pacotes)  

---

## Instalação

1. Clone este repositório  
 
  git clone https://github.com/rcm2005/SistemaHospitalar_MediaPipe.git
  cd python_mediapipe_alert



2. Instale dependências  
   ```bash
   pip install -r requirements.txt
   ```

---

## Como Executar

### 1. Modo Webcam (captura ao vivo)

python gesture_detector.py --camera 0

- `--camera` define o índice da webcam (padrão 0).

### 2. Modo Vídeo de Teste (arquivo MP4)

python gesture_detector.py --video test_videos/escuro_mao_levantada.mp4

- `--video` aponta para qualquer arquivo de vídeo em `test_videos/`.

### 3. Ajustar Delay entre Alertas

python gesture_detector.py --camera 0 --delay 15

- `--delay` define o intervalo mínimo (em segundos) entre alertas consecutivos (padrão 30).

---

## Configurações Importantes

- **URL_ALERTA** (no início de `gesture_detector.py`):  
  Atualize para o endereço do servidor de alertas (por exemplo, `http://192.168.15.13:5000/alerta/` ou `http://<IP_DO_SERVIDOR>:6000/alerta/`).

- **LOG_FILE**:  
  Arquivo onde os logs são gravados (`alert_log.txt`).  
  Será criado automaticamente na execução.

- **alert.mp3**:  
  Caso queira tocar um som específico, coloque um arquivo `alert.mp3` na mesma pasta do script.  
  Se não existir, o script emitirá um beep simples no console.

---

## Exemplos

- Usando cURL para simular alerta HTTP:

  curl -X POST http://localhost:6000/alerta/        -H "Content-Type: application/json"        -d '{{"origem":"TesteCURL","mensagem":"GestureSimulado","gravidade":"Alta"}}'


- Exibir conteúdo de `alert_log.txt`:

  cat alert_log.txt


---

## Vídeo Demonstrativo (YouTube)



---

## Observações

- Em ambientes muito escuros, a performance do MediaPipe pode diminuir.  
  Ajuste iluminação conforme necessário.  
- Se `playsound` não estiver instalado ou `alert.mp3` faltar, o script ainda funciona corretamente (beep de fallback).  
- O ESP32/Raspberry Pi pode capturar imagens e enviar JSON a este script—  
  mas isso é opcional e não documentado aqui; será apenas demonstrado no vídeo.
