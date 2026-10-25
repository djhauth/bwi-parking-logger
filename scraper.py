import os
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

URL = "https://bwiairport.com/to-from-bwi/parking/"
CSV_FILE = "bwi_parking_data.csv"

# Browser header to prevent bot blocking
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def main():
  # Eastern Time timestamp
  tz = pytz.timezone("US/Eastern")
  timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

  try:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
  except Exception as e:
    print(f"Failed to reach BWI site: {e}")
    return

  soup = BeautifulSoup(response.text, "html.parser")

  # Target the exact tags from the live site
  avail_el = soup.find("span", attrs={"data-key": "hourly__available"})
  total_el = soup.find("span", attrs={"data-key": "hourly__total"})

  if not avail_el or not total_el:
    print("Could not find parking data elements on the page.")
    return

  avail_text = avail_el.get_text(strip=True).replace(",", "")
  total_text = total_el.get_text(strip=True).replace(",", "")

  try:
    available = int(avail_text)
    total = int(total_text)
    occupied = total - available
  except ValueError:
    print(f"Non-numeric values found: {avail_text}, {total_text}")
    return

  # Create CSV header if file doesn't exist yet
  file_exists = os.path.isfile(CSV_FILE)
  with open(CSV_FILE, mode="a", encoding="utf-8") as f:
    if not file_exists:
      f.write("Timestamp_EDT,Available_Spots,Total_Spots,Occupied_Spots\n")
    f.write(f"{timestamp},{available},{total},{occupied}\n")

  print(
      f"[{timestamp}] Successfully logged: {available} available, {occupied}"
      f" occupied."
  )


if __name__ == "__main__":
  main()
