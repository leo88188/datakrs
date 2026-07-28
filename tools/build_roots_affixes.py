#!/usr/bin/env python3
"""Build structured IELTS roots, prefixes and suffixes study data."""

from __future__ import annotations

import json
import re
from pathlib import Path


OUT = Path("public/assets/english/data/roots-affixes.json")
IELTS100 = Path("public/assets/english/data/ielts100.json")
VOCAB_JING = Path("public/assets/english/data/vocab-jing.json")


ROOTS = [
    ("act/ag", "做，行动，驱动", ["action", "active", "agent"], "看到 act/ag 先联想到行动和执行。"),
    ("anim", "生命，精神，气息", ["animal", "animate", "unanimous"], "和 alive 的生命感相关。"),
    ("ann/enn", "年", ["annual", "anniversary", "perennial"], "annual report 就是年度报告。"),
    ("anthrop", "人，人类", ["anthropology", "anthropic", "misanthrope"], "anthropology 是人类学。"),
    ("aqu", "水", ["aquatic", "aquarium", "aqueduct"], "aquarium 是水族馆。"),
    ("aud", "听", ["audio", "audience", "auditory"], "audio 与听觉直接相关。"),
    ("auto", "自己，自动", ["automatic", "autonomy", "autobiography"], "auto 常表示自己完成。"),
    ("bio", "生命，生物", ["biology", "biography", "biodegradable"], "bio 是生物和生命。"),
    ("cap/cept/cip", "拿，抓，接受", ["capture", "accept", "recipient"], "accept 是把东西接过来。"),
    ("ced/ceed/cess", "走，前进，退让", ["proceed", "access", "recede"], "process 是推进出来的过程。"),
    ("chron", "时间", ["chronic", "chronology", "synchronize"], "chronology 是时间顺序。"),
    ("cid/cis", "切，杀，决定", ["decide", "precise", "suicide"], "decide 原意是切断选择。"),
    ("circ", "圆，周围", ["circle", "circumstance", "circuit"], "circumstance 是围绕着你的情况。"),
    ("claim/clam", "喊，宣称", ["claim", "proclaim", "exclaim"], "exclaim 是喊出来。"),
    ("cogn/gnos", "知道，认识", ["cognitive", "recognize", "diagnosis"], "cognitive 是认知的。"),
    ("corp", "身体，实体", ["corporate", "corpse", "incorporate"], "corporate 原意是形成一个身体。"),
    ("cred", "相信，信任", ["credit", "credible", "incredible"], "credible 是可相信的。"),
    ("cur/curs", "跑，流动", ["current", "occur", "excursion"], "current 有流动和当前之意。"),
    ("cycl", "圆，循环", ["cycle", "recycle", "cyclone"], "cycle 是循环。"),
    ("dem", "人民，人群", ["democracy", "demographic", "epidemic"], "democracy 是人民治理。"),
    ("dict", "说，命令", ["dictionary", "predict", "dictate"], "predict 是提前说。"),
    ("duc/duct", "引导，带领", ["produce", "conduct", "education"], "education 是把能力引出来。"),
    ("fac/fect/fic", "做，制造", ["factory", "effect", "efficient"], "factory 是做东西的地方。"),
    ("fer", "带来，携带", ["transfer", "refer", "fertile"], "transfer 是带着越过去。"),
    ("fid", "信任，忠诚", ["confident", "fidelity", "confide"], "confidence 来自信任。"),
    ("fin", "结束，边界", ["final", "define", "infinite"], "define 是划定边界。"),
    ("flex/flect", "弯曲，转向", ["flexible", "reflect", "deflect"], "reflect 是光线转回来。"),
    ("form", "形状，形成", ["form", "inform", "transform"], "transform 是改变形态。"),
    ("fort", "强，力量", ["force", "effort", "fortify"], "fortify 是加强。"),
    ("fract/frag", "破碎", ["fraction", "fragment", "fragile"], "fragment 是碎片。"),
    ("gen", "产生，种类", ["generate", "gene", "general"], "generate 是产生。"),
    ("geo", "地球，土地", ["geography", "geology", "geothermal"], "geography 是地理。"),
    ("grad/gress", "步，等级，前进", ["graduate", "progress", "gradual"], "progress 是向前走。"),
    ("graph", "写，画，记录", ["graphic", "photograph", "paragraph"], "graph 关联记录和图。"),
    ("hab/hibit", "持有，居住，习惯", ["habit", "habitat", "exhibit"], "habitat 是居住地。"),
    ("ject", "投掷，抛出", ["project", "reject", "eject"], "reject 是扔回去。"),
    ("jud/jur", "法律，判断", ["judge", "jury", "justice"], "judge 是判断。"),
    ("junct", "连接", ["junction", "conjunction", "adjunct"], "junction 是连接点。"),
    ("labor", "劳动，工作", ["labor", "collaborate", "elaborate"], "collaborate 是一起工作。"),
    ("lat", "带，携带，侧面", ["translate", "relate", "lateral"], "translate 是把意思带过去。"),
    ("leg/lect", "读，选择，法律", ["lecture", "collect", "legal"], "collect 是选到一起。"),
    ("liber", "自由", ["liberty", "liberal", "liberate"], "liberate 是解放。"),
    ("loc", "地方，位置", ["local", "locate", "allocate"], "locate 是找位置。"),
    ("log/loqu", "说，词，逻辑", ["logic", "dialogue", "eloquent"], "dialogue 是相互说。"),
    ("luc/lum", "光", ["lucid", "illuminate", "luminous"], "luminous 是发光的。"),
    ("magn", "大", ["magnify", "magnitude", "magnificent"], "magnify 是放大。"),
    ("manu", "手", ["manual", "manufacture", "manuscript"], "manual 是手工的。"),
    ("mar/mer", "海", ["marine", "maritime", "submarine"], "marine 是海洋的。"),
    ("mater/matr", "母亲，来源", ["maternal", "matrix", "maternity"], "maternal 是母性的。"),
    ("medi", "中间，调解", ["medium", "mediate", "intermediate"], "mediate 是在中间调停。"),
    ("mem", "记忆", ["memory", "memorial", "remember"], "memorial 是纪念物。"),
    ("migr", "迁移", ["migrate", "immigrant", "emigration"], "migration 是迁徙。"),
    ("min", "小，少", ["minimum", "minor", "diminish"], "minimum 是最小量。"),
    ("mit/miss", "送，放出", ["submit", "mission", "emit"], "submit 是送上去。"),
    ("mob/mot/mov", "移动", ["mobile", "motion", "remove"], "mobile 是可移动的。"),
    ("morph", "形态", ["morphology", "transform", "amorphous"], "morphology 是形态学。"),
    ("nat", "出生，自然", ["native", "nature", "innate"], "native 是出生地的。"),
    ("nav", "船，航行", ["navy", "navigate", "naval"], "navigate 是航行定位。"),
    ("neg", "否定", ["negative", "neglect", "negotiate"], "negative 是否定的。"),
    ("nom/nym", "名字，名称", ["nominate", "anonymous", "synonym"], "anonymous 是无名的。"),
    ("nov", "新", ["novel", "innovate", "renovate"], "innovation 是引入新事物。"),
    ("numer", "数", ["number", "numerous", "enumerate"], "numerous 是数量多。"),
    ("omni", "全部", ["omnivore", "omnipresent", "omnibus"], "omni 表示全。"),
    ("path", "感受，疾病，路径", ["empathy", "pathology", "sympathy"], "empathy 是感同身受。"),
    ("ped", "脚，儿童，教育", ["pedestrian", "pedal", "pediatric"], "pedestrian 是步行者。"),
    ("pel/puls", "推，驱动", ["compel", "impulse", "repel"], "compel 是推动别人做。"),
    ("pend/pens", "悬挂，称重，支付", ["depend", "suspend", "expense"], "depend 是挂靠在某物上。"),
    ("phon", "声音", ["phone", "phonetic", "symphony"], "phonetic 是语音的。"),
    ("photo", "光", ["photo", "photosynthesis", "photocopy"], "photosynthesis 是光合作用。"),
    ("plac", "平静，取悦，地方", ["place", "placid", "replace"], "placid 是平静的。"),
    ("port", "携带，港口", ["transport", "portable", "import"], "portable 是可携带的。"),
    ("pos/pon", "放置", ["position", "compose", "postpone"], "compose 是放到一起。"),
    ("prim", "第一，主要", ["primary", "prime", "primitive"], "primary 是首要的。"),
    ("prob/prov", "证明，测试", ["prove", "approve", "probable"], "prove 是证明。"),
    ("psych", "心理，精神", ["psychology", "psychological", "psychiatry"], "psychology 是心理学。"),
    ("punct", "点，刺", ["puncture", "punctual", "punctuation"], "punctual 像点一样准时。"),
    ("quer/quis/quest", "寻找，询问", ["query", "inquiry", "request"], "question 是询问。"),
    ("rupt", "破裂", ["interrupt", "erupt", "corrupt"], "interrupt 是打断。"),
    ("sci", "知道，知识", ["science", "conscious", "omniscient"], "science 是系统知识。"),
    ("scrib/script", "写", ["describe", "script", "manuscript"], "describe 是写下来说明。"),
    ("sect/sec", "切，分开", ["section", "sector", "dissect"], "section 是切出来的一部分。"),
    ("sens/sent", "感觉，观点", ["sense", "sensitive", "consent"], "sensitive 是有感觉的。"),
    ("sequ/sec", "跟随，连续", ["sequence", "consequence", "subsequent"], "subsequent 是随后发生。"),
    ("serv", "服务，保存", ["service", "preserve", "conservation"], "preserve 是保存。"),
    ("sign", "标记，信号", ["signal", "design", "significant"], "significant 是有标记意义的。"),
    ("simil/simul", "相同，相似", ["similar", "simulate", "simultaneous"], "simulate 是模仿相似状态。"),
    ("sol", "太阳，单独", ["solar", "solo", "solitary"], "solar 是太阳的。"),
    ("spec/spic", "看", ["spectator", "inspect", "perspective"], "inspect 是向里看。"),
    ("spir", "呼吸，精神", ["spirit", "inspire", "respiration"], "inspire 原意是吸入气息。"),
    ("sta/stat/stit", "站立，状态", ["stable", "status", "institution"], "stable 是站得住。"),
    ("struct", "建造", ["structure", "construct", "infrastructure"], "construct 是建造。"),
    ("tang/tact", "触摸", ["tangible", "contact", "intact"], "tangible 是可触摸的。"),
    ("temp", "时间，节奏", ["temporary", "contemporary", "tempo"], "temporary 是有时间限制。"),
    ("ten/tain", "握住，保持", ["contain", "retain", "maintain"], "retain 是保留住。"),
    ("tend/tens/tent", "伸展，趋向", ["extend", "intense", "tendency"], "tendency 是倾向。"),
    ("terr", "土地，恐惧", ["territory", "terrain", "terror"], "territory 是土地范围。"),
    ("therm", "热", ["thermal", "thermometer", "geothermal"], "thermometer 是温度计。"),
    ("tract", "拉，引", ["attract", "contract", "extract"], "extract 是拉出来。"),
    ("urb", "城市", ["urban", "suburb", "urbanization"], "urbanization 是城市化。"),
    ("vac", "空", ["vacant", "vacuum", "evacuate"], "vacuum 是真空。"),
    ("ven/vent", "来", ["event", "intervene", "convention"], "event 是发生来到的事。"),
    ("ver", "真", ["verify", "verdict", "veracity"], "verify 是确认真实。"),
    ("vid/vis", "看", ["video", "visible", "evidence"], "evidence 是看得出的证据。"),
    ("vit/viv", "生命", ["vital", "survive", "vivid"], "vivid 是有生命感的。"),
    ("voc/vok", "声音，呼叫", ["voice", "vocabulary", "evoke"], "evoke 是唤起。"),
]


