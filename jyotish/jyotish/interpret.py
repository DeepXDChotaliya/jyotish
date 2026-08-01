"""
The reading corpus. Static Parashari material, no computation.

Everything here answers "why", not "what". The engine says a lord sits in a
house; this module says what that has traditionally meant and on what grounds,
so the console can always show its reasoning instead of asserting a verdict.

Sources are the standard Parashari stream: BPHS phala adhyayas for lord-in-house,
Phaladeepika and Saravali for the sign and karaka material. Where authorities
disagree the more commonly taught reading is given.
"""

# ---------------------------------------------------------------------------
# Houses
# ---------------------------------------------------------------------------

HOUSES = [
    {
        "num": 1, "name": "Tanu", "title": "Body and self",
        "theme": "The physical vehicle, constitution, temperament, the shape a "
                 "life takes from the outside.",
        "keywords": ["body", "vitality", "personality", "head", "early life",
                     "how others read you"],
        "category": "Kendra / Trikona", "kind": "dharma",
    },
    {
        "num": 2, "name": "Dhana", "title": "Wealth and speech",
        "theme": "Accumulated resources, the voice, the family you were fed by, "
                 "and what you can say out loud.",
        "keywords": ["savings", "speech", "face", "food", "family of origin",
                     "values"],
        "category": "Maraka", "kind": "artha",
    },
    {
        "num": 3, "name": "Sahaja", "title": "Courage and siblings",
        "theme": "Self-effort, the nerve to act, younger siblings, short "
                 "journeys, hands and the appetite for risk.",
        "keywords": ["courage", "siblings", "skill", "communication", "arms",
                     "initiative"],
        "category": "Upachaya", "kind": "kama",
    },
    {
        "num": 4, "name": "Sukha", "title": "Home and inner peace",
        "theme": "The mother, the house, the land, the chest, and the felt "
                 "sense of being at ease anywhere.",
        "keywords": ["mother", "property", "vehicles", "education", "heart",
                     "emotional ground"],
        "category": "Kendra", "kind": "moksha",
    },
    {
        "num": 5, "name": "Putra", "title": "Mind, children, past merit",
        "theme": "Intelligence, creative issue, children, mantra, speculation, "
                 "and the credit carried in from before.",
        "keywords": ["intelligence", "children", "creativity", "romance",
                     "mantra", "purva punya"],
        "category": "Trikona", "kind": "dharma",
    },
    {
        "num": 6, "name": "Ripu", "title": "Conflict, debt, service",
        "theme": "Enemies, illness, borrowing, daily work, and the discipline "
                 "that comes only from friction.",
        "keywords": ["illness", "debt", "enemies", "service", "litigation",
                     "maternal uncle", "routine"],
        "category": "Dusthana / Upachaya", "kind": "artha",
    },
    {
        "num": 7, "name": "Kalatra", "title": "Partnership",
        "theme": "The spouse, the business partner, open dealings with others, "
                 "and everything negotiated rather than owned.",
        "keywords": ["marriage", "partners", "contracts", "trade", "the public",
                     "travel abroad"],
        "category": "Kendra / Maraka", "kind": "kama",
    },
    {
        "num": 8, "name": "Randhra", "title": "Transformation and the hidden",
        "theme": "Longevity, inheritance, other people's money, occult study, "
                 "and every ending that forces a new form.",
        "keywords": ["longevity", "inheritance", "crisis", "occult", "surgery",
                     "in-laws", "sudden events"],
        "category": "Dusthana", "kind": "moksha",
    },
    {
        "num": 9, "name": "Dharma", "title": "Fortune and belief",
        "theme": "The father, the teacher, law and philosophy, long journeys, "
                 "and grace that arrives without being earned.",
        "keywords": ["father", "guru", "luck", "law", "pilgrimage", "higher "
                     "learning", "dharma"],
        "category": "Trikona", "kind": "dharma",
    },
    {
        "num": 10, "name": "Karma", "title": "Work and standing",
        "theme": "Profession, authority, reputation, and the mark the world "
                 "agrees you have made.",
        "keywords": ["career", "status", "authority", "father", "government",
                     "public role"],
        "category": "Kendra / Upachaya", "kind": "artha",
    },
    {
        "num": 11, "name": "Labha", "title": "Gains and network",
        "theme": "Income, elder siblings, friends, ambitions realised, and "
                 "everything that arrives through other people.",
        "keywords": ["income", "gains", "friends", "elder siblings", "hopes",
                     "networks"],
        "category": "Upachaya", "kind": "kama",
    },
    {
        "num": 12, "name": "Vyaya", "title": "Loss, release, foreign lands",
        "theme": "Expenditure, isolation, sleep and the bed, foreign residence, "
                 "and liberation as the final expense.",
        "keywords": ["expense", "foreign lands", "seclusion", "sleep", "moksha",
                     "hospitals", "charity"],
        "category": "Dusthana", "kind": "moksha",
    },
]

