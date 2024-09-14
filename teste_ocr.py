import os
import cv2
import numpy as np
import subprocess

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

            # Salvar a imagem com o retângulo ao redor do botão "X"
            cv2.imwrite("detected_x_button.png", img)
            return True
        else:
            print("Botão 'X' não encontrado.")
            return False

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return None

# Detecção automática do caminho atual
current_directory = os.getcwd()  # Obtém o diretório atual onde o script está sendo executado
image_filename = "screenshot.png"
template_filename = "x_icon_template.png"  # Seu template de ícone do "X"

# Usando os.path.join para garantir que o caminho esteja correto
image_path = os.path.join(current_directory, image_filename)
template_path = os.path.join(current_directory, template_filename)

# Testando a função de detecção de template
detect_x_button(image_path, template_path)
