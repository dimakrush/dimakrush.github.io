import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime
import time
import os
from tqdm import tqdm

def extract_date(span_element):
    """Extract and format date from span element."""
    date_text = span_element.text.strip()
    
    # Check if this looks like a date (must contain digits and periods)
    if not re.search(r'\d+\.\d+\.\d+', date_text):
        return "invalid_date"  # Return indicator that this isn't a date
        
    # Convert date format from DD.MM.YYYY to YYYY-MM-DD
    try:
        date_obj = datetime.strptime(date_text, "%d.%m.%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return "invalid_date"  # Return as invalid if parsing fails

def extract_number(text):
    """Extract number from text that may contain additional info."""
    # This extracts the main number before any small tag
    if text:
        # Extract the first number in the text
        match = re.search(r'(\d+[\s\d]*\d*)', text)
        if match:
            # Remove any spaces in the number
            return match.group(1).replace(" ", "")
    return ""

def extract_increment(text):
    """Extract increment value from small tag if present."""
    # Look for a pattern like <small>(+123)</small>
    if text:
        match = re.search(r'\(\+(\d+)\)', text)
        if match:
            return match.group(1)
    return ""

def scrape_casualties(start_date="2022-02-24"):
    """Scrape casualties data from the website starting from the specified date."""
    
    base_url = "https://index.minfin.com.ua/ua/russian-invading/casualties/"
    
    # Convert start_date to datetime object for comparison
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    
    # Prepare CSV file
    csv_filename = "russian_casualties.csv"
    
    # Define columns for the CSV file
    columns = [
        "date", "tanks", "tanks_increment", "armored_fighting_vehicles", "afv_increment",
        "artillery_systems", "artillery_increment", "mlrs", "mlrs_increment",
        "air_defense_systems", "air_defense_increment", "aircraft", "aircraft_increment",
        "helicopters", "helicopters_increment", "uav", "uav_increment",
        "cruise_missiles", "cruise_missiles_increment", "ships", "ships_increment",
        "submarines", "submarines_increment", "vehicles_fuel_tanks", "vehicles_increment",
        "special_equipment", "special_equipment_increment", "personnel", "personnel_increment"
    ]
    
    # Check if file exists to avoid overwriting
    file_exists = os.path.isfile(csv_filename)
    
    # Initialize data list
    all_data = []
    
    # Initialize set to keep track of processed dates to avoid duplicates
    processed_dates = set()
    
    # Generate all possible year-month combinations
    links_to_process = []
    
    # Current date to determine the range to generate
    current_date = datetime.now()
    
    # Generate links for all months from Feb 2022 to current month
    years = range(2022, current_date.year + 1)
    
    for year in years:
        # Determine start and end months for this year
        start_month = 2 if year == 2022 else 1  # War started in Feb 2022
        end_month = current_date.month if year == current_date.year else 12
        
        for month in range(start_month, end_month + 1):
            # Format 1: /casualties/YYYY-MM/
            links_to_process.append(f"/ua/russian-invading/casualties/{year}-{month:02d}/")
            
            # Format 2: /casualties/YYYY/MM/ (alternative format)
            links_to_process.append(f"/ua/russian-invading/casualties/{year}/{month:02d}/")
    
    # Add the main page which might contain the most recent data
    links_to_process.append('/ua/russian-invading/casualties/')
    
    print(f"Generated {len(links_to_process)} URLs to process")
    
    # Process each page
    for page_link in tqdm(links_to_process, desc="Processing pages"):
        full_url = f"https://index.minfin.com.ua{page_link}"
        print(f"\nFetching: {full_url}")
        
        try:
            response = requests.get(full_url)
            # If page doesn't exist (404), just continue to the next one
            if response.status_code == 404:
                print(f"Page not found: {full_url}")
                continue
                
            response.raise_for_status()  # Raise exception for other HTTP errors
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all casualty list items (each day is a separate li with class="gold")
            items = soup.find_all('li', class_='gold')
            
            for item in tqdm(items, desc="Processing days", leave=False):
                # Extract date
                date_span = item.find('span', class_='black')
                if not date_span:
                    continue
                
                date_str = extract_date(date_span)
                
                # Skip non-date text or invalid dates
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"Skipping invalid date format: '{date_str}'")
                    continue
                
                # Skip if date is earlier than the start date
                if date_obj < start_date_obj:
                    continue
                
                # Skip if already processed this date
                if date_str in processed_dates:
                    continue
                
                processed_dates.add(date_str)
                
                # Extract casualties data
                casualties_div = item.find('div', class_='casualties')
                if not casualties_div:
                    continue
                
                # Initialize data dict with zeros
                data = {col: "" for col in columns}
                data["date"] = date_str
                
                # Process all list items in the casualties div
                ul = casualties_div.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        li_text = li.get_text(strip=True)
                        
                        # Extract category and value based on the text content
                        if "Танки" in li_text:
                            data["tanks"] = extract_number(li_text)
                            data["tanks_increment"] = extract_increment(li_text)
                        
                        elif "ББМ" in li_text or "Бойові броньовані машини" in li_text:
                            data["armored_fighting_vehicles"] = extract_number(li_text)
                            data["afv_increment"] = extract_increment(li_text)
                        
                        elif "Артилерійські системи" in li_text:
                            data["artillery_systems"] = extract_number(li_text)
                            data["artillery_increment"] = extract_increment(li_text)
                        
                        elif "РСЗВ" in li_text or "Реактивні системи залпового вогню" in li_text:
                            data["mlrs"] = extract_number(li_text)
                            data["mlrs_increment"] = extract_increment(li_text)
                        
                        elif "Засоби ППО" in li_text:
                            data["air_defense_systems"] = extract_number(li_text)
                            data["air_defense_increment"] = extract_increment(li_text)
                        
                        elif "Літаки" in li_text:
                            data["aircraft"] = extract_number(li_text)
                            data["aircraft_increment"] = extract_increment(li_text)
                        
                        elif "Гелікоптери" in li_text:
                            data["helicopters"] = extract_number(li_text)
                            data["helicopters_increment"] = extract_increment(li_text)
                        
                        elif "БПЛА" in li_text or "Безпілотні літальні апарати" in li_text:
                            data["uav"] = extract_number(li_text)
                            data["uav_increment"] = extract_increment(li_text)
                        
                        elif "ракети" in li_text:
                            data["cruise_missiles"] = extract_number(li_text)
                            data["cruise_missiles_increment"] = extract_increment(li_text)
                        
                        elif "Кораблі" in li_text or "катери" in li_text:
                            data["ships"] = extract_number(li_text)
                            data["ships_increment"] = extract_increment(li_text)
                        
                        elif "Підводні човни" in li_text:
                            data["submarines"] = extract_number(li_text)
                            data["submarines_increment"] = extract_increment(li_text)
                        
                        elif "Автомобілі" in li_text or "автоцистерни" in li_text:
                            data["vehicles_fuel_tanks"] = extract_number(li_text)
                            data["vehicles_increment"] = extract_increment(li_text)
                        
                        elif "Спеціальна техніка" in li_text:
                            data["special_equipment"] = extract_number(li_text)
                            data["special_equipment_increment"] = extract_increment(li_text)
                        
                        elif "Особовий склад" in li_text:
                            data["personnel"] = extract_number(li_text)
                            data["personnel_increment"] = extract_increment(li_text)
                
                all_data.append(data)
                
            # Add a small delay to avoid overloading the server
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {full_url}: {e}")
            continue
    
    # Sort data by date
    all_data.sort(key=lambda x: x["date"])

    # write into the container’s working dir
    csv_filename = "russian_casualties.csv"
    out_path = os.path.join(os.getcwd(), csv_filename)
    with open(out_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(all_data)
    print(f"Wrote data to {out_path}")
    
    return all_data

if __name__ == "__main__":
    # Run the scraper with default start date
    scrape_casualties()