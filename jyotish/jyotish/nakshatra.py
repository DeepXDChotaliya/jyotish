"""
The nakshatra layer. Twenty-seven lunar mansions, and what they actually do.

The rasi chart says what a graha is. The nakshatra says how it behaves and who
it answers to. Two grahas in the same sign, degrees apart, can sit in different
nakshatras with different lords, different deities and opposite temperaments,
and in practice that difference decides the reading. It is also the layer the
whole Vimshottari dasha is built from, so anyone reading dashas is already
using nakshatras whether or not they look at them.

Three mechanics live here and each is used differently:

  Pada        Each nakshatra divides into four quarters of 3 degrees 20. The
              pada is the navamsa, so the pada lord is a second dispositor and
              the pada is where the rasi and the navamsa are actually joined.

  Tara bala   The nine-fold cycle counted from the birth Moon's nakshatra.
              Reused for every transit: a graha crossing your Vipat or Vadha
              tara behaves differently from the same graha in your Sampat.

  Nakshatra   A graha gives the results of its nakshatra lord as much as its
  dispositor  own. Chained far enough these terminate in a loop, and the graha
              that closes the loop tends to run the life.

Sources: Brihat Samhita and the Taittiriya Brahmana for the deities and
shaktis, BPHS for the padas and Vimshottari, Varahamihira for gana and yoni.
The psychological material is a modern reading of the classical shakti and
deity, and is labelled as such rather than passed off as scripture.
"""

from __future__ import annotations

from .engine import NAKSHATRAS, SIGNS

SPAN = 360 / 27          # 13 degrees 20 minutes
PADA_SPAN = SPAN / 4     # 3 degrees 20 minutes

# Tara bala: the nine-fold cycle counted from the janma nakshatra.
TARAS = [
    {"n": 1, "name": "Janma", "quality": "difficult",
     "meaning": "The birth star itself. The body and the sense of self are "
                "exposed. Not a good time to begin anything that needs you to "
                "be robust."},
    {"n": 2, "name": "Sampat", "quality": "good",
     "meaning": "Wealth. Things accumulate and arrive. One of the two best "
                "taras for starting anything material."},
    {"n": 3, "name": "Vipat", "quality": "difficult",
     "meaning": "Danger and loss. Accidents, obstruction and reversal. Avoid "
                "irreversible commitments here."},
    {"n": 4, "name": "Kshema", "quality": "good",
     "meaning": "Wellbeing. Comfort, safety and consolidation. Good for "
                "anything that needs to hold rather than grow."},
    {"n": 5, "name": "Pratyak", "quality": "difficult",
     "meaning": "Obstacles. Effort meets resistance and results arrive late "
                "or not at all."},
    {"n": 6, "name": "Sadhaka", "quality": "good",
     "meaning": "Achievement. The tara for accomplishing a specific thing. "
                "Ambition is rewarded."},
    {"n": 7, "name": "Vadha", "quality": "difficult",
     "meaning": "The killing star, also called Naidhana. The hardest of the "
                "nine. Health, reputation and money are all vulnerable. Start "
                "nothing here."},
    {"n": 8, "name": "Mitra", "quality": "good",
     "meaning": "Friend. Support arrives through people. Good for alliances, "
                "negotiation and asking for things."},
    {"n": 9, "name": "Ati Mitra", "quality": "good",
     "meaning": "Great friend, also called Parama Mitra. The most benign of "
                "the nine. Almost anything begun here is supported."},
]

# Gandanta: the junction between a water sign and a fire sign, where the
# zodiac's fabric is considered torn. The last pada of the water nakshatra and
# the first pada of the fire one.
GANDANTA_PAIRS = [(26, 0), (8, 9), (17, 18)]   # Revati/Ashwini, Ashlesha/Magha,
                                               # Jyeshtha/Mula

