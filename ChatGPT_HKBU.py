import configparser
import requests

class HKBU_ChatGPT:
    def __init__(self, basic_url=None, model_name=None, api_version=None, access_token=None):
        """
        Initialize the ChatGPT wrapper object.

        Parameters:
          basic_url: API base URL, for example "https://api.openai.com/v1"
          model_name: Model name, for example "gpt-4"
          api_version: API version (if needed, to be included in the request)
          access_token: API access key
          
        If all parameters are provided, they will be used directly; 
        otherwise, the configuration will be read from a config.ini file.
        """
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
        """
        Submit a prompt to the ChatGPT API and return the response text.

        Parameters:
          message: The prompt text from the user.

        Returns:
          The ChatGPT response text or an error message for debugging.
        """
        # Build conversation message (one round conversation)
        conversation = [{"role": "user", "content": message}]
        
        # Construct the request URL
        url = (
            f"{self.basic_url}/deployments/{self.model_name}"
            f"/chat/completions/?api-version={self.api_version}"
        )
        
        # Set request headers
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.access_token
        }
        
        # Build the payload
        payload = {'messages': conversation}
        
        # Send the request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Assuming the response format is:
            # { "choices": [ { "message": {"content": "..."} } ], ... }
            return data['choices'][0]['message']['content']
        else:
            # Return error info for debugging
            return f"Error: {response.status_code}", response.text

if __name__ == '__main__':
    # Test entry point: type prompts in the terminal to test the ChatGPT API interface
    chatgpt_test = HKBU_ChatGPT()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = chatgpt_test.submit(user_input)
        print(response)