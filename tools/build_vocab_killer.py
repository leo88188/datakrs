#!/usr/bin/env python3
"""Build a 1000-item IELTS essential vocabulary tactics dataset."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "public/assets/english/data/vocab-killer.json"
DATA_DIR = ROOT / "public/assets/english/data"


MANUAL = [
    ("however", "adv.", "然而，不过", "逻辑信号词", "转折", "The proposal is attractive; however, its long-term cost remains uncertain.", "看见它，前后观点通常发生转向。"),
    ("nevertheless", "adv.", "尽管如此，然而", "逻辑信号词", "转折", "The evidence is limited; nevertheless, the trend is worth noting.", "比 however 更正式，适合写作让步。"),
    ("conversely", "adv.", "相反地", "逻辑信号词", "转折", "Urban residents may benefit; conversely, rural communities may be overlooked.", "提示对照关系，不是简单继续。"),
    ("despite", "prep.", "尽管，即使", "逻辑信号词", "转折", "Despite rapid growth, the industry still faces labour shortages.", "后面接名词或动名词，不直接接完整句。"),
    ("whereas", "conj.", "然而，而", "逻辑信号词", "转折", "Some people value stability, whereas others prefer flexibility.", "连接两个对比事实。"),
    ("contrary", "adj./n.", "相反的；反面", "逻辑信号词", "转折", "Contrary to popular belief, remote work does not always reduce productivity.", "常用 contrary to... 表示反预期。"),
    ("consequently", "adv.", "因此，所以", "逻辑信号词", "因果", "The policy was poorly explained; consequently, public trust declined.", "强调结果，适合段落推理。"),
    ("hence", "adv.", "因此，由此", "逻辑信号词", "因果", "The evidence is incomplete; hence, further research is required.", "正式简洁，写作可替代 therefore。"),
    ("thus", "adv.", "因此，从而", "逻辑信号词", "因果", "The system reduces manual work and thus improves efficiency.", "常放句中表达结果。"),
    ("therefore", "adv.", "因此，所以", "逻辑信号词", "因果", "The data are inconsistent; therefore, the conclusion should be cautious.", "最常见因果信号词。"),
    ("contribute to", "v.", "促成，导致，有助于", "逻辑信号词", "因果", "Poor planning can contribute to traffic congestion.", "既可表示积极贡献，也可表示负面原因。"),
    ("attribute to", "v.", "把……归因于", "逻辑信号词", "因果", "The increase is often attributed to better healthcare.", "阅读里常和原因定位有关。"),
    ("furthermore", "adv.", "此外，而且", "逻辑信号词", "递进", "The plan is affordable; furthermore, it is easy to implement.", "正式递进，适合补充第二个理由。"),
    ("moreover", "adv.", "此外，而且", "逻辑信号词", "递进", "The approach saves time; moreover, it reduces errors.", "比 also 更学术。"),
    ("additionally", "adv.", "另外，此外", "逻辑信号词", "递进", "Additionally, the programme supports disadvantaged students.", "适合列举补充。"),
    ("likewise", "adv.", "同样地", "逻辑信号词", "递进", "Parents need guidance; likewise, teachers need practical support.", "提示相似关系。"),
    ("provided", "conj.", "如果，只要", "逻辑信号词", "限制条件", "Technology can improve learning, provided that teachers use it carefully.", "常用 provided that... 表条件。"),
    ("unless", "conj.", "除非，如果不", "逻辑信号词", "限制条件", "The reform will fail unless local needs are considered.", "条件反向，阅读时容易误解。"),
    ("given", "prep./conj.", "考虑到，鉴于", "逻辑信号词", "限制条件", "Given the limited budget, the project should focus on essentials.", "常用于引出背景限制。"),
    ("insofar as", "conj.", "在……范围内，就……而言", "逻辑信号词", "限制条件", "The policy is useful insofar as it protects vulnerable groups.", "高级限定表达，注意不是普通因果。"),
    ("facilitate", "v.", "促进，使便利", "核心动词", "促进/阻碍", "Digital tools can facilitate communication across departments.", "写作替代 help。"),
    ("hinder", "v.", "阻碍，妨碍", "核心动词", "促进/阻碍", "Excessive regulation may hinder innovation.", "阅读常替换 prevent / block。"),
    ("restrict", "v.", "限制，约束", "核心动词", "促进/阻碍", "Strict rules can restrict individual choice.", "常和 access / freedom 搭配。"),
    ("promote", "v.", "促进，推广", "核心动词", "促进/阻碍", "Governments should promote healthier lifestyles.", "写作高频正向动词。"),
    ("diminish", "v.", "减少，削弱", "核心动词", "变化", "Automation may diminish the need for routine labour.", "替代 reduce，但更正式。"),
    ("enhance", "v.", "提高，增强", "核心动词", "变化", "Good design can enhance user experience.", "替代 improve。"),
    ("persist", "v.", "持续存在，坚持", "核心动词", "状态", "Income inequality may persist despite economic growth.", "表示问题没有消失。"),
    ("emerge", "v.", "出现，显现", "核心动词", "变化", "New forms of employment have emerged in the digital economy.", "写趋势变化很常用。"),
    ("maintain", "v.", "维持；主张", "核心动词", "观点", "Some researchers maintain that early intervention is essential.", "注意有“主张认为”的意思。"),
    ("neglect", "v.", "忽视，疏忽", "核心动词", "观点", "Many companies neglect long-term employee development.", "阅读里常替换 overlook。"),
    ("modify", "v.", "修改，调整", "核心动词", "变化", "The method should be modified for younger learners.", "比 change 更精确。"),
    ("alter", "v.", "改变，变更", "核心动词", "变化", "Urbanisation can alter traditional lifestyles.", "常用于趋势影响。"),
    ("reveal", "v.", "揭示，显示", "核心动词", "证据", "The survey reveals a gap between intention and behaviour.", "阅读题干常见同义替换。"),
    ("indicate", "v.", "表明，暗示", "核心动词", "证据", "The figures indicate a steady decline.", "比 show 更学术。"),
    ("demonstrate", "v.", "证明，展示", "核心动词", "证据", "The experiment demonstrates the value of careful planning.", "写作论证高频。"),
    ("assume", "v.", "假设；承担", "核心动词", "观点", "Many policies assume that people act rationally.", "一词多义，要结合语境。"),
    ("confirm", "v.", "确认，证实", "核心动词", "证据", "The results confirm earlier findings.", "和 evidence / finding 搭配。"),
    ("underestimate", "v.", "低估", "核心动词", "观点", "People often underestimate the cost of poor communication.", "适合写问题严重性。"),
    ("significant", "adj.", "显著的，重要的", "评价形容词", "程度", "The policy had a significant impact on rural areas.", "替代 important。"),
    ("substantial", "adj.", "大量的，实质性的", "评价形容词", "程度", "The project requires substantial investment.", "强调数量或程度较大。"),
    ("marginal", "adj.", "微小的，边缘的", "评价形容词", "程度", "The improvement was only marginal.", "表达影响有限。"),
    ("inevitable", "adj.", "不可避免的", "评价形容词", "判断", "Some degree of change is inevitable.", "适合趋势判断。"),
    ("feasible", "adj.", "可行的", "评价形容词", "判断", "The solution is feasible but expensive.", "写方案评价常用。"),
    ("controversial", "adj.", "有争议的", "评价形容词", "判断", "The use of surveillance technology remains controversial.", "主题引入高频。"),
    ("adequate", "adj.", "足够的，适当的", "评价形容词", "程度", "Many schools lack adequate funding.", "常和 insufficient 对照。"),
    ("insufficient", "adj.", "不足的，不充分的", "评价形容词", "程度", "Insufficient evidence makes the claim weak.", "写问题原因很常用。"),
    ("prevalent", "adj.", "普遍的，流行的", "评价形容词", "范围", "Online shopping is increasingly prevalent.", "替代 common。"),
    ("predominant", "adj.", "主要的，占主导的", "评价形容词", "范围", "Cars remain the predominant mode of transport.", "强调主导地位。"),
    ("phenomenon", "n.", "现象", "抽象名词", "学术概念", "This phenomenon is common in large cities.", "写作主题句常用。"),
    ("tendency", "n.", "趋势，倾向", "抽象名词", "学术概念", "There is a tendency to rely too heavily on technology.", "表达行为趋势。"),
    ("factor", "n.", "因素", "抽象名词", "原因", "Cost is a major factor in household decisions.", "原因分析基础词。"),
    ("obstacle", "n.", "障碍，阻碍", "抽象名词", "问题", "Lack of training is a serious obstacle.", "替代 problem。"),
    ("constraint", "n.", "限制，约束", "抽象名词", "问题", "Budget constraints can delay reform.", "常用于资源限制。"),
    ("consequence", "n.", "后果，结果", "抽象名词", "结果", "One consequence is a loss of public confidence.", "因果段落核心词。"),
    ("perspective", "n.", "观点，视角", "抽象名词", "观点", "From an economic perspective, the plan is risky.", "Part 3 和写作都常用。"),
    ("motivation", "n.", "动机，积极性", "抽象名词", "心理", "Financial rewards may increase motivation.", "教育/工作高频。"),
    ("deficiency", "n.", "缺陷，不足", "抽象名词", "问题", "The report identifies several deficiencies.", "比 weakness 更正式。"),
    ("vital", "adj.", "至关重要的", "同义替换词组", "important", "Public trust is vital to effective governance.", "important = vital = crucial = significant"),
    ("crucial", "adj.", "关键的，至关重要的", "同义替换词组", "important", "Early diagnosis is crucial.", "important = vital = crucial = significant"),
    ("alter", "v.", "改变，调整", "同义替换词组", "change", "New rules may alter consumer behaviour.", "change = alter = modify = transform"),
    ("transform", "v.", "彻底改变，转型", "同义替换词组", "change", "Digital platforms have transformed retail.", "change = alter = modify = transform"),
    ("cut down", "v.", "减少，削减", "同义替换词组", "reduce", "Households can cut down on unnecessary waste.", "reduce = diminish = cut down"),
    ("advocate", "v./n.", "提倡，拥护；倡导者", "同义替换词组", "support", "Some experts advocate stricter standards.", "support = back = advocate"),
    ("back", "v.", "支持", "同义替换词组", "support", "The proposal is backed by recent research.", "support = back = advocate"),
]

MANUAL_TRANSLATIONS = {
    "however": "这个方案很有吸引力；不过，它的长期成本仍然不确定。",
    "nevertheless": "证据还有限；尽管如此，这个趋势仍然值得注意。",
    "conversely": "城市居民可能会受益；相反，农村社区可能会被忽视。",
    "despite": "尽管增长很快，这个行业仍然面临劳动力短缺。",
    "whereas": "有些人重视稳定，而另一些人更喜欢灵活性。",
    "contrary": "和很多人的看法相反，远程办公并不总是能提高生产率。",
    "consequently": "这项政策解释得不好；因此，公众信任下降了。",
    "hence": "证据并不完整；因此，还需要进一步研究。",
    "thus": "这个系统减少了人工操作，从而提高了效率。",
    "therefore": "这些数据前后不一致；所以，这个结论应该更谨慎。",
    "contribute to": "规划不佳可能会导致交通拥堵。",
    "attribute to": "这种增长通常被归因于更好的医疗服务。",
    "furthermore": "这个计划负担得起；而且，它也容易执行。",
    "moreover": "这种方法节省时间；此外，它还能减少错误。",
    "additionally": "另外，这个项目也支持弱势学生。",
    "likewise": "家长需要指导；同样，老师也需要实际支持。",
    "provided": "只要老师使用得当，技术就能改善学习。",
    "unless": "除非考虑本地需求，否则这项改革会失败。",
    "given": "考虑到预算有限，这个项目应该聚焦最基本的部分。",
    "insofar as": "只要这项政策能保护弱势群体，它就是有用的。",
    "facilitate": "数字工具可以让不同部门之间的沟通更方便。",
    "hinder": "过度监管可能会阻碍创新。",
    "restrict": "严格的规则可能会限制个人选择。",
    "promote": "政府应该推动更健康的生活方式。",
    "diminish": "自动化可能会减少对重复性劳动力的需求。",
    "enhance": "好的设计可以提升用户体验。",
    "persist": "即使经济增长，收入不平等也可能继续存在。",
    "emerge": "数字经济中出现了新的就业形式。",
    "maintain": "一些研究者认为，早期干预非常重要。",
    "neglect": "很多公司忽视了员工的长期发展。",
    "modify": "这个方法应该根据年龄较小的学习者进行调整。",
    "alter": "新规则可能会改变消费者行为。",
    "reveal": "这项调查显示，想法和实际行为之间存在差距。",
    "indicate": "这些数字表明，情况在稳定下降。",
    "demonstrate": "这个实验证明了细致规划的价值。",
    "assume": "很多政策都假设人会理性行动。",
    "confirm": "这些结果证实了早先的发现。",
    "underestimate": "人们经常低估沟通不畅带来的成本。",
    "significant": "这项政策对农村地区产生了显著影响。",
    "substantial": "这个项目需要大量投资。",
    "marginal": "这种改善非常小。",
    "inevitable": "某种程度的变化是不可避免的。",
    "feasible": "这个解决方案可行，但成本很高。",
    "controversial": "监控技术的使用仍然有争议。",
    "adequate": "很多学校缺乏足够的资金。",
    "insufficient": "证据不足会让这个说法缺乏说服力。",
    "prevalent": "网上购物越来越普遍。",
    "predominant": "汽车仍然是主要的交通方式。",
    "phenomenon": "这种现象在大城市很常见。",
    "tendency": "人们有一种过度依赖技术的倾向。",
    "factor": "成本是家庭决策中的一个重要因素。",
    "obstacle": "缺乏培训是一个严重障碍。",
    "constraint": "预算限制可能会推迟改革。",
    "consequence": "其中一个后果是公众信心下降。",
    "perspective": "从经济角度看，这个计划有风险。",
    "motivation": "金钱奖励可能会提高积极性。",
    "deficiency": "这份报告指出了几个不足之处。",
    "vital": "公众信任对有效治理至关重要。",
    "crucial": "早期诊断非常关键。",
    "transform": "数字平台已经改变了零售业。",
    "cut down": "家庭可以减少不必要的浪费。",
    "advocate": "一些专家主张采用更严格的标准。",
    "back": "最近的研究支持这项提议。",
}

EXAMPLE_OVERRIDES = {
    "key": ("Trust is a key element in any successful reform.", "信任是任何成功改革中的关键因素。"),
    "curb": ("Stricter rules may curb the overuse of private cars.", "更严格的规则可能会抑制私家车的过度使用。"),
    "grow": ("Public concern about data privacy continues to grow.", "公众对数据隐私的担忧持续增加。"),
    "rise": ("Housing prices tend to rise when demand exceeds supply.", "当需求超过供给时，房价往往会上涨。"),
    "show": ("The results show that small changes can have a large effect.", "结果显示，小变化也可能产生很大影响。"),
    "soar": ("Energy costs may soar during periods of political instability.", "在政治不稳定时期，能源成本可能会飙升。"),
    "adapt": ("Schools must adapt their teaching methods to new technology.", "学校必须让教学方法适应新技术。"),
    "imply": ("These figures imply that the policy has not worked as expected.", "这些数字意味着这项政策并没有达到预期效果。"),
    "issue": ("Air pollution remains a serious issue in many large cities.", "空气污染在许多大城市仍然是一个严重问题。"),
    "shift": ("There has been a clear shift from cash payments to mobile payments.", "从现金支付到移动支付的转变已经很明显。"),
    "adjust": ("Workers may need time to adjust to a four-day working week.", "员工可能需要时间适应每周四天工作制。"),
    "change": ("Climate change is already affecting food production.", "气候变化已经在影响粮食生产。"),
    "effect": ("The new tax had little effect on consumer behaviour.", "这项新税对消费者行为影响不大。"),
    "expand": ("The city plans to expand its public transport network.", "这座城市计划扩大公共交通网络。"),
    "impact": ("Online learning has had a lasting impact on education.", "在线学习对教育产生了长期影响。"),
    "lessen": ("Flexible working hours can lessen pressure on parents.", "灵活工作时间可以减轻父母的压力。"),
    "method": ("This method is simple, but it may not suit every learner.", "这种方法很简单，但不一定适合每个学习者。"),
    "oppose": ("Some residents oppose the construction of a new airport.", "一些居民反对建设新机场。"),
    "reduce": ("Better insulation can reduce household energy use.", "更好的隔热材料可以减少家庭能源使用。"),
    "refute": ("The new evidence helped refute the earlier claim.", "新的证据帮助反驳了早先的说法。"),
    "reject": ("The committee rejected the proposal because it was too costly.", "委员会拒绝了这个提案，因为成本太高。"),
    "result": ("The result was a more efficient public service.", "结果是公共服务变得更加高效。"),
    "revise": ("The government may revise the policy after public consultation.", "政府可能会在公众咨询后修改这项政策。"),
    "uphold": ("Courts should uphold basic rights even in difficult situations.", "即使在困难情况下，法院也应维护基本权利。"),
    "barrier": ("High tuition fees can be a barrier to higher education.", "高昂的学费可能成为接受高等教育的障碍。"),
    "central": ("Public safety is central to urban planning.", "公共安全是城市规划的核心。"),
    "decline": ("The number of young people entering the industry has declined.", "进入该行业的年轻人数量已经下降。"),
    "dispute": ("Few scientists dispute the link between smoking and disease.", "很少有科学家质疑吸烟和疾病之间的联系。"),
    "endorse": ("Many experts endorse the use of renewable energy.", "许多专家支持使用可再生能源。"),
    "justify": ("A small benefit cannot justify such a high cost.", "一点小好处无法证明如此高的成本是合理的。"),
    "measure": ("One effective measure is to improve public transport.", "一个有效措施是改善公共交通。"),
    "outcome": ("The outcome depends on how well the plan is implemented.", "结果取决于这个计划执行得有多好。"),
    "problem": ("The main problem is not technology itself, but how it is used.", "主要问题不是技术本身，而是技术如何被使用。"),
    "suggest": ("Recent surveys suggest that people value flexibility at work.", "最近的调查表明，人们重视工作中的灵活性。"),
    "support": ("The data support the argument for earlier intervention.", "这些数据支持尽早干预的观点。"),
    "approach": ("A practical approach is to start with small local trials.", "一个实际的方法是先从小规模本地试点开始。"),
    "decrease": ("Traffic accidents may decrease if speed limits are enforced.", "如果严格执行限速，交通事故可能会减少。"),
    "escalate": ("A minor disagreement can escalate into a serious conflict.", "小分歧可能升级为严重冲突。"),
    "increase": ("Remote work can increase job satisfaction for some employees.", "远程办公可以提高一些员工的工作满意度。"),
    "minimise": ("Good planning can minimise waste during construction.", "良好的规划可以减少施工过程中的浪费。"),
    "question": ("Some researchers question the reliability of the data.", "一些研究者质疑这些数据的可靠性。"),
    "solution": ("There is no simple solution to urban congestion.", "城市拥堵没有简单的解决方案。"),
    "strategy": ("The company needs a long-term strategy for staff training.", "这家公司需要一个长期的员工培训策略。"),
    "challenge": ("Young people may challenge traditional ideas about work.", "年轻人可能会挑战传统的工作观念。"),
    "criticise": ("Critics often criticise the policy for ignoring rural areas.", "批评者经常批评这项政策忽视农村地区。"),
    "essential": ("Clean water is essential for public health.", "清洁用水对公共健康至关重要。"),
    "although": ("Although online learning is convenient, it cannot fully replace classroom interaction.", "虽然在线学习很方便，但它不能完全取代课堂互动。"),
    "even though": ("Even though the policy is unpopular, it may be necessary in the short term.", "即使这项政策不受欢迎，它在短期内也可能是必要的。"),
    "nonetheless": ("The plan is expensive; nonetheless, it may bring long-term benefits.", "这个计划成本很高；尽管如此，它可能带来长期好处。"),
    "on the contrary": ("Some people think public transport is inconvenient; on the contrary, it can save time in crowded cities.", "有些人认为公共交通不方便；相反，在拥挤城市里它可以节省时间。"),
    "in contrast": ("In contrast, smaller cities often offer a lower cost of living.", "相比之下，较小的城市通常生活成本更低。"),
    "by contrast": ("Large companies can invest in training; by contrast, small firms often lack resources.", "大公司可以投资培训；相比之下，小企业往往缺乏资源。"),
    "on the other hand": ("Higher taxes may reduce consumption; on the other hand, they can fund better public services.", "更高的税可能会减少消费；另一方面，它们也能为更好的公共服务提供资金。"),
    "as a result": ("Many families moved to the suburbs; as a result, commuting time increased.", "许多家庭搬到了郊区；结果，通勤时间增加了。"),
    "accordingly": ("The risks are higher than expected; accordingly, the plan should be revised.", "风险比预期更高；因此，这个计划应该修改。"),
    "because of": ("Because of rising rents, many young people delay moving out.", "由于租金上涨，许多年轻人推迟了独立居住。"),
    "owing to": ("Owing to better public health, life expectancy has increased.", "由于公共卫生改善，预期寿命提高了。"),
    "as a consequence": ("The city failed to control pollution; as a consequence, public health suffered.", "这座城市未能控制污染；结果，公共健康受到了影响。"),
    "lead to": ("A lack of exercise can lead to serious health problems.", "缺乏运动可能导致严重的健康问题。"),
    "result in": ("Poor communication can result in delays and extra costs.", "沟通不畅可能导致延误和额外成本。"),
    "give rise to": ("Rapid urban growth can give rise to housing shortages.", "城市快速增长可能引发住房短缺。"),
    "in addition": ("The course improves grammar; in addition, it builds confidence.", "这门课程能提高语法；此外，它还能增强信心。"),
    "besides": ("The scheme is costly; besides, it may be difficult to manage.", "这个方案成本很高；而且，它可能很难管理。"),
    "not only but also": ("The programme not only teaches skills but also improves motivation.", "这个项目不仅教授技能，还能提高积极性。"),
    "similarly": ("Similarly, rural schools need reliable internet access.", "同样，农村学校也需要可靠的网络接入。"),
    "in particular": ("Older workers, in particular, may need support when technology changes.", "尤其是年长员工，在技术变化时可能需要支持。"),
    "specifically": ("The report focuses specifically on air pollution in large cities.", "这份报告专门关注大城市的空气污染。"),
    "for instance": ("Some jobs, for instance nursing and teaching, require strong communication skills.", "有些工作，例如护理和教学，需要很强的沟通能力。"),
    "for example": ("Many people save energy at home, for example by using efficient appliances.", "许多人在家节能，例如使用高效电器。"),
    "provided that": ("Working from home can be effective, provided that employees have a quiet space.", "只要员工有安静的空间，在家办公就可能有效。"),
    "as long as": ("Children can use tablets as long as screen time is limited.", "只要限制屏幕时间，孩子就可以使用平板电脑。"),
    "in terms of": ("In terms of cost, public transport is usually cheaper than driving.", "就成本而言，公共交通通常比开车便宜。"),
    "with regard to": ("With regard to safety, stricter building standards are necessary.", "关于安全，更严格的建筑标准是必要的。"),
    "role": ("Parents play an important role in shaping children's habits.", "父母在塑造孩子习惯方面发挥重要作用。"),
    "trend": ("One clear trend is the growing demand for flexible work.", "一个明显趋势是，人们对灵活工作的需求不断增加。"),
    "access": ("Rural students often have limited access to quality education.", "农村学生往往难以获得优质教育资源。"),
    "debate": ("The debate over artificial intelligence is likely to continue.", "关于人工智能的争论很可能会继续。"),
    "demand": ("Demand for public transport increases when fuel prices rise.", "燃油价格上涨时，公共交通需求会增加。"),
    "labour": ("Many farms depend on seasonal labour during harvest time.", "许多农场在收获季依赖季节性劳动力。"),
    "policy": ("A clear policy can help schools deal with online bullying.", "明确的政策可以帮助学校处理网络欺凌。"),
    "sector": ("The healthcare sector needs both technology and trained staff.", "医疗行业既需要技术，也需要训练有素的员工。"),
    "concept": ("The concept of lifelong learning is becoming more important.", "终身学习这一概念正变得越来越重要。"),
    "context": ("In this context, cheaper housing is not the only solution.", "在这种背景下，更便宜的住房并不是唯一解决办法。"),
    "feature": ("A useful feature of online courses is that students can review lessons.", "在线课程的一个有用特点是学生可以回看课程。"),
    "insight": ("The survey provides insight into why young people change jobs.", "这项调查让我们了解年轻人为什么换工作。"),
    "pattern": ("The data show a similar pattern in several countries.", "数据显示几个国家都有类似模式。"),
    "accuracy": ("The accuracy of medical information is especially important online.", "医疗信息的准确性在网上尤其重要。"),
    "analysis": ("Careful analysis can reveal problems that are not obvious at first.", "仔细分析可以揭示一开始不明显的问题。"),
    "capacity": ("The hospital does not have enough capacity to treat all patients.", "这家医院没有足够能力治疗所有病人。"),
    "category": ("Age is not the only category used in the survey.", "年龄并不是这项调查使用的唯一分类。"),
    "cohesion": ("Good cohesion makes an essay easier to follow.", "良好的衔接能让文章更容易读懂。"),
    "emphasis": ("The course places more emphasis on practical communication.", "这门课程更强调实际沟通。"),
    "evidence": ("There is strong evidence that smoking damages health.", "有强有力的证据表明吸烟损害健康。"),
    "exposure": ("Too much exposure to advertising can influence children's choices.", "过多接触广告会影响孩子的选择。"),
    "function": ("The main function of public libraries is to provide access to knowledge.", "公共图书馆的主要功能是提供获取知识的机会。"),
    "priority": ("Reducing air pollution should be a priority for large cities.", "减少空气污染应成为大城市的优先事项。"),
    "resource": ("Water is a limited resource in many dry regions.", "在许多干旱地区，水是有限资源。"),
    "response": ("The public response to the new rule was mixed.", "公众对这项新规定的反应并不一致。"),
    "advantage": ("One advantage of online learning is its flexibility.", "在线学习的一个优势是灵活。"),
    "authority": ("Local authorities should improve road safety near schools.", "地方政府应改善学校附近的道路安全。"),
    "coherence": ("Coherence is important because ideas must connect clearly.", "连贯性很重要，因为观点必须清楚连接。"),
    "community": ("A strong community can support elderly residents.", "强大的社区可以支持老年居民。"),
    "component": ("Exercise is only one component of a healthy lifestyle.", "运动只是健康生活方式的一个组成部分。"),
    "criterion": ("Cost should not be the only criterion for choosing a school.", "成本不应是选择学校的唯一标准。"),
    "dimension": ("The problem has an economic dimension as well as a social one.", "这个问题既有经济层面，也有社会层面。"),
    "diversity": ("Cultural diversity can make a city more creative.", "文化多样性可以让一座城市更有创造力。"),
    "expansion": ("The expansion of cities can put pressure on farmland.", "城市扩张会给农田带来压力。"),
    "incentive": ("Tax benefits can provide an incentive for companies to train workers.", "税收优惠可以激励公司培训员工。"),
    "objective": ("The main objective is to reduce unnecessary waste.", "主要目标是减少不必要的浪费。"),
    "reduction": ("A reduction in traffic would improve air quality.", "交通量减少会改善空气质量。"),
    "structure": ("A clear structure helps readers understand an argument.", "清晰的结构能帮助读者理解论证。"),
    "variation": ("There is wide variation in education quality between regions.", "不同地区之间的教育质量差异很大。"),
    "assessment": ("Regular assessment helps teachers understand students' progress.", "定期评估有助于老师了解学生的进步。"),
    "assumption": ("The plan is based on the assumption that prices will remain stable.", "这个计划基于价格会保持稳定的假设。"),
    "comparison": ("A comparison of the two cities shows different transport problems.", "比较这两座城市可以看出不同的交通问题。"),
    "inequality": ("Income inequality can reduce social trust.", "收入不平等会降低社会信任。"),
    "investment": ("Investment in early education can bring long-term benefits.", "投资早期教育可以带来长期收益。"),
    "limitation": ("One limitation of the study is its small sample size.", "这项研究的一个局限是样本量较小。"),
    "proportion": ("A large proportion of young adults still live with their parents.", "很大一部分年轻成年人仍然和父母住在一起。"),
    "alternative": ("Cycling is a cheap alternative to driving in crowded cities.", "在拥挤城市中，骑自行车是开车的廉价替代方式。"),
    "consumption": ("High consumption of processed food may harm health.", "大量食用加工食品可能损害健康。"),
    "interaction": ("Face-to-face interaction is important for young children.", "面对面互动对幼儿很重要。"),
    "restriction": ("A restriction on plastic bags can reduce waste.", "限制塑料袋使用可以减少垃圾。"),
    "framework": ("A clear legal framework can protect both workers and employers.", "清晰的法律框架可以同时保护员工和雇主。"),
    "important": ("It is important to consider the needs of low-income families.", "考虑低收入家庭的需求很重要。"),
    "influence": ("Parents can influence children's attitudes toward reading.", "父母会影响孩子对阅读的态度。"),
    "intensify": ("Competition for jobs may intensify during an economic downturn.", "经济低迷时期，就业竞争可能会加剧。"),
    "mechanism": ("The market needs a better mechanism for protecting consumers.", "市场需要更好的机制来保护消费者。"),
    "procedure": ("A simple procedure can make public services easier to use.", "简单的流程可以让公共服务更容易使用。"),
    "reinforce": ("Positive feedback can reinforce good learning habits.", "积极反馈可以强化良好的学习习惯。"),
    "undermine": ("Misinformation can undermine public trust in science.", "错误信息会削弱公众对科学的信任。"),
    "accumulate": ("Small daily expenses can accumulate over time.", "每天的小额支出会随着时间积累起来。"),
    "difficulty": ("Many adults have difficulty balancing work and family life.", "许多成年人很难平衡工作和家庭生活。"),
    "illustrate": ("This example illustrates the importance of early education.", "这个例子说明了早期教育的重要性。"),
    "fundamental": ("Basic literacy is fundamental to further education.", "基本读写能力是继续教育的基础。"),
    "implication": ("One implication of ageing populations is higher healthcare spending.", "人口老龄化的一个影响是医疗支出增加。"),
    "repercussion": ("Poor urban planning can have serious repercussions for public health.", "糟糕的城市规划可能对公共健康造成严重后果。"),
    "contradiction": ("There is a contradiction between cheap travel and environmental protection.", "廉价出行和环境保护之间存在矛盾。"),
    "justification": ("There is little justification for banning all forms of online learning.", "没有太多理由完全禁止所有形式的在线学习。"),
    "infrastructure": ("Better infrastructure can reduce travel time and support economic growth.", "更好的基础设施可以减少出行时间并支持经济增长。"),
    "interpretation": ("Different interpretations of the same data can lead to different policies.", "对同一数据的不同解读可能导致不同政策。"),
    "link": ("Researchers often link poor housing to health problems.", "研究者经常把住房条件差和健康问题联系起来。"),
    "rely": ("Many small businesses rely on local customers.", "许多小企业依赖本地顾客。"),
    "vary": ("The quality of public transport can vary greatly between cities.", "不同城市的公共交通质量可能差异很大。"),
    "occur": ("Serious accidents can occur when safety rules are ignored.", "忽视安全规则时，严重事故可能发生。"),
    "affect": ("Noise pollution can affect children's ability to concentrate.", "噪音污染会影响孩子的专注能力。"),
    "assess": ("Schools should assess students through more than one exam.", "学校不应只通过一次考试来评估学生。"),
    "create": ("New industries can create jobs for young people.", "新行业可以为年轻人创造就业机会。"),
    "define": ("Culture is difficult to define because it changes over time.", "文化很难定义，因为它会随时间变化。"),
    "derive": ("Many health benefits derive from regular physical activity.", "许多健康益处来自规律运动。"),
    "design": ("Cities should design streets that are safe for pedestrians.", "城市应设计对行人安全的街道。"),
    "enable": ("Affordable internet access can enable more people to study online.", "负担得起的网络接入可以让更多人在线学习。"),
    "ensure": ("Strict food standards help ensure public safety.", "严格的食品标准有助于确保公共安全。"),
    "evolve": ("Working habits continue to evolve as technology changes.", "随着技术变化，工作习惯也在不断演变。"),
    "exceed": ("Demand for housing may exceed supply in fast-growing cities.", "在快速发展的城市，住房需求可能超过供给。"),
    "expose": ("Social media can expose young people to unrealistic lifestyles.", "社交媒体可能让年轻人接触到不现实的生活方式。"),
    "impose": ("Governments may impose fines on companies that pollute rivers.", "政府可能会对污染河流的公司处以罚款。"),
    "obtain": ("Students need reliable sources to obtain accurate information.", "学生需要可靠来源来获取准确信息。"),
    "occupy": ("Cars occupy too much space in many city centres.", "汽车在许多市中心占用了太多空间。"),
    "remove": ("Removing unnecessary rules can make services more efficient.", "取消不必要的规则可以让服务更高效。"),
    "retain": ("Companies need better conditions to retain skilled workers.", "公司需要更好的条件来留住熟练员工。"),
    "submit": ("Applicants must submit their documents before the deadline.", "申请者必须在截止日期前提交文件。"),
    "target": ("Public health campaigns should target groups at higher risk.", "公共健康宣传应针对风险更高的人群。"),
    "achieve": ("A country cannot achieve progress without investing in education.", "一个国家如果不投资教育，就无法取得进步。"),
    "acquire": ("Children acquire language more easily through daily interaction.", "孩子通过日常互动更容易习得语言。"),
    "analyse": ("Researchers analyse survey data to understand public attitudes.", "研究者分析调查数据以了解公众态度。"),
    "benefit": ("Local shops can benefit from improved public transport.", "公共交通改善后，本地商店可能受益。"),
    "clarify": ("The government should clarify how the new tax will be used.", "政府应说明这项新税将如何使用。"),
    "compare": ("It is useful to compare the costs of different energy sources.", "比较不同能源的成本是有用的。"),
    "conduct": ("Universities often conduct research on social behaviour.", "大学经常开展关于社会行为的研究。"),
    "consume": ("Wealthier households tend to consume more energy.", "较富裕的家庭往往消耗更多能源。"),
    "develop": ("Children develop problem-solving skills through play.", "孩子通过游戏发展解决问题的能力。"),
    "enforce": ("Traffic laws must be enforced consistently.", "交通法规必须被持续执行。"),
    "exclude": ("High fees may exclude poorer students from higher education.", "高昂费用可能把贫困学生排除在高等教育之外。"),
    "inhibit": ("Fear of failure can inhibit creativity.", "对失败的恐惧会抑制创造力。"),
    "involve": ("Solving traffic problems often involves better planning.", "解决交通问题通常涉及更好的规划。"),
    "predict": ("It is difficult to predict how technology will change jobs.", "很难预测技术将如何改变工作。"),
    "prevent": ("Early treatment can prevent minor illnesses from becoming serious.", "早期治疗可以防止小病变严重。"),
    "proceed": ("The project should not proceed without public consultation.", "没有公众咨询，这个项目不应继续推进。"),
    "propose": ("Some experts propose a shorter working week.", "一些专家建议缩短每周工作时间。"),
    "recover": ("Local tourism may recover once transport links improve.", "交通连接改善后，本地旅游业可能恢复。"),
    "resolve": ("Better communication can resolve many workplace conflicts.", "更好的沟通可以解决许多职场冲突。"),
    "respond": ("Schools must respond quickly to bullying.", "学校必须迅速回应欺凌问题。"),
    "restore": ("Planting trees can help restore damaged land.", "植树可以帮助修复受损土地。"),
    "sustain": ("A strong economy can sustain better public services.", "强劲经济可以支撑更好的公共服务。"),
    "allocate": ("The city should allocate more money to public transport.", "这座城市应给公共交通分配更多资金。"),
    "classify": ("Researchers classify participants according to age and income.", "研究者按年龄和收入对参与者进行分类。"),
    "contrast": ("The report contrasts urban lifestyles with rural traditions.", "这份报告对比了城市生活方式和乡村传统。"),
    "convince": ("Clear evidence can convince people to change unhealthy habits.", "清晰证据可以说服人们改变不健康习惯。"),
    "estimate": ("Experts estimate that water demand will rise sharply.", "专家估计用水需求将大幅上升。"),
    "evaluate": ("Teachers should evaluate both progress and final results.", "老师应同时评价进步过程和最终结果。"),
    "generate": ("Renewable energy can generate electricity without heavy pollution.", "可再生能源可以在不造成严重污染的情况下发电。"),
    "identify": ("Early testing can identify learning difficulties before they become serious.", "早期测试可以在学习困难变严重前发现它们。"),
    "initiate": ("Local governments can initiate programmes to support small businesses.", "地方政府可以发起项目支持小企业。"),
    "maximise": ("Good time management helps students maximise their study efficiency.", "良好的时间管理帮助学生最大化学习效率。"),
    "perceive": ("Some people perceive public transport as slow and uncomfortable.", "有些人认为公共交通慢而且不舒服。"),
    "preserve": ("Museums help preserve cultural heritage for future generations.", "博物馆帮助为后代保存文化遗产。"),
    "prohibit": ("Some cities prohibit cars from entering old town centres.", "一些城市禁止汽车进入老城区中心。"),
    "purchase": ("Consumers often purchase products after seeing online reviews.", "消费者经常在看到网上评价后购买产品。"),
    "regulate": ("Governments need to regulate companies that collect personal data.", "政府需要监管收集个人数据的公司。"),
    "transfer": ("Digital technology makes it easier to transfer money overseas.", "数字技术让跨国转账更容易。"),
    "cooperate": ("Countries must cooperate to deal with climate change.", "各国必须合作应对气候变化。"),
    "determine": ("Family income can determine the quality of education a child receives.", "家庭收入可能决定孩子接受教育的质量。"),
    "eliminate": ("Better design can eliminate many common safety risks.", "更好的设计可以消除许多常见安全风险。"),
    "emphasise": ("Schools should emphasise creativity as well as exam results.", "学校不仅应重视考试成绩，也应强调创造力。"),
    "encounter": ("New immigrants often encounter language barriers.", "新移民经常遇到语言障碍。"),
    "establish": ("The city plans to establish more community health centres.", "这座城市计划建立更多社区健康中心。"),
    "integrate": ("Schools should integrate technology into lessons carefully.", "学校应谨慎地把技术融入课堂。"),
    "interpret": ("Readers must interpret charts carefully before choosing an answer.", "读者在选择答案前必须仔细解读图表。"),
    "recognise": ("Employers increasingly recognise the value of soft skills.", "雇主越来越认识到软技能的价值。"),
    "recommend": ("Doctors often recommend regular exercise for older adults.", "医生经常建议老年人规律运动。"),
    "stimulate": ("Investment in public transport can stimulate local economies.", "公共交通投资可以刺激地方经济。"),
    "compensate": ("Extra training can compensate for a lack of experience.", "额外培训可以弥补经验不足。"),
    "complement": ("Online materials can complement classroom teaching.", "在线材料可以补充课堂教学。"),
    "complicate": ("Unclear rules can complicate the application process.", "不明确的规则会使申请流程复杂化。"),
    "constitute": ("Long working hours may constitute a serious health risk.", "长时间工作可能构成严重健康风险。"),
    "coordinate": ("Schools and parents need to coordinate their efforts.", "学校和家长需要协调各自的努力。"),
    "distribute": ("The charity distributes food to low-income families.", "这个慈善机构向低收入家庭分发食物。"),
    "prioritise": ("Governments should prioritise basic healthcare in poor areas.", "政府应优先考虑贫困地区的基础医疗。"),
    "substitute": ("Online meetings cannot always substitute for face-to-face discussion.", "线上会议并不总能替代面对面讨论。"),
    "incorporate": ("A good curriculum should incorporate practical skills.", "好的课程应包含实用技能。"),
    "participate": ("Students participate more when lessons are interactive.", "课堂互动性强时，学生参与更多。"),
    "differentiate": ("Teachers need to differentiate between mistakes and lack of effort.", "老师需要区分错误和不努力。"),
    "minor": ("A minor change in wording can alter the meaning of a question.", "措辞上的小变化可能改变问题的意思。"),
    "rigid": ("Rigid working hours can make family life more difficult.", "僵化的工作时间会让家庭生活更困难。"),
    "valid": ("The conclusion is valid only if the data are reliable.", "只有数据可靠，这个结论才有效。"),
    "random": ("A random sample can make a survey more reliable.", "随机样本可以让调查更可靠。"),
    "severe": ("Severe air pollution can force schools to close.", "严重空气污染可能迫使学校停课。"),
    "stable": ("A stable income allows families to plan for the future.", "稳定收入让家庭能够规划未来。"),
    "complex": ("Urban poverty is a complex problem with many causes.", "城市贫困是一个有多种原因的复杂问题。"),
    "evident": ("It is evident that public attitudes have changed.", "很明显，公众态度已经改变。"),
    "gradual": ("A gradual increase in fees may be easier for families to accept.", "费用逐步上涨可能更容易被家庭接受。"),
    "initial": ("The initial cost of solar panels can be high.", "太阳能板的初始成本可能很高。"),
    "logical": ("A logical argument is easier to follow.", "有逻辑的论证更容易理解。"),
    "neutral": ("News reports should use neutral language.", "新闻报道应使用中立语言。"),
    "obvious": ("The most obvious solution is not always the best one.", "最明显的解决办法并不总是最好的。"),
    "overall": ("The overall result was better than expected.", "总体结果比预期更好。"),
    "primary": ("The primary reason for migration is often employment.", "迁移的主要原因通常是就业。"),
    "accurate": ("Accurate information is essential during a public health crisis.", "公共健康危机期间，准确信息至关重要。"),
    "apparent": ("It became apparent that the policy had unexpected costs.", "很明显，这项政策带来了意想不到的成本。"),
    "critical": ("Critical thinking helps students judge information more carefully.", "批判性思维帮助学生更谨慎地判断信息。"),
    "distinct": ("Urban and rural communities often have distinct needs.", "城市和农村社区往往有不同需求。"),
    "dominant": ("English remains a dominant language in international business.", "英语仍然是国际商务中的主导语言。"),
    "external": ("External funding can help schools improve their facilities.", "外部资金可以帮助学校改善设施。"),
    "flexible": ("Flexible schedules can help parents remain in work.", "灵活时间安排可以帮助父母继续工作。"),
    "implicit": ("The advertisement sends an implicit message about success.", "这则广告传递了关于成功的隐含信息。"),
    "internal": ("Internal communication is important in large organisations.", "内部沟通对大型组织很重要。"),
    "negative": ("Excessive screen time may have negative effects on sleep.", "过多屏幕时间可能对睡眠产生负面影响。"),
    "positive": ("Positive relationships at school can improve student confidence.", "学校里的积极关系可以提升学生信心。"),
    "previous": ("Previous research focused mainly on adults.", "先前的研究主要关注成年人。"),
    "profound": ("The internet has had a profound effect on communication.", "互联网对沟通产生了深刻影响。"),
    "relevant": ("Students learn faster when examples are relevant to their lives.", "例子与学生生活相关时，学生学得更快。"),
    "reliable": ("Reliable public transport can reduce dependence on cars.", "可靠的公共交通可以减少对汽车的依赖。"),
    "ambiguous": ("Ambiguous rules can lead to confusion and unfair decisions.", "模糊的规则可能导致混乱和不公平决定。"),
    "arbitrary": ("Arbitrary punishment can damage trust in schools.", "随意惩罚会损害学生对学校的信任。"),
    "desirable": ("A shorter commute is desirable for many workers.", "对许多员工来说，较短通勤时间是理想的。"),
    "effective": ("An effective policy should be easy to understand and enforce.", "有效政策应容易理解并且容易执行。"),
    "efficient": ("Efficient energy use can lower household bills.", "高效用能可以降低家庭账单。"),
    "excessive": ("Excessive homework can reduce children's time for rest.", "过多作业会减少孩子休息时间。"),
    "strategic": ("Strategic investment in education can support long-term growth.", "对教育的战略性投资可以支持长期增长。"),
    "temporary": ("Temporary jobs may not provide enough security.", "临时工作可能无法提供足够保障。"),
    "beneficial": ("Regular exercise is beneficial for both physical and mental health.", "规律运动对身心健康都有益。"),
    "consistent": ("Consistent feedback helps learners improve gradually.", "持续一致的反馈帮助学习者逐步提高。"),
    "equivalent": ("Online lessons are not always equivalent to face-to-face classes.", "线上课程并不总是等同于面对面课堂。"),
    "inadequate": ("Inadequate housing can affect children's health and education.", "住房不足会影响孩子的健康和教育。"),
    "productive": ("A quiet workplace can make employees more productive.", "安静的工作场所可以让员工更高效。"),
    "underlying": ("The underlying cause of the problem is often poverty.", "这个问题的根本原因往往是贫困。"),
    "vulnerable": ("Children are especially vulnerable to misleading advertising.", "儿童特别容易受到误导性广告影响。"),
    "appropriate": ("The punishment should be appropriate to the seriousness of the mistake.", "惩罚应与错误的严重程度相匹配。"),
    "detrimental": ("Air pollution is detrimental to children's lung development.", "空气污染对儿童肺部发育有害。"),
    "considerable": ("The project requires considerable time and money.", "这个项目需要大量时间和资金。"),
    "conventional": ("Conventional teaching methods may not suit every student.", "传统教学方法不一定适合每个学生。"),
    "mitigate": ("Planting trees can help mitigate the effects of urban heat.", "种树可以帮助缓解城市高温带来的影响。"),
    "exacerbate": ("Poor housing can exacerbate existing health problems.", "住房条件差可能会加重已有的健康问题。"),
    "attain": ("Many students struggle to attain a high level of academic writing.", "许多学生很难达到较高的学术写作水平。"),
    "undergo": ("Many cities undergo rapid change after new transport systems are built.", "新的交通系统建成后，许多城市会经历快速变化。"),
    "monitor": ("Hospitals need to monitor patient safety more closely.", "医院需要更密切地监测患者安全。"),
    "compel": ("Rising costs may compel families to delay major purchases.", "成本上升可能迫使家庭推迟大额消费。"),
    "exploit": ("Some companies exploit consumer data without clear permission.", "一些公司在没有明确许可的情况下利用消费者数据。"),
    "cultivate": ("Schools should cultivate curiosity rather than only reward test scores.", "学校应该培养好奇心，而不只是奖励考试分数。"),
    "verify": ("Researchers must verify the data before drawing conclusions.", "研究人员在得出结论前必须核实数据。"),
    "acknowledge": ("Policymakers should acknowledge the pressure on low-income families.", "政策制定者应该承认低收入家庭面临的压力。"),
    "address": ("The new law aims to address unfair treatment in the workplace.", "这项新法律旨在解决职场中的不公平待遇。"),
    "alleviate": ("Better public transport can alleviate traffic pressure in city centres.", "更好的公共交通可以缓解市中心的交通压力。"),
    "accelerate": ("Digital payment systems can accelerate business transactions.", "数字支付系统可以加快商业交易。"),
    "constrain": ("A lack of funding can constrain scientific research.", "资金不足可能会限制科学研究。"),
    "deteriorate": ("Air quality may deteriorate during periods of heavy traffic.", "交通繁忙时期，空气质量可能会恶化。"),
    "prevalence": ("The prevalence of online fraud has raised public concern.", "网络诈骗的普遍存在引发了公众担忧。"),
    "vulnerability": ("Economic vulnerability can limit a family's choices.", "经济脆弱性会限制一个家庭的选择。"),
    "sustainability": ("Sustainability should be considered before large projects are approved.", "大型项目获批前应考虑可持续性。"),
    "regulation": ("Clear regulation can reduce risks in the financial sector.", "清晰的监管可以降低金融领域的风险。"),
    "innovation": ("Innovation often depends on both investment and skilled workers.", "创新通常既依赖投资，也依赖熟练工人。"),
    "accountability": ("Public accountability helps prevent the misuse of power.", "公共问责有助于防止权力滥用。"),
    "autonomy": ("Greater autonomy can improve teachers' professional judgement.", "更大的自主权可以提升教师的专业判断。"),
    "productivity": ("Long working hours do not always lead to higher productivity.", "工作时间长并不总是带来更高的生产率。"),
    "expenditure": ("Household expenditure on energy has increased sharply.", "家庭能源支出大幅增加。"),
    "revenue": ("Tourism revenue can support local services.", "旅游收入可以支持本地服务。"),
    "welfare": ("Child welfare should be a central concern in education policy.", "儿童福祉应该是教育政策的核心关注点。"),
    "disparity": ("There is a clear disparity between urban and rural healthcare.", "城乡医疗服务之间存在明显差距。"),
    "intervention": ("Early intervention can prevent small problems from becoming serious.", "早期干预可以防止小问题变得严重。"),
    "evaluation": ("A fair evaluation should include both cost and social impact.", "公平的评估应同时包括成本和社会影响。"),
    "awareness": ("Public awareness of mental health has improved in recent years.", "近年来，公众对心理健康的认识有所提高。"),
    "comprehensive": ("A comprehensive plan should include funding, training, and evaluation.", "全面的计划应包括资金、培训和评估。"),
    "sustainable": ("A sustainable transport system must be affordable and reliable.", "可持续的交通系统必须负担得起并且可靠。"),
    "viable": ("Remote work is not a viable option for every occupation.", "远程办公并不是每种职业都可行的选择。"),
    "accessible": ("Public services should be accessible to people with disabilities.", "公共服务应该方便残障人士使用。"),
    "affordable": ("Affordable housing is essential for young workers in large cities.", "可负担住房对大城市的年轻员工非常重要。"),
    "adverse": ("Noise pollution can have adverse effects on children's learning.", "噪音污染可能对儿童学习产生不利影响。"),
    "coherent": ("A coherent argument needs clear reasons and relevant evidence.", "连贯的论证需要清晰的理由和相关证据。"),
    "empirical": ("Empirical evidence is stronger than personal opinion.", "实证证据比个人观点更有说服力。"),
    "ethical": ("The use of personal data raises ethical concerns.", "个人数据的使用引发伦理方面的担忧。"),
    "impartial": ("Judges must remain impartial when handling public disputes.", "法官在处理公共争议时必须保持公正。"),
    "inclusive": ("An inclusive school system gives support to different types of learners.", "包容性的学校体系会支持不同类型的学习者。"),
    "innovative": ("Innovative firms are more likely to adapt to market changes.", "创新型企业更有可能适应市场变化。"),
    "mature": ("A mature market usually has stable rules and informed consumers.", "成熟的市场通常有稳定的规则和理性的消费者。"),
    "scarce": ("Water may become scarce in areas affected by drought.", "受干旱影响的地区，水可能会变得稀缺。"),
    "widespread": ("Widespread smartphone use has changed how people receive news.", "智能手机的广泛使用改变了人们获取新闻的方式。"),
    "socioeconomic status": ("A child's socioeconomic status can influence access to education.", "孩子的社会经济地位可能影响其接受教育的机会。"),
    "peer pressure": ("Peer pressure can affect teenagers' choices and behaviour.", "同伴压力会影响青少年的选择和行为。"),
    "public transport": ("Reliable public transport can reduce traffic congestion.", "可靠的公共交通可以减少交通拥堵。"),
    "carbon footprint": ("Households can reduce their carbon footprint by saving energy.", "家庭可以通过节约能源来减少碳足迹。"),
    "renewable energy": ("Renewable energy can reduce dependence on fossil fuels.", "可再生能源可以减少对化石燃料的依赖。"),
    "fossil fuels": ("Many economies still rely heavily on fossil fuels.", "许多经济体仍然严重依赖化石燃料。"),
    "urban sprawl": ("Urban sprawl can increase commuting time and land use.", "城市无序扩张可能增加通勤时间和土地使用。"),
    "digital literacy": ("Digital literacy is essential for modern employment.", "数字素养对现代就业非常重要。"),
    "income inequality": ("Income inequality can weaken social trust.", "收入不平等可能削弱社会信任。"),
    "social mobility": ("Education is often seen as a path to social mobility.", "教育通常被视为实现社会流动的途径。"),
    "ageing population": ("An ageing population may place pressure on healthcare systems.", "人口老龄化可能给医疗系统带来压力。"),
    "mental health": ("Mental health support should be available in schools and workplaces.", "学校和工作场所都应该提供心理健康支持。"),
    "work-life balance": ("A better work-life balance can improve employee retention.", "更好的工作与生活平衡可以提高员工留任率。"),
    "consumer behaviour": ("Online reviews have changed consumer behaviour.", "在线评价改变了消费者行为。"),
    "data privacy": ("Data privacy has become a major concern in digital services.", "数据隐私已经成为数字服务中的重要问题。"),
    "artificial intelligence": ("Artificial intelligence can automate routine tasks.", "人工智能可以自动化处理重复性任务。"),
    "lifelong learning": ("Lifelong learning helps workers adapt to economic change.", "终身学习帮助劳动者适应经济变化。"),
    "vocational training": ("Vocational training can improve young people's employment prospects.", "职业培训可以改善年轻人的就业前景。"),
    "early childhood education": ("Early childhood education can shape later academic performance.", "幼儿教育会影响之后的学业表现。"),
    "public health": ("Public health campaigns can encourage safer behaviour.", "公共健康宣传可以鼓励更安全的行为。"),
    "civic engagement": ("Civic engagement can make local decisions more responsive.", "公民参与可以让本地决策更能回应实际需求。"),
    "cultural heritage": ("Cultural heritage should be protected during urban development.", "城市发展过程中应保护文化遗产。"),
    "gender equality": ("Gender equality can improve fairness in the labour market.", "性别平等可以改善劳动力市场中的公平性。"),
    "labour market": ("The labour market is changing as automation spreads.", "随着自动化扩展，劳动力市场正在变化。"),
    "supply chain": ("A weak supply chain can delay production and raise prices.", "薄弱的供应链可能延误生产并推高价格。"),
    "economic growth": ("Economic growth does not always improve living standards equally.", "经济增长并不总是平等地改善生活水平。"),
    "environmental degradation": ("Environmental degradation can threaten food and water security.", "环境退化可能威胁粮食和用水安全。"),
    "biodiversity loss": ("Biodiversity loss can make ecosystems less stable.", "生物多样性丧失会让生态系统更加不稳定。"),
    "traffic congestion": ("Traffic congestion wastes time and increases air pollution.", "交通拥堵浪费时间并增加空气污染。"),
    "social cohesion": ("Social cohesion is easier to maintain when inequality is low.", "不平等程度较低时，社会凝聚力更容易维持。"),
}

MANUAL_PHONETICS = {
    "however": "haʊˈevə(r)",
    "nevertheless": "ˌnevəðəˈles",
    "conversely": "ˈkɒnvɜːsli",
    "despite": "dɪˈspaɪt",
    "whereas": "ˌweərˈæz",
    "contrary": "ˈkɒntrəri",
    "therefore": "ˈðeəfɔː(r)",
    "furthermore": "ˌfɜːðəˈmɔː(r)",
    "moreover": "mɔːrˈəʊvə(r)",
    "additionally": "əˈdɪʃənəli",
    "likewise": "ˈlaɪkwaɪz",
    "unless": "ənˈles",
    "insofar as": "ˌɪnsəʊˈfɑːr æz",
    "attribute to": "əˈtrɪbjuːt tuː",
    "hinder": "ˈhɪndə(r)",
    "persist": "pəˈsɪst",
    "modify": "ˈmɒdɪfaɪ",
    "indicate": "ˈɪndɪkeɪt",
    "demonstrate": "ˈdemənstreɪt",
    "assume": "əˈsjuːm",
    "confirm": "kənˈfɜːm",
    "underestimate": "ˌʌndərˈestɪmeɪt",
    "significant": "sɪɡˈnɪfɪkənt",
    "substantial": "səbˈstænʃl",
    "marginal": "ˈmɑːdʒɪnl",
    "inevitable": "ɪnˈevɪtəbl",
    "feasible": "ˈfiːzəbl",
    "adequate": "ˈædɪkwət",
    "insufficient": "ˌɪnsəˈfɪʃnt",
    "prevalent": "ˈprevələnt",
    "predominant": "prɪˈdɒmɪnənt",
    "phenomenon": "fəˈnɒmɪnən",
    "tendency": "ˈtendənsi",
    "factor": "ˈfæktə(r)",
    "obstacle": "ˈɒbstəkl",
    "constraint": "kənˈstreɪnt",
    "consequence": "ˈkɒnsɪkwəns",
    "perspective": "pəˈspektɪv",
    "motivation": "ˌməʊtɪˈveɪʃn",
    "deficiency": "dɪˈfɪʃnsi",
    "vital": "ˈvaɪtl",
    "crucial": "ˈkruːʃl",
    "transform": "trænsˈfɔːm",
    "cut down": "kʌt daʊn",
    "advocate": "ˈædvəkeɪt",
    "although": "ɔːlˈðəʊ",
    "nonetheless": "ˌnʌnðəˈles",
    "accordingly": "əˈkɔːdɪŋli",
    "specifically": "spəˈsɪfɪkli",
    "appropriate": "əˈprəʊpriət",
    "arbitrary": "ˈɑːbɪtrəri",
    "beneficial": "ˌbenɪˈfɪʃl",
    "consistent": "kənˈsɪstənt",
    "conventional": "kənˈvenʃənl",
    "critical": "ˈkrɪtɪkl",
    "desirable": "dɪˈzaɪərəbl",
    "detrimental": "ˌdetrɪˈmentl",
    "distinct": "dɪˈstɪŋkt",
    "dominant": "ˈdɒmɪnənt",
    "efficient": "ɪˈfɪʃnt",
    "effective": "ɪˈfektɪv",
    "equivalent": "ɪˈkwɪvələnt",
    "essential": "ɪˈsenʃl",
    "excessive": "ɪkˈsesɪv",
    "fundamental": "ˌfʌndəˈmentl",
    "gradual": "ˈɡrædʒuəl",
    "implicit": "ɪmˈplɪsɪt",
    "inadequate": "ɪnˈædɪkwət",
    "logical": "ˈlɒdʒɪkl",
    "productive": "prəˈdʌktɪv",
    "profound": "prəˈfaʊnd",
    "relevant": "ˈreləvənt",
    "reliable": "rɪˈlaɪəbl",
    "strategic": "strəˈtiːdʒɪk",
    "underlying": "ˌʌndəˈlaɪɪŋ",
    "vulnerable": "ˈvʌlnərəbl",
    "mitigate": "ˈmɪtɪɡeɪt",
    "exacerbate": "ɪɡˈzæsəbeɪt",
    "attain": "əˈteɪn",
    "undergo": "ˌʌndəˈɡəʊ",
    "monitor": "ˈmɒnɪtə(r)",
    "compel": "kəmˈpel",
    "exploit": "ɪkˈsplɔɪt",
    "cultivate": "ˈkʌltɪveɪt",
    "verify": "ˈverɪfaɪ",
    "acknowledge": "əkˈnɒlɪdʒ",
    "address": "əˈdres",
    "alleviate": "əˈliːvieɪt",
    "accelerate": "əkˈseləreɪt",
    "constrain": "kənˈstreɪn",
    "deteriorate": "dɪˈtɪəriəreɪt",
    "prevalence": "ˈprevələns",
    "vulnerability": "ˌvʌlnərəˈbɪləti",
    "sustainability": "səˌsteɪnəˈbɪləti",
    "regulation": "ˌreɡjuˈleɪʃn",
    "innovation": "ˌɪnəˈveɪʃn",
    "accountability": "əˌkaʊntəˈbɪləti",
    "autonomy": "ɔːˈtɒnəmi",
    "productivity": "ˌprɒdʌkˈtɪvəti",
    "expenditure": "ɪkˈspendɪtʃə(r)",
    "revenue": "ˈrevənjuː",
    "welfare": "ˈwelfeə(r)",
    "disparity": "dɪˈspærəti",
    "intervention": "ˌɪntəˈvenʃn",
    "evaluation": "ɪˌvæljuˈeɪʃn",
    "awareness": "əˈweənəs",
    "comprehensive": "ˌkɒmprɪˈhensɪv",
    "sustainable": "səˈsteɪnəbl",
    "viable": "ˈvaɪəbl",
    "accessible": "əkˈsesəbl",
    "affordable": "əˈfɔːdəbl",
    "adverse": "ˈædvɜːs",
    "coherent": "kəʊˈhɪərənt",
    "empirical": "ɪmˈpɪrɪkl",
    "ethical": "ˈeθɪkl",
    "impartial": "ɪmˈpɑːʃl",
    "inclusive": "ɪnˈkluːsɪv",
    "innovative": "ˈɪnəvətɪv",
    "mature": "məˈtʃʊə(r)",
    "scarce": "skeəs",
    "widespread": "ˈwaɪdspred",
}

CATEGORY_RULES = [
    ("逻辑信号词", ["however", "therefore", "whereas", "although", "unless", "thus", "because", "despite", "due", "consequently", "hence", "furthermore", "moreover", "given", "while"]),
    ("核心动词", ["v.", "vi.", "vt."]),
    ("评价形容词", ["adj."]),
    ("抽象名词", ["tion", "ment", "ness", "ity", "ence", "ance", "ism", "phenomenon", "factor", "effect", "impact", "risk"]),
]

TOPIC_HINTS = {
    "教育场景": ["school", "education", "student", "pupil", "learn", "teach", "training", "academic", "课程", "学生", "教育"],
    "科技场景": ["technology", "digital", "computer", "signal", "data", "innovation", "machine", "技术", "数据", "创新"],
    "环境场景": ["environment", "climate", "pollution", "species", "resource", "carbon", "环境", "气候", "污染", "资源"],
    "城市交通": ["city", "urban", "transport", "traffic", "vehicle", "road", "城市", "交通", "车辆"],
    "商业金融": ["business", "market", "economic", "money", "trade", "cost", "salary", "investment", "商业", "经济", "成本", "薪酬"],
    "健康社会": ["health", "medical", "disease", "stress", "social", "relationship", "健康", "医疗", "社会", "关系"],
}

RAW_GROUPS = {
    "核心动词": """