PREFIXES = [
    ("a-/an-", "无，不，非", ["asymmetry", "anonymous", "atypical"], "用于表示缺失或否定。"),
    ("ab-", "离开，偏离", ["absent", "abnormal", "abstract"], "abnormal 是偏离正常。"),
    ("ad-", "向，靠近，加强", ["adapt", "advance", "allocate"], "ad 常因后面字母变化成 ac/af/al。"),
    ("ambi-", "两边，双重", ["ambiguous", "ambivalent", "ambidextrous"], "ambiguous 是两边都能解释。"),
    ("ante-", "在前，先于", ["antecedent", "antenatal", "antebellum"], "ante 表示时间上在前。"),
    ("anti-", "反对，抵抗", ["antibiotic", "antisocial", "antibody"], "anti 常表示反。"),
    ("auto-", "自己，自动", ["autonomy", "autonomous", "autobiography"], "auto 是自己完成。"),
    ("be-", "使成为，覆盖，加强", ["befriend", "belittle", "besiege"], "befriend 是使成为朋友。"),
    ("bi-", "二，双", ["bilingual", "bilateral", "biodiversity"], "bilingual 是双语。"),
    ("circum-", "环绕，周围", ["circumstance", "circumference", "circumscribe"], "circum 表示绕一圈。"),
    ("co-/com-/con-", "共同，一起，加强", ["cooperate", "combine", "connect"], "con 会随后面字母变体。"),
    ("contra-/counter-", "相反，对抗", ["contradict", "counteract", "counterpart"], "counteract 是反作用。"),
    ("de-", "向下，去掉，反向", ["decline", "devalue", "decode"], "decode 是去掉编码。"),
    ("dia-", "穿过，横跨", ["diameter", "diagnosis", "dialogue"], "dialogue 是话语穿过双方。"),
    ("dis-", "分开，否定，反向", ["disagree", "disperse", "displace"], "disagree 是不同意。"),
    ("en-/em-", "使进入，使成为", ["enable", "enrich", "empower"], "enable 是使能够。"),
    ("ex-/e-", "向外，前任", ["export", "exclude", "emit"], "export 是向外运。"),
    ("extra-", "以外，额外", ["extraordinary", "extracurricular", "extract"], "extraordinary 是超出普通。"),
    ("fore-", "预先，在前", ["forecast", "foresee", "forehead"], "forecast 是预先说。"),
    ("hyper-", "过度，超高", ["hyperactive", "hypertension", "hypercritical"], "hypertension 是高血压。"),
    ("hypo-", "不足，低下", ["hypothesis", "hypothermia", "hypoglycemia"], "hypo 常表示低。"),
    ("in-/im-/il-/ir-", "不，非", ["invisible", "impossible", "irregular"], "否定前缀，会因后面字母变形。"),
    ("in-/im-", "进入，向内", ["import", "input", "involve"], "import 是向内带入。"),
    ("inter-", "之间，相互", ["international", "interaction", "intermediate"], "interaction 是相互作用。"),
    ("intra-", "内部", ["intranet", "intracellular", "intrapersonal"], "intra 是在内部。"),
    ("intro-", "向内，引入", ["introduce", "introvert", "introspection"], "introvert 是向内转。"),
    ("mal-", "坏，错误", ["malfunction", "malnutrition", "malpractice"], "malnutrition 是营养不良。"),
    ("micro-", "微小", ["microscope", "microbe", "microeconomics"], "microeconomics 是微观经济学。"),
    ("macro-", "巨大，宏观", ["macrocosm", "macroeconomics", "macroscopic"], "macro 是宏观。"),
    ("mis-", "错误，坏", ["misunderstand", "mislead", "misuse"], "mislead 是误导。"),
    ("mono-", "单一", ["monolingual", "monopoly", "monotone"], "monopoly 是独占。"),
    ("multi-", "多", ["multicultural", "multiple", "multinational"], "multicultural 是多元文化。"),
    ("non-", "不，非", ["nonprofit", "nonverbal", "nonexistent"], "nonprofit 是非营利。"),
    ("omni-", "全，所有", ["omnivore", "omnipresent", "omniscient"], "omnivore 是杂食动物。"),
    ("over-", "过度，在上", ["overuse", "overestimate", "overlook"], "overestimate 是高估。"),
    ("pan-", "全，泛", ["pandemic", "panorama", "pan-African"], "pandemic 是广泛流行。"),
    ("per-", "贯穿，完全", ["persist", "permanent", "permeate"], "permeate 是渗透贯穿。"),
    ("peri-", "周围", ["perimeter", "periphery", "periodontal"], "perimeter 是周长。"),
    ("poly-", "多", ["polytechnic", "polygon", "polyglot"], "polyglot 是会多种语言的人。"),
    ("post-", "之后", ["postwar", "postgraduate", "postpone"], "postgraduate 是本科后。"),
    ("pre-", "之前，预先", ["predict", "preview", "prevent"], "predict 是预先说。"),
    ("pro-", "向前，支持，代表", ["progress", "promote", "proponent"], "proponent 是支持者。"),
    ("re-", "再次，回来", ["rebuild", "return", "review"], "review 是再看。"),
    ("retro-", "向后，复古", ["retrospect", "retroactive", "retrofit"], "retrospect 是回顾。"),
    ("semi-", "半，部分", ["semiconductor", "semifinal", "semiannual"], "semiannual 是半年一次。"),
    ("sub-", "在下，次级", ["subway", "substandard", "submarine"], "submarine 是水下船。"),
    ("super-/sur-", "在上，超过", ["superior", "surpass", "surface"], "surpass 是超过。"),
    ("trans-", "穿过，转移", ["transport", "transform", "transnational"], "transform 是跨形态改变。"),
    ("tri-", "三", ["triangle", "trilingual", "tripod"], "triangle 是三角形。"),
    ("ultra-", "超越，极端", ["ultraviolet", "ultramodern", "ultra-low"], "ultraviolet 是紫外的。"),
    ("un-", "不，反向", ["unknown", "uncover", "unfair"], "uncover 是把覆盖反过来。"),
    ("under-", "不足，在下", ["underestimate", "underground", "underdeveloped"], "underestimate 是低估。"),
]


