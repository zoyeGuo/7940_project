import configparser
import requests

class HKBU_ChatGPT:
    def __init__(self, basic_url=None, model_name=None, api_version=None, access_token=None):
        
        if basic_url and model_name and api_version and access_token:
            self.basic_url = basic_url
            self.model_name = model_name
            self.api_version = api_version
            self.access_token = access_token
        else:
            config = configparser.ConfigParser()
            config.read('config.ini')
            self.basic_url = config['CHATGPT']['BASICURL']
            self.model_name = config['CHATGPT']['MODELNAME']
            self.api_version = config['CHATGPT']['APIVERSION']
            self.access_token = config['CHATGPT']['ACCESS_TOKEN']

    def submit(self, message):
       
        # Build conversation message (one round conversation)
        conversation = [{"role": "user", "content": message}]
        
       
        url = (
            f"{self.basic_url}/deployments/{self.model_name}"
            f"/chat/completions/?api-version={self.api_version}"
        )
        
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.access_token
        }
        
        payload = {'messages': conversation}
        
     
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
           
            return data['choices'][0]['message']['content']
        else:
            
            return f"Error: {response.status_code}", response.text

if __name__ == '__main__':
    # Test entry point: type prompts in the terminal to test the ChatGPT API interface
    chatgpt_test = HKBU_ChatGPT()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = chatgpt_test.submit(user_input)
        print(response)