access|v.|获取；进入；使用|阅读替换
achieve|v.|实现，达到|结果
acquire|v.|获得，习得|变化
adapt|v.|适应；改编|变化
adjust|v.|调整，适应|变化
affect|v.|影响|因果
allocate|v.|分配|管理
analyse|v.|分析|证据
approach|v.|处理；接近|方法
assess|v.|评估|证据
benefit|v.|受益；有益于|因果
challenge|v.|质疑；挑战|观点
clarify|v.|阐明，澄清|证据
classify|v.|分类|方法
compare|v.|比较|方法
compensate|v.|补偿，弥补|因果
complement|v.|补充，补足|关系
complicate|v.|使复杂|变化
conduct|v.|实施；进行|方法
confirm|v.|证实，确认|证据
constitute|v.|构成|定义
consume|v.|消费；消耗|主题词
contrast|v.|对比|方法
convince|v.|说服，使相信|观点
cooperate|v.|合作|关系
coordinate|v.|协调|管理
create|v.|创造，造成|因果
decline|v.|下降；拒绝|变化
define|v.|定义，界定|方法
derive|v.|源于；获得|因果
design|v.|设计|方法
determine|v.|决定；确定|因果
develop|v.|发展；开发|变化
differentiate|v.|区分|方法
distribute|v.|分配；分布|变化
eliminate|v.|消除，淘汰|变化
emphasise|v.|强调|观点
enable|v.|使能够|因果
encounter|v.|遇到，遭遇|问题
enforce|v.|执行，强制实施|政府
ensure|v.|确保|因果
establish|v.|建立；确立|方法
estimate|v.|估计|数据
evaluate|v.|评价，评估|证据
evolve|v.|演变，进化|变化
exceed|v.|超过|数据
exclude|v.|排除|限制
expand|v.|扩大，扩张|变化
expose|v.|暴露；揭露|因果
generate|v.|产生，生成|因果
identify|v.|识别，确定|证据
illustrate|v.|说明，阐明|证据
imply|v.|暗示，意味着|证据
impose|v.|强加；征收|政府
incorporate|v.|纳入，包含|方法
increase|v.|增加|变化
influence|v.|影响|因果
inhibit|v.|抑制，阻碍|促进/阻碍
initiate|v.|开始，发起|变化
integrate|v.|整合，融入|方法
interpret|v.|解释，理解|证据
involve|v.|涉及，包含|定义
justify|v.|证明……合理|观点
link|v.|连接，关联|关系
maximise|v.|最大化|变化
minimise|v.|最小化，降低|变化
obtain|v.|获得|变化
occupy|v.|占据；占用|数据
occur|v.|发生，出现|变化
participate|v.|参与|关系
perceive|v.|感知，认为|观点
predict|v.|预测|证据
preserve|v.|保护，保存|环境
prevent|v.|阻止，预防|促进/阻碍
prioritise|v.|优先考虑|方法
proceed|v.|继续进行|过程
prohibit|v.|禁止|政府
propose|v.|提出，建议|观点
purchase|v.|购买|消费
recognise|v.|认识到；承认|观点
recommend|v.|建议，推荐|观点
recover|v.|恢复|变化
regulate|v.|监管，调节|政府
reinforce|v.|强化，加强|因果
reject|v.|拒绝，否定|观点
rely|v.|依赖，依靠|关系
remove|v.|移除，消除|变化
resolve|v.|解决|问题
respond|v.|回应，反应|观点
restore|v.|恢复，修复|环境
retain|v.|保留，保持|变化
shift|v.|转移，改变|变化
stimulate|v.|刺激，促进|促进/阻碍
submit|v.|提交；屈从|方法
substitute|v.|替代|同义替换
sustain|v.|维持，支撑|环境
target|v.|针对，以……为目标|方法
transfer|v.|转移，转让|变化
undermine|v.|削弱，破坏|因果
vary|v.|变化，差异|数据
mitigate|v.|缓解，减轻|因果
exacerbate|v.|使恶化，加剧|因果
attain|v.|达到，获得|结果
undergo|v.|经历，经受|变化
monitor|v.|监测，监督|证据
compel|v.|迫使，强迫|因果
exploit|v.|利用；剥削|商业
cultivate|v.|培养，培育|教育
verify|v.|核实，验证|证据
acknowledge|v.|承认，认可|观点
address|v.|处理，解决|问题
alleviate|v.|缓解，减轻|问题
accelerate|v.|加速，促进|变化
constrain|v.|限制，约束|限制
deteriorate|v.|恶化，变差|变化
""",
    "评价形容词": """
