const fs = require('fs');
const path = require('path');

const INPUT = path.resolve(__dirname, 'map_backup_working.html');
const OUTPUT = path.resolve(__dirname, 'map_backup_working_ar.html');

let txt;
try {
  txt = fs.readFileSync(INPUT, 'utf8');
} catch (e) {
  console.error('Error reading input file:', e.message);
  process.exit(2);
}

const replacements = {
  'January': 'يناير', 'Jan': 'يناير',
  'February': 'فبراير', 'Feb': 'فبراير',
  'March': 'مارس', 'Mar': 'مارس',
  'April': 'أبريل', 'Apr': 'أبريل',
  'May': 'مايو',
  'June': 'يونيو', 'Jun': 'يونيو',
  'July': 'يوليو', 'Jul': 'يوليو',
  'August': 'أغسطس', 'Aug': 'أغسطس',
  'September': 'سبتمبر', 'Sept': 'سبتمبر', 'Sep': 'سبتمبر',
  'October': 'أكتوبر', 'Oct': 'أكتوبر',
  'November': 'نوفمبر', 'Nov': 'نوفمبر',
  'December': 'ديسمبر', 'Dec': 'ديسمبر'
};

// Replace whole words only, case-sensitive for common abbreviations in the file.
for (const [eng, ar] of Object.entries(replacements)) {
  // Use word boundaries and escape the English string for regex
  const esc = eng.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp('\\b' + esc + '\\b', 'g');
  txt = txt.replace(re, ar);
}

try {
  fs.writeFileSync(OUTPUT, txt, 'utf8');
  console.log('Wrote translated file:', OUTPUT);
} catch (e) {
  console.error('Error writing output file:', e.message);
  process.exit(3);
}
