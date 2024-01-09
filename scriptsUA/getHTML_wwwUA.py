from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # Add this line
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome options
options = Options()
options.add_argument('--headless')  # Ensure GUI is off
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())


url = 'https://www.ua.pt/pt/sbidm/horarios'
# url = 'https://www.ua.pt/pt/sbidm/ciencia-aberta'


# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=options)
driver.get(url)

# Wait for the AJAX data to load by waiting for a specific element on the page to be present
try:
    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'Section-Header container'))
    WebDriverWait(driver, 10).until(element_present)
except TimeoutException:  # Now this exception is defined
    print("--")

html = driver.page_source

html = html[html.find('<body'):html.find('</body>')]

print()

driver.quit()

import re
import html2text
from bs4 import BeautifulSoup

# Convert HTML to BeautifulSoup object
soup = BeautifulSoup(html, 'html.parser')

# Find all anchor tags and remove them
# -- Pq? As páginas UA tem uma ancora nos H2 e H3 não visivel, com o mesmo texto para podermos ligar directamente a essa zona (o que não está a funcionar).
for anchor in soup.find_all('anchor'):
    anchor.decompose()

# Initialize html2text object
h = html2text.HTML2Text()
h.ignore_links = False

# Convert HTML to Markdown
markdown = h.handle(str(soup))

# Define the start and end strings
start_string = "https://api-assets.ua.pt/files/logos/logo_sbidm_pt.svg)](/pt/sbidm)"
end_string = "## Rodapé"

# Find the start and end indices
start_index = markdown.find(start_string) + len(start_string)
end_index = markdown.find(end_string)

# Extract the content between the start and end strings
extracted_content = markdown[start_index:end_index].strip()

# Add a blank line before the additional text if necessary
if not extracted_content.endswith('\n\n'):
    extracted_content += '\n'


# Add the additional text at the end of the file
extracted_content += f"\nPara saber mais aceda a {url}"

# Remove empty lines at the beginning of the file
extracted_content = extracted_content.lstrip('\n')

# Save the markdown content to a file
filename = re.sub(r'\W+', '_', url) + '.md'

# extracted_content: remove the extra space in the beggining of all H2 (##) and H3 (##) -- e.g.:
# ##  Ciência AbertaCiência Aberta 
# should be
# ## Ciência AbertaCiência Aberta


with open(filename, "w", encoding="utf-8") as output_file:
    output_file.write(extracted_content)
    


