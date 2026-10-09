// Storyboard scenes S01–S20 on the measured phrase timeline (analysis/transcript.json).
// Text markup: [[...]] = yellow highlight, {{...}} = purple highlight. Every on-screen
// text is checked against the phrases' screen_text by render.js.
const HOST = [60, 420, 960, 470];
const PHONE_V2 = [316, 410, 448, 780];
const PHONE_V1 = [452, 410, 448, 780];
const INSET = [620, 680, 300, 514];
const H_IMP = { text: 'الأمبوستر', step: '01', color: 'var(--red)', ink: '#fff' };
const H_BLIND = { text: 'بدون لا أشوف', step: '02', color: 'var(--green)', ink: '#fff' };
const H_MOV = { text: 'فانوس Movies', step: '03' };
const H_KIDS = { text: 'فانوس Kids', step: '04', color: 'var(--kids)', ink: '#fff' };
// «بدون لا أشوف» illustration: two pixel players facing each other (scripts/character/blind_illus.py)

module.exports = [
  {
    id: 'S01', t: [0, 1.0], phrases: [], layout: 'hook', glow: [540, 1150],
    pixels: { seed: 7, color: 'rgba(255,255,255,.85)', n: 30, area: [0, 0, 1080, 1920] },
    v1: { char: 'blink', charTop: 760 },
    v2: { logo: { top: 760, w: 760 } },
    beats: { V1: 'مربعات بكسل بيضاء تتفكك وتكشف الشخصية كبيرة، ثم رمشة.', V2: 'مربعات بكسل تتجمع إلى شعار فانوس ثم تتفكك نحو المشهد التالي.' },
    assets: '✅ الشعار، الشخصية',
  },
  {
    id: 'S02', t: [1.0, 2.41], phrases: [1], layout: 'hook', bgshot: 'G_26.5.png', glow: [540, 1150],
    v1: { bubble: 'في واحد بينكم [[مو عارف السالفة…]]', char: 'neutral_half' },
    v2: { lines: [{ t: 'في واحد بينكم', top: 600 }, { t: '[[مو عارف السالفة…]]', top: 760 }] },
    beats: { V1: 'فقاعة بنفسجية بنص العبارة، والشخصية تتكلم (الفم من شدة الصوت).', V2: 'نص كبير سطرين فوق بطاقات الأمبوستر مموّهة.' },
    assets: '✅ G05 (خلفية V2)',
  },
  {
    id: 'S03', t: [2.86, 4.1], phrases: [1, 2], layout: 'hook', bgshot: 'G_26.5.png', glow: [540, 1150],
    v1: { bubble: 'في واحد بينكم مو عارف السالفة…', strip: 'بس قاعد [[يمثّل]] إنه فاهم!', stripTop: 600, char: 'sly' },
    v2: { lines: [{ t: 'في واحد بينكم مو عارف السالفة…', top: 470, dim: true }, { t: 'بس قاعد [[يمثّل]] إنه فاهم!', top: 720 }] },
    beats: { V1: 'شريط بسطر ثانٍ يدخل تحت الفقاعة، وتعبير «تمثيل» بحاجب مرفوع.', V2: 'السطر الأول يخفت، والثاني يدخل مع اهتزاز خفيف.' },
    assets: '—',
  },
  {
    id: 'S04', t: [4.62, 5.54], phrases: [3], layout: 'hook', bgshot: 'G_26.5.png', redwash: true, glow: [540, 1150],
    v1: { stamp: 'تقدرون تكشفونه؟', stampTop: 380, char: 'suspicious' },
    v2: { stamp: 'تقدرون تكشفونه؟', stampTop: 800 },
    beats: { V1: 'ختم أحمر (لون شارة الأمبوستر) مع glitch، والشخصية تضيّق عينيها.', V2: 'الختم نفسه بعرض الشاشة.' },
    assets: '—',
  },
  {
    id: 'S05', t: [6.06, 7.69], phrases: [4], layout: 'stage', heading: H_IMP,
    stage: [{ kind: 'host', img: 'G_26.5.png', box: HOST }, { kind: 'phone', img: 'A01.png', box: INSET, pos: 'top' }],
    cap: 'هذي لعبة [[الأمبوستر]] في فانوس!', kw: 'لعبة [[الأمبوستر]]', char: 'neutral_open',
    beats: { V1: 'انتقال بكسل، ثم عنوان القسم. فئات الأمبوستر على شاشة المضيف، والهاتف يدخل بشاشة البداية. الشخصية تصغر إلى الزاوية.', V2: 'نفسه بلا شخصية، مع ترجمة كاملة.' },
    assets: '✅ G05، A01',
  },
  {
    id: 'S06', t: [8.04, 10.98], phrases: [5], layout: 'stage', heading: H_IMP, glow: [540, 700],
    stage: [{ kind: 'host', img: 'B02_pxqr.png', box: HOST }, { kind: 'phone', img: 'A05.png', box: INSET, pos: 'top' }],
    cap: 'تمسحون الـ[[QR Code]]، وكل واحد يعرف شنو الشي اللي طلع له…', kw: 'كل واحد يعرف [[شنو الشي]]', char: 'neutral_half',
    beats: { V1: 'بطاقة QR على المضيف، ثم «التلفون لازم يكون ب ايد 1» (A04)، ثم «انت مو الامبوستر، الشي اهو: عمان» (A05).', V2: 'نفسه مع ترجمة كاملة.' },
    assets: '✅ B02 (QR مستبدل برسم بكسل غير قابل للمسح)، A04، A05',
  },
  {
    id: 'S07', t: [11.43, 12.01], phrases: [6], layout: 'stage', heading: H_IMP, redwash: true,
    stage: [{ kind: 'phone', img: 'A10.png', box: PHONE_V2, pos: 'top' }],
    stageV1: [{ kind: 'phone', img: 'A10.png', box: PHONE_V1, pos: 'top' }],
    extrasV2: [{ type: 'big', t: 'إلا واحد!', top: 1215, size: 140, cls: 'redtxt' }],
    kw: 'إلا [[واحد!]]', char: 'sly',
    beats: { V1: 'ومضة حمراء وشاشة «انت الامبوستر…»، والشخصية تنظر جانبًا.', V2: 'نفسه، و«إلا واحد!» كبيرة.' },
    assets: '✅ A10',
  },
  {
    id: 'S08', t: [12.52, 15.27], phrases: [7], layout: 'stage', heading: H_IMP,
    stage: [{ kind: 'phone', img: 'A12.png', box: PHONE_V2, pos: 'top' }, { kind: 'phone', img: 'A11.png', box: [40, 470, 250, 430], pos: 'top' }],
    stageV1: [{ kind: 'phone', img: 'A12.png', box: PHONE_V1, pos: 'top' }, { kind: 'phone', img: 'A11.png', box: [90, 440, 250, 430], pos: 'top' }],
    extrasV2: [{ type: 'meter', x: 350, y: 1080, fill: 70 }], extrasV1: [{ type: 'meter', x: 486, y: 1080, fill: 70 }],
    cap: 'تبدأ جولة الأسئلة، وكل جواب [[يزيد الشك.]]', kw: 'كل جواب [[يزيد الشك]]', char: 'suspicious',
    beats: { V1: '«4 يسأل 6» (A11) ثم «اسأل اي شخص شاك فيه 0/16» (A12). عدّاد «الشك» رسم حركي فوقها وليس من الواجهة. الشخصية تتلفّت بشك.', V2: 'نفسه مع ترجمة كاملة.' },
    assets: '✅ A11، A12',
  },
  {
    id: 'S09', t: [15.69, 16.65], phrases: [8], layout: 'stage', heading: H_IMP,
    stage: [{ kind: 'phone', img: 'A13.png', box: PHONE_V2, pos: 'top' }],
    stageV1: [{ kind: 'phone', img: 'A13.png', box: PHONE_V1, pos: 'top' }],
    cap: 'وبعدها [[التصويت…]]', kw: 'وبعدها [[التصويت…]]', char: 'neutral_half',
    beats: { V1: 'إبراز زر «جاهزين للتصويت» (A12)، ثم شاشة التصويت (A13).', V2: 'نفسه.' },
    assets: '✅ A12، A13',
  },
  {
    id: 'S10', t: [17.23, 18.09], phrases: [9], layout: 'stage', heading: H_IMP, redwash: true,
    stage: [{ kind: 'phone', img: 'A14.png', box: PHONE_V2, pos: 'top' }],
    stageV1: [{ kind: 'phone', img: 'A14.png', box: PHONE_V1, pos: 'top' }],
    extrasV2: [{ type: 'big', t: 'منو [[الأمبوستر؟]]', top: 1215, size: 130 }],
    kw: 'منو [[الأمبوستر؟]]', char: 'surprised',
    beats: { V1: '«🥁 الامبوستر اهو…» مع ترقّب واهتزاز خفيف، والشخصية متفاجئة.', V2: 'نفسه مع السؤال كبيرًا.' },
    assets: '✅ A14',
  },
  {
    id: 'S11', t: [18.6, 21.09], phrases: [10, 11], layout: 'stage', heading: H_IMP,
    stage: [{ kind: 'phone', img: 'A15.png', box: PHONE_V2, pos: 'top' }, { kind: 'phone', img: 'A18.png', box: [40, 470, 250, 430], pos: 'top' }],
    stageV1: [{ kind: 'phone', img: 'A15.png', box: PHONE_V1, pos: 'top' }, { kind: 'phone', img: 'A18.png', box: [90, 440, 250, 430], pos: 'top' }],
    cap: 'يمكن أقرب واحد لك [[قاعد يقص عليك!]]', kw: '[[قاعد يقص عليك!]]', char: 'laugh',
    beats: { V1: 'الكشف «5» (A15)، ثم «فاز الفريق الثاني 🏆» (A18). الشخصية تضحك.', V2: 'نفسه مع ترجمة كاملة.' },
    assets: '✅ A15، A18',
  },
  {
    id: 'S12', t: [21.96, 23.88], phrases: [12], layout: 'stage', heading: H_BLIND,
    stage: [{ kind: 'host', img: 'G_25.3.png', box: HOST }],
    cap: 'وطبعاً عندك فئة [[«بدون لا أشوف»!]]', kw: 'فئة [[«بدون لا أشوف»]]', char: 'neutral_open',
    beats: { V1: 'انتقال بكسل والتمييز بالأخضر (لون شارة القسم). عنوان القسم وفئاته على شاشة المضيف.', V2: 'نفسه.' },
    assets: '✅ G04',
  },
  {
    id: 'S13', t: [24.55, 26.69], phrases: [13], layout: 'stage', heading: H_BLIND,
    stage: [{ kind: 'host', img: 'B04_pxqr.png', box: HOST }],
    cap: 'أنت وواحد من ربعك تمسحون الـ[[QR Code]]،', kw: 'تمسحون الـ[[QR Code]]', char: 'neutral_half',
    beats: { V1: 'بطاقة QR المزدوجة مع القواعد، وتقريب بطيء على الرمزين.', V2: 'نفسه.' },
    assets: '✅ B04 (رمزا QR مستبدلان برسم بكسل غير قابل للمسح)',
  },
  {
    id: 'S14', t: [27.18, 30.53], phrases: [14, 15], layout: 'stage', heading: H_BLIND,
    stage: [{ kind: 'phone', img: 'C01.png', box: PHONE_V2, pos: 'top' }, { kind: 'phone', img: 'C02.png', box: [40, 470, 250, 430], pos: 'top' }],
    stageV1: [{ kind: 'phone', img: 'C01.png', box: PHONE_V1, pos: 'top' }, { kind: 'phone', img: 'C02.png', box: [90, 440, 250, 430], pos: 'top' }],
    extrasV2: [{ type: 'blind', x: 772, y: 440, scale: 4 }],
    extrasV1: [{ type: 'blind', x: 70, y: 872, scale: 4.2 }],
    cap: 'وكل واحد يوجّه [[شاشة تليفونه]] للثاني،', kw: 'يوجّه [[شاشة تليفونه]] للثاني،', char: 'sly',
    beats: { V1: 'العبارة 14: «اضغط على جاهز وحط الشاشة باتجاه خصمك» (C02). العبارة 15: الصورة التي يراها الخصم فقط، «برياني» (C01)، وتحلّ ترجمتها «بدون ما يشوف شنو طلع له.» محل العبارة 14 عند 29.58 ث. رسم بكسل لشخصين متقابلين، كل واحد يرفع تلفونه وشاشته للثاني ويشوف شاشة الثاني فقط (خطّا النظر يتقاطعان). توضيح وليس واجهة.', V2: 'نفسه مع ترجمة كاملة.' },
    assets: '✅ C01، C02',
  },
  {
    id: 'S15', t: [31.82, 36.1], phrases: [16, 17], layout: 'stage', heading: H_BLIND,
    stage: [{ kind: 'host', img: 'B05.png', box: HOST }],
    extrasV2: [{ type: 'chip', t: 'نعم', bg: '#0F9C5A', x: 110, y: 930, rot: -6 }, { type: 'chip', t: 'لا', bg: 'var(--red)', x: 800, y: 960, rot: 6 }],
    extrasV1: [{ type: 'chip', t: 'نعم', bg: '#0F9C5A', x: 430, y: 930, rot: -6 }, { type: 'chip', t: 'لا', bg: 'var(--red)', x: 790, y: 960, rot: 6 }],
    cap: 'تسألون أسئلة إجابتها [[نعم]] أو [[لا…]]', kw: 'إجابتها [[نعم]] أو [[لا…]]', char: 'neutral_open',
    beats: { V1: 'فقاعتا «نعم» و«لا» تتناوبان مع إبراز قاعدة «الفريق الي عنده الدور يسأل اول سؤال» (B04). عند «لين تعرفون…» تظهر شاشة الإجابة (B05).', V2: 'نفسه مع ترجمة كاملة.' },
    assets: '✅ B04، B05',
  },
  {
    id: 'S16', t: [37.42, 40.45], phrases: [18, 19], layout: 'stage', heading: H_MOV,
    stage: [{ kind: 'host', img: 'G_movies_noprice.png', box: [60, 430, 960, 330], pos: 'top' }],
    cap: 'تحب فيلم وتقول [[حافظه؟]]', kw: 'تحب فيلم وتقول [[حافظه؟]]', char: 'sly',
    beats: { V1: 'انتقال بكسل، ثم عنوان «فانوس Movies». ملصقات الأفلام من واجهة فانوس فقط، مقصوصة فوق السعر.', V2: 'نفسه.' },
    assets: '✅ G09 مقصوص بلا أسعار',
  },
  {
    id: 'S17', t: [40.84, 43.43], phrases: [20], layout: 'stage', heading: H_MOV,
    stage: [{ kind: 'host', img: 'C05.png', box: HOST }, { kind: 'host', img: 'C04.png', box: [500, 830, 420, 205] }],
    cap: 'يتحدّاك بأسئلة عن [[الفيلم نفسه وأحداثه!]]', kw: '[[الفيلم نفسه وأحداثه!]]', char: 'neutral_open',
    beats: { V1: 'لوحة فيلم «The Terminal» بفئاته (C04)، ثم سؤال «من أي دولة يعود السيد نافورسكي» (C05). لا أسعار في الشاشتين.', V2: 'نفسه.' },
    assets: '✅ C04، C05 (C06 الإجابة احتياط)',
  },
  {
    id: 'S18', t: [44.27, 49.09], phrases: [21, 22], layout: 'stage', heading: H_KIDS,
    stage: [{ kind: 'host', img: 'G_33.5.png', box: HOST }, { kind: 'host', img: 'C03.png', box: [500, 830, 420, 205] }],
    cap: 'مع فئات ممتعة وتفاعلية في [[«فانوس Kids»!]]', kw: 'في [[«فانوس Kids»!]]', char: 'laugh',
    beats: { V1: 'انتقال بكسل والتمييز بالأزرق (لون وضع الأطفال). العبارة 21: سؤال «صح او غلط» بشارة فانوس KIDS (C03). العبارة 22: فئات الأطفال (G07).', V2: 'نفسه.' },
    assets: '✅ G07، C03',
  },
  {
    id: 'S19', t: [49.83, 52.13], phrases: [23, 24], layout: 'tiles', char: 'laugh',
    tiles: [
      { img: 'A10.png', label: 'الأمبوستر', pos: 'center 8%', box: [80, 420, 450, 300], boxV1: [90, 520, 430, 200] },
      { img: 'B04_pxqr.png', label: 'بدون لا أشوف', box: [550, 420, 450, 300], boxV1: [560, 520, 430, 200] },
      { img: 'C05.png', label: 'Movies', box: [80, 800, 450, 300], boxV1: [90, 760, 430, 200] },
      { img: 'C03.png', label: 'Kids', box: [550, 800, 450, 300], boxV1: [560, 760, 430, 200] },
    ],
    cap: 'جمّع ربعك وأهلك، [[وخلّ التحدّي يبدأ!]]',
    beats: { V1: 'الشخصية كبيرة ومتحمسة، وفوقها بطاقات الأقسام الأربعة. لا شرح للعبة الفرق.', V2: 'شبكة 2×2 من شاشات الأقسام.' },
    assets: '✅ من المشاهد السابقة',
  },
  {
    id: 'S20', t: [52.94, 55.744], phrases: [25], layout: 'end', char: 'neutral_open', glow: [540, 700],
    cta: 'حمّل تطبيق [[فانوس!]]',
    beats: { V1: 'الشعار، ثم «حمّل تطبيق فانوس!»، ثم زر alfanous.app. الشخصية تلوّح وتشير للرابط. يثبت حتى 55.744 ث.', V2: 'نفسه دون الشخصية.' },
    assets: '✅ الشعار',
  },
];
