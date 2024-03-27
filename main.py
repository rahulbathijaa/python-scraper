import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urlunparse

SCRAPINGBEE_API_KEY = ''

def scrape_with_scrapingbee(url):
    payload = {
        'api_key': SCRAPINGBEE_API_KEY,
        'url': url,
        'render_js': 'true',
    }
    response = requests.get('https://app.scrapingbee.com/api/v1/', params=payload)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.text}")
        return None

def clean_url(url):
    parsed_url = urlparse(url)
    clean_parsed_url = parsed_url._replace(query=None)  # This removes query parameters
    return urlunparse(clean_parsed_url)

def fetch_and_parse_detail_page(url):
    html_content = scrape_with_scrapingbee(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.select_one('h1.profile-header__title').text.strip()
        description_elements = soup.select('.profile-summary__text p')
        description = ' '.join([element.text for element in description_elements])
        website_link_element = soup.select_one('li.profile-quick-menu--visit a.visit-website')
        website_link = clean_url(website_link_element['href']) if website_link_element else 'N/A'
        project_size = soup.select_one('.profile-metrics--card dl dd span').text.strip() if soup.select_one('.profile-metrics--card dl dd span') else 'N/A'
        return title, website_link, description, project_size
    else:
        return 'N/A', 'N/A', 'N/A', 'N/A'

def scrape_categories_and_write_to_csv(categories):
    for category, urls in categories.items():
        csv_file_path = f'{category.replace(" & ", "_").replace(" ", "_").lower()}_details.csv'
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Agency Name', 'Website', 'Description', 'Most Common Project Size'])

            for url in urls:
                print(f"Scraping {category} from URL: {url}")
                main_page_content = scrape_with_scrapingbee(url)
                if main_page_content:
                    profile_links = parse_html_for_profile_links(main_page_content)
                    # Ensure at least one profile link is found
                    if profile_links:
                        # Fetch and parse only the first profile for testing
                        agency_name, website_link, description, project_size = fetch_and_parse_detail_page(profile_links[0])
                        writer.writerow([agency_name, website_link, description, project_size])
        print(f"Scraping complete for {category}. Data written to {csv_file_path}")

def parse_html_for_profile_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    profile_links = soup.select('li.website-profile a.directory_profile')
    base_url = "https://clutch.co"
    if profile_links:
        first_profile_link = base_url + profile_links[0]['href']
        return [first_profile_link]
    else:
        return []

# Defining categories by URL
categories = {
    'Branding': ['https://clutch.co/agencies/video-production/motion-graphics?related_services=field_pp_sl_branding'],
    'Graphic Design': ['https://clutch.co/agencies/video-production/motion-graphics?related_services=field_pp_sl_graphic_design'],
    'Web Design & Web Development': [
        'https://clutch.co/agencies/video-production/motion-graphics?related_services=field_pp_sl_web_design',
        'https://clutch.co/agencies/video-production/motion-graphics?related_services=field_pp_sl_web_programming'
    ],
    'Social Media Marketing and Advertising': [
        'https://clutch.co/agencies/video-production/motion-graphics?related_services=field_pp_sl_social_media_marketing',
        'https://clutch.co/agencies/video-production/motion-graphics?related_services=field_pp_sl_advertising'
    ]
}

# Execute scraping for all categories with limited API usage
scrape_categories_and_write_to_csv(categories)


