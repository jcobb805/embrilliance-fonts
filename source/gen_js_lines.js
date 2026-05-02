const fs = require('fs');
const path = require('path');

const m = JSON.parse(fs.readFileSync(
  path.join(__dirname, '..', 'samples', 'kristina_fonts.json'), 'utf8'
));

const officialNames = new Set([
  'bauhaus','block','bold cursive','comedy','jazz','mgm diamond','old english',
  'philly','roman','stencil','stuyvesant','university','august','brittany',
  'chalk board','circus','connecting script','dallas','diana','fancy script',
  'giddyup','isadora','mgm rounded','pacific stick','penny','roman tall',
  'script','sierra','sweet script connected','vacant','2 color varsity',
  'awesome dots','brand iron','exotic','florida','frisco','full block',
  'hobo','kids','leaf','lilith','mel script','parlor','pearl','reggae',
  'scarboro','shadow','studio','tackle twill','worms'
]);

const lines = m.map(f => {
  let displayName = f.name;
  if (officialNames.has(f.name.toLowerCase())) {
    displayName = f.name + ' (Stitched)';
  }
  const safeName = displayName.replace(/'/g, "\\'");
  return `  { name: '${safeName}', collection: 'My Library', category: '${f.category}', min: null, max: null, googleFont: null, img: '${f.image}', multiColor: ${f.multi_color} },`;
});

fs.writeFileSync(path.join(__dirname, 'kristina_lines.txt'), lines.join('\n'));
console.log(`Wrote ${lines.length} lines`);
console.log('Block-related:', lines.filter(l => l.includes('Block')).length);
console.log('Shadow-related:', lines.filter(l => l.includes('Shadow')).length);
