import subprocess
import time
import os
from PIL import Image
import pytesseract  # Para OCR

# Função para executar comandos ADB
def adb_command(command):
    subprocess.run(f'adb shell {command}', shell=True)

# Função para capturar a tela com o nome fixo 'screenshot.png'
def capture_screen():
    filename = "screenshot.png"
    
    # Captura a tela e salva no diretório acessível do dispositivo
    print("Tentando capturar a tela no dispositivo Android...")
    adb_command(f'screencap -p /sdcard/{filename}')
    
    # Verifica se o arquivo foi salvo corretamente no dispositivo Android
    check_file = subprocess.run(f'adb shell ls /sdcard/{filename}', shell=True, capture_output=True, text=True)
    
    if "No such file or directory" in check_file.stdout:
        print(f"Erro: O arquivo {filename} não foi encontrado no dispositivo.")
        return False

    # Tenta transferir o arquivo para o PC
    print(f"Tentando transferir o arquivo {filename} para o PC...")
    result = subprocess.run(f'adb pull /sdcard/{filename} ./{filename}', shell=True, capture_output=True, text=True)
    
    # Verifica se houve erro ao tentar fazer o pull da imagem
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
        # Realiza OCR na imagem
        text = pytesseract.image_to_string(img)
        
        # print(f"Texto detectado na imagem: {text.strip()}")
        # Excluir o arquivo após o uso
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Arquivo {filename} excluído após verificação.")
        # Verifica se "Watch videos", "See other tasks", ou "Recaptcha" estão no texto
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
    # Passo 1: Clicar no ícone na tela inicial (coordenadas: X=355, Y=146)
    # tap_screen(355, 146)  # Ajuste as coordenadas conforme necessário
    time.sleep(8)  # Aguardar 10 seg8999999999999978

    # Passo 2: Clicar em "Earn" (coordenadas: X=209, Y=155)
    print("Clicando em 'Earn'...")
    tap_screen(209, 155)  # Ajuste as coordenadas conforme necessário
    time.sleep(5)  # Aguardar 5 segundos

    # Passo 3: Clicar em "Videos" (coordenadas: X=663, Y=882)
    print("Clicando em 'Videos'...")
    tap_screen(663, 882)  # Ajuste as coordenadas conforme necessário

    print("Aplicativo iniciado e navegação para a seção de vídeos concluída.")
   

# Função para fechar todos os aplicativos abertos e voltar à tela inicial
def fechar_todos_os_apps():
    print("Fechando todos os aplicativos e voltando para a tela inicial...")
    adb_command('input keyevent 187')  # Abre o menu de aplicativos recentes
    time.sleep(2)
    adb_command('input swipe 360 1200 360 100')  # Fecha todos os apps (ajuste as coordenadas conforme necessário)
    time.sleep(2)

# Função para assistir um anúncio
def assistir_anuncio(anuncio_num):
    # Captura a tela para verificar o estado atual
    capture_screen()
    result = verificar_botao_watch_videos()
    print(f'Resultado da verificação do texto: {result}')
    if result == "watch_videos":
        # Toca no botão 'Assistir'
        print("Tocando no botão assistir...")
        tap_screen(313, 498)  # Ajuste as coordenadas conforme necessário

        # Aguarda o tempo de exibição do anúncio
        print("Aguardando anúncio terminar...")
        time.sleep(70)  # Exemplo de tempo do anúncio em segundos

        # Usa o botão de voltar após o anúncio
        print("Voltando à tela principal...")
        press_back_button()
        time.sleep(5)  # Aguarda a transição para a tela principal
        return True
    elif result == "see_other_tasks":
        print("Mensagem 'See other tasks' detectada. Tentando capturar vídeo...")
        
        # clicar em see_other_tasks
        tap_screen(306, 339)  # Ajuste as coordenadas conforme necessário

        # aguardar 4 segundos
        time.sleep(2)
        
        # clicar em earn (videos)
        print("Acessando vídeos para assistir...")
        tap_screen(638, 882)  # Ajuste as coordenadas conforme necessário
        # aguardar 0,3 segundos
        time.sleep(0.1)
        time.sleep(0.1)
        # tap_screen(638, 882)  # Ajuste as coordenadas conforme necessário
        tap_screen(342, 510)  # Ajuste as coordenadas conforme necessário


        # clicar em watch_videos
        print("Tocando no botão assistir...")
        # aguardar 60 segundos
        time.sleep(10)
        capture_screen()
        result = verificar_botao_watch_videos()
        if result == "see_other_tasks" or result == 'watch_videos':
            print(f'Não iniciou vídeo')
            return False
        else:
            print(f'Parece estar no anuncio, aguardando...')
            time.sleep(60)

            # press_back
            press_back_button()
            print("Voltando à tela principal...")
            time.sleep(5)
            return True



    
    elif result == "recaptcha":
        print("Recaptcha detectado. Aguardando 5 minutos antes de reiniciar...")
        time.sleep(30)  # Aguarda 5 minutos
        fechar_aplicativo("com.zareklamy")
        time.sleep(2)
        iniciar_aplicativo("com.zareklamy", "com.zareklamy.MainActivity")
        return False
    else:
        print("Tela não identificada. Tentando novamente...")
        fechar_aplicativo("com.zareklamy")
        time.sleep(2)
        iniciar_aplicativo("com.zareklamy", "com.zareklamy.MainActivity")
        return False

i=2
# Loop para assistir vários anúncios
while True:
    print(f"\x1b[33m\n\n------------------------------------------\n\nAssistindo anúncio {i}\x1b[0m")
    status = assistir_anuncio(i)
    time.sleep(5)  # Pausa entre os anúncios
    if status: i += 1
    print(f"\x1b[33m------------------------------------------\x1b[0m")
