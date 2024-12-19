import os
import json
import requests
import tkinter as tk
from tkinter import simpledialog, scrolledtext

class ChatInterface(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Gemini Chat Interface")

        # Store messages as a list of objects with a content field
        # Example: self.messages = [{'content': 'User message here'}, {'content': 'Bot response'}]
        self.messages = []

        self.api_key = self.get_api_key()
        self.is_processing = False

        # UI Elements
        self.chat_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='disabled', width=80, height=20)
        self.chat_display.pack(pady=10)

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.user_input = tk.Entry(self.input_frame)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.on_send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.on_send_button_click)
        self.send_button.pack(side=tk.LEFT, padx=5)

        self.pack()

    def add_message(self, text, is_user=True):
        self.chat_display.config(state='normal')
        if is_user:
            self.chat_display.insert(tk.END, "You: " + text + "\n")
        else:
            self.chat_display.insert(tk.END, "Bot: " + text + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def on_send_button_click(self):
        message = self.user_input.get().strip()
        if message and not self.is_processing:
            self.user_input.delete(0, tk.END)
            self.messages.append({'content': message})
            self.add_message(message, True)
            self.is_processing = True
            self.process_message(message)

    def on_send_message(self, event):
        self.on_send_button_click()

    def get_api_key(self):
        # Try to get the API key from an environment variable
        api_key = os.environ.get('AIzaSyCmxB7HokQPL9f6O7vhpxqtMMtSaMl4WeA')
        if not api_key:
            # If not found, ask the user
            api_key = simpledialog.askstring(
                "API Key Required",
                "Please enter your Gemini API key:",
                show='*'
            )
            if api_key:
                # Save the key for future use (in a real app, use a secure method)
                os.environ['GEMINI_API_KEY'] = api_key
        return api_key

    def process_message(self, message):
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            data = {
                "contents": [{"parts": [{"text": msg['content']} for msg in self.messages]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 2048
                }
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            if 'candidates' in result and len(result['candidates']) > 0:
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                self.messages.append({'content': response_text})
                self.master.after(0, self.add_message, response_text, False)
            else:
                self.master.after(0, self.add_message, "No response from the model.", False)

        except requests.exceptions.RequestException as e:
            error_message = f"Network error: {str(e)}"
            self.master.after(0, self.add_message, error_message, False)
        except json.JSONDecodeError:
            error_message = "Error decoding API response"
            self.master.after(0, self.add_message, error_message, False)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            self.master.after(0, self.add_message, error_message, False)
        finally:
            self.is_processing = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatInterface(master=root)
    app.mainloop()
     
