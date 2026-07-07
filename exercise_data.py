"""
exercise_data.py — curated cricket-focused exercise library.
Organised by category so it's easy to filter/search in the UI.
Each entry: name, category, muscle_group, equipment, difficulty, duration, calories, cues
"""

EXERCISES = [
    # ---------------- Warm-up / Dynamic Stretch ----------------
    {"name": "Jogging (light)", "category": "Warm-up", "muscle_group": "Full Body", "equipment": "None", "difficulty": "Easy", "duration": "5 min", "calories": 40, "cues": "Slow pace, raise heart rate gradually."},
    {"name": "High Knees", "category": "Warm-up", "muscle_group": "Hip Flexors/Core", "equipment": "None", "difficulty": "Easy", "duration": "2 min", "calories": 25, "cues": "Drive knees to waist height, quick cadence."},
    {"name": "Butt Kicks", "category": "Warm-up", "muscle_group": "Hamstrings", "equipment": "None", "difficulty": "Easy", "duration": "2 min", "calories": 20, "cues": "Heels to glutes, light on feet."},
    {"name": "Arm Circles", "category": "Warm-up", "muscle_group": "Shoulders", "equipment": "None", "difficulty": "Easy", "duration": "1 min", "calories": 10, "cues": "Small to big circles, both directions."},
    {"name": "Leg Swings (Front-Back)", "category": "Dynamic Stretch", "muscle_group": "Hip Flexors/Hamstrings", "equipment": "None", "difficulty": "Easy", "duration": "1 min/side", "calories": 10, "cues": "Hold wall for balance, controlled swing."},
    {"name": "Leg Swings (Side-Side)", "category": "Dynamic Stretch", "muscle_group": "Groin/Adductors", "equipment": "None", "difficulty": "Easy", "duration": "1 min/side", "calories": 10, "cues": "Keep torso upright."},
    {"name": "Walking Lunges with Twist", "category": "Dynamic Stretch", "muscle_group": "Legs/Core", "equipment": "None", "difficulty": "Medium", "duration": "2 min", "calories": 20, "cues": "Twist torso towards front leg each step."},
    {"name": "Torso Rotations", "category": "Dynamic Stretch", "muscle_group": "Core/Obliques", "equipment": "None", "difficulty": "Easy", "duration": "1 min", "calories": 10, "cues": "Rotate from the hips, keep feet planted."},
    {"name": "Inchworm Walkout", "category": "Dynamic Stretch", "muscle_group": "Hamstrings/Shoulders", "equipment": "None", "difficulty": "Medium", "duration": "1 min", "calories": 15, "cues": "Walk hands out to plank, walk feet to hands."},
    {"name": "Shoulder Pass-Throughs (band/towel)", "category": "Dynamic Stretch", "muscle_group": "Shoulders", "equipment": "Resistance band/Towel", "difficulty": "Easy", "duration": "1 min", "calories": 10, "cues": "Wide grip, pass overhead and back slowly."},

    # ---------------- Static Stretch / Cool-down ----------------
    {"name": "Hamstring Stretch (standing)", "category": "Static Stretch", "muscle_group": "Hamstrings", "equipment": "None", "difficulty": "Easy", "duration": "30 sec/side", "calories": 5, "cues": "Straight leg, hinge at hip, don't bounce."},
    {"name": "Quad Stretch (standing)", "category": "Static Stretch", "muscle_group": "Quadriceps", "equipment": "None", "difficulty": "Easy", "duration": "30 sec/side", "calories": 5, "cues": "Pull heel to glute, knees together."},
    {"name": "Calf Stretch (wall)", "category": "Static Stretch", "muscle_group": "Calves", "equipment": "Wall", "difficulty": "Easy", "duration": "30 sec/side", "calories": 5, "cues": "Back heel down, lean into wall."},
    {"name": "Butterfly Groin Stretch", "category": "Static Stretch", "muscle_group": "Groin/Hips", "equipment": "None", "difficulty": "Easy", "duration": "45 sec", "calories": 5, "cues": "Soles together, gently press knees down."},
    {"name": "Child's Pose", "category": "Static Stretch", "muscle_group": "Back/Shoulders", "equipment": "Mat", "difficulty": "Easy", "duration": "45 sec", "calories": 5, "cues": "Hips to heels, arms reaching forward, breathe."},
    {"name": "Cross-Body Shoulder Stretch", "category": "Static Stretch", "muscle_group": "Shoulders", "equipment": "None", "difficulty": "Easy", "duration": "30 sec/side", "calories": 5, "cues": "Pull arm across chest with other hand."},
    {"name": "Cat-Cow Stretch", "category": "Static Stretch", "muscle_group": "Spine", "equipment": "Mat", "difficulty": "Easy", "duration": "1 min", "calories": 8, "cues": "Slow, controlled flexion and extension."},
    {"name": "Seated Spinal Twist", "category": "Static Stretch", "muscle_group": "Spine/Obliques", "equipment": "Mat", "difficulty": "Easy", "duration": "30 sec/side", "calories": 5, "cues": "Sit tall, twist from ribcage."},
    {"name": "Lat Stretch (overhead)", "category": "Static Stretch", "muscle_group": "Lats/Shoulders", "equipment": "None", "difficulty": "Easy", "duration": "30 sec/side", "calories": 5, "cues": "Reach overhead and lean sideways."},

    # ---------------- Foam Rolling ----------------
    {"name": "Foam Roll - Quads", "category": "Foam Rolling", "muscle_group": "Quadriceps", "equipment": "Foam Roller", "difficulty": "Easy", "duration": "1 min/side", "calories": 8, "cues": "Slow roll, pause on tight spots."},
    {"name": "Foam Roll - IT Band", "category": "Foam Rolling", "muscle_group": "IT Band", "equipment": "Foam Roller", "difficulty": "Medium", "duration": "1 min/side", "calories": 8, "cues": "Roll from hip to knee along outer thigh."},
    {"name": "Foam Roll - Upper Back", "category": "Foam Rolling", "muscle_group": "Upper Back", "equipment": "Foam Roller", "difficulty": "Easy", "duration": "1 min", "calories": 8, "cues": "Support head, roll shoulder blades to mid-back."},
    {"name": "Foam Roll - Calves", "category": "Foam Rolling", "muscle_group": "Calves", "equipment": "Foam Roller", "difficulty": "Easy", "duration": "1 min/side", "calories": 8, "cues": "Cross one leg over for deeper pressure."},

    # ---------------- Strength ----------------
    {"name": "Barbell Back Squat", "category": "Strength", "muscle_group": "Legs/Glutes", "equipment": "Barbell", "difficulty": "Medium", "duration": "4x8", "calories": 60, "cues": "Chest up, knees track toes, full depth."},
    {"name": "Deadlift", "category": "Strength", "muscle_group": "Posterior Chain", "equipment": "Barbell", "difficulty": "Hard", "duration": "4x6", "calories": 70, "cues": "Neutral spine, drive through heels."},
    {"name": "Bulgarian Split Squat", "category": "Strength", "muscle_group": "Legs/Glutes", "equipment": "Bench/Dumbbells", "difficulty": "Medium", "duration": "3x10/side", "calories": 45, "cues": "Rear foot elevated, controlled descent."},
    {"name": "Bench Press", "category": "Strength", "muscle_group": "Chest/Triceps", "equipment": "Barbell/Bench", "difficulty": "Medium", "duration": "4x8", "calories": 50, "cues": "Shoulder blades retracted, controlled bar path."},
    {"name": "Pull-Ups", "category": "Strength", "muscle_group": "Back/Biceps", "equipment": "Pull-up bar", "difficulty": "Hard", "duration": "4x max", "calories": 50, "cues": "Full range, avoid swinging."},
    {"name": "Bent-Over Row", "category": "Strength", "muscle_group": "Back", "equipment": "Barbell/Dumbbells", "difficulty": "Medium", "duration": "4x10", "calories": 45, "cues": "Hinge at hips, pull to lower ribs."},
    {"name": "Overhead Press", "category": "Strength", "muscle_group": "Shoulders", "equipment": "Barbell/Dumbbells", "difficulty": "Medium", "duration": "4x8", "calories": 40, "cues": "Brace core, press straight overhead."},
    {"name": "Farmer's Carry", "category": "Strength", "muscle_group": "Grip/Core", "equipment": "Dumbbells", "difficulty": "Medium", "duration": "3x30m", "calories": 40, "cues": "Tall posture, tight grip, steady walk."},
    {"name": "Plank", "category": "Strength", "muscle_group": "Core", "equipment": "None", "difficulty": "Easy", "duration": "3x45 sec", "calories": 15, "cues": "Straight line head to heel, brace abs."},
    {"name": "Side Plank", "category": "Strength", "muscle_group": "Obliques", "equipment": "None", "difficulty": "Medium", "duration": "3x30 sec/side", "calories": 15, "cues": "Hips lifted, straight line."},
    {"name": "Russian Twists", "category": "Strength", "muscle_group": "Obliques", "equipment": "Medicine ball", "difficulty": "Medium", "duration": "3x20", "calories": 20, "cues": "Rotate from torso, feet can stay grounded for beginners."},
    {"name": "Cable Woodchopper", "category": "Strength", "muscle_group": "Core/Rotational Power", "equipment": "Cable machine", "difficulty": "Medium", "duration": "3x12/side", "calories": 25, "cues": "Rotate through hips and torso together, mimics bat/bowling action."},
    {"name": "Nordic Hamstring Curl", "category": "Strength", "muscle_group": "Hamstrings", "equipment": "Partner/Pad", "difficulty": "Hard", "duration": "3x6", "calories": 30, "cues": "Lower slowly, control the eccentric — great for injury prevention."},
    {"name": "Glute Bridge", "category": "Strength", "muscle_group": "Glutes", "equipment": "None", "difficulty": "Easy", "duration": "3x15", "calories": 20, "cues": "Squeeze glutes at top, avoid arching lower back."},
    {"name": "Copenhagen Plank", "category": "Strength", "muscle_group": "Adductors", "equipment": "Bench", "difficulty": "Hard", "duration": "3x20 sec/side", "calories": 15, "cues": "Top leg on bench, hold hips level — key groin-injury prevention drill."},

    # ---------------- Power / Explosive ----------------
    {"name": "Box Jumps", "category": "Power", "muscle_group": "Legs/Explosive", "equipment": "Plyo box", "difficulty": "Medium", "duration": "4x6", "calories": 40, "cues": "Land soft, full hip extension at top."},
    {"name": "Medicine Ball Rotational Throw", "category": "Power", "muscle_group": "Core/Rotational Power", "equipment": "Medicine ball/Wall", "difficulty": "Medium", "duration": "4x8/side", "calories": 35, "cues": "Explosive hip rotation, mimics shot/bowling power."},
    {"name": "Broad Jumps", "category": "Power", "muscle_group": "Legs/Explosive", "equipment": "None", "difficulty": "Medium", "duration": "4x5", "calories": 35, "cues": "Swing arms, land balanced."},
    {"name": "Kettlebell Swing", "category": "Power", "muscle_group": "Posterior Chain", "equipment": "Kettlebell", "difficulty": "Medium", "duration": "4x15", "calories": 45, "cues": "Hip hinge drives the swing, not the arms."},
    {"name": "Depth Jumps", "category": "Power", "muscle_group": "Legs/Reactive Strength", "equipment": "Box", "difficulty": "Hard", "duration": "4x5", "calories": 35, "cues": "Step off, minimal ground contact time on landing."},

    # ---------------- Speed / Agility ----------------
    {"name": "Sprint 20m Repeats", "category": "Speed", "muscle_group": "Full Body", "equipment": "Cones", "difficulty": "Medium", "duration": "6x20m", "calories": 50, "cues": "Full effort, walk-back recovery."},
    {"name": "Shuttle Runs (5-10-5)", "category": "Agility", "muscle_group": "Full Body", "equipment": "Cones", "difficulty": "Medium", "duration": "5 reps", "calories": 45, "cues": "Low hip position on direction change."},
    {"name": "Ladder Drills - Icky Shuffle", "category": "Agility", "muscle_group": "Footwork", "equipment": "Agility ladder", "difficulty": "Medium", "duration": "5x through", "calories": 30, "cues": "Quick feet, stay light on toes."},
    {"name": "T-Drill", "category": "Agility", "muscle_group": "Change of Direction", "equipment": "Cones", "difficulty": "Medium", "duration": "5 reps", "calories": 35, "cues": "Sprint, shuffle, backpedal — mimics fielding movement."},
    {"name": "Reaction Ball Drill", "category": "Agility", "muscle_group": "Reflexes", "equipment": "Reaction ball", "difficulty": "Medium", "duration": "5 min", "calories": 25, "cues": "React to unpredictable bounce — great for slip fielding/keeping."},

    # ---------------- Mobility / Yoga ----------------
    {"name": "Downward Dog", "category": "Yoga/Mobility", "muscle_group": "Hamstrings/Shoulders", "equipment": "Mat", "difficulty": "Easy", "duration": "1 min", "calories": 10, "cues": "Push hips up and back, heels toward floor."},
    {"name": "Pigeon Pose", "category": "Yoga/Mobility", "muscle_group": "Hips/Glutes", "equipment": "Mat", "difficulty": "Medium", "duration": "1 min/side", "calories": 8, "cues": "Square hips, breathe into the stretch."},
    {"name": "Thoracic Rotation (Open Book)", "category": "Yoga/Mobility", "muscle_group": "Thoracic Spine", "equipment": "Mat", "difficulty": "Easy", "duration": "10/side", "calories": 8, "cues": "Key for bowling action and batting swing mobility."},
    {"name": "90/90 Hip Switch", "category": "Yoga/Mobility", "muscle_group": "Hips", "equipment": "Mat", "difficulty": "Medium", "duration": "10 reps", "calories": 10, "cues": "Control the movement, keep chest tall."},
    {"name": "World's Greatest Stretch", "category": "Yoga/Mobility", "muscle_group": "Full Body", "equipment": "None", "difficulty": "Medium", "duration": "5/side", "calories": 15, "cues": "Lunge, rotate, reach — full body mobility combo."},

    # ---------------- Batsman Skill Drills ----------------
    {"name": "Shadow Batting", "category": "Batting Skill", "muscle_group": "Technique", "equipment": "Bat", "difficulty": "Easy", "duration": "10 min", "calories": 30, "cues": "Focus on balance, head position, full follow-through."},
    {"name": "Throwdowns - Front Foot", "category": "Batting Skill", "muscle_group": "Technique", "equipment": "Bat/Balls/Thrower", "difficulty": "Medium", "duration": "20 balls", "calories": 40, "cues": "Weight transfer into the shot, watch the ball onto the bat."},
    {"name": "Throwdowns - Back Foot", "category": "Batting Skill", "muscle_group": "Technique", "equipment": "Bat/Balls/Thrower", "difficulty": "Medium", "duration": "20 balls", "calories": 40, "cues": "Get back and across early, high elbow."},
    {"name": "Reaction Ball Drop Drill", "category": "Batting Skill", "muscle_group": "Reflexes", "equipment": "Tennis ball", "difficulty": "Medium", "duration": "5 min", "calories": 25, "cues": "React fast to unpredictable bounce - sharpens hand-eye."},
    {"name": "Cover Drive Repetition", "category": "Batting Skill", "muscle_group": "Technique", "equipment": "Bat/Balls", "difficulty": "Medium", "duration": "20 reps", "calories": 35, "cues": "Front elbow up, transfer weight into the shot."},
    {"name": "Pull Shot Drill (Bowling Machine)", "category": "Batting Skill", "muscle_group": "Technique", "equipment": "Bowling machine", "difficulty": "Hard", "duration": "20 balls", "calories": 40, "cues": "Rock back, eyes level, roll wrists over the ball."},
    {"name": "Sweep Shot Practice", "category": "Batting Skill", "muscle_group": "Technique", "equipment": "Bat/Balls", "difficulty": "Medium", "duration": "20 reps", "calories": 35, "cues": "Get low, watch the ball, controlled wrist roll."},
    {"name": "Bat Speed Overload/Underload Drill", "category": "Batting Skill", "muscle_group": "Power", "equipment": "Weighted/Light bat", "difficulty": "Medium", "duration": "3x10 swings", "calories": 30, "cues": "Alternate heavy and light bat to build fast-twitch bat speed."},
    {"name": "Power Hitting - Tee Work", "category": "Batting Skill", "muscle_group": "Power", "equipment": "Batting tee", "difficulty": "Medium", "duration": "20 reps", "calories": 35, "cues": "Full hip rotation and extension through the ball."},

    # ---------------- Bowler Skill Drills ----------------
    {"name": "Run-Up Rhythm Drill", "category": "Bowling Skill", "muscle_group": "Technique", "equipment": "None", "difficulty": "Medium", "duration": "10 run-ups", "calories": 30, "cues": "Consistent rhythm and acceleration into the crease."},
    {"name": "Wall Release Point Drill", "category": "Bowling Skill", "muscle_group": "Technique", "equipment": "Wall/Ball", "difficulty": "Easy", "duration": "20 reps", "calories": 25, "cues": "Consistent high release point against the wall target."},
    {"name": "Yorker Target Practice", "category": "Bowling Skill", "muscle_group": "Technique", "equipment": "Stumps/Balls", "difficulty": "Hard", "duration": "20 balls", "calories": 40, "cues": "Full length, target the base of off-stump."},
    {"name": "Bouncer Drill", "category": "Bowling Skill", "muscle_group": "Technique", "equipment": "Balls", "difficulty": "Hard", "duration": "15 balls", "calories": 40, "cues": "Back of a length, control extra effort without losing line."},
    {"name": "Hip Rotation Med Ball Throws", "category": "Bowling Skill", "muscle_group": "Power/Rotational", "equipment": "Medicine ball", "difficulty": "Medium", "duration": "3x10", "calories": 30, "cues": "Drive power from hips through to release, mimics bowling action."},
    {"name": "Shoulder Strength - External Rotation", "category": "Bowling Skill", "muscle_group": "Rotator Cuff", "equipment": "Resistance band", "difficulty": "Easy", "duration": "3x15", "calories": 10, "cues": "Elbow at side, slow controlled rotation — key injury prevention."},
    {"name": "Spin Bowling Wrist Drill", "category": "Bowling Skill", "muscle_group": "Technique", "equipment": "Ball", "difficulty": "Medium", "duration": "20 reps", "calories": 20, "cues": "Focus on wrist/finger snap and revolutions on the ball."},
    {"name": "Line & Length Target Grid", "category": "Bowling Skill", "muscle_group": "Technique", "equipment": "Cones/Marker", "difficulty": "Medium", "duration": "20 balls", "calories": 35, "cues": "Bowl to a marked grid, track consistency %."},

    # ---------------- Wicket Keeper Drills ----------------
    {"name": "Keeper Footwork Ladder", "category": "Wicketkeeping Skill", "muscle_group": "Footwork", "equipment": "Agility ladder", "difficulty": "Medium", "duration": "5 min", "calories": 30, "cues": "Stay low, quick lateral steps."},
    {"name": "Glove Work - Wall Throwdowns", "category": "Wicketkeeping Skill", "muscle_group": "Reflexes", "equipment": "Ball/Wall", "difficulty": "Medium", "duration": "30 balls", "calories": 30, "cues": "Soft hands, watch ball all the way in."},
    {"name": "Diving Drill (Both Sides)", "category": "Wicketkeeping Skill", "muscle_group": "Explosive/Reflexes", "equipment": "Mat", "difficulty": "Hard", "duration": "10/side", "calories": 40, "cues": "Push off back foot explosively, soft landing."},
    {"name": "Standing Up to Stumps Reaction Drill", "category": "Wicketkeeping Skill", "muscle_group": "Reflexes", "equipment": "Stumps/Ball", "difficulty": "Hard", "duration": "20 reps", "calories": 30, "cues": "Stay still until last moment, quick hands to the stumps."},
    {"name": "Explosive Squat Jump (Keeper Stance)", "category": "Wicketkeeping Skill", "muscle_group": "Legs/Explosive", "equipment": "None", "difficulty": "Medium", "duration": "3x10", "calories": 30, "cues": "Start in keeper crouch, explode upward."},

    # ---------------- Fielding Drills ----------------
    {"name": "Slip Catching Cradle", "category": "Fielding Skill", "muscle_group": "Reflexes", "equipment": "Catching cradle/Ball", "difficulty": "Medium", "duration": "20 catches", "calories": 30, "cues": "Soft hands, eyes on ball till it's in your hands."},
    {"name": "High Catch Drill", "category": "Fielding Skill", "muscle_group": "Tracking/Reflexes", "equipment": "Ball", "difficulty": "Medium", "duration": "15 catches", "calories": 30, "cues": "Get in line early, cushion the catch."},
    {"name": "Direct Hit Stump Target", "category": "Fielding Skill", "muscle_group": "Throwing Accuracy", "equipment": "Stumps/Ball", "difficulty": "Medium", "duration": "20 throws", "calories": 30, "cues": "Low flat trajectory, follow through toward target."},
    {"name": "Boundary Sprint & Throw", "category": "Fielding Skill", "muscle_group": "Speed/Power", "equipment": "Ball", "difficulty": "Hard", "duration": "10 reps", "calories": 45, "cues": "Sprint to ball, quick transfer, strong accurate throw."},
    {"name": "Reaction Cone Sprint", "category": "Fielding Skill", "muscle_group": "Reaction/Speed", "equipment": "Cones", "difficulty": "Medium", "duration": "8 reps", "calories": 35, "cues": "React to coach's signal/cone colour, sprint immediately."},
    {"name": "Dive & Recover Drill", "category": "Fielding Skill", "muscle_group": "Full Body", "equipment": "Mat", "difficulty": "Hard", "duration": "10 reps", "calories": 40, "cues": "Dive, field ball, get up quickly into throwing position."},

    # ---------------- Recovery ----------------
    {"name": "Contrast Water Therapy (Hot-Cold)", "category": "Recovery", "muscle_group": "Full Body", "equipment": "Two tubs", "difficulty": "Easy", "duration": "10 min", "calories": 0, "cues": "1 min hot, 1 min cold, repeat — reduces soreness."},
    {"name": "Active Recovery Walk", "category": "Recovery", "muscle_group": "Full Body", "equipment": "None", "difficulty": "Easy", "duration": "15 min", "calories": 50, "cues": "Easy pace, promotes blood flow without fatigue."},
    {"name": "Deep Breathing / Relaxation", "category": "Recovery", "muscle_group": "Nervous System", "equipment": "Mat", "difficulty": "Easy", "duration": "5 min", "calories": 5, "cues": "Slow diaphragmatic breathing, lowers stress hormones."},
    {"name": "Compression + Elevation", "category": "Recovery", "muscle_group": "Legs", "equipment": "Compression sleeves", "difficulty": "Easy", "duration": "20 min", "calories": 0, "cues": "Elevate legs above heart level post-match."},
]

