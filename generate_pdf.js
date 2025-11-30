const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Navigate to the HTML file
    const htmlPath = path.join(__dirname, 'ProfitLift_HolyGrail_Book.html');
    await page.goto(`file://${htmlPath}`, {
        waitUntil: 'networkidle0',
        timeout: 60000
    });

    // Wait for Mermaid to render
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Wait for all mermaid diagrams to be rendered
    await page.evaluate(() => {
        return new Promise((resolve) => {
            if (typeof mermaid !== 'undefined') {
                mermaid.run().then(() => {
                    setTimeout(resolve, 2000);
                });
            } else {
                setTimeout(resolve, 2000);
            }
        });
    });

    // Generate PDF with proper settings
    await page.pdf({
        path: 'ProfitLift_Complete_Documentation.pdf',
        format: 'A4',
        printBackground: true,
        preferCSSPageSize: true,
        displayHeaderFooter: false,
        // Margins are handled by CSS @page rule for better control
        margin: {
            top: 0,
            right: 0,
            bottom: 0,
            left: 0
        }
    });

    await browser.close();
    console.log('PDF generated successfully with Mermaid diagrams!');
})();
