import re
import requests
from bs4 import BeautifulSoup

def try_except(success, failure=None, *exceptions):
    try:
        return success()
    except exceptions or Exception:
        return failure() if callable(failure) else failure

def get_next_report(results, annual_reports):
    res = results[-1]
    year = max([min(list(map(lambda date: int(re.search('\d+$', date).group()), v['dates']))) for k, v in res.items()])
    data = {}
    if year >= 2012:
        key = None
        for k, data in annual_reports.items():
            if year == int(re.search('^\d+', data['file_info']['filing_date']).group()):
                key = k
        
        data = annual_reports[key]

    return year, data


def fetch_statement_links(soup, table_links, links_text):
    links = {}
    for text in links_text:
        el = soup.find('li', text=re.compile(text, re.I))
        
        if el is None:
            continue
        
        link_id = re.search("\d+", el['id']).group()
        links[text] = table_links[int(link_id) - 1]
    return links


def parse_statements(links, links_text):
    metrics = {}
    for statement in links:
        resp = requests.get('https://www.sec.gov/' + links[statement])
        soup = BeautifulSoup(resp.content, 'lxml')
        
        dates = [e.text for e in soup.find_all('th', colspan=None)]
        allowed_text = [re.escape(string) for string in links_text[statement]]
        
        # TODO: figure out why this isn't fetching the right rows
        rows = list(filter(lambda el: el.find('td', {"class": "pl"}) != None and el.find('td', {"class": "pl"}).find('a', text=re.compile(f"^({'|'.join(allowed_text)})$", re.I)) != None, soup.find_all('tr')))
        
        statement_metrics = {
            'statement_header': soup.find('th', {'class': 'tl'}).text, 
            'dates': dates
        }
        
        for row in rows: 
            key = row.find('td', {"class": "pl"}).find('a').text
            statement_metrics[key] = [e.text for e in row.find_all('td', {"class": re.compile('num(p)?')})]

        metrics[statement] = statement_metrics
    
    return metrics

def fetch_master_list(soup):
    entries = soup.find_all('entry')

    master_list_xml = {}
    for entry in entries:
        # create dict for entry
        accession_num = entry.find('accession-number').text
        entry_dict = {}

        # store category info
        category_info = entry.find('category')
        entry_dict['category'] = {}
        entry_dict['category']['label'] = category_info['label']
        entry_dict['category']['scheme'] = category_info['scheme']
        entry_dict['category']['term'] = category_info['term']

        # store file info
        entry_dict['file_info'] = {}
        entry_dict['file_info']['act'] = try_except(lambda: entry.find('act').text)
        entry_dict['file_info']['file_number'] = try_except(lambda: entry.find('file-number').text)
        entry_dict['file_info']['file_number_href'] = try_except(lambda: entry.find('file-number-href').text)
        entry_dict['file_info']['filing_date'] = entry.find('filing-date').text
        entry_dict['file_info']['filing_href'] = entry.find('filing-href').text
        entry_dict['file_info']['filing_type'] = entry.find('filing-type').text
        entry_dict['file_info']['form_number'] = try_except(lambda: entry.find('film-number').text)
        entry_dict['file_info']['form_name'] = entry.find('form-name').text
        entry_dict['file_info']['size'] = entry.find('size').text
        entry_dict['file_info']['xbrl_href'] = try_except(lambda: entry.find('xbrl_href').text)

        #store extra info
        entry_dict['request_info'] = {}
        entry_dict['request_info']['link'] = entry.find('link')['href']
        entry_dict['request_info']['title'] = entry.find('title').text
        entry_dict['request_info']['last_update'] = entry.find('updated').text

        # store in master list
        master_list_xml[accession_num] = entry_dict
    
    return master_list_xml
    