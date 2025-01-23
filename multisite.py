import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

def translate_to_gujarati(keyword):
    """Translate the input keyword from English to Gujarati using Deep Translator."""
    try:
        translated = GoogleTranslator(source='en', target='gu').translate(keyword)
        return translated
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return keyword

def fetch_article_links(base_url, keyword, site_name):
    """Fetch all article links containing the keyword for a specific site."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        if site_name == "Gujarat Samachar":
            for a in soup.find_all('a', href=True):
                if keyword in a.text:
                    href = a['href']
                    if not href.startswith("http"):
                        href = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
                    links.append(href)
        elif site_name == "Divya Bhaskar":
            for a in soup.find_all('a', href=True):
                if keyword in a.text:
                    links.append(a['href'])
        elif site_name == "Sandesh":
            for a in soup.find_all('a', href=True):
                if keyword in a.text:
                    links.append(a['href'])

        return links
    except Exception as e:
        st.error(f"An error occurred while fetching links for {site_name}: {e}")
        return []

def extract_article(link, site_name):
    """Extract the date and content from an article based on the site."""
    try:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if site_name == "Gujarat Samachar":
            date = soup.find('h5')
            article_date = date.get_text(strip=True) if date else "Date not found"
            content = soup.find('div', class_='article-body')
        elif site_name == "Divya Bhaskar":
            date = soup.find('time')
            article_date = date.get_text(strip=True) if date else "Date not found"
            content = soup.find('div', class_='article__body')
        elif site_name == "Sandesh":
            date = soup.find('span', class_='date')
            article_date = date.get_text(strip=True) if date else "Date not found"
            content = soup.find('div', class_='content')

        if content:
            article_text = "\n".join(p.get_text() for p in content.find_all('p'))
        else:
            paragraphs = soup.find_all('p')
            article_text = "\n".join(p.get_text() for p in paragraphs if p.get_text())

        return article_date, article_text if article_text else "No article content found."
    except Exception as e:
        return f"Error extracting article for {site_name}: {e}", ""

def main():
    st.set_page_config(page_title="Gujarati News Article Scraper", page_icon="📰")
    st.title("Gujarati News Article Finder")

    newspapers = {
        "Gujarat Samachar": "https://www.gujarat-samachar.com/",
        "Divya Bhaskar": "https://www.divyabhaskar.co.in/",
        "Sandesh": "https://sandesh.com/"
    }

    keyword = st.text_input("Enter a keyword (in English or Gujarati):")

    if st.button("Find and Extract Articles"):
        if keyword:
            with st.spinner("Translating and searching for articles..."):
                # Translate the keyword to Gujarati if it's in English
                keyword_gujarati = translate_to_gujarati(keyword)

                for site_name, base_url in newspapers.items():
                    st.subheader(f"Articles from {site_name}")
                    links = fetch_article_links(base_url, keyword_gujarati, site_name)

                    if links:
                        st.success(f"Found {len(links)} articles with the keyword '{keyword}' on {site_name}:")
                        for i, link in enumerate(links, start=1):
                            st.write(f"**Article {i}:** [Link]({link})")
                            with st.spinner("Extracting article content..."):
                                article_date, article_content = extract_article(link, site_name)
                                st.write(f"**Published on:** {article_date}")
                                st.write(f"**Article Content:**\n{article_content}\n")
                    else:
                        st.warning(f"No articles found with the keyword '{keyword}' on {site_name}.")
        else:
            st.error("Please enter a keyword.")

if __name__ == "__main__":
    main()
