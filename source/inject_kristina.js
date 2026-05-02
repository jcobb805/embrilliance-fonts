const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '..', 'index.html');
const linesPath = path.join(__dirname, 'kristina_lines.txt');

const html = fs.readFileSync(htmlPath, 'utf8');
const linesBlock = fs.readFileSync(linesPath, 'utf8').trimEnd();

// Find the closing ']; after Worms entry
const marker = '{ name: "Worms"';
const i = html.indexOf(marker);
if (i < 0) throw new Error('Could not find Worms entry');
const endBracket = html.indexOf('];', i);
if (endBracket < 0) throw new Error('Could not find end of FONTS array');

// If KRISTINA_FONTS already injected, replace it
const existingKBlock = html.match(/\n\nconst KRISTINA_FONTS = \[[\s\S]*?\n\];/);

const kBlock = `\n\nconst KRISTINA_FONTS = [\n${linesBlock}\n];`;

let updated;
if (existingKBlock) {
  updated = html.replace(existingKBlock[0], kBlock);
  console.log('Replaced existing KRISTINA_FONTS');
} else {
  // Insert after FONTS array's `];` line
  const insertAfter = endBracket + 2; // after `];`
  updated = html.slice(0, insertAfter) + kBlock + html.slice(insertAfter);
  console.log('Injected new KRISTINA_FONTS block');
}

fs.writeFileSync(htmlPath, updated);
console.log('Wrote', htmlPath);
