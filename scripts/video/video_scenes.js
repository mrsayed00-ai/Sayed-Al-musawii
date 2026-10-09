// Video scenes: storyboard layouts plus timing (absolute seconds on the voice
// timeline). Beats inside a phrase are visual pacing only; on-screen text
// changes only at measured phrase starts.
const base = Object.fromEntries(require('../storyboard/scenes.js').map((s) => [s.id, s]));

const HOST = [60, 420, 960, 470];
const PHONE_V2 = [316, 410, 448, 780];
const PHONE_V1 = [452, 410, 448, 780];
const INSET = [620, 680, 300, 514];
const SIDE_V2 = [40, 470, 250, 430];
const SIDE_V1 = [90, 440, 250, 430];

const phone = (img, extra = {}) => ({ kind: 'phone', img, pos: 'top', ...extra });
const host = (img, extra = {}) => ({ kind: 'host', img, ...extra });

const V = {
  S05: { stage: [host('G_26.5.png', { box: HOST }), phone('A01.png', { box: INSET, appear: 6.9 })] },
  S06: { stage: [host('B02_pxqr.png', { box: HOST }), phone(null, { box: INSET, appear: 9.0, seq: [[9.0, 'A04.png'], [9.9, 'A05.png']] })] },
  S07: { stage: [phone('A10.png', { box: PHONE_V2 })], stageV1: [phone('A10.png', { box: PHONE_V1 })], redflash: 11.43 },
  S08: { stage: [phone('A11.png', { box: SIDE_V2 }), phone('A12.png', { box: PHONE_V2, appear: 13.3 })],
         stageV1: [phone('A11.png', { box: SIDE_V1 }), phone('A12.png', { box: PHONE_V1, appear: 13.3 })],
         meter: { from: 12.52, to: 15.27 } },
  S09: { stage: [phone(null, { box: PHONE_V2, seq: [[15.69, 'A12.png'], [16.15, 'A13.png']] })],
         stageV1: [phone(null, { box: PHONE_V1, seq: [[15.69, 'A12.png'], [16.15, 'A13.png']] })] },
  S10: { stage: [phone('A14.png', { box: PHONE_V2, shake: [17.23, 18.09] })], stageV1: [phone('A14.png', { box: PHONE_V1, shake: [17.23, 18.09] })] },
  S11: { stage: [phone('A15.png', { box: PHONE_V2 }), phone('A18.png', { box: SIDE_V2, appear: 20.23 })],
         stageV1: [phone('A15.png', { box: PHONE_V1 }), phone('A18.png', { box: SIDE_V1, appear: 20.23 })] },
  S12: { stage: [host('G_25.3.png', { box: HOST })] },
  S13: { stage: [host('B04_pxqr.png', { box: HOST })] },
  S14: { stage: [phone(null, { box: PHONE_V2, seq: [[27.18, 'C02.png'], [29.58, 'C01.png']] })],
         stageV1: [phone(null, { box: PHONE_V1, seq: [[27.18, 'C02.png'], [29.58, 'C01.png']] })],
         // two pixel players facing each other, larger in the video (free space beside the phone)
         extrasV1: [{ type: 'blind', x: 52, y: 690, scale: 6 }],
         extrasV2: [{ type: 'blind', x: 18, y: 680, scale: 4.6 }] },
  S15: { stage: [host(null, { box: HOST, seq: [[31.82, 'B04_pxqr.png'], [34.25, 'B05.png']] })], chipsUntil: 34.25 },
  S16: { stage: [host('G_movies_noprice.png', { box: [60, 430, 960, 330], pos: 'top' })] },
  S17: { stage: [host(null, { box: HOST, seq: [[40.84, 'C04.png'], [42.0, 'C05.png']] })] },
  S18: { stage: [host(null, { box: HOST, seq: [[43.85, 'C03.png'], [46.38, 'G_33.5.png']] })] },
};

// captions per phrase: V2 = full text with highlight markup (must equal
// screen_text once markers are removed); V1 = keyword (a piece of it)
const CAPTIONS = {
  4: ['هذي لعبة [[الأمبوستر]] في فانوس!', 'لعبة [[الأمبوستر]]'],
  5: ['تمسحون الـ[[QR Code]]، وكل واحد يعرف شنو الشي اللي طلع له…', 'كل واحد يعرف [[شنو الشي]]'],
  6: [null, 'إلا [[واحد!]]'],
  7: ['تبدأ جولة الأسئلة، وكل جواب [[يزيد الشك.]]', 'كل جواب [[يزيد الشك]]'],
  8: ['وبعدها [[التصويت…]]', 'وبعدها [[التصويت…]]'],
  9: [null, 'منو [[الأمبوستر؟]]'],
  10: ['يمكن [[أقرب واحد لك]]', 'يمكن [[أقرب واحد لك]]'],
  11: ['[[قاعد يقص عليك!]]', '[[قاعد يقص عليك!]]'],
  12: ['وطبعاً عندك فئة [[«بدون لا أشوف»!]]', 'فئة [[«بدون لا أشوف»]]'],
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