SUFFIXES = [
    ("-able/-ible", "能够……的，值得……的", ["valuable", "visible", "sustainable"], "形容词后缀，常表示可行性。"),
    ("-acy", "性质，状态，制度", ["accuracy", "democracy", "privacy"], "常把形容或制度变成名词。"),
    ("-age", "集合，状态，费用", ["shortage", "coverage", "storage"], "shortage 是短缺状态。"),
    ("-al", "……的；行为", ["natural", "approval", "arrival"], "既可形容词也可名词。"),
    ("-ance/-ence", "状态，性质，行为", ["importance", "evidence", "resistance"], "常接动词形成抽象名词。"),
    ("-ant/-ent", "……的人/物；……的", ["assistant", "dependent", "significant"], "可作名词也可作形容词。"),
    ("-ary", "与……有关的；场所", ["temporary", "library", "voluntary"], "temporary 是暂时的。"),
    ("-ate", "使成为；具有", ["activate", "graduate", "dominate"], "常作动词后缀。"),
    ("-ation/-tion/-sion", "行为，过程，结果", ["education", "decision", "pollution"], "雅思高频抽象名词后缀。"),
    ("-ative", "有……倾向的", ["creative", "informative", "representative"], "informative 是信息量大的。"),
    ("-cy", "性质，状态", ["efficiency", "frequency", "literacy"], "literacy 是读写能力。"),
    ("-dom", "领域，状态", ["freedom", "kingdom", "wisdom"], "freedom 是自由状态。"),
    ("-ed", "已经……的，具有……的", ["developed", "skilled", "limited"], "常用于过去分词形容词。"),
    ("-ee", "被……的人", ["employee", "trainee", "refugee"], "employee 是被雇佣的人。"),
    ("-eer", "从事……的人", ["engineer", "volunteer", "pioneer"], "volunteer 是志愿者。"),
    ("-en", "使变成", ["widen", "strengthen", "shorten"], "动词后缀，表示使……。"),
    ("-en", "由……制成的", ["wooden", "golden", "woolen"], "形容词后缀，表示材质或特性。"),
    ("-er/-or", "人，工具，比较级", ["teacher", "operator", "greater"], "teacher 是教的人。"),
    ("-ery", "场所，行为，集合", ["bakery", "machinery", "bravery"], "bakery 是烘焙场所。"),
    ("-esque", "……风格的", ["picturesque", "Kafkaesque", "Romanesque"], "picturesque 是如画的。"),
    ("-ess", "女性", ["actress", "hostess", "goddess"], "现代英语中使用减少，但阅读会见到。"),
    ("-est", "最高级", ["largest", "fastest", "strongest"], "形容词副词最高级。"),
    ("-ful", "充满……的", ["useful", "meaningful", "harmful"], "harmful 是有害的。"),
    ("-fy/-ify", "使……化", ["simplify", "classify", "beautify"], "simplify 是使简单。"),
    ("-hood", "身份，时期，状态", ["childhood", "neighborhood", "likelihood"], "childhood 是童年。"),
    ("-ial", "与……有关的", ["industrial", "financial", "social"], "financial 是金融的。"),
    ("-ian", "……的人，……的", ["historian", "technician", "urbanian"], "historian 是历史学家。"),
    ("-ic", "……的", ["economic", "basic", "academic"], "academic 是学术的。"),
    ("-ical", "……的，具有……性质的", ["political", "practical", "biological"], "biological 是生物的。"),
    ("-ics", "学科，体系", ["economics", "physics", "statistics"], "economics 是经济学。"),
    ("-ile", "能够……的，属于……的", ["mobile", "fertile", "fragile"], "fragile 是易碎的。"),
    ("-ing", "正在……的；行为", ["developing", "learning", "housing"], "housing 可表示住房。"),
    ("-ion", "行为，状态，结果", ["action", "vision", "region"], "action 是行为。"),
    ("-ish", "有点……的，类似……的", ["selfish", "childish", "British"], "childish 是孩子气的。"),
    ("-ism", "主义，制度，现象", ["capitalism", "tourism", "optimism"], "tourism 是旅游业。"),
    ("-ist", "从事……的人，支持者", ["scientist", "artist", "environmentalist"], "environmentalist 是环保人士。"),
    ("-ity/-ty", "性质，状态", ["quality", "diversity", "ability"], "抽象名词高频后缀。"),
    ("-ive", "有……性质的", ["effective", "creative", "sensitive"], "sensitive 是敏感的。"),
    ("-ize/-ise", "使……化", ["modernize", "organise", "standardize"], "standardize 是标准化。"),
    ("-less", "没有……的", ["careless", "homeless", "endless"], "homeless 是无家可归的。"),
    ("-like", "像……的", ["childlike", "businesslike", "lifelike"], "lifelike 是逼真的。"),
    ("-logy/-ology", "学科，研究", ["biology", "technology", "psychology"], "psychology 是心理学。"),
    ("-ly", "……地；具有……性质", ["quickly", "friendly", "daily"], "friendly 是形容词，不只是副词。"),
    ("-ment", "行为，结果，状态", ["development", "government", "movement"], "development 是发展。"),
    ("-ness", "性质，状态", ["awareness", "happiness", "effectiveness"], "awareness 是意识。"),
    ("-ous/-ious", "充满……的", ["various", "dangerous", "curious"], "dangerous 是危险的。"),
    ("-ship", "身份，关系，技能", ["leadership", "relationship", "scholarship"], "leadership 是领导力。"),
    ("-some", "有……倾向的", ["troublesome", "tiresome", "awesome"], "troublesome 是麻烦的。"),
    ("-ure", "行为，结果", ["failure", "pressure", "exposure"], "exposure 是暴露。"),
    ("-ward/-wards", "方向", ["forward", "backward", "towards"], "forward 是向前。"),
]


