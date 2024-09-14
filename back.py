import os
import cv2
import numpy as np
import subprocess
import tkinter as tk
from PIL import Image  # Para manipular imagens
import pytesseract  # Para OCR
import time  # Para adicionar pausas quando necessário

# Função para executar comandos ADB
def adb_command(command):
    subprocess.run(f'adb shell {command}', shell=True)

# Função para aplicar a detecção de template do botão "X"
def detect_x_button(image_path, template_path):
    try:
        # Carregar a imagem e o template em escala de cinza
        img = cv2.imread(image_path, 0)
        template = cv2.imread(template_path, 0)

        # Verifica se a imagem e o template foram carregados corretamente
        if img is None:
            print(f"Erro ao carregar a imagem: {image_path}")
            return
        if template is None:
            print(f"Erro ao carregar o template: {template_path}")
            return

        # Obter as dimensões do template
        w, h = template.shape[::-1]

        # Aplicar correspondência de template
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        
        # Reduzir o threshold para encontrar correspondências menos perfeitas
        threshold = 0.4  # O threshold que funcionou
        loc = np.where(res >= threshold)

        # Verificar se encontrou o botão "X"
        if len(loc[0]) > 0:
            print("Botão 'X' encontrado.")
            for pt in zip(*loc[::-1]):
                # Desenhar um retângulo ao redor da correspondência
                cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

                # Mostrar as coordenadas do centro do botão "X"
                x_centro = pt[0] + w // 2
                y_centro = pt[1] + h // 2
                print(f"Coordenadas encontradas: X={x_centro}, Y={y_centro}")

                # Simular o clique usando ADB
                print("Tentando clicar nas coordenadas...")
                adb_command(f'input tap {x_centro} {y_centro}')
                break

            # Salvar a imagem com o retângulo ao redor do botão "X"
            cv2.imwrite("detected_x_button.png", img)
            return True
        else:
            print("Botão 'X' não encontrado.")
            return False

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return None

