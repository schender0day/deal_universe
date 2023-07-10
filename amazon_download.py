import requests
from bs4 import BeautifulSoup

# Example HTML
html = '''
<video id="detailpage-imageblock-player-1b646ee4-0193-42a2-8e70-3eb1e0ed356f-container-element_html5_api" class="vjs-tech" aria-label="Rongyuxuan Gravity Automatic Pepper and Salt Mill Grinder" playsinline="playsinline" disablepictureinpicture="true" tabindex="-1" preload="auto" poster="https://m.media-amazon.com/images/I/51JRi-Cpf4L._CR1,0,638,360_SR342,193__BG0,0,0__QL65_.jpg" src="blob:https://www.amazon.com/06d5ed59-b23a-4645-a501-ae3152ad3df4" loop=""></video>
'''

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Find the video element
video_element = soup.find('video')

# Extract the source URL
video_src = video_element.get('src')

# Download the video using the source URL
response = requests.get(video_src)

# Save the video to a file
with open('video.mp4', 'wb') as f:
    f.write(response.content)

print('Video downloaded successfully!')
