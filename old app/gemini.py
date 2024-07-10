import google.generativeai as genai

import secret


def generate_gemini_response(prompt):
    genai.configure(api_key=secret.GEMINI_API_KEY)
    default_prompt = ("You are an helpful assistant that will provide only storage instructions of guitars based on "
                      "their models and cleaning instructions based on their models. The user input will be in the "
                      "format of Guitar Model: {model name}, followed by weather the user wants cleaning instructions "
                      "or storage instructions. also answer in plain text. Remember, this needs to be short and "
                      "concise and within 70 words. If the user wants cleaning instructions, provide only the "
                      "cleaning instructions. If the user wants storage instructions, provide only the storage "
                      "instructions.")

    response = genai.generate_text(prompt=f"{default_prompt} user input: {prompt}")

    return response