# ---------------------------------------------------------------------------
# Signs
# ---------------------------------------------------------------------------

SIGNS_INFO = [
    {"name": "Aries", "sanskrit": "Mesha", "lord": "Mars", "element": "Fire",
     "mode": "Movable", "gender": "Male", "symbol": "Ram",
     "temperament": "Starts things. Direct, impatient, unwilling to be second.",
     "effect": "makes the matter urgent and self-driven, begun alone and fast"},
    {"name": "Taurus", "sanskrit": "Vrishabha", "lord": "Venus", "element": "Earth",
     "mode": "Fixed", "gender": "Female", "symbol": "Bull",
     "temperament": "Holds and accumulates. Slow to move, harder to shift.",
     "effect": "makes the matter stable, sensory and slow to change once set"},
    {"name": "Gemini", "sanskrit": "Mithuna", "lord": "Mercury", "element": "Air",
     "mode": "Dual", "gender": "Male", "symbol": "Couple",
     "temperament": "Splits and recombines. Curious, verbal, plural.",
     "effect": "splits the matter into several parallel versions and keeps it verbal"},
    {"name": "Cancer", "sanskrit": "Karka", "lord": "Moon", "element": "Water",
     "mode": "Movable", "gender": "Female", "symbol": "Crab",
     "temperament": "Shelters. Reads the room before it moves.",
     "effect": "makes the matter emotional, protective and tied to home or mother"},
    {"name": "Leo", "sanskrit": "Simha", "lord": "Sun", "element": "Fire",
     "mode": "Fixed", "gender": "Male", "symbol": "Lion",
     "temperament": "Presides. Needs the thing to be its own.",
     "effect": "makes the matter a question of authority, pride and being seen"},
    {"name": "Virgo", "sanskrit": "Kanya", "lord": "Mercury", "element": "Earth",
     "mode": "Dual", "gender": "Female", "symbol": "Maiden",
     "temperament": "Corrects. Finds the flaw first and works from there.",
     "effect": "makes the matter analytical and improvable, delivered through work"},
    {"name": "Libra", "sanskrit": "Tula", "lord": "Venus", "element": "Air",
     "mode": "Movable", "gender": "Male", "symbol": "Scales",
     "temperament": "Weighs. Moves through agreement rather than force.",
     "effect": "makes the matter relational, negotiated and dependent on balance"},
    {"name": "Scorpio", "sanskrit": "Vrischika", "lord": "Mars", "element": "Water",
     "mode": "Fixed", "gender": "Female", "symbol": "Scorpion",
     "temperament": "Goes under. Keeps its own counsel, does not forget.",
     "effect": "makes the matter secret, intense and prone to sudden reversal"},
    {"name": "Sagittarius", "sanskrit": "Dhanu", "lord": "Jupiter", "element": "Fire",
     "mode": "Dual", "gender": "Male", "symbol": "Archer",
     "temperament": "Aims far. Needs a principle before it will commit.",
     "effect": "makes the matter principled, expansive and pointed at something distant"},
    {"name": "Capricorn", "sanskrit": "Makara", "lord": "Saturn", "element": "Earth",
     "mode": "Movable", "gender": "Female", "symbol": "Crocodile",
     "temperament": "Climbs. Accepts delay as the price of structure.",
     "effect": "makes the matter slow, structural and earned rather than given"},
    {"name": "Aquarius", "sanskrit": "Kumbha", "lord": "Saturn", "element": "Air",
     "mode": "Fixed", "gender": "Male", "symbol": "Water bearer",
     "temperament": "Stands apart. Serves the many, belongs to no one.",
     "effect": "makes the matter collective, unorthodox and lived at a distance"},
    {"name": "Pisces", "sanskrit": "Meena", "lord": "Jupiter", "element": "Water",
     "mode": "Dual", "gender": "Female", "symbol": "Fishes",
     "temperament": "Dissolves. Boundaries are provisional here.",
     "effect": "makes the matter porous, imaginative and hard to hold a line on"},
]

# ---------------------------------------------------------------------------
# Grahas
# ---------------------------------------------------------------------------

