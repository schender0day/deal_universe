import os
import re
import imgkit
from PIL import Image
import openai
from bs4 import BeautifulSoup
# config = imgkit.config(wkhtmltoimage='/usr/local/bin/wkhtmltoimage', quiet=True)
from google.cloud import translate_v2 as translate
from PIL import ImageDraw, ImageFont

def extract_promotion_code_in_html(html_string):
    # Regular expression to find the promotion block
    promotion_re = re.compile(r'<p class="dm-sp-card-desc">[^<]*</p>')

    # Find the promotion block
    promotion_text = promotion_re.search(html_string)
    if promotion_text:
        # If the promotion code exists, extract it and replace the promotion block with "Promotion Code: {code}"
        promotion_code = promotion_text.group().split(':')[-1].strip(' </p>')
        html_string = html_string.replace(promotion_text.group(),
                                          f'<p class="dm-sp-card-desc"> Promotion Code: {promotion_code} </p>')

    return html_string


def translate_text_with_model(target: str, text: str, model: str = "nmt") -> dict:
    """Translates text into the target language.

    Make sure your project is allowlisted.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target, model=model)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result


def translate_text_with_chatgpt(text):
    with open("chat.txt", "r") as file:
        openai.api_key = file.read().strip()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "imagine you are a translator, you only return translation of my request, nothing else, no explanation, just the pure translation."
            },
            {
                "role": "user",
                "content": f'again, imagine you are a translator, you only return translation of my request, nothing else, no explanation, just the pure translation. and keep it under 5 words, just translate the main thing for the sentense, like the item name and size, quantity{text}'
            }
        ]
    )

    translated_text = response['choices'][0]['message']['content'].strip()

    # If the translated text has more than 7 words, split it into multiple lines
    words = translated_text.split()
    if len(words) > 7:
        translated_text = '\n'.join([' '.join(words[i:i + 7]) for i in range(0, len(words), 7)])

    # print(translated_text)

    return translated_text


def remove_chinese_in_html(html_string):
    # Regular expression to find Chinese characters
    chinese_re = re.compile(r"[\u4e00-\u9fa5]+")

    # Replace all Chinese characters in the HTML string with an empty string
    no_chinese_string = chinese_re.sub('', html_string)

    return no_chinese_string


def translate_html_with_chatgpt(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')

    # Translate <p> tags
    p_tags = soup.find_all('p', class_=lambda x: x and 'dm-sp-card-title' in x.split() and 'title-rows' in x.split())

    for p_tag in p_tags:
        original_text = p_tag.get_text()

        # translate with ChatGPT
        translated_text = translate_text_with_chatgpt(original_text)

        # replace original text with translated text
        p_tag.clear()  # remove the current contents
        p_tag.append(translated_text)  # add the new text

    # Translate alt attribute in <img> tags
    img_tags = soup.find_all('img')

    for img_tag in img_tags:
        original_text = img_tag.get('alt')

        if original_text:  # if alt attribute exists
            # translate with ChatGPT
            translated_text = translate_text_with_chatgpt(original_text)

            # replace original text with translated text
            img_tag['alt'] = translated_text

    return str(soup)


def convert_html_to_jpeg(html_string, output_file):
    temp_file = "temp.jpeg"
    options = {
        'format': 'jpeg',
        'encoding': "UTF-8",
        'quiet': ''
    }

    html_string = translate_html_with_chatgpt(html_string)
    html_string = translate_html_with_chatgpt(html_string)

    # Extract the promotion code (replace YOUR_CODE_RE with your actual regex)
    match = re.search(r'<p class="dm-sp-card-desc">(.+?)</p>', html_string)
    if match:
        promotion_code = match.group(1)
    else:
        promotion_code = 'No code found'
    # Add the promotion code to the HTML
    html_string += f'<div class="promo-code">{promotion_code}</div>'

    html_string = f'''
    <style>
        .promo-code {{
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            color: red;
            font-size: 24px;
        }}
        .dm-sp-card-rank {{
            display: none;
        }}
        .dm-sp-card-price {{
            font-size: 33px;
            font-weight: bold;
        }}
        .sale {{
            color: black;
            font-size: 33px;
        }}
        .origin {{
            color: red;
            font-size: 33px;
        }}
        .dm-sp-card-desc {{
            color: red;
            font-size: 30px;
        }}
        .dm-sp-card-title-link {{
            color: black;
            text-decoration: none;
            pointer-events: none;
            font-size: 33px;
            
        }}
        .dm-sp-card-title {{
            display: none;
        }}
        .dm-sp-card-desc {{
            display:none;       
        }}
        .promo-code {{
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 30px;
            color: red;
        }}
    </style>
    {html_string}
    '''

    imgkit.from_string(html_string, temp_file, options=options)
    img = Image.open(temp_file)

    width, height = img.size
    new_width = (height * 12) // 16

    img = img.crop((0, 0, new_width, height))

    img.save(output_file)

    os.remove(temp_file)