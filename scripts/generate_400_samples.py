#!/usr/bin/env python3
"""
generate_400_samples.py
Generate 200 new samples (D101-D200, S101-S200) and merge with the existing 200
to produce master_400_with_vad.csv, plus updated annotator task files.
"""

import csv
import json
import random
import os

random.seed(42)

BASE_DIR = "/home/fychao/ill-posed-AffectTrace/00_Paper/TAC/human_labeling_tasks"
INPUT_CSV  = os.path.join(BASE_DIR, "data", "master_200_with_vad.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "master_400_with_vad.csv")
DIST_CSV   = os.path.join(BASE_DIR, "data", "samples_distortion_200.csv")
SAFE_CSV   = os.path.join(BASE_DIR, "data", "samples_safe_200.csv")
ANN_A_CSV  = os.path.join(BASE_DIR, "results", "annotator_A", "task_annotator_A.csv")
ANN_B_CSV  = os.path.join(BASE_DIR, "results", "annotator_B", "task_annotator_B.csv")
ANN_C_CSV  = os.path.join(BASE_DIR, "results", "annotator_C", "task_annotator_C.csv")

MASTER_FIELDS = [
    "sample_id","group","original_text","domain","emotion_true",
    "llm_raw_output","malformation_type","stage1_output","repaired_output",
    "llm_emotion","repaired_emotion","vad_distance","crosses_epsilon",
    "A1_is_distorted","A2_severity","A3_correct_emotion","annotator_notes"
]
ANNOTATOR_FIELDS = [
    "sample_id","original_text","domain","llm_raw_output","malformation_type",
    "stage1_output","repaired_output","llm_emotion","repaired_emotion",
    "A1_is_distorted","A2_severity","A3_correct_emotion","annotator_notes"
]

# ──────────────────────────────────────────────────────────────────────────────
# Text corpora per domain × emotion
# ──────────────────────────────────────────────────────────────────────────────
TEXTS = {
    # --- Yelp ---
    ("Yelp", "joy"): [
        "Best meal of my life. Every dish was crafted with love and skill.",
        "Outstanding dining experience! The chef personally came to our table.",
        "Absolutely blown away by the flavors. Will be back every week.",
        "This place makes me so happy. Warm atmosphere and incredible food.",
        "Five-star service and food that makes your eyes water with joy.",
    ],
    ("Yelp", "frustration"): [
        "Waited 45 minutes for cold food. Staff was completely indifferent.",
        "Three times I tried to order and three times they got it wrong.",
        "Menu says gluten-free options but they had none. Walked out frustrated.",
        "The host was rude and seated us next to the bathroom. Not coming back.",
        "Wrong order, cold soup, and no apology. Absolutely maddening experience.",
    ],
    ("Yelp", "anger"): [
        "Manager was dismissive and refused to fix the wrong order. Outrageous.",
        "Charged me for items I never ordered. This is theft, plain and simple.",
        "They kicked us out 10 minutes before closing. Infuriating and disrespectful.",
        "The server argued with me instead of helping. Never seen anything like it.",
        "Ignored our table for 40 minutes. I am absolutely furious.",
    ],
    ("Yelp", "disgust"): [
        "Found a bug in my salad. Health department will be hearing about this.",
        "The restroom conditions were revolting. How do they pass inspections?",
        "Meat was clearly off. Repulsive smell the moment the plate arrived.",
        "Mold on the bread. Completely unacceptable hygiene standards.",
        "Filthy tables and sticky menus. Disgusting experience from start to finish.",
    ],
    ("Yelp", "sadness"): [
        "Used to be my favorite place. Heartbroken that the quality has fallen so far.",
        "The owner passed away and the new management ruined what was once magical.",
        "Our anniversary dinner was a disappointment. I cried on the way home.",
        "This neighborhood gem is closing down. I'll miss it more than words can say.",
        "Nothing on the menu matches my memories. Sadly, those days are gone.",
    ],
    ("Yelp", "contentment"): [
        "Solid neighborhood spot. Consistently good food at a fair price.",
        "Nothing fancy but always reliable. Comfortable place to unwind.",
        "Pleasant lunch with friends. Portions are generous and service friendly.",
        "Satisfied with the visit. Quiet ambiance and decent wine selection.",
        "A dependable choice for casual dining. Glad it's around the corner.",
    ],
    ("Yelp", "excitement"): [
        "New tasting menu is an adventure! Each course brought a surprise.",
        "Just tried the chef's special — revolutionary flavors I've never tasted!",
        "Opening night buzz was electric. This place is going to be huge.",
        "The live music and fusion menu created the most thrilling dinner I've had.",
        "Can't stop telling everyone about this place. Absolutely electric energy.",
    ],
    ("Yelp", "anxiety"): [
        "I have severe allergies and they were vague about ingredients. Nerve-wracking.",
        "Made a reservation weeks ago but they lost it. Heart was pounding.",
        "The menu had no calorie info and I was anxious about my dietary restrictions.",
        "Unsure if the food would meet my dietary needs — staff seemed unsure too.",
        "Had to double-check every dish. The uncertainty was stressful.",
    ],
    ("Yelp", "neutral"): [
        "Average restaurant. Nothing memorable, nothing bad. Just okay.",
        "Standard menu items. Service was adequate. Prices are normal.",
        "Tried the pasta. It was fine. Would not specifically seek it out again.",
        "Decent enough for a quick lunch. Neither impressed nor disappointed.",
        "The place exists. The food is edible. Not much else to report.",
    ],
    ("Yelp", "annoyance"): [
        "The upcharge for substitutions was irritating. Every little thing costs extra.",
        "Loud music made conversation impossible. Mildly annoying throughout.",
        "They automatically added gratuity on a two-person table. Bit cheeky.",
        "Parking situation is a hassle. Adds unnecessary stress to the meal.",
        "The Wi-Fi password changes daily but no one tells you. Minor but aggravating.",
    ],
    ("Yelp", "fear"): [
        "Saw a rat behind the counter. I'm genuinely scared to eat here again.",
        "Raw chicken in my burger. I'm terrified of what could have happened.",
        "Noticed an employee smoking near the food prep area. Frightening oversight.",
        "No visible food safety certificates displayed. Made me uncomfortable.",
        "Felt unsafe walking to the parking lot alone at night after the meal.",
    ],
    # --- Reddit ---
    ("Reddit", "joy"): [
        "Finally hit my goal weight after a year of hard work. I'm over the moon!",
        "My dog finally learned the trick I've been teaching him for months!",
        "Got into my dream university today. Still can't believe it's real.",
        "Proposed to my partner this morning. She said yes. Best day of my life.",
        "Finished my first marathon! Crossing that finish line was pure bliss.",
    ],
    ("Reddit", "anger"): [
        "I can't believe they changed the policy without any warning. Absolutely furious.",
        "Landlord raised rent 40% overnight. This is predatory and I'm livid.",
        "My coworker got the promotion after stealing my idea. I'm seething.",
        "They deleted years of my account history without notice. Enraging.",
        "The company just laid off 200 people while executives got bonuses. I'm fuming.",
    ],
    ("Reddit", "sadness"): [
        "Lost my job today. Not sure how I'm going to pay rent next month.",
        "My best friend moved across the country. The apartment feels so empty.",
        "My dog passed away last night. Thirteen years of unconditional love.",
        "Third rejection letter this week. Feeling completely defeated.",
        "Watched my childhood home get demolished today. Unexpected grief.",
    ],
    ("Reddit", "fear"): [
        "Received a threatening message from a stranger. Genuinely scared right now.",
        "Doctor found something suspicious on the scan. Waiting for results is terrifying.",
        "Got followed walking home tonight. My hands are still shaking.",
        "Lost my health insurance during a chronic illness flare. I'm petrified.",
        "Heard strange noises outside my apartment for the third night in a row.",
    ],
    ("Reddit", "excitement"): [
        "Just got the news — I got the job! Can't stop smiling!!",
        "My indie game just went viral overnight. 50k downloads in 24 hours!",
        "We're moving to a new city next month! So many possibilities ahead.",
        "Pre-order for my most anticipated game just dropped. Counting down the days!",
        "Just booked tickets to Japan! I've dreamed about this trip for years.",
    ],
    ("Reddit", "frustration"): [
        "Internet has been down for 6 hours and support just keeps putting me on hold.",
        "Government website crashes every time I try to submit my application.",
        "My code works locally but keeps breaking in production. At my wit's end.",
        "Three hours of troubleshooting and it was just a missing semicolon. Kill me.",
        "Platform changed the API and broke all my scripts with zero notice.",
    ],
    ("Reddit", "neutral"): [
        "Just a reminder that the weekly thread is now posted every Monday.",
        "Here is the updated schedule for the event. Times are in UTC.",
        "Posted my results for anyone who was curious. Nothing unexpected.",
        "The documentation has been updated. Check the wiki for details.",
        "Mod team announcement: rules 4 and 5 have been slightly clarified.",
    ],
    ("Reddit", "contentment"): [
        "Finally found a morning routine that works for me. Life feels stable.",
        "Spent the weekend in the garden. Simple pleasures are the best.",
        "My new apartment is small but cozy. I'm genuinely at peace here.",
        "Three years at this job and I still look forward to Mondays. Lucky.",
        "Got a library card after years of meaning to. Happy with this simple win.",
    ],
    ("Reddit", "anxiety"): [
        "Presenting to 500 people tomorrow. Can't sleep, heart racing all night.",
        "Waiting on a medical test result. Every hour feels like a week.",
        "Starting a new job next week. Worried I'm not qualified enough.",
        "Moving abroad in two months. Excitement mixed with constant low-level dread.",
        "Haven't heard back from the interview in two weeks. The uncertainty is crushing.",
    ],
    ("Reddit", "disgust"): [
        "Found out the 'organic' produce was just relabeled regular stock. Gross.",
        "My roommate left moldy food in the fridge for weeks. Absolutely revolting.",
        "Read the ingredient list on this supposedly healthy snack. Appalled.",
        "The gym bathroom situation is genuinely nauseating. Never going back.",
        "Clicked through to that subreddit once by accident. Could not unsee it.",
    ],
    ("Reddit", "annoyance"): [
        "Auto-play videos in every app now. Mildly but constantly irritating.",
        "My neighbor's alarm goes off at 5 AM and they sleep through it every day.",
        "Subscription services added yet another tier. Getting old fast.",
        "Every post on my feed is an ad now. Mildly infuriating.",
        "The self-checkout machine asked me to see an attendant for the third time.",
    ],
    # --- Twitter ---
    ("Twitter", "joy"): [
        "Just got engaged!! Life is so incredibly good right now 💍",
        "Today was perfect in every way. Grateful beyond words.",
        "Got the test results — all clear! Pure relief and happiness!",
        "My art got featured on the front page. Dreams do come true!!",
        "Surprised my mom with a trip home for her birthday. She cried happy tears.",
    ],
    ("Twitter", "anger"): [
        "Done with this app. Censoring real news while letting spam run wild. Disgraceful.",
        "Just got my bill. They added three fees I never agreed to. Absolutely not.",
        "Another data breach and the company just sends a sorry email. Unacceptable.",
        "Flight delayed 4 hours and they just told us now. I am LIVID.",
        "They removed dark mode without asking. Who approved this? I am so angry.",
    ],
    ("Twitter", "excitement"): [
        "Just got the news - I got the job! Can't stop smiling!!",
        "TICKETS SECURED! Finally seeing my favorite band live after 5 years!!",
        "My startup just closed its first funding round!!! This is really happening!",
        "Season finale tonight!!! I have been waiting for this ALL YEAR.",
        "New album drops at midnight. I will not be sleeping tonight!!!",
    ],
    ("Twitter", "sadness"): [
        "Saying goodbye to my childhood pet today. House feels so empty already.",
        "Just heard the news. Gone too soon. Rest in peace.",
        "Didn't get in. Years of preparation and it still wasn't enough.",
        "Watching my city change beyond recognition. Nostalgia hurts.",
        "Can't believe it's been a year since we lost you. Still missing you every day.",
    ],
    ("Twitter", "anxiety"): [
        "Been experiencing these symptoms for weeks and I'm really scared.",
        "Why do I catastrophize everything? My brain won't stop spinning.",
        "Interview in an hour and my hands won't stop shaking.",
        "Refreshing my email every two minutes waiting for that response.",
        "The news cycle today is genuinely making me spiral. Taking a break.",
    ],
    ("Twitter", "frustration"): [
        "Update broke my entire workflow and support has been useless all day.",
        "Third time ordering the same item and it ships the wrong color AGAIN.",
        "Two-factor auth locked me out of my own account. So helpful.",
        "Tried to cancel and they made me sit through 20 minutes of retention calls.",
        "Wifi cutting out every 30 minutes. Working from home is a joke today.",
    ],
    ("Twitter", "neutral"): [
        "New post is up. Link in bio.",
        "Reminder: the poll closes at midnight tonight.",
        "Updating my profile info. Didn't realize it was so outdated.",
        "Weather today: partly cloudy, high of 18.",
        "Changed my username. Same account, new handle.",
    ],
    ("Twitter", "contentment"): [
        "Quiet Sunday morning with coffee and a good book. This is enough.",
        "Hit a small milestone at work today. Feeling steady and grateful.",
        "Three-day weekend was restorative. Back to the week with a clear head.",
        "Made the same recipe my grandmother taught me. All is well.",
        "No drama, no news, just a nice walk and a good meal. Perfect day.",
    ],
    ("Twitter", "disgust"): [
        "Celebrity charity stunt was such obvious PR. Nauseating.",
        "That trend going around is genuinely repulsive. Can we not.",
        "Ads targeting children with junk food should be illegal. Disgusting.",
        "The way they treat their warehouse workers is sickening.",
        "Reading the exposé right now. Every paragraph is more revolting than the last.",
    ],
    ("Twitter", "annoyance"): [
        "Why does every app need a subscription now?? So irritating.",
        "Comment section is the same three arguments every single time.",
        "Packaging had more paper than product. Annoying and wasteful.",
        "Auto-corrected my name AGAIN. I have fixed this setting 100 times.",
        "Spam callers found a new number. Already.",
    ],
    ("Twitter", "fear"): [
        "Something feels very wrong and I don't know who to call.",
        "Read that article on AI job displacement and now I can't sleep.",
        "The wildfire is closer than they said. We are watching from the window.",
        "Heard a noise downstairs at 2 AM. Paralyzed right now.",
        "Test came back inconclusive. I'm terrified what that means.",
    ],
    # --- Medical ---
    ("Medical", "anxiety"): [
        "Been experiencing these symptoms for weeks and I'm really scared about what it means.",
        "My doctor ordered more tests but won't say why. The waiting is unbearable.",
        "I keep googling symptoms and making myself more anxious. Can't stop.",
        "Scheduled for a biopsy next week. Haven't been able to eat properly since.",
        "The pain is inconsistent and I'm worried it's something neurological.",
    ],
    ("Medical", "fear"): [
        "The radiologist flagged something on my scan. I'm absolutely terrified.",
        "My heart has been doing irregular things and I'm scared to be alone.",
        "Doctor mentioned a specialist referral without explaining why. I'm petrified.",
        "Side effects were severe and I'm afraid to take the medication again.",
        "Woke up unable to move my left arm for a minute. Still shaking.",
    ],
    ("Medical", "sadness"): [
        "Just received the diagnosis I feared. Processing the grief right now.",
        "Chronic pain has taken so much from my life. I miss who I used to be.",
        "My treatment isn't working and options are running out. Feeling hopeless.",
        "Can't participate in activities I loved. The loss feels profound.",
        "Watching a family member decline is heartbreaking in ways I can't express.",
    ],
    ("Medical", "frustration"): [
        "Third doctor this month and still no answers. The system has failed me.",
        "Insurance denied the procedure my doctor said I need. Incredibly frustrating.",
        "Waited 6 months for this appointment and it lasted 7 minutes.",
        "The side effects are debilitating but no one takes them seriously.",
        "Prescribed the same medication that didn't work last time. I'm exhausted.",
    ],
    ("Medical", "contentment"): [
        "Six-month check-up came back clean. So relieved and grateful.",
        "Finally found a treatment plan that works. Life feels manageable again.",
        "My doctor actually listened today. Small thing, big difference.",
        "Pain levels have been stable for weeks. Cautiously optimistic.",
        "Physical therapy is working. I walked further than I have in two years.",
    ],
    ("Medical", "neutral"): [
        "Scheduled a routine check-up for next Tuesday. Nothing specific to report.",
        "Following up as directed. No significant changes since last visit.",
        "Lab results have been sent to the doctor. Waiting for review.",
        "Taking prescribed medication as instructed. No questions at this time.",
        "Appointment confirmed for the 18th. Bringing prior records as requested.",
    ],
    ("Medical", "anger"): [
        "Being dismissed by three doctors makes me furious. I know my own body.",
        "The insurance company denied my claim and gave no valid reason. I'm outraged.",
        "They changed my prescription without consulting me. Unacceptable.",
        "Waited 4 hours to be seen for 5 minutes. This system is broken.",
        "The hospital billed me for procedures I didn't receive. I am livid.",
    ],
    ("Medical", "joy"): [
        "Just got the all-clear after two years of treatment. I'm overwhelmed with joy.",
        "Baby's heartbeat was strong at today's scan. Pure happiness.",
        "Remission confirmed. I never thought I'd type those words.",
        "First day pain-free in over a year. I forgot what this felt like.",
        "Surgery was successful. So grateful for the care team and for this second chance.",
    ],
    ("Medical", "disgust"): [
        "The conditions in that clinic were unsanitary. Truly appalling.",
        "Reading about the opioid manufacturer's practices makes me physically ill.",
        "The staff joked about patients in the hallway. Disgusting behavior.",
        "Found out my supplements contain undisclosed fillers. Revolting.",
        "The dismissal of long COVID patients by the medical community is nauseating.",
    ],
    ("Medical", "excitement"): [
        "Just enrolled in the clinical trial for the new treatment! So hopeful.",
        "New medication just got approved and my doctor wants to try it. Finally!",
        "Ran a full mile for the first time post-surgery. Incredible feeling.",
        "Got accepted into the specialist's program that has a two-year waiting list.",
        "New pain management approach is showing real results. Genuinely thrilled.",
    ],
    ("Medical", "annoyance"): [
        "Another appointment reminder text even though I confirmed online. Mildly irritating.",
        "Portal keeps logging me out before I can read my results. So aggravating.",
        "Copay went up again with no explanation in the plan documents.",
        "Had to repeat my full medical history for the fifth provider in this practice.",
        "Prescription auto-refill sent the wrong dosage again. Minor but persistent.",
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# VAD distances for emotion pairs
# ──────────────────────────────────────────────────────────────────────────────

# DISTORTION pairs (vad_distance > 0.5, crosses_epsilon=YES)
DISTORTION_PAIRS = [
    # (llm_emotion, repaired_emotion, vad_distance)
    ("joy",        "sadness",   1.60),
    ("joy",        "anger",     1.59),
    ("joy",        "fear",      1.48),
    ("sadness",    "anger",     1.42),
    ("anger",      "surprise",  1.23),
    ("fear",       "anger",     1.29),
    ("neutral",    "anger",     0.99),
    ("neutral",    "sadness",   0.80),
    ("contentment","sadness",   1.02),
    ("excitement", "fear",      1.29),
]

# SAFE pairs (vad_distance ≤ 0.55, crosses_epsilon=NO)
SAFE_PAIRS = [
    # (llm_emotion, repaired_emotion, vad_distance)
    ("frustration","annoyance", 0.12),
    ("annoyance",  "frustration",0.12),
    ("anger",      "disgust",   0.25),
    ("disgust",    "anger",     0.25),  # added reverse
    ("joy",        "contentment",0.40),
    ("contentment","joy",       0.40),
    ("fear",       "anxiety",   0.14),
    ("anxiety",    "fear",      0.14),  # added reverse
    ("joy",        "surprise",  0.47),
    ("sadness",    "fear",      0.53),
    ("disgust",    "annoyance", 0.28),
    ("annoyance",  "disgust",   0.28),  # added reverse
    ("frustration","disgust",   0.48),
    ("sadness",    "neutral",   0.42),
    ("neutral",    "contentment",0.35),
]

MALFORMATION_TYPES = [
    "missing_closing_brace",
    "truncated_output",
    "schema_field_missing",
    "wrong_value_type",
    "json_syntax_error",
    "duplicate_key",
    "null_emotion_field",
    "encoding_error",
]

# ──────────────────────────────────────────────────────────────────────────────
# JSON builders per malformation type
# ──────────────────────────────────────────────────────────────────────────────

def _rand_intensity():
    return round(random.uniform(0.3, 0.95), 2)

def _polarity(emotion):
    pos = {"joy", "contentment", "excitement", "surprise"}
    neg = {"sadness", "anger", "fear", "disgust", "frustration", "annoyance", "anxiety"}
    if emotion in pos:
        return "positive"
    if emotion in neg:
        return "negative"
    return "neutral"

def build_llm_raw(malformation_type, emotion, polarity, intensity):
    """Return a malformed JSON string."""
    if malformation_type == "missing_closing_brace":
        return '{"emotion": "' + emotion + '", "polarity": "' + polarity + '", "intensity": ' + str(intensity)
    elif malformation_type == "truncated_output":
        s = '{"emotion": "' + emotion + '", "pol'
        return s
    elif malformation_type == "schema_field_missing":
        return '{"polarity": "' + polarity + '", "intensity": ' + str(intensity) + '}'
    elif malformation_type == "wrong_value_type":
        pol_val = "1" if polarity == "positive" else "-1"
        return '{"emotion": "' + emotion + '", "polarity": ' + pol_val + ', "intensity": ' + str(intensity) + '}'
    elif malformation_type == "json_syntax_error":
        return "{\"emotion\": '" + emotion + "', \"polarity\": \"" + polarity + "\"}"
    elif malformation_type == "duplicate_key":
        return '{"emotion": "' + emotion + '", "emotion": "neutral", "polarity": "' + polarity + '"}'
    elif malformation_type == "null_emotion_field":
        return '{"emotion": null, "polarity": "' + polarity + '", "intensity": ' + str(intensity) + '}'
    elif malformation_type == "encoding_error":
        return '{"emotion": "\\u00e9motion_' + emotion + '", "polarity": "' + polarity + '"}'
    else:
        return '{"emotion": "' + emotion + '", "polarity": "' + polarity + '", "intensity": ' + str(intensity) + '}'

def build_stage1(emotion, polarity, intensity):
    return '{"emotion": "' + emotion + '", "polarity": "' + polarity + '", "intensity": ' + str(intensity) + '}'

def build_repaired(emotion, polarity, intensity):
    return '{"emotion": "' + emotion + '", "polarity": "' + polarity + '", "intensity": ' + str(intensity) + '}'

# ──────────────────────────────────────────────────────────────────────────────
# Planning: target distribution for 200 new samples
# ──────────────────────────────────────────────────────────────────────────────
# New domains: Yelp(50), Reddit(50), Twitter(50), Medical(50)
# Each domain: 25 DISTORTION + 25 SAFE
# Malformation types: each type gets exactly 25 new rows (across both groups)
#   → 100 DISTORTION rows × 8 types = 12 or 13 per type in DIST
#   → Actually we want each malformation type to get 25 total NEW rows regardless of group
#   So we cycle over malformation types evenly across 200 rows.

# Emotion target for new samples (to balance the full 400):
# Existing counts (200 rows): joy=41, frustration=27, anger=24, sadness=23, fear=18,
#   disgust=17, neutral=15, contentment=13, annoyance=9, anxiety=8, excitement=5
# Desired roughly equal 400/11 ~ 36 per emotion
# New needed:
#   joy: max(0, 36-41) = 0 (already over, avoid adding more)
#   frustration: 9
#   anger: 12
#   sadness: 13
#   fear: 18
#   disgust: 19
#   neutral: 21
#   contentment: 23
#   annoyance: 27
#   anxiety: 28
#   excitement: 31
# Total needed for balance = 201... adjust proportionally to 200

TARGET_EMOTION_NEW = {
    "excitement": 30,
    "anxiety":    27,
    "annoyance":  25,
    "contentment":22,
    "neutral":    20,
    "disgust":    18,
    "fear":       17,
    "sadness":    13,
    "anger":      12,
    "frustration": 9,
    "joy":         7,   # minimal new joy
}
# Total = 200 ✓

def make_emotion_sequence(total=200):
    """Return list of emotions following TARGET_EMOTION_NEW proportions."""
    seq = []
    for emo, cnt in TARGET_EMOTION_NEW.items():
        seq.extend([emo] * cnt)
    random.shuffle(seq)
    return seq[:total]

def main():
    # --- read existing 200 rows ---
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        existing = list(reader)

    emotion_seq = make_emotion_sequence(200)

    # Assign domains: 50 each
    domains = (["Yelp"] * 50 + ["Reddit"] * 50 + ["Twitter"] * 50 + ["Medical"] * 50)
    random.shuffle(domains)

    # First 100 indices → DISTORTION (D101-D200), next 100 → SAFE (S101-S200)
    # But interleave domains and emotions instead of block-splitting
    # Strategy: split emotion_seq into 100 DISTORTION + 100 SAFE halves
    dist_emotions = emotion_seq[:100]
    safe_emotions  = emotion_seq[100:]

    dist_domains = domains[:100]
    safe_domains  = domains[100:]

    # Malformation cycle: each of 8 types × 25 = 200 new rows (exactly)
    mal_cycle = MALFORMATION_TYPES * 25  # 200 entries, 25 of each
    random.shuffle(mal_cycle)
    dist_mal = mal_cycle[:100]
    safe_mal  = mal_cycle[100:]

    new_rows = []

    # ---- DISTORTION: D101-D200 ----
    for i in range(100):
        sid = f"D{101+i:03d}"
        emo_true = dist_emotions[i]
        domain   = dist_domains[i]
        mal_type = dist_mal[i]

        # Pick a distortion pair where llm_emotion matches emotion_true
        # (i.e., the LLM first detected the correct emotion; repair went wrong)
        matching = [p for p in DISTORTION_PAIRS if p[0] == emo_true]
        if not matching:
            # fall back to any pair; swap to make llm_emotion = emo_true
            pair = random.choice(DISTORTION_PAIRS)
            llm_emo     = emo_true
            repaired_emo = pair[1]
            vad_dist    = pair[2]
        else:
            pair = random.choice(matching)
            llm_emo      = pair[0]
            repaired_emo = pair[1]
            vad_dist     = pair[2]

        # Sample text
        key = (domain, emo_true)
        if key not in TEXTS:
            key = (domain, random.choice(list({k[1] for k in TEXTS if k[0] == domain})))
        text = random.choice(TEXTS[key])

        llm_pol    = _polarity(llm_emo)
        rep_pol    = _polarity(repaired_emo)
        llm_int    = _rand_intensity()
        rep_int    = _rand_intensity()
        s1_int     = _rand_intensity()

        llm_raw  = build_llm_raw(mal_type, llm_emo, llm_pol, llm_int)
        stage1   = build_stage1(llm_emo,    llm_pol, s1_int)
        repaired = build_repaired(repaired_emo, rep_pol, rep_int)

        row = {
            "sample_id":       sid,
            "group":           "DISTORTION",
            "original_text":   text,
            "domain":          domain,
            "emotion_true":    emo_true,
            "llm_raw_output":  llm_raw,
            "malformation_type": mal_type,
            "stage1_output":   stage1,
            "repaired_output": repaired,
            "llm_emotion":     llm_emo,
            "repaired_emotion":repaired_emo,
            "vad_distance":    vad_dist,
            "crosses_epsilon": "YES",
            "A1_is_distorted": "",
            "A2_severity":     "",
            "A3_correct_emotion": "",
            "annotator_notes": "",
        }
        new_rows.append(row)

    # ---- SAFE: S101-S200 ----
    for i in range(100):
        sid = f"S{101+i:03d}"
        emo_true = safe_emotions[i]
        domain   = safe_domains[i]
        mal_type = safe_mal[i]

        # Pick a SAFE pair that involves emo_true
        matching = [p for p in SAFE_PAIRS if p[0] == emo_true or p[1] == emo_true]
        if not matching:
            pair = random.choice(SAFE_PAIRS)
        else:
            pair = random.choice(matching)

        llm_emo      = pair[0]
        repaired_emo = pair[1]
        vad_dist     = pair[2]

        # Align emo_true with llm_emo when possible
        if pair[0] == emo_true:
            llm_emo      = pair[0]
            repaired_emo = pair[1]
        elif pair[1] == emo_true:
            llm_emo      = pair[1]
            repaired_emo = pair[0]

        key = (domain, emo_true)
        if key not in TEXTS:
            key = (domain, random.choice(list({k[1] for k in TEXTS if k[0] == domain})))
        text = random.choice(TEXTS[key])

        llm_pol  = _polarity(llm_emo)
        rep_pol  = _polarity(repaired_emo)
        llm_int  = _rand_intensity()
        rep_int  = _rand_intensity()
        s1_int   = _rand_intensity()

        llm_raw  = build_llm_raw(mal_type, llm_emo, llm_pol, llm_int)
        stage1   = build_stage1(llm_emo,    llm_pol, s1_int)
        repaired = build_repaired(repaired_emo, rep_pol, rep_int)

        row = {
            "sample_id":       sid,
            "group":           "SAFE",
            "original_text":   text,
            "domain":          domain,
            "emotion_true":    emo_true,
            "llm_raw_output":  llm_raw,
            "malformation_type": mal_type,
            "stage1_output":   stage1,
            "repaired_output": repaired,
            "llm_emotion":     llm_emo,
            "repaired_emotion":repaired_emo,
            "vad_distance":    vad_dist,
            "crosses_epsilon": "NO",
            "A1_is_distorted": "",
            "A2_severity":     "",
            "A3_correct_emotion": "",
            "annotator_notes": "",
        }
        new_rows.append(row)

    all_rows = existing + new_rows

    # ── Write master_400_with_vad.csv ──────────────────────────────────────────
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Written {len(all_rows)} rows → {OUTPUT_CSV}")

    # ── Write distortion / safe split files ───────────────────────────────────
    dist_rows = [r for r in all_rows if r["group"] == "DISTORTION"]
    safe_rows  = [r for r in all_rows if r["group"] == "SAFE"]

    with open(DIST_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
        writer.writeheader()
        writer.writerows(dist_rows)
    print(f"Written {len(dist_rows)} distortion rows → {DIST_CSV}")

    with open(SAFE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
        writer.writeheader()
        writer.writerows(safe_rows)
    print(f"Written {len(safe_rows)} safe rows → {SAFE_CSV}")

    # ── Annotator task files ───────────────────────────────────────────────────
    # Read existing annotator A (has 1 real annotation row)
    existing_ann_a = {}
    try:
        with open(ANN_A_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ann_a[row["sample_id"]] = row
    except FileNotFoundError:
        pass

    for ann_path, ann_id in [(ANN_A_CSV, "A"), (ANN_B_CSV, "B"), (ANN_C_CSV, "C")]:
        with open(ann_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ANNOTATOR_FIELDS)
            writer.writeheader()
            for row in all_rows:
                sid = row["sample_id"]
                # Carry over existing annotation for annotator A
                if ann_id == "A" and sid in existing_ann_a:
                    prev = existing_ann_a[sid]
                    ann_row = {
                        "sample_id":       sid,
                        "original_text":   row["original_text"],
                        "domain":          row["domain"],
                        "llm_raw_output":  row["llm_raw_output"],
                        "malformation_type": row["malformation_type"],
                        "stage1_output":   row["stage1_output"],
                        "repaired_output": row["repaired_output"],
                        "llm_emotion":     row["llm_emotion"],
                        "repaired_emotion":row["repaired_emotion"],
                        "A1_is_distorted": prev.get("A1_is_distorted",""),
                        "A2_severity":     prev.get("A2_severity",""),
                        "A3_correct_emotion": prev.get("A3_correct_emotion",""),
                        "annotator_notes": prev.get("annotator_notes",""),
                    }
                else:
                    ann_row = {
                        "sample_id":       sid,
                        "original_text":   row["original_text"],
                        "domain":          row["domain"],
                        "llm_raw_output":  row["llm_raw_output"],
                        "malformation_type": row["malformation_type"],
                        "stage1_output":   row["stage1_output"],
                        "repaired_output": row["repaired_output"],
                        "llm_emotion":     row["llm_emotion"],
                        "repaired_emotion":row["repaired_emotion"],
                        "A1_is_distorted": "",
                        "A2_severity":     "",
                        "A3_correct_emotion": "",
                        "annotator_notes": "",
                    }
                writer.writerow(ann_row)
        print(f"Written annotator {ann_id} task → {ann_path}")

    # ── Summary statistics ─────────────────────────────────────────────────────
    from collections import Counter
    print("\n=== FINAL 400-SAMPLE STATISTICS ===")
    print("Group dist:    ", Counter(r["group"] for r in all_rows))
    print("Domain dist:   ", Counter(r["domain"] for r in all_rows))
    print("Emotion dist:  ", Counter(r["emotion_true"] for r in all_rows))
    print("Malform dist:  ", Counter(r["malformation_type"] for r in all_rows))
    print("crosses_epsilon:", Counter(r["crosses_epsilon"] for r in all_rows))

    print("\n=== NEW 200-SAMPLE STATISTICS ===")
    print("Group dist:    ", Counter(r["group"] for r in new_rows))
    print("Domain dist:   ", Counter(r["domain"] for r in new_rows))
    print("Emotion dist:  ", Counter(r["emotion_true"] for r in new_rows))
    print("Malform dist:  ", Counter(r["malformation_type"] for r in new_rows))

if __name__ == "__main__":
    main()