GRAHAS_INFO = {
    "Sun": {
        "sanskrit": "Surya", "nature": "Malefic", "gender": "Male",
        "element": "Fire", "caste": "Kshatriya", "day": "Sunday",
        "karaka": "Soul, father, authority, bone, the eyes",
        "signifies": ["self", "father", "government", "vitality", "status",
                      "the spine", "ego"],
        "behaviour": "Burns off whatever it touches and puts the self at the "
                     "centre of that matter. Grahas near it lose their own voice.",
        "gem": "Ruby", "metal": "Copper",
    },
    "Moon": {
        "sanskrit": "Chandra", "nature": "Benefic when waxing", "gender": "Female",
        "element": "Water", "caste": "Vaishya", "day": "Monday",
        "karaka": "Mind, mother, fluids, the public",
        "signifies": ["mind", "mother", "emotion", "memory", "travel", "water",
                      "the public"],
        "behaviour": "Carries the mind. Whatever house it sits in is where the "
                     "attention actually lives, regardless of what the chart "
                     "otherwise promises.",
        "gem": "Pearl", "metal": "Silver",
    },
    "Mars": {
        "sanskrit": "Mangala", "nature": "Malefic", "gender": "Male",
        "element": "Fire", "caste": "Kshatriya", "day": "Tuesday",
        "karaka": "Energy, siblings, land, blood, courage",
        "signifies": ["drive", "brothers", "property", "surgery", "weapons",
                      "accidents", "engineering"],
        "behaviour": "Cuts. Gives the capacity to act and to break, and forces "
                     "a decision where a soft graha would negotiate.",
        "gem": "Red coral", "metal": "Copper",
    },
    "Mercury": {
        "sanskrit": "Budha", "nature": "Neutral, takes on company", "gender": "Neuter",
        "element": "Earth", "caste": "Shudra", "day": "Wednesday",
        "karaka": "Speech, intellect, trade, skin, nerves",
        "signifies": ["communication", "commerce", "analysis", "writing",
                      "friends", "maternal uncle", "hands"],
        "behaviour": "Takes the colour of whatever it sits with. Alone it is "
                     "clean intelligence; with a malefic it becomes clever.",
        "gem": "Emerald", "metal": "Brass",
    },
    "Jupiter": {
        "sanskrit": "Guru", "nature": "Benefic", "gender": "Male",
        "element": "Ether", "caste": "Brahmin", "day": "Thursday",
        "karaka": "Wisdom, children, wealth, husband, fat, liver",
        "signifies": ["teacher", "children", "law", "faith", "expansion",
                      "money", "counsel"],
        "behaviour": "Expands whatever it touches, for better and for worse. "
                     "Its aspect protects a house more reliably than its "
                     "occupation of it.",
        "gem": "Yellow sapphire", "metal": "Gold",
    },
    "Venus": {
        "sanskrit": "Shukra", "nature": "Benefic", "gender": "Female",
        "element": "Water", "caste": "Brahmin", "day": "Friday",
        "karaka": "Spouse, pleasure, art, vehicles, semen, kidneys",
        "signifies": ["wife", "beauty", "art", "luxury", "comfort", "desire",
                      "diplomacy"],
        "behaviour": "Makes a thing attractive and worth having. Also makes it "
                     "harder to renounce, which is why it rules both marriage "
                     "and the taste for indulgence.",
        "gem": "Diamond", "metal": "Silver",
    },
    "Saturn": {
        "sanskrit": "Shani", "nature": "Malefic", "gender": "Neuter",
        "element": "Air", "caste": "Shudra", "day": "Saturday",
        "karaka": "Time, sorrow, labour, longevity, servants, the old",
        "signifies": ["discipline", "delay", "structure", "the poor", "iron",
                      "chronic illness", "endurance"],
        "behaviour": "Delays and then makes permanent. It takes the house it "
                     "sits in away first, and returns it built properly if the "
                     "work was done.",
        "gem": "Blue sapphire", "metal": "Iron",
    },
    "Rahu": {
        "sanskrit": "Rahu", "nature": "Malefic, shadow", "gender": "Neuter",
        "element": "Air", "caste": "Outcaste", "day": "None",
        "karaka": "Obsession, foreignness, illusion, ambition",
        "signifies": ["ambition", "foreign things", "technology", "smoke",
                      "scandal", "amplification", "the unorthodox"],
        "behaviour": "Amplifies the house without ripening it. Gives the thing "
                     "in enormous quantity and withholds the satisfaction of "
                     "having it.",
        "gem": "Hessonite", "metal": "Lead",
    },
    "Ketu": {
        "sanskrit": "Ketu", "nature": "Malefic, shadow", "gender": "Neuter",
        "element": "Fire", "caste": "Outcaste", "day": "None",
        "karaka": "Detachment, moksha, past mastery, sudden loss",
        "signifies": ["renunciation", "occult", "healing", "flags", "sudden "
                      "endings", "mastery without interest"],
        "behaviour": "Subtracts. It gives skill in the house's matters and no "
                     "appetite for them, which reads as talent that refuses to "
                     "be monetised.",
        "gem": "Cat's eye", "metal": "Lead",
    },
}

