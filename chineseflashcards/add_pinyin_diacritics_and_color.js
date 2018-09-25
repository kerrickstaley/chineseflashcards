var DIACRITIC_VOWELS = [
  ['ā', 'á', 'ǎ', 'à', 'a'],
  ['ē', 'é', 'ě', 'è', 'e'],
  ['ī', 'í', 'ǐ', 'ì', 'i'],
  ['ō', 'ó', 'ǒ', 'ò', 'o'],
  ['ū', 'ú', 'ǔ', 'ù', 'u'],
  ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'],
];

function diacriticVowel(vowel, tone) {
  for (var idx = 0; idx < DIACRITIC_VOWELS.length; idx++) {
    var row = DIACRITIC_VOWELS[idx];
    if (row[4] == vowel) {
      return row[tone - 1];
    }
  }
}

function diacriticSyl(syl) {
  var rv = [];
  var tone = parseInt(syl[syl.length - 1]);
  var curr = syl[0];
  var toned = false;
  for (var idx = 1; idx < syl.length; idx++) {
    var next = syl[idx];
    if (curr == 'u' && next == ':') {
      curr = 'ü';
      continue;
    }
    if (curr == 'a'
        || curr == 'e'
        || !toned && curr == 'o' && next == 'u'
        || !toned && 'aeiouü'.indexOf(curr) != -1 && 'aeiouü'.indexOf(next) == -1) {
      rv.push(diacriticVowel(curr, tone));
      toned = true;
    } else {
      rv.push(curr);
    }
    curr = next;
  }
  return rv.join('');
}

function prettifyPinyin(pinyin) {
  return pinyin.split(' ').map(function(syl) {
    if (isNaN(parseInt(syl[syl.length - 1]))) {
      syl += '5';
    }
    return '<span class="tone' + syl[syl.length - 1] + '">' + diacriticSyl(syl) + '</span>';
  }).join(' ');
}

function main() {
  var root = document.querySelector('.pinyin');
  if (root.children.length > 0) {
    // presumably already styled, so bail out
    return;
  }
  if (root.textContent.indexOf('|') != -1) {
    // TODO handle styling Taiwan Pinyin
    return;
  }
  root.innerHTML = prettifyPinyin(root.textContent.trim());
}

// BEGIN TESTS

var testCases = [
  ["diacriticVowel('a', 3)", 'ǎ'],
  ["diacriticVowel('e', 5)", 'e'],
  ["diacriticVowel('ü', 2)", 'ǘ'],
  ["diacriticSyl('ni3')", 'nǐ'],
  ["diacriticSyl('hao3')", 'hǎo'],
  ["diacriticSyl('lu:4')", 'lǜ'],
  ["diacriticSyl('ge5')", 'ge'],
  ["prettifyPinyin('he1 dian3 lu:4 cha2 ba5')",
   '<span class="tone1">hē</span>'
   + ' <span class="tone3">diǎn</span>'
   + ' <span class="tone4">lǜ</span>'
   + ' <span class="tone2">chá</span>'
   + ' <span class="tone5">ba</span>'],
  ["prettifyPinyin('ge de')",
   '<span class="tone5">ge</span>'
   + ' <span class="tone5">de</span>'],
];

var passed = 0;
testCases.forEach(function(testCase) {
  var actual = eval(testCase[0]);
  if (eval(testCase[0]) == testCase[1]) {
    passed += 1;
  } else {
    console.log('TEST CASE FAILED: evaluated ' + testCase[0] + ' expected ' + testCase[1] + ' actual ' + actual);
  }
});
console.log('add_pinyin_diacritics_and_color.js: '
            + passed.toString()
            + '/'
            + testCases.length.toString()
            + ' cases passed');
process.exit(passed == testCases.length ? 0 : 1);
