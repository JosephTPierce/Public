import sys
import os
import re
import time
import csv
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from pyvirtualdisplay import Display

# Setting up Dirs
FINAL_OUTPUT_DIR = "output"
CLEANED_POOLS_DIR = os.path.join(FINAL_OUTPUT_DIR, "cleaned_pools")
RAW_POOLS_DIR = "raw_pool_data"

# Make sure dirs exist
os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)
os.makedirs(CLEANED_POOLS_DIR, exist_ok=True)
os.makedirs(RAW_POOLS_DIR, exist_ok=True)

# Pool data cleaning
KEEP_INDEXES = [0, 1, 2, 5, 6, 7, 9, 10]
KEEP_HEADER = [
    "Rank", "Country", "Pool", "Daily PPS $ / 100 TH",
    "MinPay", "Miners", "Hashrate", "Percent of Current Hashrate"
]

# Country sanitizing
ACCEPTED_COUNTRIES = {
    "GLOBAL", "UNITED STATES", "ASIA", "KAZAKHSTAN", "GERMANY", "RUSSIA",
    "CHINA", "CANADA", "FINLAND", "LITHUANIA", "HONG KONG", "NETHERLANDS",
    "PORTUGAL", "SINGAPORE", "THAILAND", "BRAZIL", "DENMARK"
}
TWO_LETTER_COUNTRY = re.compile(r"^[A-Z]{2}$")

# Scraping Functions

def clean_rank(rank_text):
    return rank_text.strip().rstrip('.')

def clean_coin(coin_text):
    return coin_text.strip().split('\n')[0]

def get_text(cell):
    try:
        return cell.text.strip() or cell.get_attribute("innerText").strip()
    except:
        return ""

def clean_pool_text(text):
    if not text:
        return ""
    return ' '.join(text.strip().split())

def extract_base_coin_name(coin_with_ticker):
    match = re.search(r'([A-Z]{2,})$', coin_with_ticker)
    if match:
        ticker_length = len(match.group(1))
        return coin_with_ticker[:-ticker_length]
    return coin_with_ticker

def process_coin_name(coin_display_name):
    base_name = extract_base_coin_name(coin_display_name)
    coin_url_name = base_name.lower().strip().replace(' ', '-')
    
    # Special url cases 
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

# Scraper
def scrape_top_coins(driver):
    print("Getting top coins")
    url = "https://miningpoolstats.stream/"
    
    try:
        driver.get(url)
        print(f"Loaded URL: {url}")
    except Exception as e:
        print(f"Failed to load URL: {e}")
        return []
    
    try:
        WebDriverWait(driver, 60).until(  # Increased timeout to 60 seconds
            EC.presence_of_element_located((By.ID, "coins"))
        )
        print("Coins table found")
    except TimeoutException:
        print("Timed out waiting for coins table")
        return []
    except Exception as e:
        print(f"Error waiting for coins table: {e}")
        return []
    
    time.sleep(3)  # Allow JavaScript to render content
    
    try:
        table = driver.find_element(By.ID, "coins")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} rows in coins table")
    except Exception as e:
        print(f"Error finding table rows: {e}")
        return []
    
    data = []
    
    for i, row in enumerate(rows[:20]):
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 13:
                print(f"Row {i+1} has only {len(cells)} cells, skipping")
                continue
                
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
            last_block = get_text(cells[12])
            
            data.append([
                rank, coin, algo, market_cap, emission, price, change_7d,
                volume, pools_known, pools_hashrate, network_hashrate, last_block
            ])
        except Exception as e:
            print(f"Error processing row {i+1}: {e}")
    
    # Save coins to CSV at output directory
    top_coins_file = os.path.join(FINAL_OUTPUT_DIR, "Top20Coins.csv")
    
    try:
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
    except Exception as e:
        print(f"Failed to save top coins CSV: {e}")
        return []