# ---------------------------------------------------------------------------
# Lord of house N placed in house M.
#
# 144 cells. The BPHS phala tradition, stated as a working reading rather than
# a verdict. Each line names the mechanism, because the mechanism is what lets
# you adjust the reading when dignity or aspect changes it.
# ---------------------------------------------------------------------------

LORD_IN_HOUSE = {
    1: {
        1: "The self rules itself. Strong constitution and a face that matches the person behind it. Health holds up, but the life is self-referential and other people are often kept at arm's length.",
        2: "Body and resources fuse. Money is earned through personal presence, voice or name rather than through structures. Family of origin stays materially involved. Weight and appetite tend to rise with age.",
        3: "Vitality is spent on effort. Self-made in the literal sense, courageous, restless, good with the hands. Siblings feature strongly. Nothing arrives without being pushed.",
        4: "The self is anchored at home. Comfort, property and the mother's line support the constitution. A person happiest on their own ground, sometimes reluctant to leave it.",
        5: "Intelligence is the identity. Learning, creative work and children carry the sense of self. Speculative instincts. Past merit shows up as things arriving more easily than they should.",
        6: "The body is put into conflict. Health needs management, service and routine define the days, and the person is at their best when there is something to fight. Debts and enemies are recurring themes.",
        7: "The self is completed by another. Marriage and partnership are structurally central, not optional. Travel and dealings away from home. Identity shifts noticeably after the partnership forms.",
        8: "The constitution is tested by transformation. Chronic patterns, interest in what is hidden, and a life that changes shape through crisis rather than plan. Longevity is usually good once the early tests pass.",
        9: "The self runs on fortune. Father and teachers lift the person, belief is load-bearing, and long journeys change the life. Things work out through grace more than through calculation.",
        10: "The person is their work. Public standing is fused with identity, authority comes naturally, and the reputation precedes the individual. Rest is hard to justify.",
        11: "The self gains through others. Networks, elder siblings and friends are the delivery mechanism. Ambitions get met, though the person can end up defined by their circle.",
        12: "The self is spent elsewhere. Foreign lands, seclusion, hospitals or spiritual practice draw the vitality away from the visible life. Health needs guarding. Strong moksha leaning.",
    },
    2: {
        1: "Wealth attaches to the person. Resources are held personally rather than institutionally, and speech is a defining feature. The family of origin remains part of the self image.",
        2: "The wealth house rules itself. Savings accumulate and hold. Clear voice, food matters, family wealth stays intact. Little dispersal, but also little movement.",
        3: "Money follows effort and communication. Earned through skill, siblings, writing or dealing. Not inherited, and rarely still for long.",
        4: "Wealth converts to property and comfort. Family money buys land and vehicles. The mother's side is materially significant. Assets are held rather than traded.",
        5: "Earnings come through intelligence, creative work or speculation. Children and wealth are linked. Good for advisory or teaching income, risky for gambling.",
        6: "Resources leak into debt, disputes and medical costs. Money is earned through service and competition, and there is usually borrowing in the picture. Speech can become argumentative.",
        7: "Wealth arrives through partnership, marriage or trade. The spouse's family matters financially. Business tends to outperform employment.",
        8: "Family money passes through crisis, inheritance or other people's hands. Sudden gains and sudden holes. Joint finances need explicit terms. Research or occult income is possible.",
        9: "Money follows fortune and the father. Wealth from teaching, law, publishing or long journeys. Resources tend to be principled and to arrive at the right moment.",
        10: "Earnings come from the profession and the public name. Salary and status are the vehicle. Speech is used professionally.",
        11: "Savings feed directly into gains. Compounding wealth, strong income, well-connected. One of the plainer money combinations.",
        12: "Resources drain into expense, foreign accounts or charity. Money moves out as fast as it comes in, often for genuine reasons. Family wealth is dispersed or held abroad.",
    },
    3: {
        1: "Courage is part of the constitution. Self-driven, physically capable, good with the hands. Siblings shape the early self.",
        2: "Effort produces resources. Earnings from communication, media, skill and short trips. Siblings are involved in family money.",
        3: "The house of effort rules itself. Real courage, reliable siblings, strong hands and voice. Self-reliance is the default setting.",
        4: "Initiative is spent on home and mother. Property acquired through effort. Siblings live close or share the house. Restlessness at home.",
        5: "Effort feeds intelligence and creative output. Skilled with instruments, performance or craft. Siblings and children are connected.",
        6: "Courage is spent on conflict and service. Competitive, litigious if pushed, and effective in adversarial work. Sibling relations carry friction.",
        7: "Initiative goes into partnership and trade. The spouse is often met through work or a sibling. Business travel is constant.",
        8: "Effort meets obstruction. Courage is tested by crisis, and self-driven ventures carry risk. Interest in the hidden. Sibling health needs watching.",
        9: "Effort is rewarded by fortune. Long journeys undertaken by choice, publishing, teaching. The father and siblings are linked.",
        10: "Self-effort becomes the career. Nothing in the profession is handed over. Excellent for founders, performers and anyone whose output is their own hands.",
        11: "Effort converts directly to gains. Ambitious, well-networked, and siblings support income. A dependable earning combination.",
        12: "Effort dissipates or goes abroad. Courage spent on solitary or foreign work. Siblings distant. Good for retreat practice, poor for visible reward.",
    },
    4: {
        1: "Home and self are one. The person carries their comfort with them and the mother's influence is written into the personality. Property tends to come early.",
        2: "Home converts to wealth. Property and vehicles bought and held, family money tied to land. The mother is financially involved.",
        3: "Domestic life demands effort. Moves, renovations, siblings in the house. Peace of mind depends on staying busy.",
        4: "The house of peace rules itself. Genuine ease, secure home, a supportive mother, education completed. One of the stabler placements.",
        5: "Home is where the mind is fed. Education, children and creative work happen in the house. The mother is intellectually formative.",
        6: "Domestic peace is under pressure. Disputes over property, the mother's health, and a home that does not fully settle. Work often runs from the house.",
        7: "Home moves to where the partnership is. Property through marriage, or a residence away from the birthplace. The spouse and mother interact heavily.",
        8: "The foundation is disturbed. Property through inheritance or dispute, an unsettled early home, the mother's health as a recurring theme. Deep interior life underneath it.",
        9: "Home is fortunate and often far away. Property in another place, a religious or scholarly household, the mother and father both supportive.",
        10: "Home and career occupy the same ground. Works from the house or in property, land or vehicles. Public standing built on a domestic base.",
        11: "Property and comfort convert to income. Rental, land or vehicle gains. The mother's network helps. Multiple residences are common.",
        12: "Home is elsewhere or given up. Foreign residence, ashrams, hospitals, or a house that costs more than it gives. Deep private peace, little public comfort.",
    },
    5: {
        1: "Intelligence is the identity. Quick mind, creative output, children close to the self. Past merit shows as a life that catches breaks.",
        2: "Mind produces resources. Income from advisory work, teaching, performance or speculation. Children affect the family finances.",
        3: "Intelligence expressed through skill and effort. Writing, craft, performance. Younger siblings and children are linked.",
        4: "The mind rests at home. Education completed on home ground, creative work done privately, the mother intellectually central. Children bring domestic happiness.",
        5: "The house of mind rules itself. Clear intelligence, sound judgement, children secure, mantra practice effective. One of the strongest single placements.",
        6: "Intelligence is spent on problems. Excellent diagnostic and competitive mind, but creative work meets obstruction and children's matters carry strain. Speculation is dangerous here.",
        7: "The mind is engaged by the partner. Romance leads to marriage, the spouse is intellectually matched, and children arrive through the partnership rather than before it.",
        8: "Intelligence turns to the hidden. Research, occult study, psychology. Children's matters face delay or crisis. Speculation is unsafe. Deep but unsettled mind.",
        9: "Mind and fortune align. Higher learning, teaching, philosophy, and children who are themselves fortunate. Purva punya and dharma reinforce each other. A very strong combination.",
        10: "Intelligence becomes the career. Advisory, teaching, creative or speculative professions. Children affect public standing.",
        11: "Creative work converts to gains. Income from intelligence and from children. Speculative gains are actually possible here, unlike most placements.",
        12: "Mind withdraws. Creative work done in seclusion or abroad, spiritual practice effective, children distant or delayed. Strong meditative capacity, weak public output.",
    },
    6: {
        1: "The lord of trouble sits on the body. Health, debts and enemies attach to the person directly. Read as a viparita placement only when it is strong: hardship then becomes competence.",
        2: "Debt and dispute touch the resources. Loans, medical expense, and speech that can turn combative. Earnings from service or health work.",
        3: "Conflict is met with effort. Fighting spirit, effective in competitive fields, siblings can be adversarial. Health improves with physical work.",
        4: "Trouble reaches the home. Property disputes, the mother's health, and a domestic base that needs defending. Peace of mind is the thing to protect.",
        5: "Difficulty enters mind and children. Anxiety, obstruction in creative work, and children's health as a theme. Strong analytic mind, poor speculative one.",
        6: "The house of conflict rules itself. This is Harsha yoga: the difficulty cancels itself. Real resilience, enemies defeated, illness survived, debts cleared.",
        7: "Conflict enters partnership. Disagreement in marriage or business, litigation with partners, and a spouse who may carry health issues. Open enemies rather than hidden ones.",
        8: "Two dusthanas exchange. Viparita raja yoga: chronic trouble resolves through crisis. Good for medicine, insurance, research and anything that profits from other people's difficulty.",
        9: "Difficulty touches fortune and father. Belief tested, the father's health a concern, and luck that has to be worked for. Legal and religious disputes possible.",
        10: "Conflict is the profession. Law, medicine, military, audit, debt collection. Career advances through competition and there are workplace adversaries throughout.",
        11: "Debt converts to income. Earnings from lending, service, healthcare or litigation. Gains are real but arrive with obligations attached.",
        12: "Enemies dissolve. Another viparita reading: opposition disappears of its own accord. Expenses on health, hospitals or foreign treatment. Good for hospital and prison work.",
    },
    7: {
        1: "The partner is written into the self. Marriage is structurally central and identity changes with it. Strong pull toward being one of a pair.",
        2: "Partnership brings resources. Wealth after marriage, the spouse's family financially involved, and shared money mixed with family money.",
        3: "Partnership requires effort. Spouse met through work or siblings, frequent short travel, and a marriage that stays lively rather than settled.",
        4: "Marriage settles the home. Property after marriage, spouse and mother in close contact, and domestic peace dependent on the partnership.",
        5: "Love leads to marriage. The spouse is intellectually engaging, children come through the partnership, and romance and commitment are the same track.",
        6: "Partnership meets friction. Disagreement, health matters in the spouse, or a marriage that runs alongside heavy work. Business partnerships need written terms.",
        7: "The partnership house rules itself. A committed and durable marriage, effective in trade and negotiation. Straightforward as these things go.",
        8: "Marriage transforms through crisis. Longevity of the union tested, in-laws significant, joint finances complicated. Intensity is the point of the relationship, not a fault in it.",
        9: "Fortune arrives with the partner. The spouse is a teacher in some sense, marriage often to someone from elsewhere, and luck improves after the union.",
        10: "Partner and career interlock. Business partnership, a spouse in the same field, or public standing that depends on the marriage. Marriage is publicly visible.",
        11: "Partnership produces gains. Income through the spouse or business partners, and a social circle acquired through the union.",
        12: "The partner is elsewhere. Marriage to a foreigner, separation by distance, or a union that costs more than it returns. Also read as spiritual partnership when benefics support it.",
    },
    8: {
        1: "Transformation sits on the body. Health has hidden layers, the life reshapes itself repeatedly, and there is natural access to what other people keep buried. Longevity usually good after early tests.",
        2: "Family resources pass through crisis. Inheritance, sudden loss, other people's money mixed with one's own. Speech carries weight and secrecy.",
        3: "Effort meets sudden reversal. Courage tested unexpectedly, siblings' matters unsettled. Suited to research and to work with risk.",
        4: "The foundation carries the hidden. Unsettled early home, property through inheritance or dispute, the mother's health significant. Rich interior life.",
        5: "The mind runs deep and unquiet. Occult and research capacity, obstruction in children's matters, and speculation that should be avoided outright.",
        6: "Dusthana to dusthana. Sarala yoga: crisis is met and survived. Enemies fail, chronic problems resolve, and there is unusual staying power. Strong for medicine and investigation.",
        7: "Partnership carries the transformation. The marriage brings crisis and rebuilding, in-laws are significant, joint finances need care. Longevity of the spouse is a classical concern here.",
        8: "The house of crisis rules itself. Long life, resilience, genuine occult aptitude, and inheritance that actually arrives. The difficulty is contained.",
        9: "Fortune arrives through upheaval. Belief is remade by crisis, the father's matters unsettled, and luck that comes only after loss. Strong for esoteric study.",
        10: "The career involves the hidden. Research, surgery, insurance, forensics, psychology, mining. Public standing goes through at least one full reversal.",
        11: "Gains through other people's money. Inheritance, insurance, investment, and income with strings attached. Elder siblings' matters can be difficult.",
        12: "Crisis dissolves into release. Vimala-adjacent reading: the trouble expends itself. Foreign or institutional life, hospitals, ashrams, and genuine moksha capacity.",
    },
    9: {
        1: "Fortune sits on the person. Naturally lucky, principled, and lifted by father and teachers. Belief is visible in the personality.",
        2: "Fortune becomes wealth. Money through teaching, law, publishing or the father. Resources arrive at the right time without much strain.",
        3: "Luck rewards effort. Long journeys taken deliberately, writing and teaching, and a father connected to the siblings' matters.",
        4: "Fortune settles the home. A religious or scholarly household, property in another place, both parents supportive. Deep contentment.",
        5: "Dharma and past merit meet. Higher learning, fortunate children, effective mantra practice, and advice that carries authority. Among the strongest combinations in the chart.",
        6: "Fortune is put to work against difficulty. Luck arrives through service, medicine or law, but belief gets tested and the father's health is a theme.",
        7: "The partner brings fortune. Marriage to someone from another place or tradition, and luck that turns on the union. The spouse functions as a teacher.",
        8: "Fortune passes through crisis. Belief remade by loss, the father's matters unsettled, inheritance from him. Strong for occult and esoteric study.",
        9: "The house of dharma rules itself. Genuine good fortune, a real teacher, a supportive father, and a life with a principle running through it.",
        10: "Fortune and career fuse. Authority in law, teaching, religion or policy. The father affects the profession. Reputation rests on principle.",
        11: "Fortune converts to gains. Income through teaching, law or long-distance dealing. Well-placed friends. Reliable earning combination.",
        12: "Fortune is spent abroad or inward. Residence in another country, pilgrimage, monastic leanings, and a father who is distant or absent. Strong moksha, weak worldly luck.",
    },
    10: {
        1: "The career is the person. Authority is personal rather than positional, and the reputation is inseparable from the individual. Work starts early.",
        2: "Profession produces resources. Salaried or fee-based earning, the family involved in the work, and speech used professionally.",
        3: "Career built by effort. Self-made, hands-on, communication-heavy. Siblings connected to the work. Frequent short travel.",
        4: "Career operates from home or in property. Land, vehicles, education or domestic industry. The mother affects the profession. Comfort and status are linked.",
        5: "Profession runs on intelligence. Advisory, teaching, creative or speculative work. Children affect the career and vice versa.",
        6: "Career is competitive. Law, medicine, military, service, audit. Advancement through conflict and there are always adversaries in the workplace.",
        7: "Career through partnership and the public. Business, trade, consulting, or a profession conducted away from the birthplace. The spouse is professionally involved.",
        8: "Career involves the hidden or the risky. Research, surgery, insurance, occult, mining. At least one complete reversal and rebuild of the professional life.",
        9: "Career carries dharma. Law, teaching, religion, policy, publishing. The father influences the profession. Authority is earned rather than seized.",
        10: "The career house rules itself. Clear professional direction, real standing, and a reputation that holds. Straightforward and strong.",
        11: "Career converts to gains. Income tracks status closely, ambitions met, and a professional network that pays. Reliable.",
        12: "Career is abroad or behind the scenes. Foreign employment, institutional work, hospitals, ashrams, or a role with no public credit. Expense runs high against the work.",
    },
    11: {
        1: "Gains attach to the person. Income arrives through personal presence and reputation, and ambitions are part of the identity. Elder siblings are influential.",
        2: "Gains feed savings directly. Income accumulates rather than passing through. Friends and elder siblings involved in family money. A plain wealth combination.",
        3: "Gains through effort and communication. Income from skill, media, dealing and short travel. Elder and younger siblings both feature.",
        4: "Gains convert to property and comfort. Income into land and vehicles, friends connected to the home, and the mother's network as a channel.",
        5: "Gains through intelligence and children. Income from advisory or creative work, and speculation that can actually pay. Friends met through learning.",
        6: "Gains come with obligation. Income from service, lending, medicine or litigation. Friends can become adversaries. Debts run alongside earnings.",
        7: "Gains through partnership. Income from the spouse, business partners and trade. The social circle arrives through the marriage.",
        8: "Gains through other people's resources. Inheritance, insurance, investment, and income that arrives suddenly. Elder siblings' matters unsettled.",
        9: "Gains through fortune and teaching. Income from law, publishing, long-distance work. Well-placed friends. The father supports the earning.",
        10: "Gains through profession and status. Income tracks the career directly. Ambition is public and largely met.",
        11: "The house of gains rules itself. Income is secure and grows, the network is real, and desires get fulfilled. Among the plainest good placements.",
        12: "Gains dissipate or come from abroad. Foreign income, charitable spending, and money that does not stay. Friends distant or few. Expense keeps pace with earning.",
    },
    12: {
        1: "Expense attaches to the person. Health and vitality drain into unseen places, and there is a natural pull toward seclusion, foreign lands or practice. Sleep matters more than usual.",
        2: "Resources leave. Family money dispersed or held abroad, spending outpacing saving, and speech that costs something. Often genuinely charitable rather than careless.",
        3: "Effort spent on the invisible. Solitary or foreign work, siblings distant, courage tested privately. Good for retreat practice, poor for visible reward.",
        4: "Home is elsewhere. Foreign residence, property abroad, or a house that consumes more than it returns. The mother distant or unwell. Deep private peace.",
        5: "Mind withdraws. Creative work done in seclusion, effective spiritual practice, children distant or delayed. Speculation loses money.",
        6: "Loss consumes conflict. Viparita reading: enemies and debts dissolve without a fight. Expense on health and hospitals. Suited to institutional and hospital work.",
        7: "Partner from elsewhere. Marriage abroad or at a distance, separation as a recurring theme, and a union that costs. Also read as renunciate partnership when benefics support it.",
        8: "Loss and crisis compound and then release. Foreign or institutional life, hospitals and ashrams, and genuine capacity for moksha. Inheritance is often absent or spent.",
        9: "Fortune spent abroad or inward. Long residence in another country, pilgrimage, monastic leaning, and a father who is distant. Belief becomes private.",
        10: "Career is behind the scenes or abroad. Institutional work, hospitals, foreign employment, research. Public credit is scarce even when the work is good.",
        11: "Gains leak. Income arrives and leaves, foreign earning, and friends who cost money. Ambitions get funded but not banked.",
        12: "The house of loss rules itself. Expenditure is contained, foreign residence is stable, and moksha practice is effective. The drain closes on itself.",
    },
}

