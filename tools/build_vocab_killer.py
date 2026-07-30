#!/usr/bin/env python3
"""Build a 1000-item IELTS essential vocabulary tactics dataset."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "public/assets/english/data/vocab-killer.json"


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
    "alter": "城市化会改变传统生活方式。",
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


def parse_lines(text: str, category: str) -> list[dict]:
    items = []
    for line in text.strip().splitlines():
        parts = [clean(part) for part in line.split("|")]
        if len(parts) != 4:
            continue
        term, pos, definition, subcategory = parts
        items.append(
            {
                "term": term,
                "pos": pos,
                "definition": definition,
                "category": category,
                "subcategory": subcategory,
                "sentence": example_for(term, category),
                "translation": MANUAL_TRANSLATIONS.get(term, translation_for(term, definition, category)),
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
    return templates.get(category, f"The word '{term}' is useful in IELTS reading and writing.")


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
    for family in FAMILY_SUFFIXES:
        for term in family[:4]:
            candidates.append(
                {
                    "term": term,
                    "pos": "word family",
                    "definition": family[4],
                    "category": "词族变体",
                    "subcategory": family[0],
                    "sentence": f"Use the word family around '{family[0]}' to recognise related meanings in reading.",
                    "translation": f"用 {family[0]} 这一组词族，可以在阅读中识别相关词义。",
                    "tactic": "词族一起记：名词、动词、形容词、副词互相转换，阅读和写作都会反复出现。",
                    "source": "独立考试词库",
                    "priority": "高",
                }
            )

    expansion_bases = list(candidates)
    collocation_heads = [
        ("major", "主要的"),
        ("serious", "严重的"),
        ("rapid", "快速的"),
        ("gradual", "逐渐的"),
        ("long-term", "长期的"),
        ("short-term", "短期的"),
        ("public", "公共的"),
        ("private", "私人的"),
        ("social", "社会的"),
        ("economic", "经济的"),
        ("environmental", "环境的"),
        ("technological", "技术的"),
    ]
    collocation_nouns = [
        ("impact", "影响"),
        ("factor", "因素"),
        ("change", "变化"),
        ("trend", "趋势"),
        ("policy", "政策"),
        ("approach", "方法"),
        ("benefit", "好处"),
        ("challenge", "挑战"),
        ("solution", "解决方案"),
        ("evidence", "证据"),
        ("development", "发展"),
        ("investment", "投资"),
        ("resource", "资源"),
        ("constraint", "限制"),
        ("outcome", "结果"),
    ]
    for head, head_cn in collocation_heads:
        for noun, noun_cn in collocation_nouns:
            candidates.append(
                {
                    "term": f"{head} {noun}",
                    "pos": "collocation",
                    "definition": f"{head_cn}{noun_cn}",
                    "category": "高频搭配",
                    "subcategory": noun,
                    "sentence": f"The phrase '{head} {noun}' is common in IELTS essays and reading passages.",
                    "translation": f"{head} {noun} 这个搭配在雅思写作和阅读中很常见，意思是：{head_cn}{noun_cn}。",
                    "tactic": "搭配整体记，写作时比单个词更自然，阅读时也更容易定位同义替换。",
                    "source": "独立考试词库",
                    "priority": "中",
                }
            )
    verb_collocations = [
        ("pose", "a challenge", "构成挑战"),
        ("address", "a problem", "处理问题"),
        ("tackle", "an issue", "应对议题"),
        ("raise", "awareness", "提高意识"),
        ("gain", "access", "获得机会"),
        ("provide", "evidence", "提供证据"),
        ("reach", "a conclusion", "得出结论"),
        ("draw", "a comparison", "作比较"),
        ("make", "a distinction", "作区分"),
        ("take", "measures", "采取措施"),
        ("play", "a role", "发挥作用"),
        ("have", "an impact", "产生影响"),
        ("meet", "demand", "满足需求"),
        ("reduce", "pressure", "减轻压力"),
        ("increase", "efficiency", "提高效率"),
        ("improve", "access", "改善获取机会"),
        ("protect", "privacy", "保护隐私"),
        ("restore", "confidence", "恢复信心"),
        ("maintain", "stability", "维持稳定"),
        ("promote", "equality", "促进平等"),
        ("encourage", "participation", "鼓励参与"),
        ("discourage", "consumption", "抑制消费"),
        ("limit", "exposure", "限制接触"),
        ("expand", "capacity", "扩大能力"),
        ("strengthen", "regulation", "加强监管"),
        ("weaken", "motivation", "削弱动机"),
        ("shape", "behaviour", "塑造行为"),
        ("reflect", "a trend", "反映趋势"),
        ("represent", "a shift", "代表转变"),
        ("trigger", "a response", "引发回应"),
    ]
    for verb, obj, definition in verb_collocations:
        candidates.append(
            {
                "term": f"{verb} {obj}",
                "pos": "collocation",
                "definition": definition,
                "category": "高频搭配",
                "subcategory": "动词搭配",
                "sentence": f"The phrase '{verb} {obj}' is useful for precise IELTS writing.",
                "translation": f"{verb} {obj} 这个表达适合写作使用，意思是：{definition}。",
                "tactic": "动词搭配直接服务写作，优先背整块表达。",
                "source": "独立考试词库",
                "priority": "中",
            }
        )
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
            candidates.append(
                {
                    "term": term,
                    "pos": "synonym",
                    "definition": f"{label}；同义替换组：{chain}",
                    "category": "同义替换词组",
                    "subcategory": label,
                    "sentence": f"In IELTS, '{term}' may replace another word in the same meaning group.",
                    "translation": f"在雅思里，{term} 可以和同组词互相替换，表达“{label}”。",
                    "tactic": "按中文意思成组记忆，阅读识别替换，写作主动换词。",
                    "source": "独立考试词库",
                    "priority": "高",
                }
            )
    extended_heads = [
        ("limited", "有限的"), ("sufficient", "充分的"), ("insufficient", "不足的"), ("considerable", "可观的"),
        ("potential", "潜在的"), ("negative", "负面的"), ("positive", "积极的"), ("direct", "直接的"),
        ("indirect", "间接的"), ("practical", "实际的"), ("effective", "有效的"), ("efficient", "高效的"),
        ("reliable", "可靠的"), ("accurate", "准确的"), ("widespread", "广泛的"), ("growing", "不断增长的"),
        ("declining", "下降的"), ("complex", "复杂的"), ("controversial", "有争议的"), ("essential", "必要的"),
    ]
    extended_nouns = [
        ("access", "获取机会"), ("awareness", "意识"), ("behaviour", "行为"), ("capacity", "能力"),
        ("choice", "选择"), ("community", "社区"), ("competition", "竞争"), ("concern", "担忧"),
        ("condition", "条件"), ("cost", "成本"), ("data", "数据"), ("decision", "决定"),
        ("demand", "需求"), ("education", "教育"), ("employment", "就业"), ("evidence", "证据"),
        ("experience", "经验"), ("growth", "增长"), ("income", "收入"), ("knowledge", "知识"),
        ("opportunity", "机会"), ("performance", "表现"), ("population", "人口"), ("pressure", "压力"),
        ("quality", "质量"), ("risk", "风险"), ("skill", "技能"), ("standard", "标准"),
        ("support", "支持"), ("technology", "技术"), ("welfare", "福利"), ("workforce", "劳动力"),
    ]
    for head, head_cn in extended_heads:
        for noun, noun_cn in extended_nouns:
            candidates.append(
                {
                    "term": f"{head} {noun}",
                    "pos": "collocation",
                    "definition": f"{head_cn}{noun_cn}",
                    "category": "高频搭配",
                    "subcategory": "形容词搭配",
                    "sentence": f"The collocation '{head} {noun}' helps express ideas more precisely.",
                    "translation": f"{head} {noun} 可以让表达更具体，意思是：{head_cn}{noun_cn}。",
                    "tactic": "形容词 + 抽象名词是写作常用结构，也常在阅读中作为定位块出现。",
                    "source": "独立考试词库",
                    "priority": "中",
                }
            )
    return expansion_bases + candidates


def main() -> None:
    entries = []
    seen = set()
    for term, pos, definition, category, subcategory, sentence, tactic in MANUAL:
        key = term.lower()
        seen.add(key)
        entries.append(
            {
                "id": len(entries) + 1,
                "term": term,
                "alpha": alpha(term),
                "pos": pos,
                "phonetic": "",
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
                "phonetic": "",
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
