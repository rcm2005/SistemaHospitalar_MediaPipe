import argparse
import cv2
import mediapipe as mp
import numpy as np
import requests
import time
import os
import sys

URL_ALERTA = "http://localhost:6000/alerta/"
LOG_FILE = "alert_log.txt"
DELAY_SEGUNDOS = 30

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def ajustar_low_light(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)
    processed = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
    return processed

def is_punho_fechado(landmarks) -> bool:
    wrist_y = landmarks[0].y
    tip_ids = [8, 12, 16, 20]
    return all(landmarks[i].y > wrist_y - 0.02 for i in tip_ids)

def is_mao_levantada(landmarks) -> bool:
    wrist_y = landmarks[0].y
    tip_ids = [8, 12, 16, 20]
    return all(landmarks[i].y < wrist_y - 0.05 for i in tip_ids)

def emitir_som_alerta():
    # Emite beep simples no console
    print('\a', end='', flush=True)

def registrar_log(tipo: str, descricao: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    linha = f"{timestamp} | {tipo.upper()} | {descricao}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)

def enviar_alerta_servidor(payload: dict) -> bool:
    try:
        response = requests.post(URL_ALERTA, json=payload, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"[ERRO] Servidor retornou código {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERRO] Falha ao enviar alerta ao servidor: {e}")
        return False

def processar_fluxo(video_source):
    cap = None
    try:
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise IOError("Não foi possível abrir a fonte de vídeo.")

        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        alerta_enviado = False
        last_alert_time = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[INFO] Fim do vídeo ou falha na leitura da câmera.")
                break

            frame = cv2.flip(frame, 1)
            processed = ajustar_low_light(frame)
            rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)

            try:
                results = hands.process(rgb)
            except Exception as e:
                print(f"[WARN] Falha no MediaPipe.process(): {e}")
                results = None

            alerta_atual = None

            if results and results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    lm = hand_landmarks.landmark

                    if is_mao_levantada(lm):
                        alerta_atual = "MÃO LEVANTADA"
                    elif is_punho_fechado(lm):
                        alerta_atual = "PUNHO FECHADO"

                    if alerta_atual:
                        cv2.putText(
                            frame,
                            f"ALERTA: {alerta_atual}",
                            (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2
                        )

                        agora = time.time()
                        if (not alerta_enviado) or (agora - last_alert_time) >= DELAY_SEGUNDOS:
                            description = f"{alerta_atual} detectado"
                            payload = {
                                "origem": "Camera_MediaPipe",
                                "mensagem": description,
                                "gravidade": "Alta" if alerta_atual == "PUNHO FECHADO" else "Normal"
                            }
                            success = enviar_alerta_servidor(payload)
                            if success:
                                print(f"[ALERTA] Enviado com sucesso: {payload}")
                                emitir_som_alerta()
                                registrar_log(alerta_atual, description)
                                alerta_enviado = True
                                last_alert_time = agora
                            else:
                                print(f"[ERRO] Não foi possível enviar alerta: {payload}")
                    else:
                        alerta_enviado = False

            cv2.putText(frame, "Pressione ESC para sair", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.imshow("Detector de Gestos em Ambiente Escuro", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    except Exception as e:
        print(f"[ERROR] Erro geral no processamento de vídeo: {e}")
    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Detector de Gestos em Baixa Luminosidade")
    parser.add_argument("--video", "-v", help="Caminho para arquivo de vídeo de teste. Se omitido, usa webcam.")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Índice da webcam (padrão 0).")
    parser.add_argument("--delay", "-d", type=int, default=DELAY_SEGUNDOS,
                        help=f"Delay mínimo entre alertas consecutivos em segundos (padrão {DELAY_SEGUNDOS}).")
    args = parser.parse_args()

    global DELAY_SEGUNDOS
    DELAY_SEGUNDOS = args.delay

    if args.video:
        if not os.path.isfile(args.video):
            print(f"[ERROR] Arquivo de vídeo não encontrado: {args.video}")
            sys.exit(1)
        source = args.video
    else:
        source = args.camera

    print(f"[INFO] Iniciando detecção. Fonte: {source}. Delay = {DELAY_SEGUNDOS}s")
    processar_fluxo(source)

if __name__ == "__main__":
    main()
