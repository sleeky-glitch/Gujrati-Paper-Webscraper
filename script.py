import streamlit as st
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

def translate_to_gujarati(keyword):
    """Translate the input keyword from English to Gujarati using googletrans."""
    try:
        translator = Translator()
        translated = translator.translate(keyword, src='en', dest='gu')
        return translated.text
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return keyword

def fetch_article_links(base_url, keyword):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            if keyword in a.text:
                href = a['href']
                if not href.startswith("http"):
                    href = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
                links.append(href)

        return links
    except Exception as e:
        st.error(f"An error occurred while fetching links: {e}")
        return []

def extract_article(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        date = soup.find('h5') 
        article_date = date.get_text(strip=True) if date else "Date not found"

        content = soup.find('div', class_='article-body')
        if content:
            article_text = "\n".join(p.get_text() for p in content.find_all('p'))
        else:
            paragraphs = soup.find_all('p')
            article_text = "\n".join(p.get_text() for p in paragraphs if p.get_text())

        return article_date, article_text if article_text else "No article content found."
    except Exception as e:
        return f"Error extracting article: {e}", ""

def main():
    st.set_page_config(page_title="Gujarati News Article Scraper", page_icon="📰")
    st.title("Gujarati News Article Finder")

    base_url = "https://www.gujarat-samachar.com/"

    keyword = st.text_input("Enter a keyword (in English or Gujarati):")

    if st.button("Find and Extract Articles"):
        if keyword:
            with st.spinner("Translating and searching for articles..."):
                # Translate the keyword to Gujarati if it's in English
                keyword_gujarati = translate_to_gujarati(keyword)

                # Fetch articles using the Gujarati keyword
                links = fetch_article_links(base_url, keyword_gujarati)

                if links:
                    st.success(f"Found {len(links)} articles with the keyword '{keyword}':")
                    for i, link in enumerate(links, start=1):
                        st.write(f"**Article {i}:** [Link]({link})")
                        with st.spinner("Extracting article content..."):
                            article_date, article_content = extract_article(link)
                            st.write(f"**Published on:** {article_date}")
                            st.write(f"**Article Content:**\n{article_content}\n")
                else:
                    st.warning(f"No articles found with the keyword '{keyword}'.")
        else:
            st.error("Please enter a keyword.")

if __name__ == "__main__":
    main()
