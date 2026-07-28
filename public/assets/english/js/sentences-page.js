(function () {
  "use strict";

  const state = {
    sentences: [],
    activeId: "",
    category: "all",
    collection: "ielts",
    pattern: "all",
    tone: "all",
    query: "",
    read: new Set(),
    favorite: new Set(),
    voices: [],
  };

  const els = {};
  const storageKey = "datakrs_classic_sentences_v1";

  const quoted = [
    ["q001", "This above all: to thine own self be true.", "最重要的是：忠于你自己。", "William Shakespeare", "自我", "深刻"],
    ["q002", "Brevity is the soul of wit.", "简洁是智慧的灵魂。", "William Shakespeare", "表达", "有趣"],
    ["q003", "The rest is silence.", "其余的，便是沉默。", "William Shakespeare", "人生", "深刻"],
    ["q004", "I think, therefore I am.", "我思故我在。", "Rene Descartes", "思考", "深刻"],
    ["q005", "The unexamined life is not worth living.", "未经审视的人生不值得过。", "Socrates", "思考", "深刻"],
    ["q006", "Know thyself.", "认识你自己。", "Ancient Greek maxim", "自我", "深刻"],
    ["q007", "To be, or not to be: that is the question.", "生存还是毁灭，这是问题所在。", "William Shakespeare", "选择", "深刻"],
    ["q008", "Hope is a waking dream.", "希望是清醒时的梦。", "Aristotle", "希望", "温暖"],
    ["q009", "Well begun is half done.", "良好的开始等于成功了一半。", "Aristotle", "行动", "坚定"],
    ["q010", "The journey of a thousand miles begins with one step.", "千里之行，始于足下。", "Laozi", "行动", "坚定"],
    ["q011", "Silence is a source of great strength.", "沉默是一种强大的力量。", "Laozi", "内心", "安静"],
    ["q012", "Life is really simple, but we insist on making it complicated.", "生活本来简单，是我们坚持把它变复杂。", "Confucius", "人生", "深刻"],
    ["q013", "Everything has beauty, but not everyone sees it.", "万物皆有美，但不是人人都能看见。", "Confucius", "观察", "温暖"],
    ["q014", "Study the past if you would define the future.", "想定义未来，就研究过去。", "Confucius", "学习", "坚定"],
    ["q015", "Fortune favors the bold.", "命运偏爱勇敢者。", "Virgil", "勇气", "坚定"],
    ["q016", "Time is the wisest counselor of all.", "时间是最睿智的顾问。", "Pericles", "时间", "深刻"],
    ["q017", "The only true wisdom is in knowing you know nothing.", "真正的智慧，是知道自己一无所知。", "Socrates", "学习", "深刻"],
    ["q018", "No great mind has ever existed without a touch of madness.", "伟大的头脑，常带着一点疯狂。", "Aristotle", "创造", "有趣"],
    ["q019", "He who has a why can bear almost any how.", "知道为什么而活的人，几乎能承受任何怎样去活。", "Friedrich Nietzsche", "意义", "坚定"],
    ["q020", "That which does not kill us makes us stronger.", "没有击倒我们的，会使我们更强。", "Friedrich Nietzsche", "逆境", "坚定"],
    ["q021", "What we think, we become.", "我们想什么，便会成为什么。", "Buddha", "内心", "安静"],
    ["q022", "No act of kindness is ever wasted.", "任何善意都不会白费。", "Aesop", "善意", "温暖"],
    ["q023", "Adventure is worthwhile.", "冒险是值得的。", "Aesop", "勇气", "轻快"],
    ["q024", "Beware the barrenness of a busy life.", "警惕忙碌生活里的贫瘠。", "Socrates", "生活", "深刻"],
    ["q025", "The die is cast.", "骰子已经掷下。", "Julius Caesar", "选择", "坚定"],
    ["q026", "Veni, vidi, vici.", "我来，我见，我征服。", "Julius Caesar", "行动", "坚定"],
    ["q027", "Carpe diem.", "把握今天。", "Horace", "时间", "坚定"],
    ["q028", "A room without books is like a body without a soul.", "没有书的房间，就像没有灵魂的身体。", "Cicero", "学习", "温暖"],
    ["q029", "While there is life, there is hope.", "只要生命还在，希望就在。", "Cicero", "希望", "温暖"],
    ["q030", "The secret of getting ahead is getting started.", "前进的秘密，就是开始行动。", "Mark Twain", "行动", "坚定"],
    ["q031", "The reports of my death are greatly exaggerated.", "关于我死亡的报道被严重夸大了。", "Mark Twain", "幽默", "有趣"],
    ["q032", "If you tell the truth, you do not need to remember anything.", "如果说真话，你就不用记住任何谎言。", "Mark Twain", "诚实", "有趣"],
    ["q033", "It is never too late to be what you might have been.", "成为你本可以成为的人，永远不算太晚。", "George Eliot", "成长", "温暖"],
    ["q034", "Not all those who wander are lost.", "并非所有流浪的人都迷失了方向。", "J. R. R. Tolkien", "探索", "温暖"],
    ["q035", "Facts do not cease to exist because they are ignored.", "事实不会因为被忽视而消失。", "Aldous Huxley", "现实", "深刻"],
    ["q036", "What we know is a drop; what we don't know is an ocean.", "我们所知如一滴水，未知如一片海。", "Isaac Newton", "学习", "深刻"],
    ["q037", "If I have seen further, it is by standing on the shoulders of giants.", "如果我看得更远，是因为站在巨人的肩上。", "Isaac Newton", "学习", "深刻"],
    ["q038", "Imagination is more important than knowledge.", "想象力比知识更重要。", "Albert Einstein", "创造", "坚定"],
    ["q039", "Try not to become a person of success, but a person of value.", "不要只追求成功，要努力成为有价值的人。", "Albert Einstein", "价值", "深刻"],
    ["q040", "In the middle of difficulty lies opportunity.", "困难中间藏着机会。", "Albert Einstein", "逆境", "坚定"],
    ["q041", "The important thing is not to stop questioning.", "重要的是不要停止提问。", "Albert Einstein", "思考", "坚定"],
    ["q042", "Simplicity is the ultimate sophistication.", "简单，是终极的高级。", "Leonardo da Vinci", "表达", "深刻"],
    ["q043", "Learning never exhausts the mind.", "学习从不会耗尽心智。", "Leonardo da Vinci", "学习", "温暖"],
    ["q044", "I have not failed. I've just found ways that won't work.", "我没有失败，只是发现了一些行不通的方法。", "Thomas Edison", "逆境", "坚定"],
    ["q045", "Genius is one percent inspiration and ninety-nine percent perspiration.", "天才是一分灵感加九十九分汗水。", "Thomas Edison", "努力", "坚定"],
    ["q046", "The future depends on what you do today.", "未来取决于你今天做什么。", "Mahatma Gandhi", "行动", "坚定"],
    ["q047", "Be yourself; everyone else is already taken.", "做你自己，别人都已经有人做了。", "Oscar Wilde", "自我", "有趣"],
    ["q048", "Experience is simply the name we give our mistakes.", "经验，不过是我们给错误起的名字。", "Oscar Wilde", "成长", "有趣"],
    ["q049", "To define is to limit.", "定义，就是限制。", "Oscar Wilde", "思考", "深刻"],
    ["q050", "Consistency is the last refuge of the unimaginative.", "一味一致，是缺乏想象力者最后的避难所。", "Oscar Wilde", "创造", "有趣"],
    ["q051", "The mind is everything. What you think you become.", "心是一切；你想什么，就会成为什么。", "Buddha", "内心", "安静"],
    ["q052", "Peace begins with a smile.", "和平始于一个微笑。", "Mother Teresa", "善意", "温暖"],
    ["q053", "Turn your wounds into wisdom.", "把伤口变成智慧。", "Oprah Winfrey", "成长", "坚定"],
    ["q054", "Done is better than perfect.", "完成比完美更重要。", "Sheryl Sandberg", "行动", "坚定"],
    ["q055", "Stay hungry, stay foolish.", "保持饥饿，保持天真。", "Steve Jobs", "成长", "坚定"],
    ["q056", "Innovation distinguishes between a leader and a follower.", "创新区分领导者和追随者。", "Steve Jobs", "创造", "坚定"],
  ];

  const originals = {
    "成长": [
      ["Growth begins when comfort stops being convincing.", "当舒适不再有说服力，成长就开始了。", "真正的变化通常不是因为热血，而是因为旧方式已经无法解释你想要的未来。"],
      ["A better self is built in ordinary minutes.", "更好的自己，是在普通的分钟里建成的。", "把注意力放回今天可执行的小动作，长期结果会自己显形。"],
      ["Maturity is learning to choose peace without choosing weakness.", "成熟，是学会选择平静，而不是选择软弱。", "平静不是退让，它常常是更稳定的力量。"],
      ["You do not rise by hating the place you started.", "你不会因为讨厌起点而真正上升。", "接纳起点，才更容易持续向前。"],
      ["The quietest progress is often the most permanent.", "最安静的进步，往往最持久。", "不需要每天轰轰烈烈，重要的是方向没有丢。"],
      ["A new life rarely arrives loudly; it usually starts as a new habit.", "新生活很少轰然降临，它通常从一个新习惯开始。", "习惯是人生最小的建筑单位。"],
      ["Confidence grows when promises to yourself are kept.", "自信来自你兑现给自己的承诺。", "自我信任不是喊口号，而是一次次完成。"],
      ["The person you become is hidden in what you repeat.", "你会成为什么样的人，藏在你重复做的事里。", "重复决定身份，身份决定选择。"],
      ["Do not confuse a slow season with a wasted season.", "不要把缓慢的阶段误认为浪费的阶段。", "有些阶段是在扎根，不是在开花。"],
      ["Every difficult chapter can become evidence of strength.", "每一个艰难章节，都可以成为力量的证据。", "经历本身不自动有意义，整理之后才有力量。"],
      ["Change is easier when it has a calendar, not just a wish.", "改变需要日历，而不只是愿望。", "把愿望放进时间表，才开始接近现实。"],
      ["A small win is a vote for your future self.", "一个小胜利，是投给未来自己的票。", "不要轻视小完成，它们会积累成自我认同。"],
      ["You grow faster when you stop performing growth.", "当你停止表演成长，成长反而更快。", "真实的进步不需要随时给别人看。"],
      ["Better judgment is often paid for with older mistakes.", "更好的判断力，常常由过去的错误买单。", "错误若被复盘，就不只是损失。"],
      ["Your next level will ask for a simpler discipline.", "你的下一阶段，往往需要更简单的纪律。", "复杂计划容易兴奋，简单纪律更容易改变结果。"],
      ["The hardest part of growth is leaving an old excuse unemployed.", "成长最难的部分，是让旧借口失业。", "借口消失后，行动会暴露真正的选择。"],
      ["Do not wait to feel ready; readiness often follows motion.", "不要等到准备好了才行动，准备感常常跟在行动之后。", "开始会创造信息，信息会带来准备。"],
      ["A wiser life is built by deleting what keeps winning your attention.", "更明智的生活，来自删掉那些总能赢走你注意力的东西。", "注意力在哪里，人生就被哪里塑形。"],
    ],
    "勇气": [
      ["Courage is fear that has learned to walk.", "勇气，是学会继续往前走的恐惧。", "不是没有害怕，而是害怕仍然没有拿走方向盘。"],
      ["Bravery can be as small as one honest sentence.", "勇敢也可以小到只是一句真话。", "很多关键改变，都从一次诚实表达开始。"],
      ["A bold choice is often a quiet refusal to shrink.", "大胆的选择，常常只是安静地拒绝缩小自己。", "勇气不一定喧哗，它也可以很克制。"],
      ["You cannot cross a bridge by negotiating forever with the river.", "你不能永远和河流谈判，却期待自己过桥。", "有些事需要判断，有些事需要迈步。"],
      ["Fear becomes smaller when it is given a task.", "恐惧一旦被分配任务，就会变小。", "把模糊的怕变成具体行动，情绪会下降。"],
      ["The door you avoid may be the door you need.", "你回避的门，可能正是你需要的门。", "回避有时是在保护你，有时是在困住你。"],
      ["Risk is not the opposite of safety; blindness is.", "风险的反面不是安全，盲目才是。", "真正的安全来自看清楚之后的行动。"],
      ["Some futures open only after a nervous yes.", "有些未来，只在一次紧张的同意后打开。", "紧张不代表错，可能只是你正在扩展边界。"],
      ["Do the brave thing before your excuses organize themselves.", "在借口组织起来之前，先做那件勇敢的事。", "行动越晚，内耗越会变得有条理。"],
      ["A smaller life is still a cost.", "过小的人生，也是一种代价。", "不冒险有时看似便宜，长期却很昂贵。"],
      ["If your voice shakes, let it shake and speak anyway.", "如果声音发抖，就让它发抖，然后继续说。", "表达的价值不取决于是否完美镇定。"],
      ["Courage is choosing direction before certainty arrives.", "勇气，是在确定感到来之前先选择方向。", "完全确定之后再行动，很多机会已经走远。"],
      ["The map appears after you enter the unknown.", "地图往往在你进入未知之后才出现。", "未知不是空白，它只是尚未被你走过。"],
      ["A brave life is not louder; it is less negotiable.", "勇敢的人生不一定更响亮，但更不容易被讨价还价。", "知道底线的人，行动会更清楚。"],
      ["Fear is a signal, not a sentence.", "恐惧是信号，不是判决书。", "它提醒你认真，但不应该替你决定。"],
      ["You can be careful without being closed.", "你可以谨慎，但不必封闭。", "谨慎是智慧，封闭是错过。"],
      ["The first step does not need applause; it needs your foot.", "第一步不需要掌声，只需要你的脚。", "开始本身就是证据。"],
      ["A difficult yes can rescue years from hesitation.", "一个艰难的同意，可能把多年从犹豫里救出来。", "有些选择贵在及时。"],
    ],
    "学习": [
      ["Learning is the art of staying curious after confusion.", "学习，是在困惑之后仍保持好奇的艺术。", "困惑不是失败，它常是理解即将发生的入口。"],
      ["A good question is a lantern in a crowded mind.", "好问题，是拥挤头脑里的一盏灯。", "问题越清楚，努力越不容易散掉。"],
      ["Knowledge becomes yours when you can use it on a Tuesday.", "知识能在普通星期二被你用上，才真正属于你。", "能应用的知识，比能背诵的知识更可靠。"],
      ["The best notes are promises to your future attention.", "最好的笔记，是写给未来注意力的承诺。", "笔记不是装饰，而是帮你重新进入思路。"],
      ["Understanding is slower than memory, but it stays longer.", "理解比记忆慢，但停留更久。", "不要只追求快，长期学习更看重可迁移。"],
      ["Every expert was once corrected by a beginner's mistake.", "每个专家都曾被初学者的错误纠正过。", "错误是学习系统的反馈，不是人格评价。"],
      ["Read until the world has more doors.", "一直读，直到世界出现更多门。", "阅读扩大选择，而不仅是增加信息。"],
      ["Practice turns borrowed ideas into personal tools.", "练习把借来的观点变成自己的工具。", "没有练习，知识容易只是漂亮的收藏。"],
      ["The mind grows by meeting what resists it.", "头脑在遇见阻力时生长。", "太顺的内容通常不够训练你。"],
      ["A page understood deeply beats a book skimmed proudly.", "深懂一页，胜过骄傲地略读一本书。", "学习质量不只由数量决定。"],
      ["Do not worship speed; worship return.", "不要崇拜速度，要重视回到问题上的能力。", "能反复回到关键处，才有积累。"],
      ["Revision is respect for the limits of memory.", "复习，是对记忆局限的尊重。", "忘记不是敌人，缺少复习系统才是。"],
      ["A difficult text is a gym for attention.", "难读的文本，是注意力的训练馆。", "慢下来读，往往比逃开更有收益。"],
      ["Learn the rule, then learn where it bends.", "先学习规则，再学习规则在哪里弯曲。", "真正的掌握包括边界感。"],
      ["Your vocabulary is the size of your possible thoughts.", "你的词汇量，限制着你能想到的世界。", "语言不仅表达思想，也塑造思想。"],
      ["A teacher opens a door; practice keeps it open.", "老师打开门，练习让门一直开着。", "输入重要，但输出才让能力稳定。"],
      ["The answer is useful; the method is portable.", "答案有用，方法可迁移。", "学习时要同时问：这个方法还能用在哪里？"],
      ["Curiosity is attention with a pulse.", "好奇心，是有脉搏的注意力。", "被点燃的注意力，会自己寻找材料。"],
    ],
    "时间": [
      ["Time does not shout, but it always collects.", "时间不会大喊，但它总会结账。", "每天的选择最终都会被时间汇总。"],
      ["A day is a small life with a deadline.", "一天，是带期限的小人生。", "把今天过清楚，比幻想整个人生更实际。"],
      ["Delay is expensive because it looks free.", "拖延昂贵，因为它看起来免费。", "真正的成本常常在以后才出现。"],
      ["Your calendar is a biography written in advance.", "你的日程表，是提前写下的人生传记。", "时间安排暴露真正的优先级。"],
      ["The future arrives disguised as routine.", "未来常伪装成日常抵达。", "你重复的事，正在提前塑造未来。"],
      ["Do not spend your best hours on someone else's urgency.", "不要把最好的时间花在别人的紧急感上。", "区分紧急和重要，是成年人必须学的边界。"],
      ["A minute protected is a life respected.", "保护一分钟，就是尊重一段人生。", "时间管理本质上是自我尊重。"],
      ["The clock is honest even when we are not.", "时钟很诚实，即使我们不诚实。", "它不会听解释，只记录流向。"],
      ["One focused hour can repair a scattered week.", "专注一小时，可以修复散乱的一周。", "高质量专注常常比长时间消耗更有效。"],
      ["Tomorrow is built from what today refuses to postpone.", "明天由今天拒绝拖延的事建成。", "每一次及时行动，都在保护未来。"],
      ["The past is a teacher, not a landlord.", "过去是老师，不是房东。", "它可以提醒你，但不该一直占住你。"],
      ["Use time as a bridge, not a hiding place.", "把时间当桥，不要当藏身处。", "等待可以是准备，也可以是逃避。"],
      ["What you postpone becomes heavier.", "你推迟的事，会变得更重。", "拖延会给任务加上情绪利息。"],
      ["A clear morning can change the tone of a whole day.", "一个清楚的早晨，可以改变整天的语气。", "开头越稳，后面越少补救。"],
      ["Time reveals which desires were only weather.", "时间会揭示哪些欲望只是天气。", "经不起时间的欲望，未必值得追。"],
      ["Rest is not wasted time if it returns you to yourself.", "休息如果能让你回到自己身上，就不是浪费。", "恢复力也是生产力的一部分。"],
      ["The longest journey still uses one present moment at a time.", "最长的旅程，也只能一次使用一个当下。", "焦虑常来自想一次处理全部未来。"],
      ["A life is not short when its hours are awake.", "如果每个小时是醒着的，人生并不短。", "清醒比长度更重要。"],
    ],
    "幽默": [
      ["My plans are very ambitious for someone who still forgets why he opened the fridge.", "对一个常忘记为什么打开冰箱的人来说，我的计划确实很宏大。", "幽默有时是承认人类系统并不稳定。"],
      ["I enjoy deadlines; they make my panic feel organized.", "我喜欢截止日期，它让我的慌张显得有组织。", "把慌张说出来，压力就没那么神秘。"],
      ["Some problems need wisdom; others need lunch.", "有些问题需要智慧，有些问题需要先吃饭。", "不要在低血糖时审判人生。"],
      ["I am not lazy; I am buffering.", "我不是懒，我是在缓冲。", "轻松一点，也许只是系统正在加载。"],
      ["A clean desk is a sign that the mess has moved to the mind.", "整洁的桌面说明混乱可能搬进了大脑。", "外部秩序和内部秩序并不总是同步。"],
      ["The early bird gets the worm, but the second mouse gets the cheese.", "早起的鸟有虫吃，但第二只老鼠有奶酪吃。", "速度重要，判断也重要。"],
      ["Coffee is a meeting between hope and chemistry.", "咖啡，是希望和化学的一次会议。", "有些动力确实需要一点外援。"],
      ["My comfort zone has excellent Wi-Fi.", "我的舒适区网速很好。", "舒适区难离开，通常是因为它真的很舒服。"],
      ["Common sense is rare enough to be a superpower.", "常识稀有到几乎像超能力。", "幽默的背后常是对现实的清醒观察。"],
      ["If life gives you lemons, check whether you ordered them online.", "如果生活给你柠檬，先看看是不是你自己网购的。", "有些麻烦确实是自己下单的。"],
      ["A meeting is where minutes are kept and hours are lost.", "会议是保存会议纪要、丢失小时的地方。", "这句适合提醒自己：开会要有产出。"],
      ["I have a perfectly balanced diet: one snack in each hand.", "我的饮食非常均衡：两只手各拿一份零食。", "幽默能把小放纵变得可爱一点。"],
      ["The password is strong because even I cannot remember it.", "这个密码很强，因为连我自己都记不住。", "安全性和可用性经常互相拉扯。"],
      ["The mind is willing, but the sofa is persuasive.", "心是愿意的，但沙发很有说服力。", "很多失败并非意志太弱，而是环境太会劝退。"],
      ["I do my best thinking right after I should have gone to sleep.", "我最会思考的时候，通常是本该睡觉之后。", "灵感若总在深夜来，也许白天需要留空。"],
      ["Every app wants my attention; none offers to pay rent.", "每个应用都想占用我的注意力，却没有一个愿意付房租。", "注意力是资产，不是公共广场。"],
      ["I cleaned my room and found three versions of myself.", "我打扫房间，找到了三个版本的自己。", "物品常常保存着过去的身份。"],
      ["The shortest distance between two tasks is usually procrastination.", "两个任务之间最短的距离，通常叫拖延。", "幽默地承认它，然后回到手头那一步。"],
    ],
  };

  const extraCategories = [
    ["内心", "Peace is not the absence of noise; it is the refusal to become noise.", "平静不是没有噪音，而是拒绝让自己也变成噪音。", "安静"],
    ["生活", "A rich life is measured by attention, not decoration.", "富足的人生用注意力衡量，而不是用装饰衡量。", "深刻"],
    ["创造", "Creativity is intelligence taking off its uniform.", "创造力，是智力脱下制服的样子。", "有趣"],
    ["关系", "Love is attention that has learned patience.", "爱，是学会耐心的注意力。", "温暖"],
    ["工作", "Great work is ordinary work protected from distraction.", "伟大的工作，是被保护起来、不被打扰的普通工作。", "坚定"],
    ["选择", "Every choice edits the person who makes it.", "每一个选择，都在编辑做选择的人。", "深刻"],
    ["希望", "Hope is not a prediction; it is a decision to keep planting.", "希望不是预测，而是继续种下去的决定。", "温暖"],
    ["逆境", "Hard days do not cancel your direction.", "艰难的日子不会取消你的方向。", "坚定"],
    ["表达", "A clear sentence is a kindness to another mind.", "清楚的句子，是对另一个头脑的善意。", "温暖"],
    ["观察", "Attention turns ordinary scenes into teachers.", "注意力能把普通场景变成老师。", "安静"],
    ["现实", "Reality is patient with our opinions.", "现实对我们的意见很有耐心。", "有趣"],
    ["价值", "Value begins where usefulness meets care.", "价值始于有用与用心相遇的地方。", "深刻"],
  ];

  const ieltsThemes = [
    { category: "科技", subject: "digital technology", subjectCn: "数字技术", benefit: "making information easier to reach", benefitCn: "让信息更容易获取", people: "ordinary users", peopleCn: "普通用户", problem: "privacy and attention", problemCn: "隐私和注意力", setting: "schools, offices and public services", settingCn: "学校、办公室和公共服务中" },
    { category: "教育", subject: "modern education", subjectCn: "现代教育", benefit: "opening more flexible paths to knowledge", benefitCn: "打开更灵活的知识路径", people: "students", peopleCn: "学生", problem: "exam pressure and shallow learning", problemCn: "考试压力和浅层学习", setting: "classrooms and online courses", settingCn: "课堂和线上课程中" },
    { category: "环境", subject: "environmental protection", subjectCn: "环境保护", benefit: "turning public concern into practical habits", benefitCn: "把公众关切转化为实际习惯", people: "communities", peopleCn: "社区", problem: "short-term convenience", problemCn: "短期便利", setting: "homes, factories and city planning", settingCn: "家庭、工厂和城市规划中" },
    { category: "城市", subject: "urban development", subjectCn: "城市发展", benefit: "bringing people closer to jobs and services", benefitCn: "让人们更接近工作和服务", people: "city residents", peopleCn: "城市居民", problem: "crowding and unequal access", problemCn: "拥挤和机会不均", setting: "transport, housing and public spaces", settingCn: "交通、住房和公共空间中" },
    { category: "健康", subject: "public health", subjectCn: "公共健康", benefit: "preventing problems before they become expensive", benefitCn: "在问题变昂贵之前预防它们", people: "families", peopleCn: "家庭", problem: "misinformation and unhealthy routines", problemCn: "错误信息和不健康习惯", setting: "clinics, workplaces and daily life", settingCn: "诊所、工作场所和日常生活中" },
    { category: "工作", subject: "the changing workplace", subjectCn: "不断变化的职场", benefit: "allowing people to work with greater flexibility", benefitCn: "让人们以更灵活的方式工作", people: "employees", peopleCn: "员工", problem: "burnout and unstable expectations", problemCn: "职业倦怠和不稳定期待", setting: "teams, platforms and remote meetings", settingCn: "团队、平台和远程会议中" },
    { category: "媒体", subject: "social media", subjectCn: "社交媒体", benefit: "giving individuals a public voice", benefitCn: "给个体公共表达的声音", people: "young people", peopleCn: "年轻人", problem: "comparison and unreliable information", problemCn: "攀比和不可靠信息", setting: "news feeds, short videos and online discussions", settingCn: "信息流、短视频和线上讨论中" },
    { category: "全球化", subject: "globalisation", subjectCn: "全球化", benefit: "connecting markets, ideas and cultures", benefitCn: "连接市场、观念和文化", people: "local businesses", peopleCn: "本地企业", problem: "cultural sameness and economic dependence", problemCn: "文化趋同和经济依赖", setting: "trade, travel and digital services", settingCn: "贸易、旅行和数字服务中" },
    { category: "文化", subject: "cultural heritage", subjectCn: "文化遗产", benefit: "helping people understand where they come from", benefitCn: "帮助人们理解自己的来处", people: "younger generations", peopleCn: "年轻一代", problem: "commercialisation and neglect", problemCn: "商业化和忽视", setting: "museums, festivals and family stories", settingCn: "博物馆、节日和家庭故事中" },
    { category: "政府", subject: "government policy", subjectCn: "政府政策", benefit: "coordinating resources that individuals cannot manage alone", benefitCn: "协调个人无法独自管理的资源", people: "citizens", peopleCn: "公民", problem: "bureaucracy and weak accountability", problemCn: "官僚主义和问责不足", setting: "taxation, welfare and public infrastructure", settingCn: "税收、福利和公共基础设施中" },
    { category: "交通", subject: "public transport", subjectCn: "公共交通", benefit: "reducing the cost and stress of daily movement", benefitCn: "降低日常出行的成本和压力", people: "commuters", peopleCn: "通勤者", problem: "delays and poor last-mile connections", problemCn: "延误和最后一公里连接不足", setting: "metros, buses and shared mobility systems", settingCn: "地铁、公交和共享出行系统中" },
    { category: "老龄化", subject: "population ageing", subjectCn: "人口老龄化", benefit: "encouraging societies to value experience and long-term care", benefitCn: "促使社会重视经验和长期照护", people: "older adults", peopleCn: "老年人", problem: "loneliness and pressure on services", problemCn: "孤独和公共服务压力", setting: "families, hospitals and community centres", settingCn: "家庭、医院和社区中心中" },
    { category: "旅游", subject: "international tourism", subjectCn: "国际旅游", benefit: "creating income and cultural curiosity", benefitCn: "创造收入和文化好奇心", people: "host communities", peopleCn: "接待地社区", problem: "overcrowding and fragile local identity", problemCn: "过度拥挤和脆弱的本地身份", setting: "historic districts, hotels and transport hubs", settingCn: "历史街区、酒店和交通枢纽中" },
    { category: "消费", subject: "consumer culture", subjectCn: "消费文化", benefit: "offering people more choice and convenience", benefitCn: "给人们更多选择和便利", people: "customers", peopleCn: "消费者", problem: "waste and emotional spending", problemCn: "浪费和情绪性消费", setting: "shopping platforms, advertisements and everyday routines", settingCn: "购物平台、广告和日常习惯中" },
    { category: "科学", subject: "scientific research", subjectCn: "科学研究", benefit: "turning uncertainty into testable knowledge", benefitCn: "把不确定性转化为可检验的知识", people: "researchers and the public", peopleCn: "研究者和公众", problem: "funding pressure and ethical risk", problemCn: "资金压力和伦理风险", setting: "laboratories, universities and public debates", settingCn: "实验室、大学和公共讨论中" },
    { category: "家庭", subject: "family life", subjectCn: "家庭生活", benefit: "giving people emotional security and practical support", benefitCn: "给人们情感安全和实际支持", people: "parents and children", peopleCn: "父母和孩子", problem: "time pressure and changing values", problemCn: "时间压力和价值观变化", setting: "homes, schools and working schedules", settingCn: "家庭、学校和工作安排中" },
    { category: "商务", subject: "business competition", subjectCn: "商业竞争", benefit: "pushing companies to improve products and services", benefitCn: "推动企业改进产品和服务", people: "small firms and consumers", peopleCn: "小企业和消费者", problem: "short-term profit and unfair market power", problemCn: "短期利润和不公平市场权力", setting: "retail markets, supply chains and online platforms", settingCn: "零售市场、供应链和线上平台中" },
    { category: "创业", subject: "entrepreneurship", subjectCn: "创业", benefit: "turning new ideas into jobs and practical solutions", benefitCn: "把新想法转化为就业和实际方案", people: "young founders", peopleCn: "年轻创业者", problem: "financial uncertainty and weak support systems", problemCn: "财务不确定性和支持系统薄弱", setting: "start-up hubs, universities and local economies", settingCn: "创业园区、大学和地方经济中" },
    { category: "金融", subject: "financial inclusion", subjectCn: "金融普惠", benefit: "helping people save, borrow and invest more efficiently", benefitCn: "帮助人们更高效地储蓄、借贷和投资", people: "households and small businesses", peopleCn: "家庭和小企业", problem: "debt, speculation and unequal access", problemCn: "债务、投机和机会不均", setting: "banks, mobile payments and investment platforms", settingCn: "银行、移动支付和投资平台中" },
    { category: "财务", subject: "personal financial planning", subjectCn: "个人财务规划", benefit: "making long-term goals more realistic", benefitCn: "让长期目标更现实", people: "working adults", peopleCn: "职场成年人", problem: "impulse spending and limited financial literacy", problemCn: "冲动消费和有限的财务素养", setting: "family budgets, insurance and retirement plans", settingCn: "家庭预算、保险和退休计划中" },
    { category: "税收", subject: "tax policy", subjectCn: "税收政策", benefit: "funding public goods that markets often underprovide", benefitCn: "为市场常常供给不足的公共产品提供资金", people: "taxpayers and vulnerable groups", peopleCn: "纳税人和弱势群体", problem: "avoidance, complexity and public mistrust", problemCn: "避税、复杂性和公众不信任", setting: "public budgets, welfare systems and local services", settingCn: "公共预算、福利系统和地方服务中" },
    { category: "企业责任", subject: "corporate responsibility", subjectCn: "企业责任", benefit: "aligning business success with social expectations", benefitCn: "让商业成功与社会期待保持一致", people: "employees, customers and local communities", peopleCn: "员工、客户和本地社区", problem: "greenwashing and symbolic promises", problemCn: "漂绿和象征性承诺", setting: "workplaces, supply chains and environmental reporting", settingCn: "工作场所、供应链和环境报告中" },
    { category: "人工智能", subject: "artificial intelligence", subjectCn: "人工智能", benefit: "handling complex tasks at a scale humans could not manage alone", benefitCn: "以人类难以独自处理的规模完成复杂任务", people: "workers, students and decision-makers", peopleCn: "劳动者、学生和决策者", problem: "bias, dependence and accountability", problemCn: "偏见、依赖和问责", setting: "recruitment, education, healthcare and public administration", settingCn: "招聘、教育、医疗和公共管理中" },
    { category: "数据安全", subject: "data protection", subjectCn: "数据保护", benefit: "allowing useful digital services to operate with trust", benefitCn: "让有用的数字服务在信任基础上运行", people: "internet users", peopleCn: "互联网用户", problem: "surveillance, leaks and unclear consent", problemCn: "监控、泄露和同意机制不清", setting: "apps, hospitals, schools and financial platforms", settingCn: "应用、医院、学校和金融平台中" },
    { category: "自动化", subject: "automation", subjectCn: "自动化", benefit: "removing repetitive work and raising productivity", benefitCn: "减少重复劳动并提高生产率", people: "factory workers and office staff", peopleCn: "工厂工人和办公室员工", problem: "job displacement and skill mismatch", problemCn: "岗位替代和技能错配", setting: "manufacturing, logistics and administrative work", settingCn: "制造业、物流和行政工作中" },
    { category: "平台经济", subject: "the platform economy", subjectCn: "平台经济", benefit: "connecting buyers, sellers and workers with unusual speed", benefitCn: "以极快速度连接买家、卖家和劳动者", people: "gig workers and consumers", peopleCn: "零工劳动者和消费者", problem: "algorithmic control and weak labour protection", problemCn: "算法控制和劳动保护不足", setting: "ride-hailing, food delivery and online marketplaces", settingCn: "网约车、外卖和线上市场中" },
    { category: "城市财政", subject: "urban finance", subjectCn: "城市财政", benefit: "supporting transport, housing and public facilities", benefitCn: "支持交通、住房和公共设施", people: "municipal governments and residents", peopleCn: "市政政府和居民", problem: "debt pressure and uneven neighbourhood investment", problemCn: "债务压力和社区投资不均", setting: "infrastructure projects, land use and public-private partnerships", settingCn: "基础设施项目、土地使用和公私合作中" },
    { category: "住房", subject: "housing affordability", subjectCn: "住房可负担性", benefit: "giving people a stable base for work and family life", benefitCn: "为人们的工作和家庭生活提供稳定基础", people: "young workers and low-income families", peopleCn: "年轻劳动者和低收入家庭", problem: "speculation, scarcity and long commutes", problemCn: "投机、稀缺和长距离通勤", setting: "rental markets, suburbs and city centres", settingCn: "租赁市场、郊区和市中心中" },
    { category: "社区", subject: "community development", subjectCn: "社区发展", benefit: "turning local trust into practical support", benefitCn: "把本地信任转化为实际支持", people: "residents and volunteers", peopleCn: "居民和志愿者", problem: "isolation and unequal participation", problemCn: "孤立和参与不均", setting: "neighbourhood groups, libraries and public parks", settingCn: "社区组织、图书馆和公共公园中" },
    { category: "社会公平", subject: "social equality", subjectCn: "社会公平", benefit: "allowing talent to develop regardless of background", benefitCn: "让才能不受出身限制地发展", people: "disadvantaged groups", peopleCn: "弱势群体", problem: "structural barriers and inherited disadvantage", problemCn: "结构性障碍和代际劣势", setting: "education, employment and public services", settingCn: "教育、就业和公共服务中" },
    { category: "公共服务", subject: "public service provision", subjectCn: "公共服务供给", benefit: "protecting basic dignity when private solutions are insufficient", benefitCn: "在私人方案不足时保护基本尊严", people: "citizens", peopleCn: "公民", problem: "underfunding, waiting times and inconsistent quality", problemCn: "资金不足、等待时间长和质量不稳定", setting: "schools, hospitals, transport and social care", settingCn: "学校、医院、交通和社会照护中" },
    { category: "社会信任", subject: "social trust", subjectCn: "社会信任", benefit: "reducing the cost of cooperation", benefitCn: "降低合作成本", people: "citizens, businesses and institutions", peopleCn: "公民、企业和机构", problem: "misinformation, corruption and polarisation", problemCn: "错误信息、腐败和极化", setting: "public debate, local governance and online communities", settingCn: "公共讨论、地方治理和线上社区中" },
    { category: "贫富差距", subject: "income inequality", subjectCn: "收入不平等", benefit: "revealing where opportunity is unevenly distributed", benefitCn: "揭示机会分配不均之处", people: "low-income workers and young families", peopleCn: "低收入劳动者和年轻家庭", problem: "social mobility and political resentment", problemCn: "社会流动性和政治不满", setting: "wages, housing, education and taxation", settingCn: "工资、住房、教育和税收中" },
    { category: "消费金融", subject: "consumer finance", subjectCn: "消费金融", benefit: "making purchases and emergencies easier to manage", benefitCn: "让消费和应急支出更容易管理", people: "young consumers", peopleCn: "年轻消费者", problem: "hidden fees and long-term debt", problemCn: "隐藏费用和长期债务", setting: "credit cards, online loans and buy-now-pay-later services", settingCn: "信用卡、网络贷款和先买后付服务中" },
    { category: "数字营销", subject: "digital advertising", subjectCn: "数字广告", benefit: "helping businesses reach customers with greater precision", benefitCn: "帮助企业更精准地触达客户", people: "brands and consumers", peopleCn: "品牌和消费者", problem: "manipulation, data tracking and impulsive consumption", problemCn: "操控、数据追踪和冲动消费", setting: "search engines, social media and shopping apps", settingCn: "搜索引擎、社交媒体和购物应用中" },
    { category: "供应链", subject: "global supply chain management", subjectCn: "全球供应链管理", benefit: "lowering costs and spreading specialised production", benefitCn: "降低成本并扩散专业化生产", people: "manufacturers and consumers", peopleCn: "制造商和消费者", problem: "fragility, labour standards and environmental impact", problemCn: "脆弱性、劳动标准和环境影响", setting: "factories, ports and international trade networks", settingCn: "工厂、港口和国际贸易网络中" },
    { category: "商业伦理", subject: "business ethics", subjectCn: "商业伦理", benefit: "building trust that cannot be purchased through advertising", benefitCn: "建立无法靠广告购买的信任", people: "managers, employees and customers", peopleCn: "管理者、员工和客户", problem: "conflicts of interest and weak transparency", problemCn: "利益冲突和透明度不足", setting: "pricing, hiring, data use and product safety", settingCn: "定价、招聘、数据使用和产品安全中" },
    { category: "社会媒体", subject: "online public opinion", subjectCn: "线上公共舆论", benefit: "making social problems visible more quickly", benefitCn: "更快地让社会问题被看见", people: "citizens and policymakers", peopleCn: "公民和政策制定者", problem: "emotional reactions and incomplete evidence", problemCn: "情绪化反应和证据不完整", setting: "comment sections, livestreams and public campaigns", settingCn: "评论区、直播和公共行动中" },
    { category: "城市更新", subject: "urban renewal", subjectCn: "城市更新", benefit: "reviving old districts and improving public safety", benefitCn: "复兴旧城区并改善公共安全", people: "long-term residents and new businesses", peopleCn: "长期居民和新企业", problem: "gentrification and the loss of local memory", problemCn: "绅士化和本地记忆流失", setting: "old neighbourhoods, commercial streets and transport corridors", settingCn: "老社区、商业街和交通走廊中" },
    { category: "科技监管", subject: "technology regulation", subjectCn: "科技监管", benefit: "setting boundaries before innovation creates irreversible harm", benefitCn: "在创新造成不可逆伤害之前设定边界", people: "innovators, users and regulators", peopleCn: "创新者、用户和监管者", problem: "slow legislation and fast-moving business models", problemCn: "立法缓慢和快速变化的商业模式", setting: "AI systems, fintech products and data-driven services", settingCn: "人工智能系统、金融科技产品和数据驱动服务中" },
  ];

  const ieltsComplexFrames = [
    {
      label: "让步",
      grammar: "让步状语从句 + whether 引导宾语从句",
      tone: "深刻",
      english: (item) => `Although ${item.subject} is often praised for ${item.benefit}, its real value depends on whether it helps ${item.people} make wiser choices rather than merely faster ones.`,
      chinese: (item) => `虽然${item.subjectCn}常因${item.benefitCn}而受到称赞，但它真正的价值取决于它是否帮助${item.peopleCn}做出更明智的选择，而不只是更快的选择。`,
    },
    {
      label: "定语从句",
      grammar: "非限制性定语从句 + 因果表达",
      tone: "深刻",
      english: (item) => `${capitalise(item.subject)}, which increasingly shapes decisions in ${item.setting}, should be judged not only by its efficiency but also by the kind of behaviour it encourages.`,
      chinese: (item) => `${item.subjectCn}正在越来越多地影响${item.settingCn}的决策，因此不应只按效率评价它，也应看它鼓励了什么样的行为。`,
    },
    {
      label: "分词结构",
      grammar: "分词结构 + 转折",
      tone: "坚定",
      english: (item) => `Seen from a long-term perspective, ${item.subject} is less a simple solution than a tool whose benefits depend on discipline, fairness and public trust.`,
      chinese: (item) => `从长期角度看，${item.subjectCn}与其说是简单解决方案，不如说是一种工具，其好处取决于纪律、公平和公众信任。`,
    },
    {
      label: "条件句",
      grammar: "条件句 + rather than 对比",
      tone: "坚定",
      english: (item) => `If ${item.subject} is introduced without clear rules, it may solve visible problems while quietly creating deeper ones related to ${item.problem}.`,
      chinese: (item) => `如果${item.subjectCn}在缺乏清晰规则的情况下被引入，它可能解决表面问题，却悄悄制造与${item.problemCn}有关的更深层问题。`,
    },
    {
      label: "强调句",
      grammar: "It is not...but... 强调句型",
      tone: "深刻",
      english: (item) => `It is not the existence of ${item.subject} itself, but the way people design and use it, that determines whether it becomes a source of progress or pressure.`,
      chinese: (item) => `决定${item.subjectCn}成为进步来源还是压力来源的，并不是它本身的存在，而是人们设计和使用它的方式。`,
    },
    {
      label: "对比句",
      grammar: "while 对比句 + 抽象名词",
      tone: "温暖",
      english: (item) => `While ${item.subject} can expand what ${item.people} are able to do, it should not replace the patience, judgment and responsibility that meaningful improvement requires.`,
      chinese: (item) => `虽然${item.subjectCn}能够扩展${item.peopleCn}能做的事，但它不应取代有意义的改进所需要的耐心、判断力和责任感。`,
    },
    {
      label: "比较结构",
      grammar: "the more..., the more... 比较结构",
      tone: "坚定",
      english: (item) => `The more deeply ${item.subject} enters ${item.setting}, the more important it becomes to ask who benefits, who is left out and what trade-offs are being ignored.`,
      chinese: (item) => `${item.subjectCn}越深入${item.settingCn}，我们就越需要追问谁受益、谁被排除在外，以及哪些取舍被忽视了。`,
    },
    {
      label: "名词性从句",
      grammar: "名词性从句 + 让步转折",
      tone: "深刻",
      english: (item) => `What makes ${item.subject} difficult to evaluate is that its advantages are usually immediate, whereas its hidden costs may take years to become obvious.`,
      chinese: (item) => `${item.subjectCn}难以评价的地方在于，它的好处通常立刻可见，而隐藏成本可能需要多年才变得明显。`,
    },
    {
      label: "伴随状语",
      grammar: "伴随状语 + 结果表达",
      tone: "坚定",
      english: (item) => `By making ${item.benefit} possible, ${item.subject} can improve daily life, provided that society remains alert to ${item.problem}.`,
      chinese: (item) => `${item.subjectCn}通过让${item.benefitCn}成为可能，可以改善日常生活，前提是社会始终警惕${item.problemCn}。`,
    },
    {
      label: "插入语",
      grammar: "插入语 + 平衡观点",
      tone: "安静",
      english: (item) => `${capitalise(item.subject)}, however useful it may appear, should be treated as part of a broader system rather than as a substitute for careful human judgment.`,
      chinese: (item) => `${item.subjectCn}无论看起来多么有用，都应被视为更大系统的一部分，而不是细致人为判断的替代品。`,
    },
    {
      label: "观点句",
      grammar: "定语从句 + 可迁移观点句",
      tone: "深刻",
      english: (item) => `A society that adopts ${item.subject} wisely is one that measures success by resilience, inclusion and long-term value, not by speed alone.`,
      chinese: (item) => `一个明智采用${item.subjectCn}的社会，会用韧性、包容和长期价值衡量成功，而不只用速度衡量。`,
    },
    {
      label: "倒装句",
      grammar: "倒装语气 + 写作结论句",
      tone: "坚定",
      english: (item) => `Only when ${item.subject} is guided by clear aims and ethical limits can it become a force that improves life without narrowing human choice.`,
      chinese: (item) => `只有当${item.subjectCn}受到清晰目标和伦理边界的引导时，它才能成为改善生活而不压缩人类选择的力量。`,
    },
  ];

  function $(id) {
    return document.getElementById(id);
  }

  function esc(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function capitalise(value) {
    const text = String(value || "");
    return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
  }

  function buildSentences() {
    const cards = quoted.map(([id, english, chinese, author, category, tone]) => ({
      id,
      english,
      chinese,
      author,
      category,
      tone,
      kind: "名言短句",
      note: "适合背诵、摘抄，也可以用于口语或写作中的简短引入。",
    }));
    Object.entries(originals).forEach(([category, items]) => {
      items.forEach(([english, chinese, note], index) => {
        cards.push({
          id: `o-${category}-${String(index + 1).padStart(2, "0")}`,
          english,
          chinese,
          author: "Datakrs Original",
          category,
          tone: category === "幽默" ? "有趣" : index % 3 === 0 ? "坚定" : index % 3 === 1 ? "深刻" : "温暖",
          kind: "原创金句",
          note,
        });
      });
    });
    const stems = [
      "A good life becomes clearer when",
      "The mind becomes lighter when",
      "Real confidence grows when",
      "A difficult day softens when",
      "The future changes shape when",
      "Wisdom begins when",
      "A brave person learns that",
      "The heart becomes steadier when",
      "An ordinary hour becomes meaningful when",
      "A small decision becomes powerful when",
      "The world feels wider when",
      "A tired soul recovers when",
    ];
    const endings = [
      ["you stop asking every fear for permission.", "你不再向每一种恐惧索要许可。", "勇气"],
      ["you give your attention to what can still be changed.", "你把注意力交给仍能改变的事情。", "行动"],
      ["you choose a useful step over a perfect excuse.", "你选择一个有用的步骤，而不是一个完美的借口。", "成长"],
      ["you let silence answer what noise cannot solve.", "你让沉默回答噪音解决不了的问题。", "内心"],
      ["you protect your morning from borrowed urgency.", "你保护清晨，不让它被别人的紧急感夺走。", "时间"],
      ["you read your mistakes as maps, not verdicts.", "你把错误读成地图，而不是判决。", "学习"],
      ["you make peace with being a beginner again.", "你愿意再次和初学者身份和解。", "学习"],
      ["you build the habit before demanding the result.", "你先建立习惯，再要求结果。", "努力"],
      ["you stop decorating confusion and start naming it.", "你不再装饰困惑，而是开始命名它。", "思考"],
      ["you spend less energy proving and more energy improving.", "你少花力气证明自己，多花力气改善自己。", "成长"],
      ["you can laugh without running away from the truth.", "你能笑出来，同时不逃避真相。", "幽默"],
      ["you turn comparison into information, not punishment.", "你把比较变成信息，而不是惩罚。", "自我"],
      ["you remember that attention is a form of love.", "你记得注意力也是一种爱。", "关系"],
      ["you give your work enough quiet to become excellent.", "你给工作足够的安静，让它变得优秀。", "工作"],
      ["you stop waiting for life to feel cinematic.", "你不再等待生活变得像电影。", "生活"],
      ["you notice beauty before trying to own it.", "你先看见美，而不是急着拥有它。", "观察"],
      ["you replace envy with apprenticeship.", "你用学习取代嫉妒。", "价值"],
      ["you do not let one bad chapter name the whole book.", "你不让一个糟糕章节命名整本书。", "希望"],
      ["you treat rest as maintenance, not surrender.", "你把休息当维护，而不是投降。", "生活"],
      ["you ask better questions than your anxiety asks.", "你提出比焦虑更好的问题。", "思考"],
    ];
    let serial = 1;
    stems.forEach((stem, stemIndex) => {
      endings.forEach(([ending, zh, category], endingIndex) => {
        cards.push({
          id: `m${String(serial).padStart(3, "0")}`,
          english: `${stem} ${ending}`,
          chinese: `当${zh}`,
          author: "Datakrs Original",
          category,
          tone: ["深刻", "温暖", "坚定", "安静", "有趣"][(stemIndex + endingIndex) % 5],
          kind: "灵感句",
          note: "这类句子适合每天刷读，重点感受英文节奏、抽象表达和可复用观点。",
        });
        serial += 1;
      });
    });
    extraCategories.forEach(([category, english, chinese, tone], index) => {
      cards.push({
        id: `x${String(index + 1).padStart(3, "0")}`,
        english,
        chinese,
        author: "Datakrs Original",
        category,
        tone,
        kind: "原创金句",
        note: "短句结构清楚，适合朗读、默写或改写成自己的表达。",
      });
    });
    ieltsThemes.forEach((theme, themeIndex) => {
      ieltsComplexFrames.forEach((frame, frameIndex) => {
        cards.push({
          id: `ielts-${String(themeIndex + 1).padStart(2, "0")}-${String(frameIndex + 1).padStart(2, "0")}`,
          english: frame.english(theme),
          chinese: frame.chinese(theme),
          author: "IELTS Expression",
          category: theme.category,
          tone: frame.tone,
          kind: "雅思复杂句",
          pattern: frame.label,
          grammar: frame.grammar,
          note: `句型：${frame.grammar}。用途：适合写作 Task 2 和口语 Part 3，用来讨论${theme.category.replace("雅思", "")}话题的利弊、条件、影响或结论。`,
        });
      });
    });
    return cards;
  }

  function refreshVoices() {
    if (!("speechSynthesis" in window)) return;
    state.voices = window.speechSynthesis.getVoices() || [];
  }

  function pickVoice() {
    if (!state.voices.length) refreshVoices();
    return state.voices.find((voice) => /^en[-_](US|GB)/i.test(voice.lang)) || state.voices.find((voice) => /^en/i.test(voice.lang)) || null;
  }

  function speak(text, button) {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = text.split(/\s+/).length > 12 ? 0.86 : 0.78;
    const voice = pickVoice();
    if (voice) utterance.voice = voice;
    if (button) button.classList.add("playing");
    utterance.onend = () => button && button.classList.remove("playing");
    utterance.onerror = () => button && button.classList.remove("playing");
    window.speechSynthesis.resume();
    window.speechSynthesis.speak(utterance);
  }

  function loadProgress() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
      state.activeId = saved.activeId || "";
      state.collection = saved.collection || "ielts";
      state.category = saved.category || "all";
      state.pattern = saved.pattern || "all";
      state.tone = saved.tone || "all";
      state.read = new Set(saved.read || []);
      state.favorite = new Set(saved.favorite || []);
    } catch (error) {
      state.read = new Set();
      state.favorite = new Set();
    }
  }

  function saveProgress() {
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        activeId: state.activeId,
        collection: state.collection,
        category: state.category,
        pattern: state.pattern,
        tone: state.tone,
        read: Array.from(state.read),
        favorite: Array.from(state.favorite),
      })
    );
  }

  function collectionItems() {
    if (state.collection === "ielts") return state.sentences.filter((item) => item.kind === "雅思复杂句");
    if (state.collection === "classic") return state.sentences.filter((item) => item.kind !== "雅思复杂句");
    return state.sentences;
  }

  function modeSummary(mode) {
    const count = state.sentences.filter((item) => {
      if (mode === "ielts") return item.kind === "雅思复杂句";
      if (mode === "classic") return item.kind !== "雅思复杂句";
      return true;
    }).length;
    const labels = {
      ielts: ["雅思复杂句", "写作 Task 2 / 口语 Part 3"],
      classic: ["金句素材", "哲理、幽默、名言短句"],
      all: ["全部句库", "综合刷读与收藏"],
    };
    return { count, title: labels[mode][0], desc: labels[mode][1] };
  }

  function categories() {
    let items = collectionItems();
    if (state.pattern !== "all") items = items.filter((item) => item.pattern === state.pattern);
    return ["all", ...Array.from(new Set(items.map((item) => item.category)))];
  }

  function patterns() {
    const items = collectionItems().filter((item) => item.kind === "雅思复杂句");
    return ["all", ...Array.from(new Set(items.map((item) => item.pattern).filter(Boolean)))];
  }

  function tones() {
    return ["all", ...Array.from(new Set(collectionItems().map((item) => item.tone)))];
  }

  function filteredSentences() {
    const query = state.query.trim().toLowerCase();
    return collectionItems().filter((item) => {
      if (state.pattern !== "all" && item.pattern !== state.pattern) return false;
      if (state.category !== "all" && item.category !== state.category) return false;
      if (state.tone !== "all" && item.tone !== state.tone) return false;
      if (!query) return true;
      return [item.english, item.chinese, item.author, item.category, item.tone, item.kind, item.pattern, item.grammar, item.note].join(" ").toLowerCase().includes(query);
    });
  }

  function activeSentence() {
    return state.sentences.find((item) => item.id === state.activeId) || filteredSentences()[0] || state.sentences[0];
  }

  function renderTabs(container, values, active, attr, allLabel) {
    container.innerHTML = values
      .map((value) => `<button class="vocab-chapter-tab${value === active ? " active" : ""}" type="button" data-${attr}="${esc(value)}">${esc(value === "all" ? allLabel : value)}</button>`)
      .join("");
  }

  function renderModes() {
    els.modes.innerHTML = ["ielts", "classic", "all"]
      .map((mode) => {
        const summary = modeSummary(mode);
        return `
          <button class="sentence-mode-card${state.collection === mode ? " active" : ""}" type="button" data-sentence-mode="${esc(mode)}">
            <strong>${esc(summary.title)}</strong>
            <span>${esc(summary.count)} 句</span>
            <small>${esc(summary.desc)}</small>
          </button>
        `;
      })
      .join("");
  }

  function renderList() {
    const items = filteredSentences();
    if (items.length && !items.some((item) => item.id === state.activeId)) state.activeId = items[0].id;
    els.count.textContent = `${items.length} 句`;
    els.list.innerHTML = items
      .map(
        (item, index) => `
          <button class="classic-sentence-row${item.id === state.activeId ? " active" : ""}${state.favorite.has(item.id) ? " favorite" : ""}" type="button" data-sentence-id="${esc(item.id)}">
            <span>${String(index + 1).padStart(3, "0")}</span>
            <strong>${esc(item.english)}</strong>
            <small>${esc(item.category)} · ${esc(item.tone)} · ${esc(item.author)}</small>
          </button>
        `
      )
      .join("");
    if (!items.length) els.list.innerHTML = '<div class="reading-empty">没有匹配句子，换个关键词试试。</div>';
  }

  function renderCard() {
    const item = activeSentence();
    if (!item) return;
    const items = filteredSentences();
    const index = Math.max(0, items.findIndex((entry) => entry.id === item.id));
    const hasPrev = index > 0;
    const hasNext = index < items.length - 1;
    els.card.innerHTML = `
      <div class="classic-card-meta">
        <span>${esc(item.kind)}</span>
        <span>${esc(item.category)}</span>
        <span>${esc(item.tone)}</span>
        <span>${esc(index + 1)} / ${esc(items.length)}</span>
      </div>
      <h1>${esc(item.english)}</h1>
      <p class="classic-card-translation">${esc(item.chinese)}</p>
      <div class="classic-card-source">${esc(item.author)}</div>
      <p class="classic-card-note">${esc(item.note)}</p>
      <div class="classic-card-actions">
        <button type="button" data-speak-current>朗读</button>
        <button type="button" data-card-nav="prev"${hasPrev ? "" : " disabled"}>上一句</button>
        <button type="button" data-card-nav="next"${hasNext ? "" : " disabled"}>下一句</button>
        <button type="button" data-toggle-favorite>${state.favorite.has(item.id) ? "已收藏" : "收藏"}</button>
        <button type="button" data-toggle-read>${state.read.has(item.id) ? "已读" : "标记已读"}</button>
      </div>
    `;
    saveProgress();
  }

  function render() {
    renderModes();
    renderTabs(els.patterns, patterns(), state.pattern, "sentence-pattern", "全部句型");
    renderTabs(els.categories, categories(), state.category, "sentence-category", "全部主题");
    renderTabs(els.tones, tones(), state.tone, "sentence-tone", "全部语气");
    renderList();
    renderCard();
  }

  function switchSentence(direction) {
    const items = filteredSentences();
    if (!items.length) return;
    const current = Math.max(0, items.findIndex((item) => item.id === state.activeId));
    const nextIndex = direction === "prev" ? current - 1 : current + 1;
    if (!items[nextIndex]) return;
    state.activeId = items[nextIndex].id;
    render();
    const row = els.list.querySelector(".classic-sentence-row.active");
    if (row) row.scrollIntoView({ block: "nearest" });
    els.card.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function bindEvents() {
    els.search.addEventListener("input", () => {
      state.query = els.search.value;
      render();
    });
    els.clear.addEventListener("click", () => {
      state.query = "";
      els.search.value = "";
      render();
    });
    els.modes.addEventListener("click", (event) => {
      const button = event.target.closest("[data-sentence-mode]");
      if (!button) return;
      state.collection = button.dataset.sentenceMode;
      state.category = "all";
      state.pattern = "all";
      state.tone = "all";
      render();
    });
    els.patterns.addEventListener("click", (event) => {
      const button = event.target.closest("[data-sentence-pattern]");
      if (!button) return;
      state.pattern = button.dataset.sentencePattern;
      state.category = "all";
      render();
    });
    els.categories.addEventListener("click", (event) => {
      const button = event.target.closest("[data-sentence-category]");
      if (!button) return;
      state.category = button.dataset.sentenceCategory;
      render();
    });
    els.tones.addEventListener("click", (event) => {
      const button = event.target.closest("[data-sentence-tone]");
      if (!button) return;
      state.tone = button.dataset.sentenceTone;
      render();
    });
    els.list.addEventListener("click", (event) => {
      const button = event.target.closest("[data-sentence-id]");
      if (!button) return;
      state.activeId = button.dataset.sentenceId;
      render();
      els.card.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    els.random.addEventListener("click", () => {
      const items = filteredSentences();
      if (!items.length) return;
      const next = items[Math.floor(Math.random() * items.length)];
      state.activeId = next.id;
      render();
      els.card.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    els.card.addEventListener("click", (event) => {
      const item = activeSentence();
      if (event.target.closest("[data-speak-current]")) {
        speak(item.english, event.target.closest("button"));
        return;
      }
      const nav = event.target.closest("[data-card-nav]");
      if (nav) {
        switchSentence(nav.dataset.cardNav);
        return;
      }
      if (event.target.closest("[data-toggle-favorite]")) {
        if (state.favorite.has(item.id)) state.favorite.delete(item.id);
        else state.favorite.add(item.id);
        render();
        return;
      }
      if (event.target.closest("[data-toggle-read]")) {
        if (state.read.has(item.id)) state.read.delete(item.id);
        else state.read.add(item.id);
        render();
      }
    });
  }

  function init() {
    els.search = $("classicSentenceSearch");
    els.clear = $("classicSentenceClear");
    els.modes = $("classicSentenceModes");
    els.patterns = $("classicSentencePatterns");
    els.categories = $("classicSentenceCategories");
    els.tones = $("classicSentenceTones");
    els.card = $("classicSentenceCard");
    els.list = $("classicSentenceList");
    els.count = $("classicSentenceCount");
    els.random = $("classicSentenceRandom");
    state.sentences = buildSentences();
    loadProgress();
    if (!state.activeId || !filteredSentences().some((item) => item.id === state.activeId)) {
      const items = filteredSentences();
      state.activeId = items[0] && items[0].id;
    }
    refreshVoices();
    if ("speechSynthesis" in window) window.speechSynthesis.onvoiceschanged = refreshVoices;
    bindEvents();
    render();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
