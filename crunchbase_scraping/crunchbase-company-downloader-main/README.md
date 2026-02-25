
***

# Crunchbase Search Results Scraper

This is a simple browser console script designed to scrape company data from a single Crunchbase search results page and download it as a CSV file.

The script is intended for quick, manual data extraction on a page-by-page basis.

---

## Features

* **Scrapes the Current Page**: Extracts data from all company rows currently visible on a Crunchbase search results page.
* **Key Data Fields**: Captures essential company information based on the visual order of the columns:
    * Organization Name
    * Industries
    * Founded Date
    * Last Funding Type
    * Headquarters Location
    * Description
    * CB Rank (Organization & Company)
    * Stage
    * Website
* **CSV Export**: Converts the scraped data into a clean, ready-to-use CSV format.
* **Automatic Download**: Triggers a file download directly from the browser.
* **Smart File Naming**: Automatically detects the page number and names the file accordingly (e.g., `crunchbase_page_1.csv`, `crunchbase_page_2.csv`, etc.) to keep your downloads organized.

---

## How to Use

Follow these steps to use the script:

1.  **Navigate to Crunchbase**: Go to the search results page you want to scrape.
2.  **Load All Results**: Scroll to the very bottom of the page to ensure all 50 results are loaded in the browser.
3.  **Open Developer Console**:
    * **Mac**: `Cmd + Option + J`
    * **Windows/Linux**: `Ctrl + Shift + J`
4.  **Copy & Paste Script**: Copy the entire contents of the `scrapeCurrentPage.js` script.
5.  **Run Script**: Paste the script into the console and press **Enter**.
6.  **Download**: A CSV file will be downloaded to your computer automatically.
7.  **Repeat for Next Pages**: To scrape more data, manually click the "Next" button on the Crunchbase page and repeat steps 2-5.



---

## Important Limitations

Please be aware of the following limitations before using the script:

* **Manual Page-by-Page Process**: This script **cannot** automatically navigate between pages. It is designed to be run manually on each page you wish to scrape.
* **Fragile by Nature**: The script relies on the specific HTML structure and CSS class names of the Crunchbase website. **If Crunchbase updates its website layout, this script will likely break** and will need to be updated.
* **Dependent on Column Order**: The script extracts data based on the *position* of the columns (e.g., column 2 is the name, column 3 is industries, etc.). If you add, remove, or reorder the columns on the Crunchbase website, the script will extract incorrect data into the wrong CSV columns.

---

## Disclaimer

This script is intended for educational and personal use. Please be responsible and respect the Crunchbase Terms of Service. Automated or excessive scraping can put a strain on their servers and may lead to your IP address being blocked.
