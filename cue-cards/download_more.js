const https = require('https');
const fs = require('fs');
const path = require('path');

const newPairs = [
  {
    "topic": "Hospital room with beds",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/98.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/98.webp",
    "aiSide": "left"
  },
  {
    "topic": "Woman taking a mirror selfie in bedroom",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/21.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/21.webp",
    "aiSide": "right"
  },
  {
    "topic": "Classroom with empty student desks",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/119.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/119.webp",
    "aiSide": "left"
  },
  {
    "topic": "People crossing a busy city street",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/32.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/32.webp",
    "aiSide": "left"
  },
  {
    "topic": "Close up macro shot of a human eye",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/96.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/96.webp",
    "aiSide": "right"
  },
  {
    "topic": "Person riding a bicycle on a city street",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/14.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/14.webp",
    "aiSide": "left"
  },
  {
    "topic": "Barista making coffee at an espresso machine",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/43.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/43.webp",
    "aiSide": "right"
  },
  {
    "topic": "Eating crepes at a café table",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/6.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/6.webp",
    "aiSide": "right"
  },
  {
    "topic": "Woman taking a photo outdoors in city",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/65.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/65.webp",
    "aiSide": "left"
  },
  {
    "topic": "Hanging disco balls with red/blue lighting",
    "leftUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/real3/109.webp",
    "rightUrl": "https://s3.eu-west-1.amazonaws.com/static.sightengine.com/ai-or-not/ai3/109.webp",
    "aiSide": "right"
  }
];

const downloadFile = (url, dest) => {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => reject(err));
    });
  });
};

async function main() {
  const imagesDir = path.join(__dirname, 'images');
  if (!fs.existsSync(imagesDir)) fs.mkdirSync(imagesDir);

  for (let i = 0; i < newPairs.length; i++) {
    const pairNum = i + 11; // We already have 1 to 10
    const p = newPairs[i];
    
    console.log(`Downloading Pair ${pairNum}...`);
    await downloadFile(p.leftUrl, path.join(imagesDir, `pair${pairNum}_left.webp`));
    await downloadFile(p.rightUrl, path.join(imagesDir, `pair${pairNum}_right.webp`));
  }
  console.log('All downloads completed!');
}

main().catch(console.error);
