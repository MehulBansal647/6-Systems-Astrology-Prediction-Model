// Canonical iztro (JavaScript) Zi Wei Dou Shu calculation. Reads JSON args from argv[2].
// Usage: node src/ziwei_iztro.js '{"mode":"solar","date":"2001-5-29","timeIndex":9,"gender":"男","fixLeap":true,"horoscopeDates":["2026-11-09"]}'
const path = require('path');
const { astro } = require(path.join(__dirname, '..', 'js', 'node_modules', 'iztro'));
const args = JSON.parse(process.argv[2]);
astro.config({ yearDivide: 'normal', horoscopeDivide: 'normal' });
const lang = args.language || 'zh-CN';
let a;
if (args.mode === 'lunar') {
  a = astro.byLunar(args.date, args.timeIndex, args.gender, !!args.isLeapMonth, args.fixLeap !== false, lang);
} else {
  a = astro.bySolar(args.date, args.timeIndex, args.gender, args.fixLeap !== false, lang);
}
const out = {
  solarDate: a.solarDate, lunarDate: a.lunarDate, chineseDate: a.chineseDate, time: a.time, timeRange: a.timeRange,
  sign: a.sign, zodiac: a.zodiac, soulBranch: a.earthlyBranchOfSoulPalace, bodyBranch: a.earthlyBranchOfBodyPalace,
  soul: a.soul, body: a.body, fiveElementsClass: a.fiveElementsClass,
  palaces: a.palaces.map(p => ({
    index: p.index, name: p.name, isBodyPalace: p.isBodyPalace, isOriginalPalace: p.isOriginalPalace,
    heavenlyStem: p.heavenlyStem, earthlyBranch: p.earthlyBranch,
    majorStars: p.majorStars.map(s => ({ name: s.name, type: s.type, brightness: s.brightness || '', mutagen: s.mutagen || '' })),
    minorStars: p.minorStars.map(s => ({ name: s.name, type: s.type, brightness: s.brightness || '', mutagen: s.mutagen || '' })),
    decadal: p.decadal, ages: p.ages,
  })),
  horoscopes: {},
};
for (const d of (args.horoscopeDates || [])) {
  const h = a.horoscope(d);
  out.horoscopes[d] = {
    decadal: { index: h.decadal.index, heavenlyStem: h.decadal.heavenlyStem, earthlyBranch: h.decadal.earthlyBranch, mutagen: h.decadal.mutagen },
    age: { index: h.age.index, nominalAge: h.age.nominalAge },
    yearly: { index: h.yearly.index, heavenlyStem: h.yearly.heavenlyStem, earthlyBranch: h.yearly.earthlyBranch, mutagen: h.yearly.mutagen },
  };
}
process.stdout.write(JSON.stringify(out));