accurate|adj.|准确的|证据
ambiguous|adj.|模糊的，有歧义的|判断
apparent|adj.|明显的；表面的|判断
appropriate|adj.|合适的，恰当的|判断
arbitrary|adj.|任意的，武断的|判断
beneficial|adj.|有益的|评价
complex|adj.|复杂的|判断
consistent|adj.|一致的，持续的|判断
considerable|adj.|相当大的，可观的|程度
conventional|adj.|传统的，常规的|判断
critical|adj.|关键的；批判的|评价
desirable|adj.|值得拥有的，可取的|评价
detrimental|adj.|有害的|评价
distinct|adj.|明显不同的|判断
dominant|adj.|占主导的|范围
efficient|adj.|高效的|评价
effective|adj.|有效的|评价
equivalent|adj.|等同的，相当的|比较
essential|adj.|必要的，本质的|评价
evident|adj.|明显的|证据
excessive|adj.|过度的|程度
external|adj.|外部的|范围
flexible|adj.|灵活的|评价
fundamental|adj.|根本的，基础的|评价
gradual|adj.|逐渐的|变化
implicit|adj.|含蓄的，暗含的|判断
inadequate|adj.|不足的，不充分的|程度
initial|adj.|最初的|过程
internal|adj.|内部的|范围
logical|adj.|合乎逻辑的|逻辑
minor|adj.|较小的，次要的|程度
negative|adj.|负面的|评价
neutral|adj.|中立的|评价
obvious|adj.|明显的|判断
overall|adj.|总体的|范围
positive|adj.|积极的|评价
previous|adj.|先前的|过程
primary|adj.|主要的，首要的|范围
productive|adj.|富有成效的|评价
profound|adj.|深刻的，重大的|程度
random|adj.|随机的|判断
relevant|adj.|相关的|判断
reliable|adj.|可靠的|证据
rigid|adj.|僵化的|评价
severe|adj.|严重的|程度
stable|adj.|稳定的|变化
strategic|adj.|战略性的|评价
temporary|adj.|临时的|过程
underlying|adj.|潜在的，根本的|原因
valid|adj.|有效的，有根据的|证据
vulnerable|adj.|脆弱的，易受伤害的|社会
comprehensive|adj.|全面的，综合的|范围
sustainable|adj.|可持续的|评价
viable|adj.|可行的，能成功的|判断
accessible|adj.|可进入的，易获得的|社会
affordable|adj.|负担得起的|程度
adverse|adj.|不利的，有害的|评价
coherent|adj.|连贯的，条理清楚的|逻辑
empirical|adj.|实证的，基于经验的|证据
ethical|adj.|伦理的，道德的|评价
impartial|adj.|公正的，不偏不倚的|评价
inclusive|adj.|包容的，兼收并蓄的|社会
innovative|adj.|创新的|评价
mature|adj.|成熟的|判断
scarce|adj.|稀缺的，不足的|程度
widespread|adj.|广泛的，普遍的|范围
""",
    "抽象名词": """