def load_word_lookup() -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    if IELTS100.exists():
        data = json.loads(IELTS100.read_text(encoding="utf-8"))
        for sentence in data.get("sentences", []):
            for word in sentence.get("words", []):
                term = (word.get("term") or "").strip()
                if not term:
                    continue
                lookup[term.lower()] = {
                    "word": term,
                    "phonetic": word.get("phonetic") or "",
                    "meaning": word.get("definition") or "",
                    "pos": word.get("pos") or "",
                }
    if VOCAB_JING.exists():
        data = json.loads(VOCAB_JING.read_text(encoding="utf-8"))
        for word in data.get("words", []):
            term = (word.get("word") or "").strip()
            if not term:
                continue
            lookup.setdefault(
                term.lower(),
                {
                    "word": term,
                    "phonetic": "",
                    "meaning": word.get("definition") or "",
                    "pos": word.get("pos") or "",
                },
            )
    return lookup


def morpheme_tokens(morpheme: str) -> list[str]:
    return [token.strip("-") for token in re.split(r"[/\s]+", morpheme.lower()) if len(token.strip("-")) >= 3]


def fallback_meaning(word: str, morpheme: str, meaning: str) -> str:
    return f"含有 {morpheme}，常与“{meaning}”相关"


def word_matches_morpheme(word: str, morpheme: str, tokens: list[str]) -> bool:
    if morpheme.startswith("-"):
        return any(word.endswith(token) for token in tokens)
    if morpheme.endswith("-"):
        return any(word.startswith(token) for token in tokens)
    return any(token in word for token in tokens)


