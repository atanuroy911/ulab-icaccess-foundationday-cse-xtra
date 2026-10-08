/**
 * PDF Generator for ULAB 23rd Foundation Day AI-or-Human Cue Cards
 * 
 * Usage:
 *   node generate_pdf.js [setsCount] [shuffle]
 * 
 * Examples:
 *   node generate_pdf.js 20 true   <- Generates 20 sets of cards, shuffled, into one PDF.
 *   node generate_pdf.js 1 false   <- Generates 1 set, not shuffled.
 */

const puppeteer = require('puppeteer');
const path = require('path');

const HTML_FILE = path.resolve(__dirname, 'cue_cards_generator.html');

async function generatePDF(setsCount, shuffle) {
  console.log(`\n🖨️  Generating PDF with ${setsCount} sets (Shuffle: ${shuffle})...`);
  console.log(`⏳ This might take a few minutes for large sets like 20...`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();

  // Load the generator HTML file (unlimited timeout for large renders)
  await page.goto(`file://${HTML_FILE}`, { waitUntil: 'networkidle0', timeout: 0 });

  // Wait for Google Fonts to load
  await new Promise(r => setTimeout(r, 2000));

  // Set the inputs and trigger generation
  await page.evaluate((sets, shuf) => {
    document.getElementById('setsCount').value = sets;
    document.getElementById('shuffleCards').checked = shuf;
    generateCards(); // defined in the HTML
  }, setsCount, shuffle);

  // Wait a generous moment for DOM to render 600+ elements
  await new Promise(r => setTimeout(r, 5000));

  let shuffleStr = shuffle ? '_shuffled' : '';
  const outputFile = path.resolve(__dirname, `ULAB_Foundation_Day_Cue_Cards_${setsCount}sets${shuffleStr}.pdf`);

  await page.pdf({
    path: outputFile,
    format: 'A4',
    printBackground: true,
    margin: { top: '10mm', right: '10mm', bottom: '10mm', left: '10mm' },
    timeout: 0 // Unlimited timeout for PDF generation
  });

  await browser.close();
  console.log(`✅ PDF saved: ${outputFile}`);
  return outputFile;
}

async function main() {
  let sets = parseInt(process.argv[2]) || 20; // default 20 sets
  let shuffle = process.argv[3] === 'true';   // default false unless 'true' provided

  await generatePDF(sets, shuffle);
  console.log('\n🎉 PDF generated successfully!');
}

main().catch(console.error);
