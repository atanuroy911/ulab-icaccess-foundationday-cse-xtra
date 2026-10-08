const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('json') || url.includes('api')) {
      try {
        const text = await response.text();
        console.log('Intercepted:', url, text.substring(0, 200));
      } catch (e) {}
    }
  });

  console.log('Navigating to sightengine...');
  await page.goto('https://sightengine.com/which-image-is-ai', { waitUntil: 'networkidle2' });
  
  // click the first image to trigger next round
  await page.waitForTimeout(2000);
  try {
    await page.evaluate(() => {
      let imgs = document.querySelectorAll('img');
      if(imgs.length > 0) imgs[0].click();
    });
  } catch(e) {}
  
  await page.waitForTimeout(2000);
  
  await browser.close();
})();
