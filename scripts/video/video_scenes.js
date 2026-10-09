// Video scenes: storyboard layouts plus timing. Every time is derived from the
// measured phrases of the current recording (analysis/transcript.json):
// P(n) = start of phrase n, E(n) = its end, SEG(n, k) = start of its k-th VAD
// segment, AT(n, f) = a fraction f into the phrase. Beats inside a phrase are
// visual pacing only; on-screen text changes only at measured phrase starts.
const base = Object.fromEntries(require('../storyboard/scenes.js').map((s) => [s.id, s]));
const TR = require('../../analysis/transcript.json');
const PH = Object.fromEntries(TR.phrases.map((p) => [p.id, p]));
const P = (n) => PH[n].start;
const E = (n) => PH[n].end;
const SEG = (n, k) => PH[n].vad_segments[k][0];
const AT = (n, f) => +(P(n) + f * (E(n) - P(n))).toFixed(3);
const CUT = (a) => +((E(a) + P(a + 1)) / 2).toFixed(2); // mid-silence between phrase a and a+1

const HOST = [60, 420, 960, 470];
const PHONE_V2 = [316, 410, 448, 780];
const PHONE_V1 = [452, 410, 448, 780];
const INSET = [620, 680, 300, 514];
const SIDE_V2 = [40, 470, 250, 430];
const SIDE_V1 = [90, 440, 250, 430];

const phone = (img, extra = {}) => ({ kind: 'phone', img, pos: 'top', ...extra });
const host = (img, extra = {}) => ({ kind: 'host', img, ...extra });

const V = {
  S05: { stage: [host('G_26.5.png', { box: HOST }), phone('A01.png', { box: INSET, appear: AT(4, 0.5) })] },
  S06: { stage: [host('B02_pxqr.png', { box: HOST }), phone(null, { box: INSET, appear: SEG(5, 1), seq: [[SEG(5, 1), 'A04.png'], [AT(5, 0.72), 'A05.png']] })] },
  S07: { stage: [phone('A10.png', { box: PHONE_V2 })], stageV1: [phone('A10.png', { box: PHONE_V1 })], redflash: P(6) },
  S08: { stage: [phone('A11.png', { box: SIDE_V2 }), phone('A12.png', { box: PHONE_V2, appear: AT(7, 0.28) })],
         stageV1: [phone('A11.png', { box: SIDE_V1 }), phone('A12.png', { box: PHONE_V1, appear: AT(7, 0.28) })],
         meter: { from: P(7), to: E(7) } },
  S09: { stage: [phone(null, { box: PHONE_V2, seq: [[P(8), 'A12.png'], [AT(8, 0.48), 'A13.png']] })],
         stageV1: [phone(null, { box: PHONE_V1, seq: [[P(8), 'A12.png'], [AT(8, 0.48), 'A13.png']] })] },
  S10: { stage: [phone('A14.png', { box: PHONE_V2, shake: [P(9), E(9)] })], stageV1: [phone('A14.png', { box: PHONE_V1, shake: [P(9), E(9)] })] },
  S11: { stage: [phone('A15.png', { box: PHONE_V2 }), phone('A18.png', { box: SIDE_V2, appear: P(11) })],
         stageV1: [phone('A15.png', { box: PHONE_V1 }), phone('A18.png', { box: SIDE_V1, appear: P(11) })] },
  S12: { stage: [host('G_25.3.png', { box: HOST })] },
  S13: { stage: [host('B04_pxqr.png', { box: HOST })] },
  S14: { stage: [phone(null, { box: PHONE_V2, seq: [[P(14), 'C02.png'], [P(15), 'C01.png']] })],
         stageV1: [phone(null, { box: PHONE_V1, seq: [[P(14), 'C02.png'], [P(15), 'C01.png']] })],
         // two pixel players facing each other, larger in the video (free space beside the phone)
         extrasV1: [{ type: 'blind', x: 52, y: 690, scale: 6 }],
         extrasV2: [{ type: 'blind', x: 18, y: 680, scale: 4.6 }] },
  S15: { stage: [host(null, { box: HOST, seq: [[P(16), 'B04_pxqr.png'], [P(17), 'B05.png']] })], chipsUntil: P(17) },
  S16: { stage: [host('G_movies_noprice.png', { box: [60, 430, 960, 330], pos: 'top' })] },
  S17: { stage: [host(null, { box: HOST, seq: [[P(20), 'C04.png'], [AT(20, 0.45), 'C05.png']] })] },
  S18: { stage: [host(null, { box: HOST, seq: [[CUT(20), 'C03.png'], [P(22), 'G_33.5.png']] })] },
};

// captions per phrase: V2 = full text with highlight markup (must equal
// screen_text once markers are removed); V1 = keyword (a piece of it)
const CAPTIONS = {
  4: ['هذي لعبة [[الأمبوستر]] في فانوس!', 'لعبة [[الأمبوستر]]'],
  5: ['تمسحون الـ[[QR Code]]، والكل يعرف الشي اللي طلع له…', 'والكل يعرف [[الشي اللي طلع له]]'],
  6: [null, 'إلا [[واحد!]]'],
  7: ['تبدأ جولة الأسئلة، وكل جواب [[يزيد الشك.]]', 'كل جواب [[يزيد الشك]]'],
  8: ['وبعدها [[التصويت…]]', 'وبعدها [[التصويت…]]'],
  9: [null, 'منو [[الأمبوستر؟]]'],
  10: ['يمكن [[أقرب واحد لك]]', 'يمكن [[أقرب واحد لك]]'],
  11: ['[[قاعد يقص عليك!]]', '[[قاعد يقص عليك!]]'],
  12: ['وعندك [[«بدون لا أشوف»!]]', '[[«بدون لا أشوف»!]]'],
  13: ['أنت وواحد من ربعك تمسحون الـ[[QR Code]]،', 'تمسحون الـ[[QR Code]]'],
  14: ['وكل واحد يوجّه [[شاشة تليفونه]] للثاني،', 'يوجّه [[شاشة تليفونه]] للثاني،'],
  15: ['[[بدون ما يشوف]] شنو طلع له.', '[[بدون ما يشوف]] شنو طلع له.'],
  16: ['تسألون أسئلة إجابتها [[نعم]] أو [[لا…]]', 'إجابتها [[نعم]] أو [[لا…]]'],
  17: ['لين تعرفون [[شنو الشي]] اللي عندكم!', 'لين تعرفون [[شنو الشي]]'],
  18: ['تحب فيلم وتقول [[حافظه؟]]', 'تحب فيلم وتقول [[حافظه؟]]'],
  19: ['[[«فانوس Movies»]]', '[[«فانوس Movies»]]'],
  20: ['يتحدّاك بأسئلة عن [[الفيلم نفسه وأحداثه!]]', '[[الفيلم نفسه وأحداثه!]]'],
  21: ['والصغار لهم [[وناستهم]] بعد،', 'والصغار لهم [[وناستهم]]'],
  22: ['مع فئات ممتعة وتفاعلية في [[«فانوس Kids»!]]', 'في [[«فانوس Kids»!]]'],
  23: ['جمّع [[ربعك وأهلك]]،', 'جمّع [[ربعك وأهلك]]،'],
  24: ['[[وخلّ التحدّي يبدأ!]]', '[[وخلّ التحدّي يبدأ!]]'],
};

const scenes = Object.values(base).map((s) => ({ ...s, ...(V[s.id] || {}) }));
module.exports = { scenes, CAPTIONS };
