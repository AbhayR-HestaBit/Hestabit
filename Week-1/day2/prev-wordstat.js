#!/usr/bin/env node

const args= process.argv.slice(2);

function parseArgs(args) {
const options ={
file:null,
top:10,
minLen:1,
unique:false,
};

for (let i =0; i< args.length; i++) {
const arg = args[i];

if (arg === "--file") {
options.file = args[++i];
} else if (arg === "--top") {
options.top = Number(args[++i]);
} else if (arg === "--minLen") {
options.minLen = NUmber(args[++i]);
} else if (arg === "--unique") {
options.unique = true;
}
}
return options;
}

const options = parseArgs(args);
console.log("Parsed options:", options);