# Função para capturar a tela com o nome fixo 'screenshot.png'
def capture_screen():
    filename = "screenshot.png"
    
    adb_command(f'screencap -p /sdcard/{filename}')
    
    check_file = subprocess.run(f'adb shell ls /sdcard/{filename}', shell=True, capture_output=True, text=True)
    
    if "No such file or directory" in check_file.stdout:
        print(f"Erro: O arquivo {filename} não foi encontrado no dispositivo.")
        return False

    result = subprocess.run(f'adb pull /sdcard/{filename} ./{filename}', shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Erro ao transferir o arquivo: {result.stderr}")
        return False
    else:
        if os.path.exists(filename):
            print(f"Arquivo {filename} transferido com sucesso.")
            return True
        else:
            print(f"Erro: O arquivo {filename} não foi encontrado após transferência.")
            return False

# Função para verificar o conteúdo da tela
def verificar_botao_watch_videos():
    filename = "screenshot.png"
    try:
        if not os.path.exists(filename):
            print(f"Erro: Arquivo {filename} não existe no PC.")
            return "error"
        
        img = Image.open(filename)
        text = pytesseract.image_to_string(img)
        
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Arquivo {filename} excluído após verificação.")
        
        if "see other tasks" in text.lower():
            return "see_other_tasks"
        elif "recaptcha" in text.lower() or "não sou um robô" in text.lower():
            return "recaptcha"
        elif "watch videos" in text.lower():
            return "watch_videos"
        else:
            return "not_found"
    except Exception as e:
        print(f"Erro ao abrir a imagem: {e}")
        return "error"

# Função para tocar em uma coordenada específica
def tap_screen(x, y):
    adb_command(f'input tap {x} {y}')

# Função para simular o botão de voltar
def press_back_button():
    adb_command('input keyevent 4')

# Função para fechar o aplicativo
def fechar_aplicativo(package_name):
    adb_command(f'am force-stop {package_name}')

# Função para iniciar o aplicativo
def iniciar_aplicativo(package_name, activity_name):
    adb_command(f'monkey -p {package_name} -c android.intent.category.LAUNCHER 1')
    time.sleep(15)
    iniciar_aplicativo_videos()

# Função para iniciar o aplicativo e navegar até a seção de vídeos
def iniciar_aplicativo_videos():
    print(f'REINICIANDO APLICATIVO...')
    time.sleep(8)
    tap_screen(209, 155)
    time.sleep(5)
    tap_screen(663, 882)
    print("Aplicativo iniciado e navegação para a seção de vídeos concluída.")

# Função para limpar o cache (apagar dados) do aplicativo
def limpar_cache(package_name):
    adb_command(f'pm clear {package_name}')
    print(f"Cache e dados de {package_name} apagados.")

# Função para reiniciar o aplicativo
def reiniciar_aplicativo():
    fechar_aplicativo("com.zareklamy")
    iniciar_aplicativo("com.zareklamy", "com.zareklamy.MainActivity")

# Função para assistir um anúncio
def assistir_anuncio(anuncio_num):
    capture_screen()
    result = verificar_botao_watch_videos()
    print(f'Resultado da verificação do texto: {result}')
    if result == "watch_videos":
        tap_screen(313, 498)
        print("Aguardando anúncio terminar...")
        time.sleep(70)
        press_back_button()
        time.sleep(5)
        return True
    elif result == "see_other_tasks":
        tap_screen(306, 339)
        time.sleep(2)
        tap_screen(638, 882)
        time.sleep(0.3)
        tap_screen(342, 510)
        time.sleep(10)
        capture_screen()
        result = verificar_botao_watch_videos()
        if result == "see_other_tasks" or result == 'watch_videos':
            print(f'Não iniciou vídeo')
            return False
        else:
            print(f'Parece estar no anuncio, aguardando...')
            time.sleep(60)
            press_back_button()
            time.sleep(5)
            return True
    elif result == "recaptcha":
        print("Recaptcha detectado. Aguardando 30 segundos antes de reiniciar...")
        time.sleep(30)
        reiniciar_aplicativo()
        return False
    else:
        print("Tela não identificada. Tentando novamente...")
        reiniciar_aplicativo()
        return False

# Função para iniciar a execução automática
def execucao_automatica():
    i = 2
    while True:
        print(f"\x1b[33m\n\n------------------------------------------\n\nAssistindo anúncio {i}\x1b[0m")
        status = assistir_anuncio(i)
        time.sleep(5)
        if status:
            i += 1
        print(f"\x1b[33m------------------------------------------\x1b[0m")

def clicar_em_watch():
        tap_screen(313, 498)

# Função para capturar eventos de teclas
def key_event(event):
    key = event.char
    if key == '7':
        clicar_em_watch()

    elif key == '8':  # Adiciona a funcionalidade de buscar e clicar no botão "X"
        clicar_no_botao_x()

    elif key == '9':
        press_back_button()
    elif key == '4':
        tap_screen(369, 347)
    elif key == '5':
        tap_screen(630, 1584)
    elif key == '6':
        execucao_automatica()
    elif key == '1':
        tap_screen(646, 895)
    elif key == '2':
        reiniciar_aplicativo()
    elif key == '3':
        limpar_cache("com.zareklamy")

# Função para clicar no botão "X" na parte superior da tela
def clicar_no_botao_x():
    current_directory = os.getcwd()  # Obtém o diretório atual onde o script está sendo executado
    image_filename = "screenshot.png"
    capture_screen()
    template_filename = "icon_template_x.png"  # Seu template de ícone do "X"

    # Usando os.path.join para garantir que o caminho esteja correto
    image_path = os.path.join(current_directory, image_filename)
    template_path = os.path.join(current_directory, template_filename)

    # Testando a função de detecção de template
    detect_x_button(image_path, template_path)

# Função para criar a interface gráfica do teclado numérico
def create_gui():
    root = tk.Tk()
    root.title("Teclado Numérico - Controle ADB")
    root.geometry("400x200")
    root.attributes('-topmost', True)

    root.bind("<Key>", key_event)  # Vincula os eventos de teclado

    tk.Button(root, text="7 - Watch Videos", command=lambda: clicar_em_watch(), width=15, height=2).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(root, text="8 - Fechar (X)", command=clicar_no_botao_x, width=15, height=2).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="9 - Voltar (←)", command=press_back_button, width=15, height=2).grid(row=0, column=2, padx=5, pady=5)

    tk.Button(root, text="4 - See others tasks", command=lambda: tap_screen(369, 347), width=15, height=2).grid(row=1, column=0, padx=5, pady=5)
    tk.Button(root, text="5 - Fechar Horizontal", command=lambda: tap_screen(630, 1584), width=15, height=2).grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="6 - Automático", command=execucao_automatica, width=15, height=2).grid(row=1, column=2, padx=5, pady=5)

    tk.Button(root, text="1 - Earn Videos", command=lambda: tap_screen(646, 895), width=15, height=2).grid(row=2, column=0, padx=5, pady=5)
    tk.Button(root, text="2 - Reiniciar App", command=reiniciar_aplicativo, width=15, height=2).grid(row=2, column=1, padx=5, pady=5)
    tk.Button(root, text="3 - Limpar Cachê", command=lambda: limpar_cache("com.zareklamy"), width=15, height=2).grid(row=2, column=2, padx=5, pady=5)

    root.mainloop()

# Executar a interface gráfica
if __name__ == "__main__":
    create_gui()
