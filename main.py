import sys
import os
import re
import time
import csv
import traceback
import shutil
import zipfile
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from pyvirtualdisplay import Display


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FINAL_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
CLEANED_POOLS_DIR = os.path.join(FINAL_OUTPUT_DIR, "cleaned_pools")
RAW_POOLS_DIR = os.path.join(SCRIPT_DIR, "raw_pool_data")
WEB_DIR = "/var/www/html/mining_data"  # Web srv directory

# Create all dirs
os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
os.makedirs(CLEANED_POOLS_DIR, exist_ok=True)
os.makedirs(RAW_POOLS_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

# Data cleaning setup
KEEP_INDEXES = [0, 1, 2, 5, 6, 7, 9, 10]
KEEP_HEADER = [
    "Rank", "Country", "Pool", "Daily PPS $ / 100 TH",
    "MinPay", "Miners", "Hashrate", "Percent of Current Hashrate"
]

ACCEPTED_COUNTRIES = {
    "GLOBAL", "UNITED STATES", "ASIA", "KAZAKHSTAN", "GERMANY", "RUSSIA",
    "CHINA", "CANADA", "FINLAND", "LITHUANIA", "HONG KONG", "NETHERLANDS",
    "PORTUGAL", "SINGAPORE", "THAILAND", "BRAZIL", "DENMARK"
}
TWO_LETTER_COUNTRY = re.compile(r"^[A-Z]{2}$")

# SCRAPING FUNCTIONS
def clean_rank(rank_text):
    return rank_text.strip().rstrip('.')

def clean_coin(coin_text):
    cleaned = ' '.join(coin_text.strip().splitlines())
    # Remove extra spaces
    return re.sub(r'\s+', ' ', cleaned).strip()

def get_text(cell):
    try:
        text = cell.text.strip() or cell.get_attribute("innerText").strip()
        return text.replace('\n', ' ')
    except:
        return ""

def clean_pool_text(text):
    if not text:
        return ""
    return ' '.join(text.strip().split())

# Removes ticker
def extract_base_coin_name(coin_with_ticker):
    match = re.search(r'([A-Z]{2,})$', coin_with_ticker)
    if match:
        ticker_length = len(match.group(1))
        return coin_with_ticker[:-ticker_length]
    return coin_with_ticker

# Convert name to URL
def process_coin_name(coin_display_name):
    base_name = extract_base_coin_name(coin_display_name)
    coin_url_name = base_name.lower().strip().replace(' ', '-')
    
    # Special cases
    if "SV" in coin_display_name and "bitcoin" in coin_url_name:
        return "bitcoinsv"
    elif "Cash" in coin_display_name and "bitcoin" in coin_url_name:
        return "bitcoincash"
    elif "Classic" in coin_display_name and "ethereum" in coin_url_name:
        return "ethereumclassic"
    elif "DigiByte" in coin_display_name and "SHA-256" in coin_display_name:
        return "digibyte"
    elif "MimbleWimble" in coin_display_name:
        return "mimblewimble" 
    elif "Nervos Network" in coin_display_name:
        return "nervos"
    return coin_url_name

def extract_country_and_pool(text):
    multi_word_countries = [
        "United States", "United Kingdom", "North Korea", "South Korea", 
        "New Zealand", "Costa Rica", "Puerto Rico", "Saudi Arabia", 
        "Czech Republic", "South Africa", "Hong Kong"
    ]
    
    for country in multi_word_countries:
        if text.startswith(country):
            return country, text[len(country):].strip()
    
    parts = text.split(maxsplit=1)
    return (parts[0], parts[1]) if len(parts) > 1 else ("Unknown", text)

def clean_pool_name(pool_name):
    plus_index = pool_name.find('+')
    return pool_name[:plus_index].strip() if plus_index > 0 else pool_name

def clean_blocks_data(blocks_text):
    if not blocks_text:
        return "No Data"
    
    colon_index = blocks_text.find(':')
    if colon_index > 0:
        blocks_text = blocks_text[:colon_index].strip()
    
    return re.sub(r'(\d+)([-+])', r'\1 \2', blocks_text)

def scrape_top_coins(driver):
    print("Getting top coins")
    url = "https://miningpoolstats.stream/"
    driver.get(url)
    
    # Wait for table to load
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "coins"))
    )
    time.sleep(3)  # Let page load
    table = driver.find_element(By.ID, "coins")
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    
    print(f"Found {len(rows)} rows")
    data = []
    
    for i, row in enumerate(rows[:20]):  # Get top 20 coins
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 13:
            print(f"Row {i+1} has only {len(cells)} fields, skipping")
            continue
            
        try:
            # Getting data
            rank = clean_rank(get_text(cells[0]))
            coin = clean_coin(get_text(cells[1]))
            algo = get_text(cells[2])
            market_cap = get_text(cells[3])
            emission = get_text(cells[4])
            price = get_text(cells[5])
            change_7d = get_text(cells[6])
            volume = get_text(cells[7])
            pools_known = get_text(cells[8])
            pools_hashrate = get_text(cells[9])
            network_hashrate = get_text(cells[10])
            last_block = clean_pool_text(get_text(cells[12]))
            
            data.append([
                rank, coin, algo, market_cap, emission, price, change_7d,
                volume, pools_known, pools_hashrate, network_hashrate, last_block
            ])
        except Exception as e:
            print(f"Error processing row {i+1}: {e}")
    
    # Save to CSV
    top_coins_file = os.path.join(FINAL_OUTPUT_DIR, "Top20Coins.csv")
    headers = [
        "Rank", "Coin", "Algorithm", "MarketCap", "Emission(Last 24h)",
        "Price(USD)", "7Day Price Change", "Volume(Last 24h)",
        "Pools(known)", "PoolsHashrate", "NetworkHashrate", "LastBlock Found"
    ]
    
    with open(top_coins_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Top coins saved to: {top_coins_file}")
    return data

def scrape_coin_pools(driver, coin_data):
    print("\nScraping pool data\n")
    
    for row in coin_data:
        rank = row[0]
        coin_display_name = row[1]
        coin_url_name = process_coin_name(coin_display_name)
        url = f"https://miningpoolstats.stream/{coin_url_name}"
        
        print(f"Scraping {coin_display_name}")
        driver.get(url)
        
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "pools"))
            )
            time.sleep(3)  # Let page load
            
            pools_table = driver.find_element(By.ID, "pools")
            tbody = pools_table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            headers = [
                "Rank", "Country", "Pool", "PoolFee", 
                "Daily PPS $ / 100 TH", "MinPay", "Miners", 
                "Hashrate", "Network %", "Blocks and Expected Block Diff", 
                "BlockHeight", "LastFound"
            ]
            
            coin_pools = []
            count = 0
            
            for row in rows:
                # Skip ad rows
                if "show1100" in row.get_attribute("class"):
                    continue
                    
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 3:
                    continue
                    
                row_data = []
                
                # Get each cell
                row_data.append(clean_pool_text(cells[0].get_attribute("textContent")).strip('.'))  # Rank
                
                # Country and Pool
                country_pool_text = clean_pool_text(cells[1].get_attribute("textContent"))
                country, pool = extract_country_and_pool(country_pool_text)
                row_data.append(country)
                row_data.append(clean_pool_name(pool))
                
                # Other cells
                for i in range(2, 11):
                    if len(cells) > i:
                        text = clean_pool_text(cells[i].get_attribute("textContent"))
                        if i == 8:
                            row_data.append(clean_blocks_data(text))
                        else:
                            row_data.append(text if text else "No Data")
                    else:
                        row_data.append("No Data")
                
                if any(row_data):
                    coin_pools.append(row_data)
                    count += 1
                
                # Limit to top 15 pools per coin
                if count >= 15:
                    break
            
            # Save raw data
            safe_name = re.sub(r'[^\w\-]', '_', coin_url_name)
            coin_file = os.path.join(RAW_POOLS_DIR, f"{safe_name}_pools.csv")
            
            with open(coin_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(coin_pools)
            
            print(f"  Processed {len(coin_pools)} pools")
            time.sleep(2)  # For bot detection
            
        except Exception as e:
            print(f"Error scraping {coin_display_name}: {e}")
            traceback.print_exc()
    
    print("All raw pool data saved")

# Cleaning 
def normalise_country(raw: str) -> str:
    """Standardize country names"""
    token = raw.strip().split(",", 1)[0].strip().strip('"')
    upper = token.upper()
    if TWO_LETTER_COUNTRY.match(upper):
        return upper
    if upper in ACCEPTED_COUNTRIES:
        return token
    return "N/A"

# Get the domain name from pool names
def cleanup_pool(name: str) -> str:
    name = name.replace("Multi-Coin", "").strip().strip('"')
    domain_pattern = re.compile(r'([a-zA-Z0-9-]+\.(?:com|io|net|org|info|biz|us|cn|uk|de))')
    matches = domain_pattern.findall(name)
    return matches[0] if matches else name

def clean_single_file(in_path: str, out_path: str) -> None:
    with open(in_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:

        reader, writer = csv.reader(fin), csv.writer(fout)
        next(reader, None)  # Skip header
        writer.writerow(KEEP_HEADER)

        for row in reader:
            if len(row) < max(KEEP_INDEXES) + 1:
                continue

            cleaned = [row[i].strip() for i in KEEP_INDEXES]
            cleaned[1] = normalise_country(cleaned[1])  # Country
            cleaned[2] = cleanup_pool(cleaned[2])          # Pool name
            writer.writerow(cleaned)

def clean_pool_data():
    print("\nCleaning pool data\n")
    cleaned_count = 0
    
    for fname in os.listdir(RAW_POOLS_DIR):
        if fname.lower().endswith(".csv"):
            in_path = os.path.join(RAW_POOLS_DIR, fname)
            out_path = os.path.join(CLEANED_POOLS_DIR, fname)
            clean_single_file(in_path, out_path)
            cleaned_count += 1
            print(f"  {fname} complete")
    
    print(f"Cleaned {cleaned_count} pools")

# Setup Firefox headless
def setup_driver():
    print("Setting up Firefox driver")
    try:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        options.binary_location = "/usr/bin/firefox-esr"
        
        service = FirefoxService(
            executable_path="/usr/local/bin/geckodriver",
            service_args=["--marionette-port", "2828"]
        )
        
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_window_size(1920, 1080)
        print("Firefox driver init completed")
        return driver
    except Exception as e:
        print(f"Firefox setup failed: {e}")
        traceback.print_exc()
        raise RuntimeError("Failed to init Firefox driver")

def cleanup_raw_data():
    print("\nCleaning up raw data...")
    if os.path.exists(RAW_POOLS_DIR):
        shutil.rmtree(RAW_POOLS_DIR)
    else:
        print("Raw data directory not found")

# Uploads to server
def publish_to_web():
    print("\nUploading to web server...")
    
    # Clean old files (keep 7 days)
    now = time.time()
    for f in os.listdir(WEB_DIR):
        file_path = os.path.join(WEB_DIR, f)
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - 7 * 86400:
            os.remove(file_path)
    
    # Copy Top20Coins.csv
    top_coins = os.path.join(FINAL_OUTPUT_DIR, "Top20Coins.csv")
    if os.path.exists(top_coins):
        shutil.copy2(top_coins, WEB_DIR)
    
    # Copy cleaned pools
    for fname in os.listdir(CLEANED_POOLS_DIR):
        if fname.endswith(".csv"):
            src = os.path.join(CLEANED_POOLS_DIR, fname)
            shutil.copy2(src, WEB_DIR)
    
    # Create timestamped zip 
    timestamp = time.strftime("%Y%m%d-%H_%M")
    zip_path = os.path.join(WEB_DIR, f"mining_data_{timestamp}.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for fname in os.listdir(WEB_DIR):
            if fname.endswith(".csv"):
                file_path = os.path.join(WEB_DIR, fname)
                zipf.write(file_path, os.path.basename(file_path))
    
    return zip_path

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def main():
    # Start headless display
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    start_time = time.time()
    driver = None
    
    try:
        # Setup and start scraping
        driver = setup_driver()
        top_coins_data = scrape_top_coins(driver)
        
        if not top_coins_data:
            print("No coins found, exiting")
            return
        
        scrape_coin_pools(driver, top_coins_data)
        clean_pool_data()
        cleanup_raw_data()
        
        # Publish to web srv
        zip_path = publish_to_web()
        ip_address = get_ip_address()
        
        # Time sats
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        # Final output
        print("\n" + "="*50)
        print(f"Completed in {minutes}m {seconds}s")
        print(f"\n  http://{ip_address}/mining_data/")
        print("\nFiles:")
        print(f"  - Top20Coins.csv")
        print(f"  - [coin_name]_pools.csv (for each coin)")
        print(f"\nDownload all files as zip:")
        print(f"  http://{ip_address}/mining_data/{os.path.basename(zip_path)}")
        print("="*50)
        
    except Exception as e:
        print(f"\nScript failed: {e}")
        traceback.print_exc()
    finally:
        # Cleanup 
        if driver:
            driver.quit()
        display.stop()

if __name__ == "__main__":
    main()