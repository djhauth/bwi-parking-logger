import os
from datetime import datetime
import pytz
import requests

API_URL = "https://bwiairport.com/wp-admin/admin-ajax.php"
CSV_FILE = "bwi_parking_data.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}

PAYLOAD = {"action": "get_parking_data"}


def main():
  tz = pytz.timezone("US/Eastern")
  timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

  try:
    response = requests.post(
        API_URL, data=PAYLOAD, headers=HEADERS, timeout=15
    )
    response.raise_for_status()
    data = response.json()
  except Exception as e:
    print(f"Failed to fetch parking API: {e}")
    return

  try:
    hourly = data["counts"]["hourly"]
    available = int(hourly["available"])
    total = int(hourly["total"])
    occupied = total - available
  except (KeyError, TypeError, ValueError) as e:
    print(f"Error parsing hourly garage fields: {e}")
    return

  file_exists = os.path.isfile(CSV_FILE)
  with open(CSV_FILE, mode="a", encoding="utf-8") as f:
    if not file_exists:
      f.write("Timestamp_EDT,Available_Spots,Total_Spots,Occupied_Spots\n")
    f.write(f"{timestamp},{available},{total},{occupied}\n")

  print(
      f"[{timestamp}] Logged: {available} available of {total} total"
      f" ({occupied} occupied)."
  )


if __name__ == "__main__":
  main()
