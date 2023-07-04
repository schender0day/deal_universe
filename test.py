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

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=f"{text}\n\nTranslate the above text to English in less than 10 words, only product name , not brand name, no location:",
        temperature=0.3,
        max_tokens=200
    )

    translated_text = response.choices[0].text.strip()

    # If the translated text has more than 7 words, split it into multiple lines
    words = translated_text.split()
    if len(words) > 7:
        translated_text = '\n'.join([' '.join(words[i:i+7]) for i in range(0, len(words), 7)])

    print(translated_text)

    return translated_text

def translate_chinese_in_html(html_string):
    # Regular expression to find Chinese characters
    chinese_re = re.compile(r"[\u4e00-\u9fa5]+")

    # Find all Chinese texts in the HTML string
    chinese_texts = chinese_re.findall(html_string)

    # Translate each Chinese text and replace it in the HTML string
    for text in chinese_texts:
        translated_text = translate_text_with_chatgpt(text)
        html_string = html_string.replace(text, translated_text)

    return html_string

def convert_html_to_jpeg(html_string, output_file):
    temp_file = "temp.jpeg"
    options = {
        'format': 'jpeg',
        'encoding': "UTF-8",
    }

    # Extract promotion code in the HTML string
    html_string = extract_promotion_code_in_html(html_string)

    # Translate Chinese in the HTML string to English
    html_string = translate_chinese_in_html(html_string)

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
    # img = img.resize((500, 500), Image.LANCZOS)

    width, height = img.size
    img = img.crop((0, 0, height, height))

    img.save(output_file)

    # optionally delete the temporary file
    # import os
    # os.remove(temp_file)

convert_html_to_jpeg('<!-- 排行信息 --> <i class="dm-sp-card-rank" data-rank="10">10</i> <!-- 主图 --> <a class="dm-sp-card-img" target="_blank" trkrip="home-hotSps" href="https://www.dealmoon.com/product/-arctic-ocean-mandarin-soda-drink-beibingyang-orange-sparkling-juice-chinese-traditional-soda-beverage-11-1-fl-oz-330ml-per-can-24-cans/5751949"> <img src="https://imgcache.dealmoon.com/thumbimg.dealmoon.com/dealmoon/c9e/f1a/8af/26af3c1199f7e69fffef085.jpg_480_480_2_83c2.jpg" alt="北冰洋罐装橙汁汽水 11.1oz 24罐"> </a> <!-- 基本信息 --> <a trkrip="home-hotSps" class="dm-sp-card-title-link" target="_blank" href="https://www.dealmoon.com/product/-arctic-ocean-mandarin-soda-drink-beibingyang-orange-sparkling-juice-chinese-traditional-soda-beverage-11-1-fl-oz-330ml-per-can-24-cans/5751949"> <p class="dm-sp-card-price"> <span class="sale">$28.65</span><del class="origin">$41.99</del> </p> <p class="dm-sp-card-title"> 北冰洋罐装橙汁汽水 11.1oz 24罐 </p> <p class="dm-sp-card-desc"> 需购买3件 码: DM1004PD </p> </a>', 'test.jpeg')