access|n.|获取机会；入口|学术概念
accuracy|n.|准确性|证据
advantage|n.|优势|评价
alternative|n.|替代选择|方法
analysis|n.|分析|证据
approach|n.|方法，途径|方法
assessment|n.|评估|证据
assumption|n.|假设|观点
authority|n.|权威；当局|政府
capacity|n.|能力；容量|程度
category|n.|类别|方法
coherence|n.|连贯性|写作
cohesion|n.|衔接性|写作
community|n.|社区，群体|社会
comparison|n.|比较|方法
component|n.|组成部分|定义
concept|n.|概念|学术概念
consumption|n.|消费；消耗|消费
context|n.|背景，语境|学术概念
contradiction|n.|矛盾|逻辑
criterion|n.|标准，准则|评价
debate|n.|争论，辩论|观点
decline|n.|下降，衰退|变化
demand|n.|需求；要求|商业
dimension|n.|方面，维度|学术概念
diversity|n.|多样性|社会
emphasis|n.|强调，重点|观点
evidence|n.|证据|证据
expansion|n.|扩张，扩大|变化
exposure|n.|暴露；接触|因果
feature|n.|特征，特点|描述
framework|n.|框架|方法
function|n.|功能，作用|定义
impact|n.|影响|因果
implication|n.|含义；影响|因果
incentive|n.|激励，诱因|心理
inequality|n.|不平等|社会
infrastructure|n.|基础设施|城市
insight|n.|洞察，见解|观点
interaction|n.|互动，相互作用|关系
interpretation|n.|解释，理解|证据
investment|n.|投资|金融
issue|n.|问题，议题|观点
justification|n.|理由，正当性|观点
labour|n.|劳动；劳动力|工作
limitation|n.|限制，局限|问题
mechanism|n.|机制|学术概念
method|n.|方法|方法
objective|n.|目标；adj. 客观的|观点
outcome|n.|结果|结果
pattern|n.|模式，规律|描述
policy|n.|政策|政府
priority|n.|优先事项|方法
proportion|n.|比例|数据
reduction|n.|减少|变化
resource|n.|资源|环境
response|n.|回应，反应|观点
restriction|n.|限制|问题
role|n.|角色，作用|定义
sector|n.|部门，领域|主题词
strategy|n.|策略|方法
structure|n.|结构|方法
trend|n.|趋势|数据
variation|n.|变化，差异|数据
prevalence|n.|普遍，流行|社会
vulnerability|n.|脆弱性，易受伤害|社会
sustainability|n.|可持续性|环境
regulation|n.|监管，规定|政府
innovation|n.|创新|科技
accountability|n.|问责，责任制|政府
autonomy|n.|自主权，自主性|社会
productivity|n.|生产率|工作
expenditure|n.|支出，花费|金融
revenue|n.|收入，收益|商业
welfare|n.|福利，福祉|社会
disparity|n.|差距，不平等|社会
intervention|n.|干预，介入|方法
evaluation|n.|评估，评价|证据
awareness|n.|意识，认识|心理
""",
    "常见术语": """