CATEGORIES = sorted(set(e["category"] for e in EXERCISES))
POSITION_CATEGORY_MAP = {
    "Batsman": ["Batting Skill", "Strength", "Power", "Static Stretch", "Dynamic Stretch", "Yoga/Mobility"],
    "Bowler": ["Bowling Skill", "Strength", "Power", "Speed", "Static Stretch", "Dynamic Stretch", "Yoga/Mobility"],
    "Wicket Keeper": ["Wicketkeeping Skill", "Agility", "Static Stretch", "Dynamic Stretch", "Yoga/Mobility"],
    "All Rounder": ["Batting Skill", "Bowling Skill", "Fielding Skill", "Strength", "Power"],
    "Fielder": ["Fielding Skill", "Agility", "Speed", "Static Stretch"],
}


def filter_exercises(category=None, muscle_group=None, equipment=None, difficulty=None, search=None):
    results = EXERCISES
    if category and category != "All":
        results = [e for e in results if e["category"] == category]
    if muscle_group:
        results = [e for e in results if muscle_group.lower() in e["muscle_group"].lower()]
    if equipment:
        results = [e for e in results if equipment.lower() in e["equipment"].lower()]
    if difficulty and difficulty != "All":
        results = [e for e in results if e["difficulty"] == difficulty]
    if search:
        s = search.lower()
        results = [e for e in results if s in e["name"].lower() or s in e["muscle_group"].lower()]
    return results