def scrape_coin_pools(driver, coin_data):
    print("\nScraping pool data")
    
    if not coin_data:
        print("No coin data available for pool scraping")
        return
    
    for row in coin_data:
        if len(row) < 2:
            print("Skipping invalid coin data row")
            continue
            
        rank = row[0]
        coin_display_name = row[1]
        coin_url_name = process_coin_name(coin_display_name)
        url = f"https://miningpoolstats.stream/{coin_url_name}"
        
        print(f"Scraping {coin_display_name}")
        
        try:
            driver.get(url)
            print(f"Loaded coin URL: {url}")
        except Exception as e:
            print(f"Failed to load coin URL: {e}")
            continue
        
        try:
            # Dismiss cookie consent if it appears
            try:
                cookie_accept = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "cookie-consent-accept"))
                )
                cookie_accept.click()
                print("Dismissed cookie consent")
                time.sleep(1)
            except:
                pass  # Cookie consent not found
            
            WebDriverWait(driver, 60).until(  # Increased timeout to 60 seconds
                EC.presence_of_element_located((By.ID, "pools"))
            )
            print("Pools table found")
            time.sleep(3)  # Allow JavaScript to render
            
            pools_table = driver.find_element(By.ID, "pools")
            tbody = pools_table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            print(f"Found {len(rows)} pool rows")
        except TimeoutException:
            print(f"Timed out waiting for pools table for {coin_display_name}")
            continue
        except Exception as e:
            print(f"Error loading pools for {coin_display_name}: {e}")
            continue
        
        headers = [
            "Rank", "Country", "Pool", "PoolFee", 
            "Daily PPS $ / 100 TH", "MinPay", "Miners", 
            "Hashrate", "Network %", "Blocks and Expected Block Diff", 
            "BlockHeight", "LastFound"
        ]
        
        coin_pools = []
        count = 0
        
        for row in rows:
            if "show1100" in row.get_attribute("class"):
                continue
                
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 3:
                    continue
                    
                row_data = []
                
                # Rank
                rank_text = clean_pool_text(cells[0].get_attribute("textContent")).strip('.')
                row_data.append(rank_text)
                
                # Country and Pool
                country_pool_text = clean_pool_text(cells[1].get_attribute("textContent"))
                country, pool = extract_country_and_pool(country_pool_text)
                pool = clean_pool_name(pool)
                row_data.append(country)
                row_data.append(pool)
                
                # PoolFee (cell 2)
                if len(cells) > 2:
                    text = clean_pool_text(cells[2].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # Daily PPS (cell 3)
                if len(cells) > 3:
                    text = clean_pool_text(cells[3].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # MinPay (cell 4)
                if len(cells) > 4:
                    text = clean_pool_text(cells[4].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # Miners (cell 5)
                if len(cells) > 5:
                    text = clean_pool_text(cells[5].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # Hashrate (cell 6)
                if len(cells) > 6:
                    text = clean_pool_text(cells[6].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # Network % (cell 7)
                if len(cells) > 7:
                    text = clean_pool_text(cells[7].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # Blocks and Expected Block Diff (cell 8)
                if len(cells) > 8:
                    text = clean_pool_text(cells[8].get_attribute("textContent"))
                    row_data.append(clean_blocks_data(text))
                else:
                    row_data.append("No Data")
                
                # BlockHeight (cell 9)
                if len(cells) > 9:
                    text = clean_pool_text(cells[9].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                # LastFound (cell 10)
                if len(cells) > 10:
                    text = clean_pool_text(cells[10].get_attribute("textContent"))
                    row_data.append(text if text else "No Data")
                else:
                    row_data.append("No Data")
                
                if any(row_data):
                    coin_pools.append(row_data)
                    count += 1
                
                if count >= 15:
                    break
            except Exception as e:
                print(f"Error processing pool row: {e}")
                continue
        
        # Save coin raw pool data to temp dir
        safe_name = re.sub(r'[^\w\-]', '_', coin_url_name)
        coin_file = os.path.join(RAW_POOLS_DIR, f"{safe_name}_pools.csv")
        
        try:
            with open(coin_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(coin_pools)
            
            print(f"  Saved {len(coin_pools)} pools for {coin_display_name}")
        except Exception as e:
            print(f"Failed to save pool data for {coin_display_name}: {e}")
        
        time.sleep(3)  # Avoid bot detection
    
    print("Pool scraping completed")

# Cleaning
def normalise_country(raw: str) -> str:
    token = raw.strip().split(",", 1)[0].strip().strip('"')
    upper = token.upper()
    if TWO_LETTER_COUNTRY.match(upper):
        return upper
    if upper in ACCEPTED_COUNTRIES:
        return token
    return "N/A"

def tidy_pool(name: str) -> str:
    name = name.replace("Multi-Coin", "").strip().strip('"')
    domain_pattern = re.compile(r'([a-zA-Z0-9-]+\.(?:com|io|net|org|info|biz|us|cn|uk|de))')
    matches = domain_pattern.findall(name)
    return matches[0] if matches else name

def clean_single_file(in_path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    try:
        with open(in_path, newline="", encoding="utf-8") as fin, \
             open(out_path, "w", newline="", encoding="utf-8") as fout:

            reader, writer = csv.reader(fin), csv.writer(fout)
            next(reader, None)  # Skip original header
            writer.writerow(KEEP_HEADER)

            for row in reader:
                if len(row) < max(KEEP_INDEXES) + 1:
                    continue

                cleaned = [row[i].strip() for i in KEEP_INDEXES]
                cleaned[1] = normalise_country(cleaned[1])
                cleaned[2] = tidy_pool(cleaned[2])
                writer.writerow(cleaned)
    except Exception as e:
        print(f"Error cleaning file {in_path}: {e}")

def clean_pool_data():
    print("\nCleaning pool data")
    cleaned_count = 0
    
    if not os.path.exists(RAW_POOLS_DIR):
        print(f"Raw pools directory not found: {RAW_POOLS_DIR}")
        return
    
    for fname in os.listdir(RAW_POOLS_DIR):
        if fname.lower().endswith(".csv"):
            in_path = os.path.join(RAW_POOLS_DIR, fname)
            out_path = os.path.join(CLEANED_POOLS_DIR, fname)
            
            if not os.path.exists(in_path):
                print(f"File not found: {in_path}")
                continue
                
            try:
                clean_single_file(in_path, out_path)
                cleaned_count += 1
                print(f"  Cleaned {fname}")
            except Exception as e:
                print(f"Failed to clean {fname}: {e}")
    
    print(f"Cleaned {cleaned_count} pool files")

# Robust driver setup with virtual display
def setup_driver():
    print("Setting up virtual display and Firefox driver")
    
    # Start virtual display
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    print("Virtual display started")
    
    try:
        # Configure Firefox options
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Set explicit paths
        options.binary_location = "/usr/bin/firefox"
        service = FirefoxService(
            executable_path="/usr/local/bin/geckodriver",
            log_path=os.path.join(os.getcwd(), "geckodriver.log")  # Log file for debugging
        )
        
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(90)  # Increased page load timeout
        driver.implicitly_wait(10)  # Implicit wait for elements
        print("Firefox driver initialized successfully")
        return driver, display
    except Exception as e:
        print(f"Firefox setup failed: {e}")
        traceback.print_exc()
        display.stop()
        raise RuntimeError("Failed to initialize WebDriver")

def main():
    start_time = time.time()
    driver = None
    display = None
    
    try:
        driver, display = setup_driver()
        
        top_coins_data = scrape_top_coins(driver)
        
        if not top_coins_data:
            print("No coins found, exiting")
            return
        
        scrape_coin_pools(driver, top_coins_data)
        
        clean_pool_data()
        
        # Completion stats
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        print("\nCompleted in:")
        print(f"  {minutes} minutes and {seconds} seconds")
        print("\nOutputs at:")
        print(f"  Top coins: {os.path.abspath(os.path.join(FINAL_OUTPUT_DIR, 'Top20Coins.csv'))}")
        print(f"  Cleaned pools: {os.path.abspath(CLEANED_POOLS_DIR)}/")
        
    except Exception as e:
        print(f"Script failed: {e}")
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed")
            except:
                pass
        if display:
            try:
                display.stop()
                print("Virtual display stopped")
            except:
                pass

if __name__ == "__main__":
    main()