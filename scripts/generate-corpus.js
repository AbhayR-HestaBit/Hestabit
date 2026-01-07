const fs = require("fs");
const WORD_COUNT = 250_000;
const output = fs.createWriteStream("data/corpus.txt");

let written =0;

function write() {
let ok = true;

while (written< WORD_COUNT && ok) {
const word = `word${written} `;
ok = output.write(word);
written++;
}

if (written <WORD_COUNT) {
output.once("drain", write);
}else{
output.end();
console.log("Corpus generated:", written, "words");
}
}

write();
