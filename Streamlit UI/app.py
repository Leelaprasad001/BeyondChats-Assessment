import re
import requests
import pandas as pd
import streamlit as st

url = "https://devapi.beyondchats.com/api/get_message_with_sources"
url_pattern = re.compile(r'https?://[^\s)]+')

try:
    response = requests.get(url)
    response.raise_for_status()  
    data = response.json()
    total_pages = data['data']['last_page']
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"Other error occurred: {err}")


def fetch_and_transform_data(num_pages, base_url):
    all_rows = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data['data']['data']:
                message_id = item['id']
                response_text = item['response']
                for source in item['source']:
                    source_id = source['id']
                    source_context = source['context']
                    source_link = source.get('link', None)
                    all_rows.append([message_id, response_text, source_id, source_context, source_link])

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    df = pd.DataFrame(all_rows, columns=['id', 'response', 'source_id', 'source_context', 'source_link'])
    return df

def find_first_url(text):
    match = url_pattern.search(text)
    return match.group(0) if match else None


st.title("Fetch Valid Citations from the URL Below")
st.write("https://devapi.beyondchats.com/api/get_message_with_sources")
num_pages = st.selectbox("Select the number of pages to be fetched:", list(range(1, total_pages + 1)))

# Fetch citations button
if st.button("Fetch"):
    df = fetch_and_transform_data(num_pages, url)
    for index, row in df.iterrows():
        if df.iloc[index]['source_link'] in [None, ""]:
            found_url = find_first_url(row['source_context'])
            if found_url:
                df.at[index, 'source_link'] = found_url
    citations = []

    for index, row in df.iterrows():
        if row['source_link'] is not None and row['source_link'] != "":
            citation = {
                "id": str(row['source_id']),
                "link": row['source_link']
            }
            citations.append(citation)
    if citations:
        # Display citations in a table
        citations_df = pd.DataFrame(citations)
        st.write("Number of  citations found : ", len(citations))
        st.table(citations_df)
    else:
        st.write("No citations found.")
