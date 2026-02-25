// This script scrapes the current page and saves the data to a uniquely named CSV file.
async function scrapeCurrentPage() {
    console.log("Starting scrape...");

    // --- Part 1: Data Extraction ---
    const companyRows = document.querySelectorAll("grid-row");
    if (companyRows.length === 0) {
        return console.error("No company rows found.");
    }

    console.log(`Found ${companyRows.length} companies on this page. Extracting data...`);
    const scrapedData = [];

    companyRows.forEach(row => {
        const getCellText = colNumber => {
            const cell = row.querySelector(`grid-cell:nth-child(${colNumber})`);
            return cell ? cell.innerText.trim().replace(/\n/g, ' | ') : "";
        };

        scrapedData.push({
            organizationName: getCellText(2),
            industries: getCellText(3),
            foundedDate: getCellText(4),
            lastFundingType: getCellText(5),
            headquartersLocation: getCellText(6),
            description: getCellText(7),
            cbRankOrg: getCellText(8),
            stage: getCellText(9),
            cbRankCompany: getCellText(10),
            website: getCellText(11),
        });
    });

    // --- Part 2: Convert to CSV and Download ---
    if (scrapedData.length === 0) {
        return console.log("Extraction complete, but no data was found.");
    }
    
    // Automatically detect page number for the filename
    let pageNum = "1";
    const activePageElement = document.querySelector('a.mat-button-base.mat-paginator-navigation-next + a');
    if (activePageElement) {
        pageNum = activePageElement.innerText.trim();
    } else {
        pageNum = prompt("Could not auto-detect page number. Please enter the current page number:", "1");
    }
    const fileName = `crunchbase_page_${pageNum}.csv`;

    const header = Object.keys(scrapedData[0]).join(",");
    const rows = scrapedData.map(obj =>
        Object.values(obj).map(val => `"${String(val).replace(/"/g, '""')}"`).join(",")
    );

    const csvContent = [header, ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    console.log(`Success! Downloaded ${scrapedData.length} rows to ${fileName}.`);
}

scrapeCurrentPage();