NAKSHATRA_DATA = [
    {
        "name": "Ashwini", "lord": "Ketu", "deity": "Ashwini Kumaras",
        "symbol": "The head of a horse", "gana": "Deva", "yoni": "Horse",
        "yoni_gender": "male", "nadi": "Vata", "guna": "Rajas",
        "tattva": "Earth", "varna": "Vaishya", "body": "Knees and the upper feet",
        "shakti": "Shidhra vyapani shakti, the power to reach things quickly",
        "drive": "To move first and heal fast. Ashwini wants to be the one who "
                 "arrives before anyone else and fixes what is broken.",
        "gift": "Speed, initiative, an instinct for emergency, and a genuine "
                "healing capacity. Recovers from setbacks faster than seems "
                "reasonable.",
        "shadow": "Impatience that becomes recklessness. Starts everything and "
                  "stays for none of it. Treats its own body as inexhaustible "
                  "until it is not.",
        "wound": "A fear of being left behind, which is why it will not slow "
                 "down long enough to be caught up with.",
        "work": "Stay past the interesting part. Ashwini's whole growth is in "
                "the boring middle of things it has already started.",
    },
    {
        "name": "Bharani", "lord": "Venus", "deity": "Yama, lord of death",
        "symbol": "The yoni, the womb", "gana": "Manushya", "yoni": "Elephant",
        "yoni_gender": "male", "nadi": "Pitta", "guna": "Rajas",
        "tattva": "Earth", "varna": "Mleccha", "body": "The head and forehead",
        "shakti": "Apabharani shakti, the power to carry things away",
        "drive": "To hold the extremes. Bharani stands at the gate between "
                 "creation and destruction and refuses to pretend either is "
                 "avoidable.",
        "gift": "Enormous capacity to bear what other people cannot. Creative "
                "fertility, sexual and artistic force, and moral seriousness "
                "about consequence.",
        "shadow": "Judgement dressed as principle. Extremism. Bearing burdens "
                  "that were never yours and then resenting the weight.",
        "wound": "An early encounter with limitation or loss that made the "
                 "world feel like something to be endured rather than enjoyed.",
        "work": "Learn what is actually yours to carry. Bharani suffers most "
                "from burdens it picked up voluntarily and cannot put down.",
    },
    {
        "name": "Krittika", "lord": "Sun", "deity": "Agni, fire",
        "symbol": "A razor, a flame", "gana": "Rakshasa", "yoni": "Goat",
        "yoni_gender": "female", "nadi": "Kapha", "guna": "Rajas",
        "tattva": "Earth", "varna": "Brahmin", "body": "The hips and waist",
        "shakti": "Dahana shakti, the power to burn",
        "drive": "To purify by cutting. Krittika separates the real from the "
                 "false and does not soften the verdict.",
        "gift": "Penetrating clarity, moral courage, and an ability to name the "
                "thing everyone else is avoiding. Genuine leadership.",
        "shadow": "Criticism that scorches. Righteousness. Confusing being "
                  "correct with being kind, and losing people to it.",
        "wound": "Being cut early by someone whose judgement it trusted, and "
                 "learning to strike first.",
        "work": "Ask whether the truth needs saying now, by you, in that tone. "
                "Krittika's fire is useful; its timing rarely is.",
    },
    {
        "name": "Rohini", "lord": "Moon", "deity": "Brahma, the creator",
        "symbol": "An ox cart, a chariot", "gana": "Manushya", "yoni": "Serpent",
        "yoni_gender": "male", "nadi": "Kapha", "guna": "Rajas",
        "tattva": "Earth", "varna": "Shudra", "body": "The legs and shins",
        "shakti": "Rohana shakti, the power to make things grow",
        "drive": "To grow something real and beautiful and keep it. Rohini "
                 "wants the harvest, not the idea of the harvest.",
        "gift": "Magnetism, artistic and material fertility, and the patience "
                "to let things ripen. People and resources gather around it.",
        "shadow": "Possessiveness. Attachment to comfort and to being desired. "
                  "Material fixation that quietly becomes the whole point.",
        "wound": "A hunger for security that no amount of security satisfies, "
                 "usually seeded by early scarcity of attention rather than "
                 "of things.",
        "work": "Practise giving away something you like. Rohini grows most "
                "when it proves to itself that it can let go.",
    },
    {
        "name": "Mrigashira", "lord": "Mars", "deity": "Soma, the moon god",
        "symbol": "The head of a deer", "gana": "Deva", "yoni": "Serpent",
        "yoni_gender": "female", "nadi": "Pitta", "guna": "Tamas",
        "tattva": "Earth", "varna": "Servant", "body": "The eyebrows and eyes",
        "shakti": "Prinana shakti, the power to give fulfilment",
        "drive": "To search. Mrigashira is always scenting for something "
                 "better, and the searching is more native to it than the "
                 "finding.",
        "gift": "Curiosity, refinement, a gentle intelligence, and a real nose "
                "for quality in people, work and things.",
        "shadow": "Restlessness that never settles. Perpetual dissatisfaction. "
                  "Suspicion, and a tendency to keep looking after the good "
                  "thing has already arrived.",
        "wound": "A sense that the real thing is always elsewhere, which makes "
                 "arrival feel like settling.",
        "work": "Finish the search consciously. Decide that this is it, and "
                "then stay long enough to find out whether it was.",
    },
    {
        "name": "Ardra", "lord": "Rahu", "deity": "Rudra, the storm",
        "symbol": "A teardrop, a diamond", "gana": "Manushya", "yoni": "Dog",
        "yoni_gender": "female", "nadi": "Vata", "guna": "Tamas",
        "tattva": "Water", "varna": "Butcher", "body": "The hair and the eyes",
        "shakti": "Yatna shakti, the power to make effort",
        "drive": "To break something open so it can be understood. Ardra is "
                 "the storm that clears the air, and it does not apologise "
                 "for the damage on the way.",
        "gift": "Fierce intelligence, emotional honesty, and real transformative "
                "power. Excellent in crisis, research and anything that has to "
                "be taken apart before it can be fixed.",
        "shadow": "Destruction for its own sake. Emotional volatility. "
                  "Cruelty in argument, and a taste for the storm itself.",
        "wound": "Early grief that was not allowed to be expressed, which "
                 "later comes out as intensity in the wrong places.",
        "work": "Let the grief be grief. Ardra converts unfelt sorrow into "
                "anger with remarkable efficiency, and the anger solves nothing.",
    },
    {
        "name": "Punarvasu", "lord": "Jupiter", "deity": "Aditi, the boundless mother",
        "symbol": "A quiver of arrows", "gana": "Deva", "yoni": "Cat",
        "yoni_gender": "female", "nadi": "Vata", "guna": "Sattva",
        "tattva": "Water", "varna": "Vaishya", "body": "The fingers and nose",
        "shakti": "Vasutva prapana shakti, the power to regain what was lost",
        "drive": "To return. Punarvasu is the star of the second chance, and "
                 "it believes, correctly, that things can be restored.",
        "gift": "Resilience, generosity, philosophical calm, and an ability to "
                "begin again without bitterness. Genuinely good at forgiveness.",
        "shadow": "Repeating the same cycle and calling it renewal. Vagueness "
                  "about commitment because there is always another chance. "
                  "Giving away more than it has.",
        "wound": "An early loss of home or safety, which built the conviction "
                 "that nothing is permanent, including the good.",
        "work": "Notice the difference between returning and circling. "
                "Punarvasu grows when one cycle is finally broken rather than "
                "renewed.",
    },
    {
        "name": "Pushya", "lord": "Saturn", "deity": "Brihaspati, teacher of the gods",
        "symbol": "A cow's udder, a lotus", "gana": "Deva", "yoni": "Goat",
        "yoni_gender": "male", "nadi": "Pitta", "guna": "Tamas",
        "tattva": "Water", "varna": "Kshatriya", "body": "The mouth and face",
        "shakti": "Brahmavarchasa shakti, the power to create spiritual energy",
        "drive": "To nourish and protect. Pushya is the most auspicious of the "
                 "twenty-seven precisely because it wants nothing for itself "
                 "first.",
        "gift": "Steadiness, care, moral weight, and the ability to hold other "
                "people while they fall apart. Deep, unglamorous reliability.",
        "shadow": "Over-caretaking that becomes control. Rigidity about how "
                  "things should be done. Martyrdom, and the quiet accounting "
                  "that goes with it.",
        "wound": "Being needed before being loved, and never quite believing "
                 "the second would survive without the first.",
        "work": "Receive something without immediately reciprocating. Pushya "
                "is far better at giving, which is precisely why it should "
                "practise the other side.",
    },
    {
        "name": "Ashlesha", "lord": "Mercury", "deity": "The Nagas, serpent spirits",
        "symbol": "A coiled serpent", "gana": "Rakshasa", "yoni": "Cat",
        "yoni_gender": "male", "nadi": "Kapha", "guna": "Sattva",
        "tattva": "Water", "varna": "Mleccha", "body": "The joints and nails",
        "shakti": "Visasleshana shakti, the power to inflict poison",
        "drive": "To see through people and hold what it learns in reserve. "
                 "Ashlesha understands motive faster than anyone and says less "
                 "about it.",
        "gift": "Penetrating psychological insight, hypnotic presence, healing "
                "capacity, and real mastery of whatever it studies. The best "
                "diagnostician in the zodiac.",
        "shadow": "Manipulation. Using insight as leverage. Coiling around "
                  "people, and a poison that is usually administered as "
                  "concern.",
        "wound": "An early environment where directness was unsafe, so "
                 "intelligence became indirect as a survival measure.",
        "work": "Say the direct thing. Ashlesha's whole liberation is in "
                "learning that it no longer needs the coil to be safe.",
    },
    {
        "name": "Magha", "lord": "Ketu", "deity": "The Pitris, the ancestors",
        "symbol": "A throne, a palanquin", "gana": "Rakshasa", "yoni": "Rat",
        "yoni_gender": "male", "nadi": "Kapha", "guna": "Tamas",
        "tattva": "Water", "varna": "Shudra", "body": "The nose and lips",
        "shakti": "Tyage kshepani shakti, the power to leave the body",
        "drive": "To honour and continue the line. Magha is the seat, and it "
                 "feels the weight of everyone who sat in it before.",
        "gift": "Natural dignity, real authority, respect for tradition, and a "
                "genuine sense of duty to what came before and what comes after.",
        "shadow": "Entitlement. Living off inherited standing rather than "
                  "earning it. Arrogance, and contempt for those without "
                  "lineage.",
        "wound": "An ancestral debt or a family expectation that was never "
                 "negotiable, which makes achievement feel like obligation.",
        "work": "Separate what you inherited from what you chose. Magha only "
                "becomes itself once it stops performing the ancestors.",
    },
    {
        "name": "Purva Phalguni", "lord": "Venus", "deity": "Bhaga, god of delight",
        "symbol": "The front legs of a bed, a hammock", "gana": "Manushya",
        "yoni": "Rat", "yoni_gender": "female", "nadi": "Pitta", "guna": "Rajas",
        "tattva": "Water", "varna": "Brahmin", "body": "The right hand",
        "shakti": "Prajanana shakti, the power to procreate",
        "drive": "To enjoy, create and be adored. Purva Phalguni takes pleasure "
                 "seriously and considers rest a legitimate goal.",
        "gift": "Charm, creativity, generosity, sexual and artistic vitality, "
                "and a genuine talent for making life pleasant for others.",
        "shadow": "Indolence. Vanity. Pleasure pursued past the point of "
                  "returns, and relationships treated as entertainment.",
        "wound": "A need to be found delightful, usually because approval "
                 "arrived early and conditionally.",
        "work": "Do one thing that will never be admired. Purva Phalguni "
                "matures the moment it can act without an audience.",
    },
    {
        "name": "Uttara Phalguni", "lord": "Sun", "deity": "Aryaman, god of contracts",
        "symbol": "The back legs of a bed", "gana": "Manushya", "yoni": "Cow",
        "yoni_gender": "male", "nadi": "Vata", "guna": "Rajas",
        "tattva": "Fire", "varna": "Kshatriya", "body": "The left hand",
        "shakti": "Chayani shakti, the power to accumulate through union",
        "drive": "To build something lasting with another person. Uttara "
                 "Phalguni is the star of the honoured agreement.",
        "gift": "Reliability, generosity within commitment, organisational "
                "skill, and real loyalty. Excellent at partnership of every "
                "kind.",
        "shadow": "Over-dependence on the relationship for identity. Rigidity "
                  "about roles. Resentment when the contract is honoured on "
                  "one side only.",
        "wound": "A promise broken early, which made contracts feel more "
                 "trustworthy than affection.",
        "work": "Ask for renegotiation instead of enduring the old terms. "
                "Uttara Phalguni is unusually bad at admitting an arrangement "
                "has stopped working.",
    },
    {
        "name": "Hasta", "lord": "Moon", "deity": "Savitar, the solar creator",
        "symbol": "A hand, a closed fist", "gana": "Deva", "yoni": "Buffalo",
        "yoni_gender": "female", "nadi": "Vata", "guna": "Rajas",
        "tattva": "Fire", "varna": "Vaishya", "body": "The hands and fingers",
        "shakti": "Hasta sthapaniya agama shakti, the power to put what one "
                  "seeks into one's own hand",
        "drive": "To make things and to make them well. Hasta wants the thing "
                 "in its hand, finished, working.",
        "gift": "Skill, dexterity, cleverness, wit, and the ability to "
                "manifest an idea into an object. The craftsman of the zodiac.",
        "shadow": "Cunning. Sleight of hand, literal and moral. Anxiety, "
                  "control through fussing, and a mind that will not put the "
                  "work down.",
        "wound": "A belief that nothing arrives unless it is personally "
                 "produced, which makes rest feel like risk.",
        "work": "Let something be given to you rather than made by you. Hasta "
                "exhausts itself by treating every good thing as a task.",
    },
    {
        "name": "Chitra", "lord": "Mars", "deity": "Tvashtar, the celestial architect",
        "symbol": "A bright jewel, a pearl", "gana": "Rakshasa", "yoni": "Tiger",
        "yoni_gender": "female", "nadi": "Pitta", "guna": "Tamas",
        "tattva": "Fire", "varna": "Servant", "body": "The neck and forehead",
        "shakti": "Punya chayani shakti, the power to accumulate merit",
        "drive": "To make something beautiful and be recognised for it. Chitra "
                 "is design, form and the pleasure of a thing well shaped.",
        "gift": "Aesthetic brilliance, design sense, charisma, and the ability "
                "to give form to what other people can only feel.",
        "shadow": "Surface over substance. Vanity about appearance and image. "
                  "Illusion built so skilfully that its maker believes it.",
        "wound": "Being valued for how things looked rather than how they "
                 "were, and learning to manage the surface early.",
        "work": "Show the unfinished version. Chitra grows only where it "
                "allows itself to be seen before it is presentable.",
    },
    {
        "name": "Swati", "lord": "Rahu", "deity": "Vayu, the wind",
        "symbol": "A young shoot bending in the wind, coral", "gana": "Deva",
        "yoni": "Buffalo", "yoni_gender": "male", "nadi": "Kapha",
        "guna": "Tamas", "tattva": "Fire", "varna": "Butcher",
        "body": "The chest", "shakti": "Pradhvamsa shakti, the power to scatter",
        "drive": "To be free and self-directed. Swati will bend indefinitely "
                 "and will not be tied.",
        "gift": "Independence, adaptability, diplomacy, business instinct, and "
                "genuine skill at moving between worlds without belonging to "
                "any.",
        "shadow": "Rootlessness. Commitment avoidance dressed as freedom. "
                  "Scattering its own efforts, and restlessness that never "
                  "compounds into anything.",
        "wound": "An early lesson that dependence is dangerous, which turned "
                 "self-sufficiency into a rule rather than a choice.",
        "work": "Commit to one thing for longer than is comfortable. Swati's "
                "gift only becomes an achievement when something is allowed "
                "to take root.",
    },
    {
        "name": "Vishakha", "lord": "Jupiter", "deity": "Indra and Agni",
        "symbol": "A triumphal archway, a potter's wheel", "gana": "Rakshasa",
        "yoni": "Tiger", "yoni_gender": "male", "nadi": "Kapha", "guna": "Rajas",
        "tattva": "Fire", "varna": "Mleccha", "body": "The arms and breasts",
        "shakti": "Vyapana shakti, the power to achieve many fruits",
        "drive": "To arrive. Vishakha is goal-directed to an unusual degree "
                 "and will endure a great deal to reach the thing it named.",
        "gift": "Determination, ambition, endurance, and the capacity to "
                "sustain effort across years. Genuinely achieves what it sets "
                "out to.",
        "shadow": "Ruthlessness near the finish. Envy. Never arriving, because "
                  "a new goal is named the moment the old one is reached.",
        "wound": "A conviction that worth must be won, so achievement is "
                 "compulsory rather than chosen.",
        "work": "Stop at the top of one thing and stay there. Vishakha "
                "consistently robs itself of the arrival it worked for.",
    },
    {
        "name": "Anuradha", "lord": "Saturn", "deity": "Mitra, god of friendship",
        "symbol": "A lotus, a staff", "gana": "Deva", "yoni": "Deer",
        "yoni_gender": "female", "nadi": "Pitta", "guna": "Tamas",
        "tattva": "Fire", "varna": "Shudra", "body": "The stomach",
        "shakti": "Radhana shakti, the power of worship and devotion",
        "drive": "To belong through devotion. Anuradha builds friendship the "
                 "way other stars build careers, patiently and for life.",
        "gift": "Loyalty, warmth under a reserved surface, organisational "
                "ability, and a talent for holding a group together. Succeeds "
                "abroad and among strangers.",
        "shadow": "Devotion to the undeserving. Suppressed anger. Loneliness "
                  "carried privately while appearing entirely fine.",
        "wound": "An early experience of exclusion, which made belonging "
                 "something to be earned continuously rather than assumed.",
        "work": "Say when you are hurt, at the time. Anuradha's friendships "
                "fail not from conflict but from everything it did not "
                "mention.",
    },
    {
        "name": "Jyeshtha", "lord": "Mercury", "deity": "Indra, king of the gods",
        "symbol": "A circular amulet, an earring", "gana": "Rakshasa",
        "yoni": "Deer", "yoni_gender": "male", "nadi": "Vata", "guna": "Sattva",
        "tattva": "Air", "varna": "Servant", "body": "The neck and right side",
        "shakti": "Arohana shakti, the power to rise and conquer",
        "drive": "To be the eldest, the one responsible, the one who carries "
                 "it. Jyeshtha takes the senior position whether or not it "
                 "was offered.",
        "gift": "Authority, protectiveness, courage, occult insight, and real "
                "competence under pressure. Defends its people absolutely.",
        "shadow": "Arrogance. Secrecy. Isolation at the top, and a habit of "
                  "carrying everything alone and then resenting that nobody "
                  "helped.",
        "wound": "Responsibility handed over too young, so needing help became "
                 "the one unacceptable state.",
        "work": "Delegate something that matters. Jyeshtha's isolation is "
                "self-built and only dismantles from the inside.",
    },
    {
        "name": "Mula", "lord": "Ketu", "deity": "Nirriti, goddess of dissolution",
        "symbol": "A bunch of tied roots", "gana": "Rakshasa", "yoni": "Dog",
        "yoni_gender": "male", "nadi": "Vata", "guna": "Tamas",
        "tattva": "Air", "varna": "Butcher", "body": "The feet",
        "shakti": "Barhana shakti, the power to uproot and destroy",
        "drive": "To get to the root, whatever has to be pulled up on the way. "
                 "Mula cannot leave a false foundation standing.",
        "gift": "Radical honesty, investigative depth, philosophical courage, "
                "and genuine capacity for renunciation. Goes where others will "
                "not.",
        "shadow": "Destruction without a plan for afterwards. Nihilism. "
                  "Uprooting good things to see what is underneath.",
        "wound": "An early upheaval that removed the ground entirely, teaching "
                 "it that foundations are illusions worth testing.",
        "work": "Build one thing and leave it standing. Mula's task is not "
                "more dismantling; it is tolerating something that holds.",
    },
    {
        "name": "Purva Ashadha", "lord": "Venus", "deity": "Apas, the waters",
        "symbol": "An elephant tusk, a fan", "gana": "Manushya", "yoni": "Monkey",
        "yoni_gender": "male", "nadi": "Pitta", "guna": "Rajas",
        "tattva": "Air", "varna": "Brahmin", "body": "The thighs",
        "shakti": "Varchagrahana shakti, the power to invigorate",
        "drive": "To convince and to prevail. Purva Ashadha has an unshakeable "
                 "conviction it is right, and it usually persuades the room.",
        "gift": "Eloquence, optimism, courage, and an invigorating effect on "
                "everyone nearby. Genuinely inspiring, and hard to defeat.",
        "shadow": "Stubbornness immune to evidence. Argumentativeness. "
                  "Confidence in a bad position held past all reason.",
        "wound": "Early doubt that was overcome by force of will, which made "
                 "certainty feel like survival.",
        "work": "Change your mind out loud, in front of someone. Purva Ashadha "
                "treats revision as defeat, which is the only thing that "
                "actually defeats it.",
    },
    {
        "name": "Uttara Ashadha", "lord": "Sun", "deity": "The Vishvadevas, the universal gods",
        "symbol": "The planks of a bed, an elephant tusk", "gana": "Manushya",
        "yoni": "Mongoose", "yoni_gender": "neutral", "nadi": "Kapha",
        "guna": "Sattva", "tattva": "Air", "varna": "Kshatriya",
        "body": "The thighs", "shakti": "Apradhrishya shakti, the power to "
                                        "win a victory that cannot be reversed",
        "drive": "To win permanently and rightly. Uttara Ashadha will not take "
                 "a victory it cannot defend on principle.",
        "gift": "Integrity, patience, leadership that lasts, and the rare "
                "ability to win without leaving enemies. Late success that "
                "does not unwind.",
        "shadow": "Rigidity. Self-righteousness. Waiting for perfect conditions "
                  "and calling the delay principle.",
        "wound": "A standard set impossibly high early, so anything less than "
                 "complete feels like failure.",
        "work": "Accept a partial win. Uttara Ashadha loses years to holding "
                "out for the version that never comes.",
    },
    {
        "name": "Shravana", "lord": "Moon", "deity": "Vishnu, the preserver",
        "symbol": "An ear, three footprints", "gana": "Deva", "yoni": "Monkey",
        "yoni_gender": "female", "nadi": "Kapha", "guna": "Rajas",
        "tattva": "Air", "varna": "Mleccha", "body": "The ears",
        "shakti": "Samhanana shakti, the power to connect things together",
        "drive": "To listen and to understand. Shravana learns by receiving, "
                 "and it hears what was not said.",
        "gift": "Deep listening, scholarship, connection-making, and a talent "
                "for being the person who knows how everything relates. "
                "Trusted with what people do not tell others.",
        "shadow": "Gossip. Learning about life instead of living it. Absorbing "
                  "other people's views until its own is unlocatable.",
        "wound": "Being the confidant before being the child, so its own voice "
                 "arrived late and quietly.",
        "work": "Say your own position first, before you have heard the room. "
                "Shravana knows what everyone thinks except itself.",
    },
    {
        "name": "Dhanishta", "lord": "Mars", "deity": "The eight Vasus",
        "symbol": "A drum, a flute", "gana": "Rakshasa", "yoni": "Lion",
        "yoni_gender": "female", "nadi": "Pitta", "guna": "Tamas",
        "tattva": "Ether", "varna": "Servant", "body": "The back",
        "shakti": "Khyapayitri shakti, the power to bring fame and abundance",
        "drive": "To keep the rhythm and be heard doing it. Dhanishta is the "
                 "drum: it sets the tempo everyone else moves to.",
        "gift": "Timing, musicality, wealth-generating instinct, group "
                "leadership, and real generosity when it is doing well.",
        "shadow": "Materialism. Noise mistaken for substance. Emotional "
                  "coldness underneath a very sociable exterior.",
        "wound": "Value learned as performance, so being still feels like "
                 "being nobody.",
        "work": "Sit in silence with someone you love and do not perform. "
                "Dhanishta's intimacy problem is entirely a rhythm problem.",
    },
    {
        "name": "Shatabhisha", "lord": "Rahu", "deity": "Varuna, god of cosmic waters",
        "symbol": "An empty circle, a hundred healers", "gana": "Rakshasa",
        "yoni": "Horse", "yoni_gender": "female", "nadi": "Vata",
        "guna": "Tamas", "tattva": "Ether", "varna": "Butcher",
        "body": "The jaw and chin", "shakti": "Bheshaja shakti, the power to heal",
        "drive": "To find the hidden cause and correct it. Shatabhisha is the "
                 "physician who works alone and does not explain the method.",
        "gift": "Healing capacity, scientific and mystical intelligence at "
                "once, independence, and a genuine ability to see systems "
                "other people cannot.",
        "shadow": "Isolation. Secrecy. Coldness. Curing everyone else while "
                  "refusing all treatment for itself.",
        "wound": "Early solitude that became a preference, then a fortress, "
                 "then a limitation.",
        "work": "Let someone in on the problem before you have solved it. "
                "Shatabhisha is the empty circle, and it can choose to open.",
    },
    {
        "name": "Purva Bhadrapada", "lord": "Jupiter", "deity": "Aja Ekapada, the one-footed goat",
        "symbol": "The front legs of a funeral cot, a two-faced man",
        "gana": "Manushya", "yoni": "Lion", "yoni_gender": "male",
        "nadi": "Vata", "guna": "Sattva", "tattva": "Ether", "varna": "Brahmin",
        "body": "The sides and ribs",
        "shakti": "Yajamana udyamana shakti, the power to raise the spiritual fire",
        "drive": "To burn through the ordinary toward something absolute. "
                 "Purva Bhadrapada is not interested in a moderate life.",
        "gift": "Visionary intensity, spiritual seriousness, fearlessness about "
                "death and the occult, and genuine mystical capacity.",
        "shadow": "Extremism. Two faces: the pious and the appetitive, neither "
                  "admitting the other. Self-punishment mistaken for practice.",
        "wound": "An early exposure to something too large to process, which "
                 "left ordinary life feeling insufficient.",
        "work": "Find the sacred in something small and repetitive. Purva "
                "Bhadrapada's fire consumes it whenever it refuses the "
                "ordinary.",
    },
    {
        "name": "Uttara Bhadrapada", "lord": "Saturn", "deity": "Ahir Budhnya, the serpent of the deep",
        "symbol": "The back legs of a funeral cot, a serpent in the depths",
        "gana": "Manushya", "yoni": "Cow", "yoni_gender": "female",
        "nadi": "Pitta", "guna": "Tamas", "tattva": "Ether", "varna": "Kshatriya",
        "body": "The shins", "shakti": "Varshodyamana shakti, the power to "
                                       "bring the rain",
        "drive": "To go deep and stay calm there. Uttara Bhadrapada holds the "
                 "still water underneath everything moving on the surface.",
        "gift": "Profound patience, wisdom without display, compassion, and "
                "genuine spiritual depth. The steadiest of the twenty-seven.",
        "shadow": "Withdrawal into the depths and never resurfacing. Passivity "
                  "presented as acceptance. Depression that looks like "
                  "equanimity.",
        "wound": "A sorrow absorbed so completely that it became the baseline "
                 "and stopped being visible as sorrow.",
        "work": "Come up and act. Uttara Bhadrapada's wisdom is real and its "
                "stillness is often avoidance wearing the same face.",
    },
    {
        "name": "Revati", "lord": "Mercury", "deity": "Pushan, the nourisher and guide",
        "symbol": "A fish, a drum", "gana": "Deva", "yoni": "Elephant",
        "yoni_gender": "female", "nadi": "Kapha", "guna": "Sattva",
        "tattva": "Ether", "varna": "Shudra", "body": "The feet and ankles",
        "shakti": "Kshiradyapani shakti, the power to nourish and to see "
                  "travellers safely home",
        "drive": "To care for whatever is in its path and see it safely "
                 "onward. Revati is the last star, and it knows how to let go.",
        "gift": "Kindness without agenda, imagination, protection of the weak, "
                "and an unusual ability to finish things gracefully.",
        "shadow": "No boundaries at all. Absorbing everyone's condition. "
                  "Escapism, and a sadness about endings that arrives long "
                  "before they do.",
        "wound": "A porousness that was never taught to close, so other "
                 "people's states have always felt like its own.",
        "work": "Decide in advance what you will not take on, and hold it. "
                "Revati's compassion is genuine and its boundarylessness is "
                "what exhausts it.",
    },
]