# ---------------------------------------------------------------------------
# Functional nature by lagna.
#
# A graha's real behaviour in a chart is set by what it rules, not by its
# natural benefic or malefic label. Kendra lords that are natural benefics lose
# their power to bless; malefics that rule kendras become harmless. Trikona
# lords are always good. 6/8/12 lords carry difficulty unless they also rule a
# trikona, and the strongest raja yogas come from a graha ruling both.
# ---------------------------------------------------------------------------

FUNCTIONAL_RULES = {
    "yogakaraka": "Rules both a kendra and a trikona. The single most useful "
                  "graha in the chart, and its dasha is usually the making of "
                  "the life.",
    "benefic": "Rules a trikona. Its results are supportive wherever it sits.",
    "kendra_benefic": "A natural benefic ruling an angle. Kendradhipatya dosha: "
                      "it loses its capacity to bless, without becoming harmful.",
    "kendra_malefic": "A natural malefic ruling an angle. The angle strips its "
                      "malefice and it behaves well.",
    "malefic": "Rules a dusthana. It carries the difficulty of that house into "
               "wherever it sits, and into its dasha.",
    "maraka": "Rules a maraka house. Not evil, but it presides over endings and "
              "usually times them.",
    "neutral": "Rules neither a trikona nor a dusthana. It gives the results of "
               "the houses it rules without adding a verdict of its own.",
}

