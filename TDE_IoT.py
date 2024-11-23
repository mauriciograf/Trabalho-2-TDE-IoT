import paho.mqtt.client as mqtt
import requests
import json
import random
import time

# Configurações do Mosquitto
LOCAL_BROKER = "localhost"
LOCAL_PORT = 1884
LOCAL_TOPIC = "sensor1/temperature"

# Configurações do Tago.io
DEVICE_TOKEN = "2918dc61-0856-420a-9c14-c418a2fe87de"
TAGO_URL = "https://api.tago.io/data"

# Função para gerar dados simulados aleatórios
def generate_random_data():
	temperature = round(random.uniform(-8, 43), 2)  # Temperatura fora da realidade: -8°C a 43°C
	humidity = round(random.uniform(-2, 110), 2)  	# Umidade irrealista: -2% a 110%
	noise = round(random.uniform(-10, 110), 2)    	# Ruído irrealista: -10 dB a 110 dB
	light = round(random.uniform(0, 1200), 2)     	# Luz irrealista: 0 a 1200 lumens

	return {
    	"temperature": temperature,
    	"humidity": humidity,
    	"noise": noise,
    	"light": light
	}

# Função para verificar outliers
def check_for_outliers(data):
	if data["temperature"] < -5 or data["temperature"] > 40:
    	return False  # Outlier na temperatura

	if data["humidity"] < 0 or data["humidity"] > 100:
    	return False  # Outlier na umidade

	if data["noise"] < 0 or data["noise"] > 100:
    	return False  # Outlier no ruído

	if data["light"] < 0 or data["light"] > 1000:
    	return False  # Outlier na luz

	return True  # Dados válidos (não são outliers)

# Função para enviar os dados ao Tago.io via HTTP
def send_data_to_tago(data):
	payload = [
    	{"variable": "temperature", "value": data["temperature"]},
    	{"variable": "humidity", "value": data["humidity"]},
    	{"variable": "noise", "value": data["noise"]},
    	{"variable": "light", "value": data["light"]}
	]
    
	headers = {
    	"Content-Type": "application/json",
    	"Authorization": DEVICE_TOKEN
	}

	# Envia os dados ao Tago.io
	response = requests.post(TAGO_URL, headers=headers, json=payload)

	# Verifica a resposta do Tago.io
	if response.status_code == 200 or response.status_code == 202:
    	print(f"Dados enviados ao Tago.io com sucesso: {payload}")
	else:
    	print(f"Erro ao enviar dados: {response.status_code} - {response.text}")

# Main
def main():
	client = mqtt.Client()
	client.connect(LOCAL_BROKER, LOCAL_PORT, 60)
	client.subscribe(LOCAL_TOPIC)

	client.loop_start()

	try:
    	while True:
        	# Gerar dados aleatórios
        	data = generate_random_data()
        	print(f"Gerando dados aleatórios: {data}")

        	# Verificar se os dados são outliers
        	if check_for_outliers(data):
            	# Enviar dados válidos ao Tago.io
            	send_data_to_tago(data)
        	else:
            	print(f"Outlier detectado, dados não enviados: {data}")

        	# Aguarda 5 segundos antes de gerar e enviar novamente
        	time.sleep(5)

	except KeyboardInterrupt:
    	print("Interrompendo o script...")
    	client.loop_stop()
    	client.disconnect()

if __name__ == "__main__":
	main()