socioeconomic status|n.|社会经济地位|社会
peer pressure|n.|同伴压力|教育
public transport|n.|公共交通|城市交通
carbon footprint|n.|碳足迹|环境
renewable energy|n.|可再生能源|环境
fossil fuels|n.|化石燃料|环境
urban sprawl|n.|城市无序扩张|城市交通
digital literacy|n.|数字素养|科技
income inequality|n.|收入不平等|社会
social mobility|n.|社会流动|社会
ageing population|n.|人口老龄化|社会
mental health|n.|心理健康|健康
work-life balance|n.|工作与生活平衡|工作
consumer behaviour|n.|消费者行为|商业
data privacy|n.|数据隐私|科技
artificial intelligence|n.|人工智能|科技
lifelong learning|n.|终身学习|教育
vocational training|n.|职业培训|教育
early childhood education|n.|幼儿教育|教育
public health|n.|公共健康|健康
civic engagement|n.|公民参与|社会
cultural heritage|n.|文化遗产|文化
gender equality|n.|性别平等|社会
labour market|n.|劳动力市场|工作
supply chain|n.|供应链|商业
economic growth|n.|经济增长|商业
environmental degradation|n.|环境退化|环境
biodiversity loss|n.|生物多样性丧失|环境
traffic congestion|n.|交通拥堵|城市交通
social cohesion|n.|社会凝聚力|社会
""",
    "逻辑信号词": """