# Yogakaraka graha for each lagna, where one exists. Movable signs produce them
# because a single graha catches both an angle and a trine.
YOGAKARAKA = {
    1: "Saturn",    # Taurus: 9th Capricorn and 10th Aquarius
    3: "Mars",      # Cancer: 5th Scorpio and 10th Aries
    4: "Mars",      # Leo: 4th Scorpio and 9th Aries
    6: "Saturn",    # Libra: 4th Capricorn and 5th Aquarius
    9: "Venus",     # Capricorn: 5th Taurus and 10th Libra
    10: "Venus",    # Aquarius: 4th Taurus and 9th Libra
}

# ---------------------------------------------------------------------------
# Modifiers. These are appended to a base reading rather than replacing it.
# ---------------------------------------------------------------------------

DIGNITY_MODIFIER = {
    "Exalted": "Exalted, so this reading runs at full strength and arrives "
               "early and cleanly.",
    "Moolatrikona": "In moolatrikona, so the reading holds with very little "
                    "qualification.",
    "Own sign": "In its own sign, so it answers to nobody and delivers the "
                "reading directly.",
    "Great friend's sign": "In a great friend's sign, so the dispositor "
                           "actively supports the result.",
    "Friend's sign": "In a friendly sign, so the result comes with support.",
    "Neutral's sign": "In a neutral sign, so the result is neither helped nor "
                      "obstructed by the dispositor.",
    "Enemy's sign": "In an enemy's sign, so the result is obstructed and "
                    "usually arrives late or partial.",
    "Great enemy's sign": "In a great enemy's sign, so expect real resistance "
                          "to this reading.",
    "Debilitated": "Debilitated, so the reading operates without confidence. "
                   "Check for neecha bhanga before calling it a failure.",
    "Node": "A node has no dignity of its own. Read it through its dispositor "
            "and through the graha it sits with.",
}

STATE_MODIFIER = {
    "combust": "Combust, so the graha's own agenda is burnt off and it acts on "
               "the Sun's terms instead: through authority, the father, or the "
               "self rather than for its own significations.",
    "retrograde": "Retrograde, so the results arrive out of sequence. Classical "
                  "opinion holds retrograde grahas strong in output but "
                  "unreliable in timing, and matters often need a second pass.",
    "vargottama": "Vargottama, so what the rasi chart promises the navamsa "
                  "confirms. Treat this reading as reliable.",
    "dig_bala": "At full directional strength here, which adds real force to "
                "the reading.",
    "sandhi": "On a sign boundary, so the reading loses definition. Verify the "
              "birth time before leaning on it.",
}