# Pada lords follow the navamsa: pada 1 of Ashwini is Aries navamsa, and the
# sequence runs continuously through all 108 padas.
PADA_NAVAMSA_START = 0


def index_of(longitude: float) -> int:
    return int(longitude // SPAN) % 27


def pada_of(longitude: float) -> int:
    within = longitude % SPAN
    return int(within // PADA_SPAN) + 1


def pada_navamsa_sign(longitude: float) -> int:
    """The navamsa sign a pada falls in. 108 padas, 12 signs, 9 each."""
    absolute_pada = int(longitude // PADA_SPAN)      # 0 to 107
    return absolute_pada % 12


def data(index: int) -> dict:
    return NAKSHATRA_DATA[index % 27]


def degrees_in(longitude: float) -> float:
    return longitude % SPAN


def percent_through(longitude: float) -> float:
    return 100.0 * (longitude % SPAN) / SPAN


def is_gandanta(longitude: float) -> dict | None:
    """The torn junction between a water sign and a fire sign.

    Classically the most vulnerable degrees in the zodiac. The last pada of
    Revati, Ashlesha or Jyeshtha, and the first pada of Ashwini, Magha or Mula.
    """
    n = index_of(longitude)
    within = degrees_in(longitude)
    for water, fire in GANDANTA_PAIRS:
        if n == water and within >= SPAN - PADA_SPAN:
            return {
                "side": "water", "nakshatra": NAKSHATRAS[n],
                "note": "In the final pada of %s, the water side of a gandanta "
                        "junction. Classically the most fragile degrees in the "
                        "zodiac: the old cycle has not finished dissolving. "
                        "Read as depth and vulnerability together, and verify "
                        "the birth time, because a few minutes moves it." %
                        NAKSHATRAS[n],
            }
        if n == fire and within < PADA_SPAN:
            return {
                "side": "fire", "nakshatra": NAKSHATRAS[n],
                "note": "In the first pada of %s, the fire side of a gandanta "
                        "junction. A new cycle beginning with nothing "
                        "underneath it yet. Marks unusual capacity bought at "
                        "the price of early instability in that graha's "
                        "matters." % NAKSHATRAS[n],
            }
    return None


def tara_bala(janma_nakshatra: int, target_nakshatra: int) -> dict:
    """Which of the nine taras a nakshatra falls in, counted from the birth star."""
    count = ((target_nakshatra - janma_nakshatra) % 27) + 1
    tara_index = (count - 1) % 9
    t = dict(TARAS[tara_index])
    t["count"] = count
    t["cycle"] = (count - 1) // 9 + 1
    return t


def nakshatra_report(longitude: float, janma: int = None) -> dict:
    """Everything about one position's nakshatra placement."""
    n = index_of(longitude)
    d = data(n)
    pada = pada_of(longitude)
    nav = pada_navamsa_sign(longitude)
    out = {
        "index": n,
        "name": NAKSHATRAS[n],
        "pada": pada,
        "degrees_in": round(degrees_in(longitude), 4),
        "percent": round(percent_through(longitude), 1),
        "pada_navamsa": SIGNS[nav],
        "pada_navamsa_index": nav,
        "pada_lord": _pada_lord(nav),
        "range": "%s to %s" % (_deg(n * SPAN), _deg((n + 1) * SPAN)),
        "gandanta": is_gandanta(longitude),
    }
    out.update({k: d[k] for k in (
        "lord", "deity", "symbol", "gana", "yoni", "yoni_gender", "nadi",
        "guna", "tattva", "varna", "body", "shakti", "drive", "gift",
        "shadow", "wound", "work")})
    out["pada_note"] = _pada_note(d, pada, nav)
    if janma is not None:
        out["tara"] = tara_bala(janma, n)
    return out


def _pada_lord(navamsa_sign: int) -> str:
    from .engine import SIGN_LORDS
    return SIGN_LORDS[navamsa_sign % 12]


def _deg(x: float) -> str:
    sign = int(x // 30) % 12
    within = x - int(x // 30) * 30
    return "%s %02d°%02d'" % (SIGNS[sign][:3], int(within),
                                   round((within % 1) * 60))


_PADA_FLAVOUR = {
    1: ("Dharma pada", "the first quarter, where the nakshatra's energy is "
                       "expressed most directly and most personally"),
    2: ("Artha pada", "the second quarter, where the energy turns practical "
                      "and looks for material form"),
    3: ("Kama pada", "the third quarter, where the energy becomes relational "
                     "and wants connection or expression"),
    4: ("Moksha pada", "the fourth quarter, where the energy turns inward and "
                       "starts letting go of what it built"),
}


def _pada_note(d: dict, pada: int, navamsa_sign: int) -> str:
    label, flavour = _PADA_FLAVOUR[pada]
    lord = _pada_lord(navamsa_sign)
    return ("Pada %d of %d, %s: %s. The navamsa is %s, ruled by %s, so %s's "
            "%s is delivered on %s's terms." % (
                pada, 4, label, flavour, SIGNS[navamsa_sign], lord,
                d["name"], d["shakti"].split(",")[0], lord))


def dispositor_chain(chart, graha: str, max_depth: int = 8) -> dict:
    """Follow the nakshatra lords until the chain repeats.

    A graha delivers through the lord of the nakshatra it occupies. Chain that
    and you reach a loop, because the set is finite. The graha that closes the
    loop is where the chain's results actually land, and in practice it tends
    to dominate the life far more than its own dignity suggests.
    """
    from .engine import nakshatra_lord

    seen, chain = [], []
    current = graha
    while current not in seen and len(chain) < max_depth:
        seen.append(current)
        g = chart.grahas.get(current)
        if g is None:
            break
        lord = nakshatra_lord(g.nakshatra)
        chain.append({
            "graha": current,
            "nakshatra": g.nakshatra_name,
            "pada": g.pada,
            "house": g.house,
            "sign": SIGNS[g.sign],
            "points_to": lord,
        })
        if lord == current:
            return {"chain": chain, "terminates_in": current,
                    "kind": "self",
                    "note": "%s sits in its own nakshatra, so the chain stops "
                            "immediately. It answers to nobody and delivers on "
                            "its own terms." % current}
        current = lord

    loop_start = seen.index(current) if current in seen else 0
    loop = [c["graha"] for c in chain[loop_start:]]
    return {
        "chain": chain,
        "terminates_in": current,
        "loop": loop,
        "kind": "loop" if len(loop) > 1 else "self",
        "note": "The chain from %s runs %s and then closes on %s. Whatever %s "
                "promises is finally delivered through %s, which sits in the "
                "%s. That is where to look when %s's results do not match its "
                "own condition." % (
                    graha, " to ".join(c["graha"] for c in chain), current,
                    graha, current,
                    _ord_safe(chart.grahas[current].house
                              if current in chart.grahas else 0),
                    graha),
    }


def _ord_safe(n: int) -> str:
    if not n:
        return "chart"
    return "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(
        n if n < 20 else n % 10, "th"))
