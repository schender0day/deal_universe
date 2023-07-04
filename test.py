import re
import imgkit
from PIL import Image
import openai

def extract_promotion_code_in_html(html_string):
    # Regular expression to find the promotion block
    promotion_re = re.compile(r'<p class="dm-sp-card-desc">[^<]*</p>')

    # Find the promotion block
    promotion_text = promotion_re.search(html_string)
    if promotion_text:
        # If the promotion code exists, extract it and replace the promotion block with "Promotion Code: {code}"
        promotion_code = promotion_text.group().split(':')[-1].strip(' </p>')
        html_string = html_string.replace(promotion_text.group(), f'<p class="dm-sp-card-desc"> Promotion Code: {promotion_code} </p>')

    return html_string

def translate_text_with_chatgpt(text):
    with open("chat.txt", "r") as file:
        openai.api_key = file.read().strip()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Translate the given text to English, making sure to only keep the product name and important details, Example will be: Amazon Ringbell, Iphone 12 ProMax, do not inlcude anything like 'translation' or chinese characters, chinese romaji in output, no more than 10 words in output"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    translated_text = response['choices'][0]['message']['content'].strip()

    # If the translated text has more than 7 words, split it into multiple lines
    words = translated_text.split()
    if len(words) > 7:
        translated_text = '\n'.join([' '.join(words[i:i+7]) for i in range(0, len(words), 7)])

    print(translated_text)

    return translated_text

def remove_chinese_in_html(html_string):
    # Regular expression to find Chinese characters
    chinese_re = re.compile(r"[\u4e00-\u9fa5]+")

    # Replace all Chinese characters in the HTML string with an empty string
    no_chinese_string = chinese_re.sub('', html_string)

    return no_chinese_string

def convert_html_to_jpeg(html_string, output_file):
    temp_file = "temp.jpeg"
    options = {
        'format': 'jpeg',
        'encoding': "UTF-8",
    }

    # Extract promotion code in the HTML string
    html_string = extract_promotion_code_in_html(html_string)

    # Remove Chinese characters in the HTML string
    html_string = remove_chinese_in_html(html_string)

    html_string = f'''
    <style>
        .dm-sp-card-rank {{
            display: none;
            }}
        .dm-sp-card-price {{
            font-size: 28px;
            font-weight: bold;
        }}
        .sale {{
            color: black;
            font-size: 28px;
        }}
        .origin {{
            color: red;
            font-size: 28px;
        }}
        .dm-sp-card-desc {{
            color: red;
            font-size: 28px;
        }}
        .dm-sp-card-title-link {{
            color: black;
            text-decoration: none;
            pointer-events: none;
            font-size: 20px;
        }}
    </style>
    {html_string}
    '''

    imgkit.from_string(html_string, temp_file, options=options)
    img = Image.open(temp_file)

    width, height = img.size
    img = img.crop((0, 0, height, height))

    img.save(output_file)