although|conj.|尽管，虽然|转折
even though|conj.|即使，尽管|转折
nonetheless|adv.|尽管如此|转折
on the contrary|adv.|相反|转折
in contrast|adv.|相比之下|转折
by contrast|adv.|相比之下|转折
on the other hand|adv.|另一方面|转折
as a result|adv.|结果，因此|因果
accordingly|adv.|因此，相应地|因果
because of|prep.|因为，由于|因果
owing to|prep.|由于|因果
as a consequence|adv.|结果，因此|因果
lead to|v.|导致，通向|因果
result in|v.|导致|因果
give rise to|v.|引起，导致|因果
in addition|adv.|此外|递进
besides|adv.|此外，而且|递进
not only but also|conj.|不仅……而且……|递进
similarly|adv.|类似地|递进
in particular|adv.|尤其，特别是|强调
specifically|adv.|具体来说|强调
for instance|adv.|例如|举例
for example|adv.|例如|举例
provided that|conj.|只要，如果|限制条件
as long as|conj.|只要|限制条件
in terms of|prep.|就……而言|限定范围
with regard to|prep.|关于，就……而言|限定范围
""",
}

TOPIC_BANK = """
education|n.|教育|教育场景
curriculum|n.|课程|教育场景
literacy|n.|读写能力；素养|教育场景
tuition|n.|学费；教学|教育场景
discipline|n.|纪律；学科|教育场景
qualification|n.|资格，学历|教育场景
scholarship|n.|奖学金；学术研究|教育场景
technology|n.|技术|科技场景
automation|n.|自动化|科技场景
innovation|n.|创新|科技场景
algorithm|n.|算法|科技场景
database|n.|数据库|科技场景
privacy|n.|隐私|科技场景
surveillance|n.|监控|科技场景
environment|n.|环境|环境场景
emission|n.|排放|环境场景
pollution|n.|污染|环境场景
conservation|n.|保护，保存|环境场景
biodiversity|n.|生物多样性|环境场景
sustainability|n.|可持续性|环境场景
renewable|adj.|可再生的|环境场景
urbanisation|n.|城市化|城市交通
congestion|n.|拥堵|城市交通
commuter|n.|通勤者|城市交通
pedestrian|n.|行人|城市交通
vehicle|n.|车辆|城市交通
suburb|n.|郊区|城市交通
infrastructure|n.|基础设施|城市交通
employment|n.|就业|工作场景
occupation|n.|职业|工作场景
workforce|n.|劳动力|工作场景
productivity|n.|生产率|工作场景
remuneration|n.|薪酬|工作场景
promotion|n.|晋升；推广|工作场景
redundancy|n.|裁员；冗余|工作场景
healthcare|n.|医疗保健|健康场景
diagnosis|n.|诊断|健康场景
treatment|n.|治疗|健康场景
symptom|n.|症状|健康场景
nutrition|n.|营养|健康场景
obesity|n.|肥胖|健康场景
wellbeing|n.|健康幸福|健康场景
advertising|n.|广告|媒体场景
journalism|n.|新闻业|媒体场景
broadcast|n.|广播；播出|媒体场景
audience|n.|观众，听众|媒体场景
misinformation|n.|错误信息|媒体场景
censorship|n.|审查制度|媒体场景
platform|n.|平台|媒体场景
government|n.|政府|政府法律
legislation|n.|立法，法律|政府法律
regulation|n.|法规，监管|政府法律
taxation|n.|税收|政府法律
citizenship|n.|公民身份|政府法律
crime|n.|犯罪|政府法律
punishment|n.|惩罚|政府法律
culture|n.|文化|文化社会
heritage|n.|遗产|文化社会
tradition|n.|传统|文化社会
identity|n.|身份认同|文化社会
minority|n.|少数群体|文化社会
migration|n.|迁移，移民|文化社会
globalisation|n.|全球化|文化社会
consumer|n.|消费者|商业金融
revenue|n.|收入，收益|商业金融
profit|n.|利润|商业金融
budget|n.|预算|商业金融
inflation|n.|通货膨胀|商业金融
interest|n.|利息；兴趣|商业金融
subsidy|n.|补贴|商业金融
tourism|n.|旅游业|旅游场景
destination|n.|目的地|旅游场景
accommodation|n.|住宿|旅游场景
itinerary|n.|行程|旅游场景
hospitality|n.|款待；酒店服务业|旅游场景
attraction|n.|景点；吸引力|旅游场景
""".strip()

FAMILY_SUFFIXES = [
    ("analysis", "analyse", "analytical", "analytically", "分析；分析的；分析地"),
    ("assessment", "assess", "assessable", "assessor", "评估；评估的；评估者"),
    ("benefit", "beneficial", "beneficiary", "benefit from", "好处；有益的；受益者；受益于"),
    ("creation", "create", "creative", "creatively", "创造；创造的；创造性地"),
    ("development", "develop", "developed", "developing", "发展；发展起来的；发展中的"),
    ("economy", "economic", "economical", "economically", "经济；经济的；节约的；经济上"),
    ("education", "educate", "educational", "educator", "教育；教育的；教育者"),
    ("environment", "environmental", "environmentally", "environmentalist", "环境；环境的；环境上；环保人士"),
    ("evidence", "evident", "evidently", "evidential", "证据；明显的；明显地；证据的"),
    ("finance", "financial", "financially", "financier", "金融；金融的；财政上；金融家"),
    ("globalisation", "globalise", "global", "globally", "全球化；全球化；全球的；全球范围地"),
    ("innovation", "innovate", "innovative", "innovator", "创新；创新；创新的；创新者"),
    ("investment", "invest", "investor", "investigate", "投资；投资；投资者；调查"),
    ("legislation", "legislate", "legal", "legally", "立法；立法；法律的；合法地"),
    ("motivation", "motivate", "motivated", "motivating", "动机；激励；有动力的；激励人的"),
    ("participation", "participate", "participant", "participatory", "参与；参与；参与者；参与式的"),
    ("pollution", "pollute", "pollutant", "polluted", "污染；污染；污染物；受污染的"),
    ("productivity", "produce", "productive", "productively", "生产率；生产；高效的；高效地"),
    ("regulation", "regulate", "regulatory", "regulator", "监管；监管；监管的；监管者"),
    ("sustainability", "sustain", "sustainable", "sustainably", "可持续性；维持；可持续的；可持续地"),
]


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def alpha(term: str) -> str:
    match = re.search(r"[A-Za-z]", term)
    return match.group(0).upper() if match else "#"


def load_phonetics() -> dict[str, str]:
    phonetics: dict[str, str] = {}
    ielts100_path = DATA_DIR / "ielts100.json"
    core_path = DATA_DIR / "core-vocab.json"
    if ielts100_path.exists():
        data = json.loads(ielts100_path.read_text(encoding="utf-8"))
        for sentence in data.get("sentences", []):
            for word in sentence.get("words", []):
                if word.get("term") and word.get("phonetic"):
                    phonetics.setdefault(word["term"].lower(), clean(word["phonetic"]))
    if core_path.exists():
        data = json.loads(core_path.read_text(encoding="utf-8"))
        for word in data.get("words", []):
            if word.get("term") and word.get("phonetic"):
                phonetics.setdefault(word["term"].lower(), clean(word["phonetic"]))
    return phonetics


def parse_lines(text: str, category: str) -> list[dict]:
    items = []
    for line in text.strip().splitlines():
        parts = [clean(part) for part in line.split("|")]
        if len(parts) != 4:
            continue
        term, pos, definition, subcategory = parts
        sentence, translation = EXAMPLE_OVERRIDES.get(
            term,
            (example_for(term, category), MANUAL_TRANSLATIONS.get(term, topic_translation_for(term, definition, category))),
        )
        items.append(
            {
                "term": term,
                "pos": pos,
                "definition": definition,
                "category": category,
                "subcategory": subcategory,
                "sentence": sentence,
                "translation": translation,
                "tactic": tactic_for(category, subcategory),
                "source": "独立考试词库",
                "priority": "高",
            }
        )
    return items


def example_for(term: str, category: str) -> str:
    if " " in term:
        return f"We can use '{term}' to express the idea more clearly."
    templates = {
        "核心动词": f"Governments and individuals can {term} the outcome in different ways.",
        "评价形容词": f"This is a {term} issue in academic discussion.",
        "抽象名词": f"The {term} should be explained with clear evidence.",
        "逻辑信号词": f"{term.capitalize()}, the second idea changes how we understand the first one.",
    }
    if category == "话题场景词":
        return f"Public debate about {term} often involves cost, fairness, and long-term impact."
    return f"Clear evidence can make an argument about {term} more convincing."


def topic_translation_for(term: str, definition: str, category: str) -> str:
    clean_definition = definition.split("；", 1)[0]
    if category == "话题场景词":
        return f"关于{clean_definition}的公共讨论，通常会涉及成本、公平和长期影响。"
    return translation_for(term, definition, category)


def translation_for(term: str, definition: str, category: str) -> str:
    clean_definition = definition.split("；", 1)[0]
    if category == "逻辑信号词":
        return f"这句话使用 {term} 表示逻辑关系，意思是：{clean_definition}。"
    if category == "核心动词":
        return f"{term} 是常见动词，意思是：{clean_definition}。"
    if category == "评价形容词":
        return f"{term} 可以用来评价事物，意思是：{clean_definition}。"
    if category == "抽象名词":
        return f"{term} 是常见抽象名词，意思是：{clean_definition}。"
    if category == "同义替换词组":
        return f"{term} 属于同义替换表达，意思是：{clean_definition}。"
    return f"这句话里 {term} 的意思是：{clean_definition}。"


def tactic_for(category: str, subcategory: str) -> str:
    if category == "逻辑信号词":
        return "先判断它标记的是转折、因果、递进还是限制，再看前后句关系。"
    if category == "核心动词":
        return "阅读里先认同义替换；写作里优先替换 help / make / show / change。"
    if category == "评价形容词":
        return "用来评价程度、可行性、好坏和重要性，适合写作观点句。"
    if category == "抽象名词":
        return "适合搭建论证：原因、影响、问题、方法、趋势和结果。"
    if category == "同义替换词组":
        return "按一组一组记，不要孤立背单词。"
    return f"按{subcategory}场景记中文核心义，再配一个自己的例句。"


def independent_candidates() -> list[dict]:
    candidates = []
    for category, raw in RAW_GROUPS.items():
        candidates.extend(parse_lines(raw, category))
    candidates.extend(parse_lines(TOPIC_BANK, "话题场景词"))
    expansion_bases = list(candidates)
    synonym_sets = {
        "重要": ["important", "vital", "crucial", "essential", "significant", "fundamental", "central", "key"],
        "改变": ["change", "alter", "modify", "transform", "shift", "adjust", "adapt", "revise"],
        "减少": ["reduce", "decrease", "diminish", "decline", "lessen", "curb", "cut down", "minimise"],
        "增加": ["increase", "rise", "grow", "expand", "escalate", "accumulate", "intensify", "soar"],
        "支持": ["support", "back", "advocate", "endorse", "justify", "reinforce", "uphold", "promote"],
        "反对": ["oppose", "reject", "challenge", "criticise", "question", "dispute", "undermine", "refute"],
        "显示": ["show", "indicate", "reveal", "demonstrate", "suggest", "imply", "illustrate", "confirm"],
        "问题": ["problem", "issue", "challenge", "obstacle", "barrier", "difficulty", "constraint", "deficiency"],
        "方法": ["method", "approach", "strategy", "measure", "solution", "framework", "mechanism", "procedure"],
        "影响": ["impact", "effect", "influence", "consequence", "implication", "outcome", "result", "repercussion"],
    }
    for label, terms in synonym_sets.items():
        chain = " = ".join(terms)
        for term in terms:
            sentence, translation = EXAMPLE_OVERRIDES.get(
                term,
                (f"A clear example can show how '{term}' works in a real argument.", f"一个清晰的例子可以说明 {term} 在真实论证中如何使用。"),
            )
            candidates.append(
                {
                    "term": term,
                    "pos": "synonym",
                    "definition": f"{label}；同义替换组：{chain}",
                    "category": "同义替换词组",
                    "subcategory": label,
                    "sentence": sentence,
                    "translation": translation,
                    "tactic": "按中文意思成组记忆，阅读识别替换，写作主动换词。",
                    "source": "独立考试词库",
                    "priority": "高",
                }
            )
    return expansion_bases + candidates


def main() -> None:
    entries = []
    seen = set()
    phonetics = load_phonetics()
    for term, pos, definition, category, subcategory, sentence, tactic in MANUAL:
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        entries.append(
            {
                "id": len(entries) + 1,
                "term": term,
                "alpha": alpha(term),
                "pos": pos,
                "phonetic": phonetics.get(term.lower(), MANUAL_PHONETICS.get(term.lower(), "")),
                "definition": definition,
                "category": category,
                "subcategory": subcategory,
                "sentence": sentence,
                "translation": MANUAL_TRANSLATIONS.get(term, translation_for(term, definition, category)),
                "tactic": tactic,
                "source": "手工必备",
                "priority": "最高",
            }
        )

    candidates = independent_candidates()
    candidates.sort(key=lambda item: (0 if item.get("priority") == "高" else 1, item["category"], len(item["term"]), item["term"].lower()))
    for item in candidates:
        if len(entries) >= 1000:
            break
        key = item["term"].lower()
        if key in seen:
            continue
        seen.add(key)
        entries.append(
            {
                "id": len(entries) + 1,
                "term": item["term"],
                "alpha": alpha(item["term"]),
                "pos": item["pos"],
                "phonetic": phonetics.get(item["term"].lower(), MANUAL_PHONETICS.get(item["term"].lower(), "")),
                "definition": item["definition"],
                "category": item["category"],
                "subcategory": item["subcategory"],
                "sentence": item["sentence"],
                "translation": item["translation"],
                "tactic": item["tactic"],
                "source": item["source"],
                "priority": "高",
            }
        )

    category_counts = Counter(entry["category"] for entry in entries)
    alpha_counts = Counter(entry["alpha"] for entry in entries)
    output = {
        "meta": {
            "title": "雅思单词必杀技",
            "wordCount": len(entries),
            "source": "独立整理：学术词表思路 + 雅思写作评分关注点 + 常见话题词",
            "version": "2026-07-30",
        },
        "categories": [{"name": name, "count": count} for name, count in category_counts.items()],
        "alphas": [{"letter": letter, "count": alpha_counts.get(letter, 0)} for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if alpha_counts.get(letter, 0)],
        "words": entries,
    }
    TARGET.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {TARGET} with {len(entries)} words")


if __name__ == "__main__":
    main()