def build_examples(
    morpheme: str,
    meaning: str,
    examples: list[str],
    lookup: dict[str, dict],
) -> list[dict]:
    result = []
    seen = set()

    def add(word: str) -> None:
        key = word.lower()
        if key in seen or len(result) >= 4:
            return
        seen.add(key)
        model = lookup.get(key, {})
        result.append(
            {
                "word": model.get("word") or word,
                "phonetic": model.get("phonetic") or "",
                "meaning": model.get("meaning") or fallback_meaning(word, morpheme, meaning),
                "pos": model.get("pos") or "",
            }
        )

    for word in examples:
        add(word)

    tokens = morpheme_tokens(morpheme)
    if tokens:
        matches = []
        for key, model in lookup.items():
            if not model.get("phonetic"):
                continue
            if word_matches_morpheme(key, morpheme, tokens):
                matches.append(model["word"])
        for word in sorted(matches, key=lambda item: (len(item), item.lower())):
            if len(result) >= 4 or sum(1 for item in result if item.get("phonetic")) >= 2:
                break
            add(word)

    return result[:4]


def make_items(kind: str, label: str, rows: list[tuple[str, str, list[str], str]], lookup: dict[str, dict]) -> list[dict]:
    return [
        {
            "id": f"{kind}-{index:03d}",
            "type": kind,
            "typeLabel": label,
            "morpheme": morpheme,
            "meaning": meaning,
            "examples": build_examples(morpheme, meaning, examples, lookup),
            "memoryTip": tip,
        }
        for index, (morpheme, meaning, examples, tip) in enumerate(rows, 1)
    ]


def main() -> int:
    roots = ROOTS[:100]
    prefixes = PREFIXES[:50]
    suffixes = SUFFIXES[:50]
    lookup = load_word_lookup()
    data = {
        "meta": {
            "title": "雅思英文词根词缀",
            "rootCount": len(roots),
            "prefixCount": len(prefixes),
            "suffixCount": len(suffixes),
            "totalCount": len(roots) + len(prefixes) + len(suffixes),
            "version": "1.0.0",
        },
        "groups": [
            {"type": "root", "label": "词根", "count": len(roots), "dailySize": 10},
            {"type": "prefix", "label": "前缀", "count": len(prefixes), "dailySize": 10},
            {"type": "suffix", "label": "后缀", "count": len(suffixes), "dailySize": 10},
        ],
        "items": make_items("root", "词根", roots, lookup)
        + make_items("prefix", "前缀", prefixes, lookup)
        + make_items("suffix", "后缀", suffixes, lookup),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(data["meta"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
